import asyncio
from pyppeteer import launch
from typing import Dict
import os
from contextlib import asynccontextmanager

class BrowserManager:
    _browser = None
    _pages: Dict = {}  # Track pages by URL to prevent duplicate scraping
    _reference_count = 0
    _lock = asyncio.Lock()
    
    @classmethod
    async def get_browser(cls):
        async with cls._lock:
            if not cls._browser:
                cls._browser = await launch(
                    executablePath=os.getenv("CHROMIUM_PATH"),
                    headless=True,
                    args=['--no-sandbox', '--disable-dev-shm-usage'],
                    autoClose=False
                )
            cls._reference_count += 1
        return cls._browser

    @classmethod
    @asynccontextmanager
    async def get_page(cls, url: str):
        browser = await cls.get_browser()
        page = None
        try:
            page = await browser.newPage()
            cls._pages[url] = page
            yield page
        finally:
            if page:
                try:
                    # Remove from tracking dict first
                    if url in cls._pages:
                        del cls._pages[url]
                    
                    # Check if the browser is still alive before closing the page
                    if cls._browser and not page.isClosed():
                        try:
                            await page.close()
                        except Exception as e:
                            print(f"Error closing page: {e}")
                except Exception as e:
                    print(f"Error during page cleanup for {url}: {e}")
                
                # Update reference count and potentially close browser
                async with cls._lock:
                    cls._reference_count -= 1
                    if cls._reference_count == 0:
                        try:
                            if cls._browser:
                                await cls._browser.close()
                        except Exception as e:
                            print(f"Error closing browser: {e}")
                        finally:
                            cls._browser = None

    @classmethod
    async def close_browser(cls):
        """Close the browser if it exists"""
        async with cls._lock:
            if cls._browser:
                try:
                    await cls._browser.close()
                except Exception as e:
                    print(f"Error during browser closure: {e}")
                finally:
                    cls._browser = None
                    cls._reference_count = 0
                    cls._pages.clear()
