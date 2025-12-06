# 本番環境への記事自動投稿ガイド

このドキュメントでは、LogiShiftの記事自動生成システムを本番環境のWordPressに適用する方法を説明します。

## 目次

1. [前提条件](#前提条件)
2. [本番環境のセットアップ](#本番環境のセットアップ)
3. [セキュリティ設定](#セキュリティ設定)
4. [記事の自動投稿方法](#記事の自動投稿方法)
5. [スケジュール実行の設定](#スケジュール実行の設定)
6. [トラブルシューティング](#トラブルシューティング)

---

## 前提条件

- 本番WordPressサイトがHTTPS対応済み
- WordPressのREST APIが有効
- サーバーへのSSHアクセス権限（スケジュール実行の場合）
- Python 3.8以上がインストール済み

---

## 本番環境のセットアップ

### 1. WordPress Application Passwordの作成

本番環境ではBasic Authプラグインは使用せず、WordPress標準の**Application Passwords**を使用します。

#### 手順:

1. WordPress管理画面にログイン
2. **ユーザー** → **プロフィール**に移動
3. 下部の「**アプリケーションパスワード**」セクションを見つける
4. 新しいアプリケーション名を入力（例: `LogiShift Automation`）
5. **新しいアプリケーションパスワードを追加**をクリック
6. 生成されたパスワードをコピー（**スペースを含めてコピー**、または**スペースを除去**）

> [!IMPORTANT]
> Application Passwordsは**HTTPS環境でのみ動作**します。HTTPサイトでは使用できません。

#### Application Passwordsが表示されない場合:

以下のコードを`wp-config.php`に追加してください:

```php
define('WP_APPLICATION_PASSWORDS', true);
```

---

### 2. 環境変数ファイルの設定

本番環境用の`.env`ファイルを作成します。

#### `.env.production` の作成:

```bash
# Gemini API
GEMINI_API_KEY=your_actual_gemini_api_key_here

# WordPress Production
WP_URL=https://your-production-site.com
WP_USER=your_wordpress_username
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
```

> [!WARNING]
> `.env`ファイルには機密情報が含まれるため、**絶対にGitにコミットしないでください**。`.gitignore`に追加されていることを確認してください。

#### 環境変数の説明:

| 変数名 | 説明 | 例 |
|--------|------|-----|
| `GEMINI_API_KEY` | Google AI StudioのAPIキー | `AIzaSy...` |
| `WP_URL` | 本番WordPressのURL（**HTTPSが必須**） | `https://logishift.jp` |
| `WP_USER` | WordPress管理者ユーザー名 | `admin` |
| `WP_APP_PASSWORD` | Application Password（スペース含む/なし両方OK） | `xxxx xxxx xxxx xxxx` |

---

### 3. サーバーへのデプロイ

#### 方法A: サーバー上で直接セットアップ

```bash
# サーバーにSSH接続
ssh user@your-server.com

# プロジェクトディレクトリを作成
mkdir -p ~/logishift-automation
cd ~/logishift-automation

# ファイルをアップロード（ローカルから実行）
scp -r automation/ user@your-server.com:~/logishift-automation/

# サーバー上で仮想環境を作成
python3 -m venv venv
source venv/bin/activate

# 依存関係をインストール
pip install -r automation/requirements.txt

# 環境変数ファイルを作成
nano automation/.env
# 上記の内容を貼り付けて保存
```

#### 方法B: Dockerを使用（推奨）

```bash
# Dockerfileを作成
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY automation/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY automation/ .

CMD ["python", "pipeline.py"]
EOF

# Dockerイメージをビルド
docker build -t logishift-automation .

# 環境変数を渡して実行
docker run --env-file automation/.env logishift-automation
```

---

## セキュリティ設定

### 1. ファイルパーミッションの設定

```bash
# .envファイルを読み取り専用に
chmod 600 automation/.env

# スクリプトを実行可能に
chmod +x automation/*.py
```

### 2. WordPress REST APIのセキュリティ

本番環境では、REST APIへのアクセスを制限することを推奨します。

#### `.htaccess`での制限例:

```apache
# REST APIへのアクセスを特定IPのみ許可
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteCond %{REQUEST_URI} ^/wp-json/ [NC]
RewriteCond %{REMOTE_ADDR} !^123\.456\.789\.0$ # サーバーのIPアドレス
RewriteRule ^(.*)$ - [F,L]
</IfModule>
```

---

## 記事の自動投稿方法

### 基本的な使用方法

#### 1. 単一記事の生成と投稿

```bash
# 仮想環境を有効化
source venv/bin/activate

# 記事を生成して下書き保存
python automation/generate_article.py \
  --keyword "物流DX 2025年トレンド" \
  --type "know"

# スケジュール投稿（指定日時に自動公開）
python automation/generate_article.py \
  --keyword "倉庫管理システム 比較" \
  --type "buy" \
  --schedule "2025-12-05 10:00"
```

#### 2. パイプラインによる自動生成

```bash
# 過去1日分のニュースから関連記事を収集し、1記事生成
python automation/pipeline.py

# 過去3日分、閾値80点以上、最大5記事生成
python automation/pipeline.py --days 3 --threshold 80 --limit 5

# ドライラン（投稿せずに確認のみ）
python automation/pipeline.py --dry-run
```

### コマンドラインオプション

#### `generate_article.py`

| オプション | 説明 | 必須 | 例 |
|----------|------|------|-----|
| `--keyword` | 記事のキーワード | ✅ | `--keyword "物流DX"` |
| `--type` | 記事タイプ | ❌ | `--type "know"` (デフォルト) |
| `--dry-run` | 投稿せずプレビューのみ | ❌ | `--dry-run` |
| `--schedule` | 公開予定日時 | ❌ | `--schedule "2025-12-05 10:00"` |
| `--context` | 記事コンテキスト（JSON） | ❌ | ニュース記事用 |

**記事タイプ:**
- `know`: ノウハウ・解説記事
- `buy`: 製品比較・導入ガイド
- `do`: 実践・手順記事
- `news`: ニュース記事
- `global`: 海外トレンド記事

#### `pipeline.py`

| オプション | 説明 | デフォルト |
|----------|------|------------|
| `--days` | 収集対象の過去日数 | 1 |
| `--threshold` | 記事生成のスコア閾値 | 85 |
| `--limit` | 生成する最大記事数 | 1 |
| `--score-limit` | スコアリングする最大記事数 | 0（全件） |
| `--dry-run` | 投稿を行わない | False |

---

## スケジュール実行の設定

### 方法1: Cron（Linux/macOS）

毎日自動的に記事を生成・投稿する設定です。

#### Cronの設定:

```bash
# Crontabを編集
crontab -e

# 以下を追加（毎日午前9時に実行）
0 9 * * * cd ~/logishift-automation && source venv/bin/activate && python automation/pipeline.py --limit 1 >> ~/logishift-automation/logs/cron.log 2>&1

# 週に3回（月・水・金の午前9時）
0 9 * * 1,3,5 cd ~/logishift-automation && source venv/bin/activate && python automation/pipeline.py --limit 2 >> ~/logishift-automation/logs/cron.log 2>&1
```

#### Cron時刻の書式:

```
分 時 日 月 曜日 コマンド
0  9  *  *  *   (毎日午前9時)
0  9  *  *  1   (毎週月曜日午前9時)
*/30 * * * *    (30分ごと)
```

#### ログディレクトリの作成:

```bash
mkdir -p ~/logishift-automation/logs
```

---

### 方法2: systemd Timer（Linux推奨）

より柔軟なスケジュール管理が可能です。

#### サービスファイルの作成:

```bash
# /etc/systemd/system/logishift-automation.service
sudo nano /etc/systemd/system/logishift-automation.service
```

```ini
[Unit]
Description=LogiShift Article Automation
After=network.target

[Service]
Type=oneshot
User=your-username
WorkingDirectory=/home/your-username/logishift-automation
Environment="PATH=/home/your-username/logishift-automation/venv/bin"
ExecStart=/home/your-username/logishift-automation/venv/bin/python automation/pipeline.py --limit 1
StandardOutput=append:/home/your-username/logishift-automation/logs/automation.log
StandardError=append:/home/your-username/logishift-automation/logs/automation.log

[Install]
WantedBy=multi-user.target
```

#### タイマーファイルの作成:

```bash
# /etc/systemd/system/logishift-automation.timer
sudo nano /etc/systemd/system/logishift-automation.timer
```

```ini
[Unit]
Description=LogiShift Article Automation Timer
Requires=logishift-automation.service

[Timer]
OnCalendar=daily
OnCalendar=09:00
Persistent=true

[Install]
WantedBy=timers.target
```

#### タイマーの有効化:

```bash
# タイマーを有効化
sudo systemctl enable logishift-automation.timer
sudo systemctl start logishift-automation.timer

# ステータス確認
sudo systemctl status logishift-automation.timer

# 次回実行時刻を確認
sudo systemctl list-timers
```

---

### 方法3: GitHub Actions（クラウド実行）

サーバーを持たない場合、GitHub Actionsで実行できます。

#### `.github/workflows/auto-post.yml`

```yaml
name: Auto Post Articles

on:
  schedule:
    # 毎日午前9時（UTC 0:00 = JST 9:00）
    - cron: '0 0 * * *'
  workflow_dispatch: # 手動実行も可能

jobs:
  generate-and-post:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r automation/requirements.txt
    
    - name: Generate and post article
      env:
        GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        WP_URL: ${{ secrets.WP_URL }}
        WP_USER: ${{ secrets.WP_USER }}
        WP_APP_PASSWORD: ${{ secrets.WP_APP_PASSWORD }}
      run: |
        python automation/pipeline.py --limit 1
```

#### GitHub Secretsの設定:

1. GitHubリポジトリの**Settings** → **Secrets and variables** → **Actions**
2. **New repository secret**をクリック
3. 以下のシークレットを追加:
   - `GEMINI_API_KEY`
   - `WP_URL`
   - `WP_USER`
   - `WP_APP_PASSWORD`

---

## トラブルシューティング

### 1. 認証エラー

#### エラー: `401 Unauthorized`

**原因:**
- Application Passwordが間違っている
- HTTPサイトでApplication Passwordsを使用している

**解決策:**
```bash
# Application Passwordを再生成
# WordPress管理画面 → ユーザー → プロフィール → アプリケーションパスワード

# HTTPSが有効か確認
curl -I https://your-site.com | grep "HTTP/"

# .envファイルの確認
cat automation/.env | grep WP_
```

---

### 2. REST APIエラー

#### エラー: `rest_cannot_create`

**原因:**
- ユーザーに投稿権限がない
- REST APIが無効化されている

**解決策:**
```php
// wp-config.phpに追加（REST APIを有効化）
define('REST_API_ENABLED', true);

// ユーザー権限を確認（管理者権限が必要）
```

---

### 3. Gemini APIエラー

#### エラー: `RESOURCE_EXHAUSTED`

**原因:**
- APIの利用制限に達した

**解決策:**
```bash
# レート制限を確認
# Google AI Studio: https://aistudio.google.com/app/apikey

# リトライ間隔を設定
python automation/pipeline.py --limit 1 --days 1
sleep 60 # 60秒待機
python automation/pipeline.py --limit 1 --days 1
```

---

### 4. 画像アップロードエラー

#### エラー: `Failed to upload image`

**原因:**
- ファイルサイズが大きすぎる
- WordPressのアップロード制限

**解決策:**
```php
// wp-config.phpに追加
@ini_set('upload_max_filesize', '10M');
@ini_set('post_max_size', '10M');
```

または`.htaccess`に追加:
```apache
php_value upload_max_filesize 10M
php_value post_max_size 10M
```

---

### 5. スケジュール投稿が実行されない

#### 原因:
- WordPressのWP-Cronが動作していない

**解決策:**
```bash
# WP-Cronを手動で実行
curl https://your-site.com/wp-cron.php

# または、システムCronで定期実行
# Crontabに追加:
*/15 * * * * curl https://your-site.com/wp-cron.php > /dev/null 2>&1
```

---

## ベストプラクティス

### 1. 段階的なデプロイ

```bash
# ステップ1: ドライランで動作確認
python automation/pipeline.py --dry-run

# ステップ2: 1記事のみ下書き投稿
python automation/generate_article.py --keyword "テストキーワード"

# ステップ3: スケジュール投稿のテスト
python automation/generate_article.py \
  --keyword "テストキーワード" \
  --schedule "2025-12-03 10:00"

# ステップ4: 本番運用開始
python automation/pipeline.py --limit 1
```

### 2. ログの監視

```bash
# ログファイルをリアルタイムで監視
tail -f ~/logishift-automation/logs/cron.log

# エラーのみ抽出
grep -i "error\|failed" ~/logishift-automation/logs/cron.log
```

### 3. バックアップ

```bash
# 生成された記事のバックアップ
tar -czf backup-$(date +%Y%m%d).tar.gz automation/generated_articles/

# 定期的なバックアップ（Cronに追加）
0 2 * * 0 tar -czf ~/backups/logishift-$(date +\%Y\%m\%d).tar.gz ~/logishift-automation/automation/generated_articles/
```

---

## まとめ

このガイドに従って、本番環境への記事自動投稿システムを構築できます。

**重要なポイント:**
- ✅ HTTPSが必須（Application Passwords使用のため）
- ✅ `.env`ファイルは絶対にGitにコミットしない
- ✅ まずはドライランで動作確認
- ✅ ログを定期的に監視
- ✅ バックアップを忘れずに

**推奨スケジュール:**
- 毎日1記事: `pipeline.py --limit 1`
- 週3回2記事ずつ: `pipeline.py --limit 2`（月・水・金）

ご不明な点があれば、`automation/README.md`も併せてご確認ください。
