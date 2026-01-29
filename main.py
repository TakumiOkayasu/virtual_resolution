import argparse
import asyncio
import sys
import termios
import tty
from datetime import datetime
from pathlib import Path

from src import detect_screen_info, BrowserLauncher
from src.browser_launcher import parse_basic_auth_url

__version__ = "1.0.0"
SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


def read_key() -> str:
    """Read a single key from stdin without waiting for Enter."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


async def interactive_mode(launcher: BrowserLauncher, page, full_page: bool) -> None:
    """Interactive mode: P for screenshot, Q/Enter to quit."""
    print("Interactive mode: [P] Screenshot, [Q/Enter] Quit")
    loop = asyncio.get_event_loop()

    while True:
        key = await loop.run_in_executor(None, read_key)
        key_lower = key.lower()

        if key_lower == "p":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            path = SCREENSHOT_DIR / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            await launcher.take_screenshot(page, str(path), full_page=full_page)
            print(f"Screenshot saved: {path}")
        elif key_lower == "q" or key in ("\r", "\n"):
            break


async def run(
    url: str,
    screenshot_path: str | None,
    full_page: bool,
    user: str | None = None,
    password: str | None = None,
    use_chrome: bool = False,
) -> None:
    screen = detect_screen_info()
    print(f"Detected: {screen.width}x{screen.height} @ {screen.scale_factor * 100:.0f}%")
    print(f"Effective: {screen.effective_width}x{screen.effective_height}")

    url, url_creds = parse_basic_auth_url(url)
    if user and password:
        http_credentials = {"username": user, "password": password}
    elif url_creds:
        http_credentials = url_creds
    else:
        http_credentials = None

    browser_channel = "chrome" if use_chrome else None
    launcher = BrowserLauncher(screen, http_credentials=http_credentials, browser_channel=browser_channel)

    async with launcher.launch() as page:
        await launcher.navigate(page, url)
        print(f"Navigated to: {url}")

        if screenshot_path:
            path = Path(screenshot_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            await launcher.take_screenshot(page, screenshot_path, full_page=full_page)
            print(f"Screenshot saved: {screenshot_path}")
        else:
            await interactive_mode(launcher, page, full_page)


def main() -> None:
    epilog = """\
使用例:
  %(prog)s https://example.com/
      指定URLをブラウザで開く（インタラクティブモード）

  %(prog)s https://example.com/ -s
      スクリーンショットを撮影して終了（デフォルト: screenshots/screenshot.png）

  %(prog)s https://example.com/ -s /path/to/image.png -f
      ページ全体のスクリーンショットを指定パスに保存

  %(prog)s "http://user:pass@example.com/"
      Basic認証が必要なサイトにアクセス（URL埋め込み形式）

  %(prog)s https://example.com/ --user admin --password secret
      Basic認証が必要なサイトにアクセス（CLI引数形式）

  %(prog)s https://example.com/ --chrome
      Chromiumの代わりにGoogle Chromeを使用

インタラクティブモード:
  [P] スクリーンショットを撮影（タイムスタンプ付きファイル名で保存）
  [Q] または [Enter] で終了

注意事項:
  - 日本語文字化け対策: READMEの「日本語フォントの設定」を参照
  - Chromeを使用するには事前に `playwright install chrome` が必要
"""
    parser = argparse.ArgumentParser(
        prog="virtual-resolution",
        description="WSL2環境からWindowsの画面解像度とDPIスケーリングを自動検出し、"
        "PlaywrightでブラウザをFullHD (1920x1080) で起動する自動化ツール",
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
    )
    # グループ名を日本語化
    parser._positionals.title = "必須引数"
    parser._optionals.title = "オプション"

    parser.add_argument("-h", "--help", action="help", help="このヘルプメッセージを表示して終了")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}", help="バージョン情報を表示して終了")
    parser.add_argument(
        "url",
        help="アクセスするURL（例: https://example.com/, http://user:pass@example.com/）",
    )
    parser.add_argument(
        "-s",
        "--screenshot",
        metavar="PATH",
        nargs="?",
        const=str(SCREENSHOT_DIR / "screenshot.png"),
        help=f"スクリーンショットの保存先パス (省略時: {SCREENSHOT_DIR}/screenshot.png)",
    )
    parser.add_argument(
        "-f", "--full-page", action="store_true", help="ページ全体のスクリーンショットを撮影"
    )
    parser.add_argument("--user", help="Basic認証ユーザー名")
    parser.add_argument("--password", help="Basic認証パスワード")
    parser.add_argument(
        "--chrome", action="store_true", help="Google Chromeを使用 (デフォルト: Chromium)"
    )

    args = parser.parse_args()
    asyncio.run(run(args.url, args.screenshot, args.full_page, args.user, args.password, args.chrome))


if __name__ == "__main__":
    main()
