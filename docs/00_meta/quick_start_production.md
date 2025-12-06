# 本番環境クイックスタートガイド

本番WordPressへの記事自動投稿を**最短5分**でセットアップする手順です。

## 📋 事前チェックリスト

- [ ] 本番サイトがHTTPS対応済み
- [ ] WordPress管理者アカウントでログイン可能
- [ ] サーバーへのSSHアクセス可能（またはGitHub Actions使用）

---

## 🚀 5分でセットアップ

### ステップ1: Application Passwordの作成（2分）

1. WordPress管理画面にログイン
2. **ユーザー** → **プロフィール**
3. 下部の「**アプリケーションパスワード**」セクション
4. 名前を入力: `LogiShift Automation`
5. **新しいアプリケーションパスワードを追加**
6. 生成されたパスワードをコピー（スペース含む）

### ステップ2: 環境変数の設定（1分）

`automation/.env`ファイルを編集:


```

### ステップ3: 動作確認（2分）

```bash
# 仮想環境を有効化
source automation/venv/bin/activate

# ドライランで確認
python automation/pipeline.py --dry-run

# 1記事を下書き投稿
python automation/pipeline.py --limit 1
```

---

## 📅 自動実行の設定

### Cronで毎日自動投稿（推奨）

```bash
# Crontabを編集
crontab -e

# 毎日午前9時に1記事投稿
0 9 * * * cd ~/logishift-automation && source venv/bin/activate && python automation/pipeline.py --limit 1 >> ~/logs/cron.log 2>&1
```

### GitHub Actionsで自動投稿（サーバー不要）

`.github/workflows/auto-post.yml`を作成:

```yaml
name: Auto Post
on:
  schedule:
    - cron: '0 0 * * *' # 毎日午前9時（JST）
  workflow_dispatch:

jobs:
  post:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - run: pip install -r automation/requirements.txt
    - env:
        GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        WP_URL: ${{ secrets.WP_URL }}
        WP_USER: ${{ secrets.WP_USER }}
        WP_APP_PASSWORD: ${{ secrets.WP_APP_PASSWORD }}
      run: python automation/pipeline.py --limit 1
```

**GitHub Secretsに以下を追加:**
- `GEMINI_API_KEY`
- `WP_URL`
- `WP_USER`
- `WP_APP_PASSWORD`

---

## 🎯 よく使うコマンド

```bash
# 1記事を下書き投稿
python automation/pipeline.py --limit 1

# 3記事を生成（スコア80点以上）
python automation/pipeline.py --limit 3 --threshold 80

# 特定キーワードで記事生成
python automation/generate_article.py --keyword "物流DX 2025"

# スケジュール投稿（12月5日 10時公開）
python automation/generate_article.py \
  --keyword "倉庫管理システム" \
  --schedule "2025-12-05 10:00"

# ドライラン（投稿せず確認のみ）
python automation/pipeline.py --dry-run
```

---

## ⚠️ トラブルシューティング

### 認証エラー（401）

```bash
# Application Passwordを再生成
# WordPress管理画面 → ユーザー → プロフィール

# .envファイルを確認
cat automation/.env
```

### 画像アップロードエラー

```php
// wp-config.phpに追加
@ini_set('upload_max_filesize', '10M');
@ini_set('post_max_size', '10M');
```

### スケジュール投稿が実行されない

```bash
# WP-Cronを手動実行
curl https://your-site.com/wp-cron.php
```

---

## 📚 詳細ドキュメント

より詳しい情報は以下を参照:
- [本番環境デプロイガイド](./production_deployment_guide.md)
- [自動化ツールREADME](../../automation/README.md)

---

## ✅ 推奨運用

| 頻度 | コマンド | 説明 |
|------|---------|------|
| 毎日 | `pipeline.py --limit 1` | 1記事自動投稿 |
| 週3回 | `pipeline.py --limit 2` | 月・水・金に2記事ずつ |
| 手動 | `generate_article.py --keyword "..."` | 特定テーマの記事 |

**セキュリティ:**
- `.env`ファイルは絶対にGitにコミットしない
- Application Passwordは定期的に再生成
- ログファイルを定期的に確認

**バックアップ:**
```bash
# 生成記事のバックアップ
tar -czf backup-$(date +%Y%m%d).tar.gz automation/generated_articles/
```
