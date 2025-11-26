# LogiShift 記事自動生成ツール

Gemini APIを使用してSEO最適化された記事を自動生成し、WordPressに投稿するツールです。

## 機能

- ✅ キーワードから高品質な記事を自動生成（約4,000〜5,000文字）
- ✅ WordPressへの自動投稿（下書き or 予約投稿）
- ✅ MarkdownからHTMLへの自動変換
- ✅ スケジュール投稿機能

## セットアップ

### 1. 仮想環境の作成と依存関係のインストール

```bash
cd automation
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env` ファイルを作成し、以下の情報を設定：

```bash
# Gemini API
GEMINI_API_KEY=your_api_key_here

# WordPress
WP_URL=http://localhost:8000
WP_USER=your_username
WP_APP_PASSWORD=your_password
```

**取得方法:**
- **Gemini API Key**: [Google AI Studio](https://aistudio.google.com/app/apikey) で取得
- **WordPress Password**: 管理画面のログインパスワード（ローカル環境の場合）

### 3. WordPress Basic Auth プラグインのインストール

ローカル環境でREST APIを使用するため、Basic Authenticationプラグインが必要です：

```bash
# プラグインのダウンロードとインストール（既に実行済みの場合は不要）
curl -L https://github.com/WP-API/Basic-Auth/archive/master.zip -o /tmp/basic-auth.zip
unzip -q /tmp/basic-auth.zip -d /tmp/
docker cp /tmp/Basic-Auth-master logishift-wp:/var/www/html/wp-content/plugins/basic-auth
```

WordPress管理画面（プラグイン）で「Basic Authentication」を有効化してください。

## 使い方

### 基本的な使用方法

```bash
# 仮想環境を有効化
source automation/venv/bin/activate

# 記事を生成して下書き保存
python automation/generate_article.py --keyword "物流DX"

# プレビューのみ（投稿しない）
python automation/generate_article.py --keyword "物流DX" --dry-run

# スケジュール投稿（指定日時に自動公開）
python automation/generate_article.py --keyword "物流DX" --schedule "2025-11-27 10:00"
```

### コマンドラインオプション

| オプション | 説明 | 必須 | 例 |
|----------|------|------|-----|
| `--keyword` | 記事のキーワード | ✅ | `--keyword "物流DX"` |
| `--dry-run` | プレビューのみ（投稿しない） | ❌ | `--dry-run` |
| `--schedule` | 公開予定日時 | ❌ | `--schedule "2025-11-27 10:00"` |

### スケジュール投稿の日時フォーマット

以下の形式をサポート：
- `YYYY-MM-DD HH:MM` （例: `2025-11-27 10:00`）
- `YYYY-MM-DD HH:MM:SS` （例: `2025-11-27 10:00:00`）

## 生成される記事の仕様

- **ターゲット読者**: 物流担当者、倉庫管理者、経営層
- **構成**: 導入 → 課題 → 解決策 → まとめ
- **文字数**: 約2,000文字以上
- **文体**: です・ます調
- **フォーマット**: Markdown（自動的にHTMLに変換）

## トラブルシューティング

### 認証エラーが発生する

- `.env` ファイルのユーザー名とパスワードが正しいか確認
- Basic Authentication プラグインが有効化されているか確認

### 記事が投稿されない

- WordPressが起動しているか確認: `docker ps | grep logishift`
- ネットワーク接続を確認

### Gemini APIエラー

- APIキーが正しいか確認
- APIの利用制限に達していないか確認

## ファイル構成

```
automation/
├── README.md              # このファイル
├── .env                   # 環境変数（要作成）
├── requirements.txt       # 依存ライブラリ
├── venv/                  # Python仮想環境
├── gemini_client.py       # Gemini API クライアント
├── wp_client.py           # WordPress REST API クライアント
├── generate_article.py    # メインスクリプト
└── test_auth.py           # 認証テストスクリプト
```

## ライセンス

このプロジェクトは内部利用のみを目的としています。
