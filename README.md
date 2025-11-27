# virtual-resolution

Windows の画面解像度とスケーリングを自動検出し、Playwright で Chromium ブラウザを適切なサイズで起動するツール。

## 機能

- Windows の画面解像度とDPIスケーリングを自動検出
- 実効解像度 (物理解像度 / スケーリング倍率) でブラウザを起動
- スクリーンショット撮影
- Web操作の自動化基盤

## 必要条件

- Python 3.12以上
- WSL2 (Windows Subsystem for Linux)
- Playwright の依存ライブラリ

```bash
sudo apt-get install libnspr4 libnss3 libasound2t64
```

## インストール

```bash
uv sync
uv run playwright install chromium
```

## 使い方

### ブラウザを起動してインタラクティブに操作

```bash
uv run python main.py https://example.com
```

Enter キーを押すとブラウザが閉じます。

### スクリーンショットを撮影

```bash
uv run python main.py https://example.com -s examples/screenshot.png
```

### ページ全体のスクリーンショット

```bash
uv run python main.py https://example.com -s examples/full.png -f
```

## オプション

| オプション | 説明 |
|-----------|------|
| `-s`, `--screenshot PATH` | スクリーンショットの保存先パス |
| `-f`, `--full-page` | ページ全体のスクリーンショットを撮影 |

## 動作例

4Kモニター (3840x2160) で200%スケーリングを使用している場合:

```
Detected: 3840x2160 @ 200%
Effective: 1920x1080
Navigated to: https://example.com
Screenshot saved: examples/screenshot.png
```

ブラウザは実効解像度 (1920x1080) で起動します。
