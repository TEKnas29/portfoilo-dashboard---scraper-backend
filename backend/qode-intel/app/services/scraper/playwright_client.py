from typing import List
from datetime import datetime, timezone
from app.models.tweet import Tweet
from app.utils.text import extract_entities
from app.utils.logging import logger
import asyncio
import sys
import platform
import os

# Fix Windows event loop policy
if platform.system() == 'Windows':
    if sys.version_info >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

try:
    from playwright.async_api import async_playwright
except Exception:  # pragma: no cover
    async_playwright = None


class PlaywrightClient:
    STATE_FILE = "/app/twitter_state.json"

    async def _login(self, page):
        username = os.getenv("TWITTER_USERNAME")
        password = os.getenv("TWITTER_PASSWORD")

        if not username or not password:
            raise RuntimeError("TWITTER_USERNAME and TWITTER_PASSWORD env vars are required")

        logger.info("Logging into Twitter...")
        await page.goto("https://x.com/login", timeout=60000)

        # Step 1: Username
        await page.wait_for_selector('input[name="text"]')
        await page.fill('input[name="text"]', username)
        await page.press('input[name="text"]', "Enter")

        # Step 2: Either "password" OR "confirm username/email"
        try:
            # Try password first
            await page.wait_for_selector('input[name="password"]', timeout=5000)
            logger.info("Password field detected directly")
        except:
            # If no password field, Twitter is asking to re-enter username/email
            logger.info("Twitter asked for username/email confirmation")
            await page.wait_for_selector('input[name="text"]')
            await page.fill('input[name="text"]', username)
            await page.press('input[name="text"]', "Enter")

            # Now wait for password field again
            await page.wait_for_selector('input[name="password"]', timeout=10000)

        # Step 3: Password
        await page.fill('input[name="password"]', password)
        await page.press('input[name="password"]', "Enter")

        # Step 4: Wait for successful login
        await page.wait_for_selector('nav[role="navigation"]', timeout=20000)

        # Save session state
        context = page.context
        await context.storage_state(path=self.STATE_FILE)
        logger.info("Twitter login successful. Session state saved.")

    async def _get_authenticated_page(self, playwright):
        browser = await playwright.firefox.launch(headless=True)
        context = None

        if os.path.exists(self.STATE_FILE):
            logger.info("Loading existing Twitter session state...")
            context = await browser.new_context(storage_state=self.STATE_FILE)
        else:
            logger.info("No saved state found. Will login fresh.")
            context = await browser.new_context()

        page = await context.new_page()
        try:
            await page.goto("https://x.com/home", timeout=15000)
            if "login" in page.url:
                logger.info("Session expired. Performing fresh login...")
                await self._login(page)
        except Exception:
            logger.info("Error checking session. Performing fresh login...")
            await self._login(page)

        return browser, context, page

    async def _scrape_hashtag(self, hashtag: str, since_utc: datetime, until_utc: datetime, limit: int) -> List[Tweet]:
        if async_playwright is None:
            logger.warning("Playwright not installed; skipping fallback.")
            return []

        q = f"%23{hashtag.strip('#')}%20lang%3Aen"
        url = f"https://x.com/search?q={q}&src=typed_query&f=live"
        tweets: List[Tweet] = []
        seen = set()

        try:
            async with async_playwright() as p:
                browser, context, page = await self._get_authenticated_page(p)
                logger.info(f"Navigating to {url}")
                await page.goto(url, timeout=60000)

                last_height = 0
                no_new_count = 0
                MAX_NO_NEW_SCROLLS = 3
                SCROLL_STEP = 1200
                WAIT_AFTER_SCROLL = 2.5

                while len(tweets) < limit:
                    logger.info(f"Length of tweets: {len(tweets)}")

                    try:
                        await page.wait_for_selector("article", timeout=15000)
                        cards = await page.locator("article").all()
                        logger.info(f"Found {len(cards)} tweet cards")

                        new_tweets_this_scroll = 0

                        # Process tweets concurrently
                        async def process_card(card):
                            nonlocal new_tweets_this_scroll
                            try:
                                content_nodes = await card.locator("div[data-testid='tweetText']").all()
                                content = " ".join([await n.inner_text() for n in content_nodes]).strip()
                                if not content:
                                    return

                                tweet_link = await card.locator("a[href*='/status/']").first.get_attribute("href")
                                if not tweet_link:
                                    return
                                tid = tweet_link.split("/status/")[-1].split("?")[0]

                                username_link = await card.locator("a[href^='/']").first.get_attribute("href")
                                username = username_link.strip("/") if username_link and username_link.count("/") == 1 else ""

                                if not tid or tid in seen:
                                    return
                                seen.add(tid)

                                mentions, hashtags_ex = extract_entities(content)
                                ts = datetime.now(timezone.utc)

                                tweets.append(Tweet(
                                    id=tid,
                                    username=username,
                                    timestamp=ts,
                                    content=content,
                                    mentions=mentions,
                                    hashtags=list({*(hashtags_ex), hashtag.strip('#').lower()}),
                                ))
                                new_tweets_this_scroll += 1
                            except Exception as e:
                                logger.debug(f"Error processing card: {e}")

                        await asyncio.gather(*[process_card(card) for card in cards])

                        if len(tweets) >= limit:
                            break

                        # Scroll and wait
                        await page.mouse.wheel(0, SCROLL_STEP)
                        await asyncio.sleep(WAIT_AFTER_SCROLL)

                        new_height = await page.evaluate("() => document.body.scrollHeight")
                        if new_height == last_height and new_tweets_this_scroll == 0:
                            no_new_count += 1
                            logger.info(f"No new tweets ({no_new_count}/{MAX_NO_NEW_SCROLLS})")
                        else:
                            no_new_count = 0
                        last_height = new_height

                        if no_new_count >= MAX_NO_NEW_SCROLLS:
                            logger.info("Reached end of page or no new tweets found")
                            break

                    except Exception as e:
                        logger.error(f"Error during scrolling/waiting: {e}")
                        break

                await browser.close()

        except Exception as e:
            logger.error(f"Error in Playwright setup: {e}")
            if browser:
                try:
                    await browser.close()
                except:
                    pass
            return []

        # Filter by timestamp
        out = [t for t in tweets if since_utc <= t.timestamp <= until_utc]
        logger.info(f"Playwright emitted {len(out)} tweets for {hashtag}")
        return out[:limit]

    async def scrape_async(self, hashtags: List[str], since_utc: datetime, until_utc: datetime, limit: int) -> List[Tweet]:
        try:
            per = max(1, limit // max(1, len(hashtags)))
            logger.info(f"Starting scrape for hashtags: {hashtags}")

            tasks = [self._scrape_hashtag(h, since_utc, until_utc, per) for h in hashtags]
            res = await asyncio.gather(*tasks, return_exceptions=True)

            tweets: List[Tweet] = []
            for idx, r in enumerate(res):
                if isinstance(r, Exception):
                    logger.error(f"Error scraping {hashtags[idx]}: {str(r)}")
                    continue
                if isinstance(r, list):
                    tweets.extend(r)

            uniq = {}
            for t in tweets:
                uniq[t.id] = t

            return list(uniq.values())[:limit]

        except Exception as e:
            logger.error(f"Error in scrape_async: {str(e)}")
            raise
