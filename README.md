# virtual-resolution

Windows の画面解像度とスケーリングを自動検出し、Playwright で Chromium ブラウザを FullHD (1920x1080) で起動するツール。

## 機能

- Windows の画面解像度とDPIスケーリングを自動検出
- 実効解像度 (物理解像度 / スケーリング倍率) でブラウザを起動
- Chromium / Google Chrome 選択可能
- ウィンドウリサイズ自動防止
- スクリーンショット撮影 (表示領域 / ページ全体)
- Basic認証対応 (URL埋め込み / CLI引数)
- 自己署名証明書のサイトに対応

## 必要条件

- Python 3.12以上
- WSL2 (Windows Subsystem for Linux)
- Playwright の依存ライブラリ

```bash
sudo apt-get install libnspr4 libnss3 libasound2t64
```

### 日本語フォントの設定 (文字化け防止)

日本語サイトを表示する場合、以下のいずれかの方法でフォントを設定してください。

#### 方法1: Windows のフォントを使用 (推奨)

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

#### 方法2: Linux 用フォントをインストール

```bash
sudo apt-get install fonts-noto-cjk
fc-cache -fv
```

## インストール

```bash
uv sync
uv run playwright install chromium

# Google Chrome を使用する場合
uv run playwright install chrome
```

## 使い方

### ブラウザを起動してインタラクティブに操作

```bash
# Chromium (デフォルト)
uv run python main.py https://example.com

# Google Chrome
uv run python main.py https://example.com --chrome
```

インタラクティブモードでは以下のキー操作が可能です:

| キー          | 動作                                                                  |
| ------------- | --------------------------------------------------------------------- |
| `P`           | スクリーンショットを撮影 (screenshots/screenshot_YYYYMMDD_HHMMSS.png) |
| `Q` / `Enter` | ブラウザを閉じて終了                                                  |

### スクリーンショットを撮影

```bash
# デフォルトパスに保存
uv run python main.py https://example.com -s

# パス指定
uv run python main.py https://example.com -s examples/screenshot.png
```

### ページ全体のスクリーンショット

```bash
uv run python main.py https://example.com -s examples/full.png -f
```

### Basic認証が必要なサイト

```bash
# URL埋め込み形式
uv run python main.py "http://user:pass@example.com/"

# CLI引数形式 (こちらが優先)
uv run python main.py https://example.com/ --user admin --password secret
```

## オプション

| オプション           | 説明                                                |
| -------------------- | --------------------------------------------------- |
| `-h`, `--help`       | ヘルプメッセージを表示                              |
| `--version`          | バージョン情報を表示                                |
| `-s`, `--screenshot` | スクリーンショットの保存先パス (省略時: デフォルト) |
| `-f`, `--full-page`  | ページ全体のスクリーンショットを撮影                |
| `--user`             | Basic認証ユーザー名                                 |
| `--password`         | Basic認証パスワード                                 |
| `--chrome`           | Google Chrome を使用 (デフォルト: Chromium)         |

## 動作例

4Kモニター (3840x2160) で200%スケーリングを使用している場合:

```text
Detected: 3840x2160 @ 200%
Effective: 1920x1080
Navigated to: https://example.com
Screenshot saved: examples/screenshot.png
```

ブラウザは常に FullHD (1920x1080) で起動します。

## 開発

```bash
# 依存関係インストール (開発用)
uv sync --dev

# テスト実行
uv run pytest -v

# 型チェック
uv run mypy .
```

## 備考

- ウィンドウサイズを変更しても自動的に元のサイズに戻ります
- 自己署名証明書のサイトは `ignore_https_errors` で対応済み

## ライセンス

MIT
