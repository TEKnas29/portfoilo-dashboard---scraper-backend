import asyncio
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def main():
    try:
        logger.info("Starting Playwright test")
        async with async_playwright() as p:
            logger.info("Installing Firefox")
            await p.firefox.install()
            logger.info("Launching Firefox")
            browser = await p.firefox.launch(headless=True)
            logger.info("Creating new page")
            page = await browser.new_page()
            logger.info("Navigating to example.com")
            await page.goto("https://example.com")
            logger.info("Getting page title")
            title = await page.title()
            print(f"Page title: {title}")
            await browser.close()
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
