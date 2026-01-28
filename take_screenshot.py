"""認証付きスクリーンショット撮影（最小限スクリプト）

Usage:
    uv run python take_screenshot.py <URL_PATH> <OUTPUT_PATH> [-f]

Example:
    uv run python take_screenshot.py "/raw-stocks?mode=search" screenshots/raw_stocks.png -f
"""
import argparse
import asyncio
from pathlib import Path
from src import detect_screen_info, BrowserLauncher

BASE_URL = "http://localhost"


async def run(path: str, output: str, full_page: bool) -> None:
    screen = detect_screen_info()
    launcher = BrowserLauncher(screen)

    async with launcher.launch() as page:
        # ログイン
        await page.goto(f"{BASE_URL}/users/login")
        await page.wait_for_load_state("networkidle")
        await page.fill('input[name="employee_number"]', "1")
        await page.fill('input[name="password"]', "admin")
        await page.click('button[name="login"]')
        await page.wait_for_load_state("networkidle")

        # 対象ページへ遷移
        url = f"{BASE_URL}{path}"
        await page.goto(url)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(1000)

        # スクリーンショット
        out = Path(output)
        out.parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(out), full_page=full_page)
        print(f"Screenshot saved: {out}")


def main():
    parser = argparse.ArgumentParser(description="認証付きスクリーンショット")
    parser.add_argument("path", help="URLパス (例: /raw-stocks?mode=search)")
    parser.add_argument("output", help="出力ファイルパス")
    parser.add_argument("-f", "--full-page", action="store_true")
    args = parser.parse_args()
    asyncio.run(run(args.path, args.output, args.full_page))


if __name__ == "__main__":
    main()
