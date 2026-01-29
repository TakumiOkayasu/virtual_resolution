from contextlib import asynccontextmanager
from typing import AsyncIterator
from urllib.parse import urlparse, urlunparse

from playwright.async_api import async_playwright, Page

from .screen_detector import ScreenInfo


def parse_basic_auth_url(url: str) -> tuple[str, dict[str, str] | None]:
    parsed = urlparse(url)
    if parsed.username and parsed.password:
        creds = {"username": parsed.username, "password": parsed.password}
        clean = parsed._replace(netloc=parsed.hostname + (f":{parsed.port}" if parsed.port else ""))
        return urlunparse(clean), creds
    return url, None


class BrowserLauncher:
    def __init__(
        self,
        screen_info: ScreenInfo,
        viewport_offset: tuple[int, int] = (0, 0),
        headless: bool = False,
        http_credentials: dict[str, str] | None = None,
        browser_channel: str | None = None,
    ):
        self.screen_info = screen_info
        self.viewport_offset = viewport_offset
        self.headless = headless
        self.http_credentials = http_credentials
        self.browser_channel = browser_channel

    def get_viewport_size(self) -> dict[str, int]:
        """Always return FullHD (1920x1080) viewport."""
        return {
            "width": 1920 - self.viewport_offset[0],
            "height": 1080 - self.viewport_offset[1],
        }

    @asynccontextmanager
    async def launch(self) -> AsyncIterator[Page]:
        async with async_playwright() as p:
            viewport = self.get_viewport_size()
            launch_options: dict = {
                "headless": self.headless,
                "args": [
                    "--lang=ja-JP",
                    "--accept-lang=ja-JP,ja",
                    "--no-sandbox",
                    f"--window-size={viewport['width']},{viewport['height']}",
                ],
            }
            if self.browser_channel:
                launch_options["channel"] = self.browser_channel
            browser = await p.chromium.launch(**launch_options)
            context_options: dict = {
                "viewport": self.get_viewport_size(),
                "locale": "ja-JP",
                "timezone_id": "Asia/Tokyo",
                "extra_http_headers": {
                    "Accept-Language": "ja-JP,ja;q=0.9",
                },
                "geolocation": {"latitude": 35.6762, "longitude": 139.6503},
                "permissions": ["geolocation"],
                "ignore_https_errors": True,
            }
            if self.http_credentials:
                context_options["http_credentials"] = self.http_credentials
            context = await browser.new_context(**context_options)
            await context.add_init_script(f"""
                Object.defineProperty(navigator, 'language', {{ get: () => 'ja-JP' }});
                Object.defineProperty(navigator, 'languages', {{ get: () => ['ja-JP', 'ja'] }});

                // Resize prevention
                const _targetWidth = {viewport['width']};
                const _targetHeight = {viewport['height']};
                window.addEventListener('resize', () => {{
                    if (window.innerWidth !== _targetWidth || window.innerHeight !== _targetHeight) {{
                        window.resizeTo(_targetWidth, _targetHeight);
                    }}
                }});
            """)
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
