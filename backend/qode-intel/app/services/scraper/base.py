# app/services/scraper/base.py

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)


class ScraperBase:
    def __init__(self, raw_dir: str = "data/raw/twitter"):
        self.raw_dir = raw_dir
        os.makedirs(self.raw_dir, exist_ok=True)

    async def scrape(self, hashtags: List[str], limit: int = 2000) -> str:
        """
        Scrape tweets with Playwright only.
        Returns path to raw JSONL file.
        """
        job_id = datetime.utcnow().strftime("scrape_%Y%m%d_%H%M%S")
        outfile = os.path.join(self.raw_dir, f"{job_id}.jsonl")

        tweets = await self._scrape_with_playwright(hashtags, limit)

        with open(outfile, "w", encoding="utf-8") as f:
            for tw in tweets:
                f.write(json.dumps(tw, ensure_ascii=False) + "\n")

        logger.info(f"✅ Saved {len(tweets)} tweets to {outfile}")
        return outfile

    # -------------------
    # Playwright Scraper
    # -------------------
    async def _scrape_with_playwright(self, hashtags: List[str], limit: int = 2000) -> List[Dict]:
        from playwright.async_api import async_playwright

        query = " OR ".join([f'%23{tag.lstrip("#")}' for tag in hashtags])
        url = f"https://x.com/search?q={query}&f=live&lang=en"

        tweets = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=60000)

            last_height = 0
            while len(tweets) < limit:
                cards = await page.query_selector_all("article")
                for card in cards[len(tweets):]:
                    try:
                        content = await card.inner_text()
                        tweets.append({
                            "content": content,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                        if len(tweets) >= limit:
                            break
                    except Exception:
                        continue

                # scroll down
                await page.mouse.wheel(0, 3000)
                await asyncio.sleep(2)

                new_height = await page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            await browser.close()

        logger.info(f"✅ Playwright scraped {len(tweets)} tweets")
        return tweets
