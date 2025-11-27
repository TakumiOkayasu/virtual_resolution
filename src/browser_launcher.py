from contextlib import asynccontextmanager
from typing import AsyncIterator

from playwright.async_api import async_playwright, Page

from .screen_detector import ScreenInfo


class BrowserLauncher:
    def __init__(
        self,
        screen_info: ScreenInfo,
        viewport_offset: tuple[int, int] = (0, 0),
        headless: bool = False,
    ):
        self.screen_info = screen_info
        self.viewport_offset = viewport_offset
        self.headless = headless

    def get_viewport_size(self) -> dict[str, int]:
        return {
            "width": self.screen_info.effective_width - self.viewport_offset[0],
            "height": self.screen_info.effective_height - self.viewport_offset[1],
        }

    @asynccontextmanager
    async def launch(self) -> AsyncIterator[Page]:
        async with async_playwright() as p:
            viewport = self.get_viewport_size()
            browser = await p.chromium.launch(
                headless=self.headless,
                args=[
                    "--lang=ja-JP,ja",
                    "--no-sandbox",
                    f"--window-size={viewport['width']},{viewport['height']}",
                    "--disable-resize",
                ],
            )
            context = await browser.new_context(
                viewport=self.get_viewport_size(),
                locale="ja-JP",
            )
            page = await context.new_page()
            try:
                yield page
            finally:
                await context.close()
                await browser.close()

    async def take_screenshot(
        self, page: Page, path: str, full_page: bool = False
    ) -> None:
        await page.screenshot(path=path, full_page=full_page)

    async def navigate(self, page: Page, url: str) -> None:
        await page.goto(url)
