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

    async def login_and_save_state(self, username: str, password: str) -> bool:
        """Login to Twitter and save the authentication state"""
        if not username or not password:
            raise ValueError("Username and password are required")

        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                return await self._perform_login(page, username, password)
            finally:
                await browser.close()

    async def _perform_login(self, page, username: str, password: str) -> bool:

        logger.info("Logging into Twitter...")
        await page.goto("https://x.com/login", timeout=60000)

        # Step 1: Username
        await page.fill('input[name="text"]', username)
        await page.press('input[name="text"]', "Enter")

        # Step 2: Wait for password or alternative flow
        try:
            await page.wait_for_selector('input[name="password"]', timeout=15000)
            logger.info("Password field detected directly")
        except Exception:
            logger.info("Twitter asked for additional confirmation")
            try:
                if await page.locator('input[name="text"]').count():
                    logger.info("Confirming username/email again")
                    await page.fill('input[name="text"]', username)
                    await page.press('input[name="text"]', "Enter")
                    await page.wait_for_selector('input[name="password"]', timeout=20000)
                elif await page.locator('input[name="verification_code"]').count():
                    logger.error("Twitter requested verification code (not supported)")
                    raise RuntimeError("Verification code required, cannot proceed with automation")
                else:
                    raise RuntimeError("Password field not found; unknown login flow")
            except Exception as e:
                # Capture screenshot for debugging
                await page.screenshot(path="/app/login_debug.png")
                logger.error(f"Login failed; screenshot saved at /app/login_debug.png: {e}")
                raise

        # Step 3: Password
        await page.fill('input[name="password"]', password)
        await page.press('input[name="password"]', "Enter")

        # Step 4: Wait for successful login
        await page.wait_for_selector('nav[role="navigation"]', timeout=30000)

        # Save session state
        await page.context.storage_state(path=self.STATE_FILE)
        logger.info("Twitter login successful. Session state saved.")

    async def check_login_state(self) -> bool:
        """Check if the saved login state is valid"""
        if not os.path.exists(self.STATE_FILE):
            return False

        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=True)
            try:
                context = await browser.new_context(storage_state=self.STATE_FILE)
                page = await context.new_page()
                await page.goto("https://x.com/home", timeout=15000)
                return "login" not in page.url
            except Exception as e:
                logger.error(f"Error checking login state: {e}")
                return False
            finally:
                await browser.close()

    async def _get_authenticated_context(self, playwright):
        """Get an authenticated browser context using saved state"""
        if not os.path.exists(self.STATE_FILE):
            raise RuntimeError("No login state found. Please login first.")

        browser = await playwright.firefox.launch(headless=True)
        try:
            context = await browser.new_context(storage_state=self.STATE_FILE)
            page = await context.new_page()
            await page.goto("https://x.com/home", timeout=15000)
            
            if "login" in page.url:
                await browser.close()
                raise RuntimeError("Session expired. Please login again.")
                
            return browser, context
        except Exception as e:
            await browser.close()
            raise RuntimeError(f"Failed to authenticate: {e}")

    async def _scrape_hashtag(
        self, page, hashtag: str, since_utc: datetime, until_utc: datetime, limit: int
    ) -> List[Tweet]:
        q = f"%23{hashtag.strip('#')}%20lang%3Aen"
        url = f"https://x.com/search?q={q}&src=typed_query&f=live"
        tweets: List[Tweet] = []
        seen = set()

        logger.info(f"Navigating to {url}")
        await page.goto(url, timeout=60000)

        last_height, no_new_count = 0, 0
        MAX_NO_NEW_SCROLLS = 3
        SCROLL_STEP = 2000
        WAIT_AFTER_SCROLL = 2

        sem = asyncio.Semaphore(20)  # limit concurrent card processing

        async def process_card(card):
            async with sem:
                try:
                    data = await card.evaluate(
                        """(el) => {
                        const content = [...el.querySelectorAll("div[data-testid='tweetText']")]
                            .map(n => n.innerText).join(" ").trim();
                        const link = el.querySelector("a[href*='/status/']")?.getAttribute("href");
                        const user = el.querySelector("a[href^='/']")?.getAttribute("href") || "";
                        return { content, link, user };
                    }"""
                    )

                    if not data or not data["content"] or not data["link"]:
                        return None

                    tid = data["link"].split("/status/")[-1].split("?")[0]
                    if tid in seen:
                        return None
                    seen.add(tid)

                    ts = datetime.now(timezone.utc)
                    if not (since_utc <= ts <= until_utc):
                        return None

                    mentions, hashtags_ex = extract_entities(data["content"])

                    return Tweet(
                        id=tid,
                        username=data["user"].strip("/"),
                        timestamp=ts,
                        content=data["content"],
                        mentions=mentions,
                        hashtags=list({*hashtags_ex, hashtag.strip('#').lower()}),
                    )
                except Exception as e:
                    logger.debug(f"Error processing card: {e}")
                    return None

        while len(tweets) < limit:
            try:
                await page.wait_for_selector("article", timeout=10000)
                cards = await page.locator("article").all()
                logger.info(f"Found {len(cards)} tweet cards")

                results = await asyncio.gather(*[process_card(c) for c in cards])
                new_items = [r for r in results if r]
                tweets.extend(new_items)

                if len(tweets) >= limit:
                    break

                await page.evaluate(f"window.scrollBy(0, {SCROLL_STEP})")
                await asyncio.sleep(WAIT_AFTER_SCROLL)

                new_height = await page.evaluate("() => document.body.scrollHeight")
                if new_height == last_height and not new_items:
                    no_new_count += 1
                    if no_new_count >= MAX_NO_NEW_SCROLLS:
                        logger.info("Reached end of page or no new tweets found")
                        break
                else:
                    no_new_count = 0
                last_height = new_height

            except Exception as e:
                logger.error(f"Error during scrolling/waiting: {e}")
                break

        return tweets[:limit]

    async def scrape_async(
        self, hashtags: List[str], since_utc: datetime, until_utc: datetime, limit: int
    ) -> List[Tweet]:
        if async_playwright is None:
            logger.warning("Playwright not installed; skipping scrape.")
            return []

        tweets: List[Tweet] = []
        per = max(1, limit // max(1, len(hashtags)))

        browser = None
        try:
            async with async_playwright() as p:
                browser, context = await self._get_authenticated_context(p)
                page = await context.new_page()

                tasks = [self._scrape_hashtag(page, h, since_utc, until_utc, per) for h in hashtags]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                for idx, r in enumerate(results):
                    if isinstance(r, Exception):
                        logger.error(f"Error scraping {hashtags[idx]}: {r}")
                        continue
                    tweets.extend(r)

        finally:
            if browser:
                await browser.close()

        uniq = {t.id: t for t in tweets}
        return list(uniq.values())[:limit]
