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

### 日本語フォントの設定 (文字化け防止)

日本語サイトを表示する場合、以下のいずれかの方法でフォントを設定してください。

**方法 1: Windows のフォントを使用 (推奨)**

```bash
sudo tee /etc/fonts/local.conf << 'EOF'
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
  <dir>/mnt/c/Windows/Fonts</dir>
</fontconfig>
EOF

sudo fc-cache -fv
```

**方法 2: Linux 用フォントをインストール**

```bash
sudo apt-get install fonts-noto-cjk
fc-cache -fv
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
