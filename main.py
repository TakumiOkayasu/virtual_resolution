import argparse
import asyncio

from screen_detector import detect_screen_info
from browser_launcher import BrowserLauncher


async def run(url: str, screenshot_path: str | None, full_page: bool) -> None:
    screen = detect_screen_info()
    print(f"Detected: {screen.width}x{screen.height} @ {screen.scale_factor * 100:.0f}%")
    print(f"Effective: {screen.effective_width}x{screen.effective_height}")

    launcher = BrowserLauncher(screen)

    async with launcher.launch() as page:
        await launcher.navigate(page, url)
        print(f"Navigated to: {url}")

        if screenshot_path:
            await launcher.take_screenshot(page, screenshot_path, full_page=full_page)
            print(f"Screenshot saved: {screenshot_path}")
        else:
            print("Press Enter to close browser...")
            await asyncio.get_event_loop().run_in_executor(None, input)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="画面解像度を自動検出してChromiumブラウザを起動するツール"
    )
    parser.add_argument("url", help="アクセスするURL")
    parser.add_argument(
        "-s", "--screenshot", metavar="PATH", help="スクリーンショットの保存先パス"
    )
    parser.add_argument(
        "-f", "--full-page", action="store_true", help="ページ全体のスクリーンショットを撮影"
    )

    args = parser.parse_args()
    asyncio.run(run(args.url, args.screenshot, args.full_page))


if __name__ == "__main__":
    main()
