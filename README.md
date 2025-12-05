# LogiShift - 物流業界特化型SEOメディア

物流業界の課題解決（コスト削減、DX推進、2024年問題など）に貢献する高品質な情報を提供するSEOメディアです。

## プロジェクト構成

```
.
├── themes/logishift/          # WordPressテーマ
├── automation/                # 記事自動生成システム
├── docs/                      # ドキュメント
└── .github/workflows/         # GitHub Actions
```

## サーバー接続

### SSH接続

```bash
# Xserverに接続
ssh xserver-logishift

# または直接指定
ssh -p 10022 xs937213@sv16718.xserver.jp
```

### サーバー情報

- **ホスト:** sv16718.xserver.jp
- **ポート:** 10022
- **ユーザー:** xs937213
- **サイトURL:** https://logishift.net

## デプロイ方法

### 1. テーマのデプロイ

GitHub Actions で自動デプロイされます。

**自動デプロイ:**
```bash
# themes/logishift/ 配下を編集してコミット
git add themes/logishift/
git commit -m "feat: Update theme"
git push origin main
```

GitHub Actions が自動的に：
1. `themes/logishift/` をサーバーにデプロイ
2. パーミッションを設定

**手動デプロイ（緊急時）:**
```bash
# ローカルから実行
scp -P 10022 -r themes/logishift/ xs937213@sv16718.xserver.jp:~/logishift.net/public_html/wp-content/themes/
```

### 2. Automation スクリプトのデプロイ

GitHub Actions で自動デプロイされます。

**自動デプロイ:**
```bash
# automation/ 配下を編集してコミット
git add automation/
git commit -m "feat: Update automation scripts"
git push origin main
```

GitHub Actions が自動的に：
1. `automation/` ディレクトリをサーバーにデプロイ
2. Python 依存パッケージをインストール

**手動デプロイ（緊急時）:**
```bash
# ローカルから実行
scp -P 10022 -r automation/ xs937213@sv16718.xserver.jp:~/logishift-automation/
```

## 記事自動生成

### ローカル（Mac）での実行

```bash
# プロジェクトディレクトリに移動
cd /Users/matsumotoakira/Documents/Private_development/media

# 仮想環境を作成（初回のみ）
python3 -m venv automation/venv

# 仮想環境を有効化
source automation/venv/bin/activate

# 依存パッケージをインストール（初回のみ）
pip install -r automation/requirements.txt

# 記事生成を実行
python automation/pipeline.py

# オプション指定
python automation/pipeline.py --hours 6 --limit 3 --threshold 85

# ドライラン（記事を投稿せずに確認）
python automation/pipeline.py --dry-run --limit 1

# 仮想環境を無効化
deactivate
```

### サーバーでの実行

```bash
# サーバーに接続
ssh xserver-logishift

# automation ディレクトリに移動
cd ~/logishift-automation/automation

# Miniconda 環境を有効化（自動的に有効化されます）
# (base) プロンプトが表示されていることを確認

# 記事生成を実行
python pipeline.py

# オプション指定
python pipeline.py --hours 6 --limit 3 --threshold 85

# ドライラン（記事を投稿せずに確認）
python pipeline.py --dry-run --limit 1
```

**注意:** サーバーでは Vertex AI の認証情報が設定されていないため、`.env` ファイルで `GEMINI_API_KEY` を使用してください。`GOOGLE_CLOUD_PROJECT` と `GOOGLE_CLOUD_LOCATION` の行をコメントアウトするか削除してください。


### GitHub Actions での定期実行（予定）

`.github/workflows/generate-articles.yml` を作成して、cron で定期実行する予定です。

例: 毎日12時に実行
```yaml
on:
  schedule:
    - cron: '0 3 * * *'  # UTC 3:00 = JST 12:00
  workflow_dispatch:
```

## 環境変数

サーバー上の `.env` ファイル（`~/logishift-automation/automation/.env`）に以下を設定：

```bash
# Gemini API
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_LOCATION=us-central1
GEMINI_API_KEY=your_api_key

# WordPress
WORDPRESS_URL=https://logishift.net
WORDPRESS_USERNAME=your_username
WORDPRESS_APP_PASSWORD=your_app_password
```

**重要:** `.env` ファイルは Git にコミットしないでください（`.gitignore` に含まれています）。

## Python 環境

サーバーでは **Miniconda** を使用しています。

```bash
# Python バージョン確認
python --version  # Python 3.13.9

# conda 環境確認
conda --version   # conda 25.9.1

# インストール済みパッケージ確認
pip list
```

## トラブルシューティング

### テーマが反映されない

```bash
# サーバーでパーミッションを確認
ssh xserver-logishift
chmod -R 755 ~/logishift.net/public_html/wp-content/themes/logishift
```

### Automation スクリプトが動かない

```bash
# サーバーで依存パッケージを再インストール
ssh xserver-logishift
cd ~/logishift-automation/automation
conda install -c conda-forge lxml -y
pip install -r requirements.txt
```

### GitHub Actions が失敗する

1. GitHub リポジトリの Settings → Secrets and variables → Actions
2. 以下の Secrets が正しく設定されているか確認：
   - `SERVER_HOST`: sv16718.xserver.jp
   - `SERVER_USER`: xs937213
   - `SSH_PRIVATE_KEY`: SSH秘密鍵
   - `SSH_PORT`: 10022

## 関連ドキュメント

- [テーマデプロイガイド](docs/00_meta/theme_deployment_guide.md)
- [本番環境デプロイガイド](docs/00_meta/production_deployment_guide.md)
- [Automation 戦略](docs/03_automation/automation_strategy.md)
- [コンテンツ戦略](docs/03_automation/content_strategy.md)

## ライセンス

プライベートプロジェクト
