from typing import List
from datetime import datetime, timezone
from app.models.tweet import Tweet
from app.utils.text import extract_entities
import asyncio
import sys
import platform
import os

# Fix Windows event loop policy
if platform.system() == "Windows":
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
        await page.goto("https://x.com/login", timeout=60000)

        # Username
        await page.fill('input[name="text"]', username)
        await page.press('input[name="text"]', "Enter")

        # Password / alternative flows
        try:
            await page.wait_for_selector('input[name="password"]', timeout=15000)
        except Exception:
            if await page.locator('input[name="text"]').count():
                await page.fill('input[name="text"]', username)
                await page.press('input[name="text"]', "Enter")
                await page.wait_for_selector('input[name="password"]', timeout=20000)
            elif await page.locator('input[name="verification_code"]').count():
                raise RuntimeError(
                    "Verification code required, cannot proceed with automation"
                )
            else:
                raise RuntimeError("Password field not found; unknown login flow")

        # Password
        await page.fill('input[name="password"]', password)
        await page.press('input[name="password"]', "Enter")

        # Successful login
        await page.wait_for_selector('nav[role="navigation"]', timeout=30000)
        await page.context.storage_state(path=self.STATE_FILE)

    async def check_login_state(self) -> bool:
        if not os.path.exists(self.STATE_FILE):
            return False
        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=True)
            try:
                context = await browser.new_context(storage_state=self.STATE_FILE)
                page = await context.new_page()
                await page.goto("https://x.com/home", timeout=15000)
                return "login" not in page.url
            except Exception:
                return False
            finally:
                await browser.close()

    async def _get_authenticated_context(self, playwright):
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

        await page.goto(url, timeout=60000)

        last_height, no_new_count = 0, 0
        MAX_NO_NEW_SCROLLS = 3
        SCROLL_STEP = 2000
        WAIT_AFTER_SCROLL = 2

        sem = asyncio.Semaphore(20)

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
                        hashtags=list({*hashtags_ex, hashtag.strip("#").lower()}),
                    )
                except Exception:
                    return None

        while len(tweets) < limit:
            try:
                await page.wait_for_selector("article", timeout=10000)
                cards = await page.locator("article").all()

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
                        break
                else:
                    no_new_count = 0
                last_height = new_height

            except Exception:
                break

        return tweets[:limit]

    async def scrape_async(
        self, hashtags: List[str], since_utc: datetime, until_utc: datetime, limit: int
    ) -> List[Tweet]:
        if async_playwright is None:
            return []

        tweets: List[Tweet] = []
        per = max(1, limit // max(1, len(hashtags)))
        BATCH_SIZE = 3

        browser = None
        try:
            async with async_playwright() as p:
                browser, context = await self._get_authenticated_context(p)

                for i in range(0, len(hashtags), BATCH_SIZE):
                    batch = hashtags[i : i + BATCH_SIZE]
                    pages = [await context.new_page() for _ in batch]
                    tasks = [
                        self._scrape_hashtag(pages[j], h, since_utc, until_utc, per)
                        for j, h in enumerate(batch)
                    ]

                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    for page in pages:
                        await page.close()

                    for r in results:
                        if isinstance(r, Exception):
                            continue
                        tweets.extend(r)
        finally:
            if browser:
                await browser.close()

        uniq = {t.id: t for t in tweets}
        return list(uniq.values())[:limit]
