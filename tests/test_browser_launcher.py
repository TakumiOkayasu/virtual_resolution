import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from screen_detector import ScreenInfo
from browser_launcher import BrowserLauncher


class TestBrowserLauncher:
    def test_launcher_creation_with_screen_info(self):
        screen = ScreenInfo(width=3840, height=2160, scale_factor=2.0)
        launcher = BrowserLauncher(screen)
        assert launcher.screen_info == screen

    def test_viewport_size_uses_effective_resolution(self):
        screen = ScreenInfo(width=3840, height=2160, scale_factor=2.0)
        launcher = BrowserLauncher(screen)
        viewport = launcher.get_viewport_size()
        assert viewport["width"] == 1920
        assert viewport["height"] == 1080

    def test_viewport_size_with_custom_offset(self):
        screen = ScreenInfo(width=3840, height=2160, scale_factor=2.0)
        launcher = BrowserLauncher(screen, viewport_offset=(0, 100))
        viewport = launcher.get_viewport_size()
        # height reduced by taskbar offset
        assert viewport["width"] == 1920
        assert viewport["height"] == 980


class TestBrowserLauncherAsync:
    @pytest.mark.asyncio
    async def test_launch_creates_browser_and_page(self):
        screen = ScreenInfo(width=1920, height=1080, scale_factor=1.0)
        launcher = BrowserLauncher(screen)

        mock_page = AsyncMock()
        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)

        mock_browser = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)

        mock_playwright = AsyncMock()
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)

        with patch("browser_launcher.async_playwright") as mock_async_pw:
            mock_async_pw.return_value.__aenter__ = AsyncMock(
                return_value=mock_playwright
            )
            mock_async_pw.return_value.__aexit__ = AsyncMock(return_value=None)

            async with launcher.launch() as page:
                assert page == mock_page

    @pytest.mark.asyncio
    async def test_screenshot_saves_to_file(self):
        screen = ScreenInfo(width=1920, height=1080, scale_factor=1.0)
        launcher = BrowserLauncher(screen)

        mock_page = AsyncMock()
        mock_page.screenshot = AsyncMock()

        await launcher.take_screenshot(mock_page, "test.png")
        mock_page.screenshot.assert_called_once_with(path="test.png", full_page=False)

    @pytest.mark.asyncio
    async def test_screenshot_full_page(self):
        screen = ScreenInfo(width=1920, height=1080, scale_factor=1.0)
        launcher = BrowserLauncher(screen)

        mock_page = AsyncMock()
        mock_page.screenshot = AsyncMock()

        await launcher.take_screenshot(mock_page, "test.png", full_page=True)
        mock_page.screenshot.assert_called_once_with(path="test.png", full_page=True)

    @pytest.mark.asyncio
    async def test_navigate_to_url(self):
        screen = ScreenInfo(width=1920, height=1080, scale_factor=1.0)
        launcher = BrowserLauncher(screen)

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()

        await launcher.navigate(mock_page, "https://example.com")
        mock_page.goto.assert_called_once_with("https://example.com")
