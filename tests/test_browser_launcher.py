import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from src import ScreenInfo, BrowserLauncher
from src.browser_launcher import parse_basic_auth_url


class TestBrowserLauncher:
    def test_launcher_creation_with_screen_info(self):
        screen = ScreenInfo(width=3840, height=2160, scale_factor=2.0)
        launcher = BrowserLauncher(screen)
        assert launcher.screen_info == screen

    def test_viewport_size_returns_fullhd(self):
        """Viewport is always FullHD regardless of screen info."""
        screen = ScreenInfo(width=3840, height=2160, scale_factor=2.0)
        launcher = BrowserLauncher(screen)
        viewport = launcher.get_viewport_size()
        assert viewport["width"] == 1920
        assert viewport["height"] == 1080

    def test_viewport_size_returns_fullhd_for_any_screen(self):
        """Viewport is FullHD even with different screen resolutions."""
        screen = ScreenInfo(width=2560, height=1440, scale_factor=1.5)
        launcher = BrowserLauncher(screen)
        viewport = launcher.get_viewport_size()
        assert viewport["width"] == 1920
        assert viewport["height"] == 1080

    def test_viewport_size_with_custom_offset(self):
        screen = ScreenInfo(width=3840, height=2160, scale_factor=2.0)
        launcher = BrowserLauncher(screen, viewport_offset=(0, 100))
        viewport = launcher.get_viewport_size()
        # FullHD with height reduced by offset
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

        with patch("src.browser_launcher.async_playwright") as mock_async_pw:
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

    @pytest.mark.asyncio
    async def test_launch_with_http_credentials(self):
        screen = ScreenInfo(width=1920, height=1080, scale_factor=1.0)
        creds = {"username": "user", "password": "pass"}
        launcher = BrowserLauncher(screen, http_credentials=creds)

        mock_page = AsyncMock()
        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)

        mock_browser = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)

        mock_playwright = AsyncMock()
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)

        with patch("src.browser_launcher.async_playwright") as mock_async_pw:
            mock_async_pw.return_value.__aenter__ = AsyncMock(
                return_value=mock_playwright
            )
            mock_async_pw.return_value.__aexit__ = AsyncMock(return_value=None)

            async with launcher.launch() as page:
                assert page == mock_page

            call_kwargs = mock_browser.new_context.call_args[1]
            assert call_kwargs["http_credentials"] == creds

    @pytest.mark.asyncio
    async def test_launch_without_http_credentials(self):
        screen = ScreenInfo(width=1920, height=1080, scale_factor=1.0)
        launcher = BrowserLauncher(screen)

        mock_page = AsyncMock()
        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)

        mock_browser = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)

        mock_playwright = AsyncMock()
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)

        with patch("src.browser_launcher.async_playwright") as mock_async_pw:
            mock_async_pw.return_value.__aenter__ = AsyncMock(
                return_value=mock_playwright
            )
            mock_async_pw.return_value.__aexit__ = AsyncMock(return_value=None)

            async with launcher.launch() as page:
                assert page == mock_page

            call_kwargs = mock_browser.new_context.call_args[1]
            assert "http_credentials" not in call_kwargs


class TestParseBasicAuthUrl:
    def test_url_with_credentials(self):
        url, creds = parse_basic_auth_url("http://user:pass@example.com/path")
        assert url == "http://example.com/path"
        assert creds == {"username": "user", "password": "pass"}

    def test_url_without_credentials(self):
        url, creds = parse_basic_auth_url("https://example.com/path")
        assert url == "https://example.com/path"
        assert creds is None

    def test_url_with_port_and_credentials(self):
        url, creds = parse_basic_auth_url("http://admin:secret@localhost:8080/app")
        assert url == "http://localhost:8080/app"
        assert creds == {"username": "admin", "password": "secret"}

    def test_url_with_query_and_credentials(self):
        url, creds = parse_basic_auth_url("http://u:p@host.com/path?q=1&r=2")
        assert url == "http://host.com/path?q=1&r=2"
        assert creds == {"username": "u", "password": "p"}
