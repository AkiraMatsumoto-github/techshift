# 自作テーマの本番環境デプロイガイド

LogiShiftテーマをローカル環境から本番サーバーのWordPressに反映させる方法を説明します。

## 📋 前提条件

- [ ] サーバーへのSSH/SFTP/FTPアクセス権限
- [ ] 本番WordPressが稼働中
- [ ] ローカルでテーマが正常に動作している

---

## 🚀 推奨デプロイフロー

現在のリポジトリには`automation/`, `docs/`, `themes/`など複数のディレクトリが含まれていますが、
**`themes/logishift`だけ**をサーバーにデプロイする3段階の方法を推奨します。

---

## ✅ 初回デプロイ: Git Sparse Checkout

サーバー側で`themes/logishift`ディレクトリのみをチェックアウトします。

### ワンライナーで実行（推奨）

```bash
# ローカルから実行（サーバーに自動接続してセットアップ）
ssh xserver-logishift << 'EOF'
mkdir -p ~/logishift-repo
cd ~/logishift-repo
git init
git remote add origin https://github.com/AkiraMatsumoto-github/logishift.git
git config core.sparseCheckout true
echo "themes/logishift/" >> .git/info/sparse-checkout
git pull origin main
# Xserverのパスに合わせて変更
mkdir -p ~/logishift.net/public_html/wp-content/themes/logishift
rsync -av --delete themes/logishift/ ~/logishift.net/public_html/wp-content/themes/logishift/
# Xserverでは通常ユーザー権限で動作するためchownは不要、または制限される場合があります
chmod -R 755 ~/logishift.net/public_html/wp-content/themes/logishift/
# NginxのリロードはXserverではユーザー権限でできないため省略（自動反映されるか、管理画面で操作）
echo "✅ 初回デプロイ完了！"
EOF
```

### 手動で実行する場合

```bash
# サーバーにSSH接続
# サーバーにSSH接続
ssh xserver-logishift

# 作業ディレクトリを作成
mkdir -p ~/logishift-repo
cd ~/logishift-repo

# リポジトリを初期化（ファイルはまだダウンロードしない）
git init
git remote add origin https://github.com/AkiraMatsumoto-github/logishift.git

# Sparse Checkoutを有効化
git config core.sparseCheckout true

# チェックアウトするディレクトリを指定（themes/logishift のみ）
echo "themes/logishift/" >> .git/info/sparse-checkout

# 指定したディレクトリのみをプル
git pull origin main

# テーマディレクトリが存在することを確認
ls -la themes/logishift/

# WordPressのテーマディレクトリに同期 (Xserverのパス例)
rsync -av --delete themes/logishift/ ~/logishift.net/public_html/wp-content/themes/logishift/

# パーミッション設定
chmod -R 755 ~/logishift.net/public_html/wp-content/themes/logishift/

# キャッシュクリア
sudo systemctl reload nginx

echo "✅ 初回デプロイ完了！"
```

---

## 🔄 日常の更新: GitHub Actions（自動デプロイ）

`git push`するだけで自動的にサーバーに反映されます。

### ステップ1: GitHub Actionsワークフローを作成

`.github/workflows/deploy-theme.yml`を作成:

```yaml
name: Deploy Theme to Production

on:
  push:
    branches: [ main ]
    paths:
      - 'themes/logishift/**'  # このディレクトリが変更された時だけ実行
  workflow_dispatch:  # 手動実行も可能

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v3
      with:
        sparse-checkout: |
          themes/logishift
        sparse-checkout-cone-mode: false
    
    - name: Deploy to server via rsync
      uses: burnett01/rsync-deployments@5.2
      with:
        switches: -avz --delete
        path: themes/logishift/
        remote_path: /var/www/html/wp-content/themes/logishift/
        remote_host: ${{ secrets.SERVER_HOST }}
        remote_user: ${{ secrets.SERVER_USER }}
        remote_key: ${{ secrets.SSH_PRIVATE_KEY }}
    
    - name: Set permissions and reload
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.SERVER_HOST }}
        username: ${{ secrets.SERVER_USER }}
        key: ${{ secrets.SSH_PRIVATE_KEY }}
        port: 10022
        script: |
          # Xserver用パス
          rsync -av --delete themes/logishift/ ~/logishift.net/public_html/wp-content/themes/logishift/
          chmod -R 755 ~/logishift.net/public_html/wp-content/themes/logishift
          echo "✅ デプロイ完了！"
```

### ステップ2: SSH鍵を作成（まだない場合）

```bash
# ローカルで実行
ssh-keygen -t ed25519 -C "github-actions@logishift.net" -f ~/.ssh/logishift_deploy

# 公開鍵をサーバーに追加
ssh-copy-id -i ~/.ssh/logishift_deploy.pub tarunosuke@logishift.net

# 秘密鍵の内容を表示（GitHub Secretsに貼り付ける）
cat ~/.ssh/logishift_deploy
```

### ステップ3: GitHub Secretsを設定

GitHubリポジトリの **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

以下の3つを追加:

| Name | Value |
|------|-------|
| `SERVER_HOST` | `sv15718.xserver.jp` |
| `SERVER_USER` | `xs937213` |
| `SSH_PRIVATE_KEY` | 上記で表示された秘密鍵の内容全体 |

### ステップ4: 使い方

```bash
# ローカルで開発
cd /Users/matsumotoakira/Documents/Private_development/media

# テーマを編集
# themes/logishift/style.css などを変更

# Gitにコミット＆プッシュ
git add themes/logishift/
git commit -m "Update theme design"
git push origin main

# → 自動的にサーバーにデプロイされる！
# GitHubの Actions タブで進捗を確認できます
```

---

## 🚨 緊急時: Git Archive（手動デプロイ）

GitHub Actionsが使えない場合や、即座にデプロイしたい場合の方法です。

### ワンライナーで実行

```bash
# ローカルで実行（すべて自動）
cd /Users/matsumotoakira/Documents/Private_development/media && \
git archive --format=tar.gz --prefix=logishift/ HEAD:themes/logishift > logishift-theme.tar.gz && \
scp logishift-theme.tar.gz tarunosuke@logishift.net:~/ && \
ssh tarunosuke@logishift.net "cd /var/www/html/wp-content/themes && \
sudo tar -czf ~/logishift-backup-\$(date +%Y%m%d-%H%M%S).tar.gz logishift/ 2>/dev/null; \
sudo tar -xzf ~/logishift-theme.tar.gz && \
sudo chown -R www-data:www-data logishift/ && \
sudo chmod -R 755 logishift/ && \
sudo systemctl reload nginx && \
rm ~/logishift-theme.tar.gz && \
echo '✅ 緊急デプロイ完了！'" && \
rm logishift-theme.tar.gz
```

### 手動で実行する場合

```bash
# ステップ1: ローカルでアーカイブ作成
cd /Users/matsumotoakira/Documents/Private_development/media
git archive --format=tar.gz --prefix=logishift/ HEAD:themes/logishift > logishift-theme.tar.gz

# ステップ2: サーバーにアップロード
scp logishift-theme.tar.gz tarunosuke@logishift.net:~/

# ステップ3: サーバーで解凍・適用
ssh tarunosuke@logishift.net

# バックアップ作成
cd /var/www/html/wp-content/themes
sudo tar -czf ~/logishift-backup-$(date +%Y%m%d-%H%M%S).tar.gz logishift/ 2>/dev/null

# 新テーマを解凍
sudo tar -xzf ~/logishift-theme.tar.gz

# パーミッション設定
sudo chown -R www-data:www-data logishift/
sudo chmod -R 755 logishift/

# キャッシュクリア
sudo systemctl reload nginx

# 一時ファイル削除
rm ~/logishift-theme.tar.gz

echo "✅ 緊急デプロイ完了！"
```

---

## 📊 デプロイ方法の比較

| 方法 | 使用タイミング | 所要時間 | 難易度 | 自動化 |
|------|--------------|---------|--------|--------|
| **Sparse Checkout** | 初回セットアップ | 5分 | ⭐⭐ | 半自動 |
| **GitHub Actions** | 日常の更新 | 1分 | ⭐ | 完全自動 |
| **Git Archive** | 緊急時 | 2分 | ⭐⭐ | 半自動 |

---

## 🎯 推奨ワークフロー

```
1. 初回デプロイ
   ↓ Sparse Checkout（1回のみ）
   
2. 日常の開発
   ↓ git push → GitHub Actions（自動）
   
3. 緊急時
   ↓ Git Archive（手動）
```

---

## 🔧 デプロイ後の設定

### 1. テーマの有効化

#### 方法A: WordPress管理画面（推奨）

1. WordPress管理画面にログイン
2. **外観** → **テーマ**に移動
3. **LogiShift**テーマを見つける
4. **有効化**をクリック

#### 方法B: WP-CLI（コマンドライン）

```bash
# サーバーにSSH接続
ssh username@your-server.com

# WordPressディレクトリに移動
cd /var/www/html

# テーマを有効化
wp theme activate logishift

# テーマ一覧を確認
wp theme list
```

---

### 2. パーミッションの確認

```bash
# テーマディレクトリのパーミッション確認
ls -la /var/www/html/wp-content/themes/logishift/

# 正しいパーミッション設定
sudo chown -R www-data:www-data /var/www/html/wp-content/themes/logishift/
sudo find /var/www/html/wp-content/themes/logishift/ -type d -exec chmod 755 {} \;
sudo find /var/www/html/wp-content/themes/logishift/ -type f -exec chmod 644 {} \;
```

**パーミッションの説明:**
- ディレクトリ: `755` (rwxr-xr-x)
- ファイル: `644` (rw-r--r--)
- 所有者: `www-data:www-data` (Apacheユーザー)

---

### 3. キャッシュのクリア

```bash
# WordPress Object Cacheをクリア（WP-CLI）
wp cache flush

# Nginxキャッシュをクリア（Nginxの場合）
sudo rm -rf /var/cache/nginx/*
sudo systemctl reload nginx

# Apacheキャッシュをクリア（Apacheの場合）
sudo systemctl reload apache2
```

---

## 📝 デプロイチェックリスト

デプロイ前に確認すべき項目:

- [ ] ローカル環境でテーマが正常に動作している
- [ ] `style.css`のバージョン番号を更新
- [ ] 不要なファイル（`.DS_Store`, `node_modules`など）を除外
- [ ] データベースのバックアップを取得
- [ ] テーマファイルのバックアップを取得

```bash
# 本番環境のバックアップ（デプロイ前）
ssh username@your-server.com "cd /var/www/html/wp-content/themes && tar -czf logishift-backup-$(date +%Y%m%d).tar.gz logishift/"
```

---

## 🎯 実践例: 完全なデプロイフロー

### シナリオ: ローカルで開発したテーマを本番環境に反映

```bash
# ========================================
# ローカル環境での作業
# ========================================

# 1. テーマのバージョンを更新
cd /Users/matsumotoakira/Documents/Private_development/media/themes/logishift
# style.cssの Version: 1.0.0 → 1.0.1 に変更

# 2. Gitにコミット
git add .
git commit -m "Update theme to v1.0.1 - Add new features"
git push origin main

# 3. テーマを圧縮
cd /Users/matsumotoakira/Documents/Private_development/media
tar -czf logishift-theme-v1.0.1.tar.gz themes/logishift/

# ========================================
# サーバー環境での作業
# ========================================

# 4. サーバーにアップロード
scp logishift-theme-v1.0.1.tar.gz username@logishift.net:~/

# 5. サーバーにSSH接続
ssh username@logishift.net

# 6. 既存テーマをバックアップ
cd /var/www/html/wp-content/themes
sudo tar -czf logishift-backup-$(date +%Y%m%d-%H%M%S).tar.gz logishift/
sudo mv logishift-backup-*.tar.gz ~/backups/

# 7. 既存テーマを削除（または名前変更）
sudo mv logishift logishift.old

# 8. 新しいテーマを解凍
sudo tar -xzf ~/logishift-theme-v1.0.1.tar.gz

# 9. パーミッション設定
sudo chown -R www-data:www-data logishift/
sudo find logishift/ -type d -exec chmod 755 {} \;
sudo find logishift/ -type f -exec chmod 644 {} \;

# 10. キャッシュクリア
wp cache flush
sudo systemctl reload nginx  # または apache2

# 11. 動作確認
curl -I https://logishift.net

# 12. 問題なければ古いテーマを削除
sudo rm -rf logishift.old
rm ~/logishift-theme-v1.0.1.tar.gz
```

---

## 🔍 デプロイ後の確認

### 1. ブラウザで確認

- [ ] トップページが正しく表示される
- [ ] カテゴリページが正しく表示される
- [ ] 個別記事ページが正しく表示される
- [ ] ファビコンが表示される
- [ ] CSSが正しく読み込まれている
- [ ] JavaScriptが正しく動作している

### 2. コマンドラインで確認

```bash
# テーマが正しくインストールされているか確認
wp theme list

# 有効なテーマを確認
wp theme status logishift

# エラーログを確認
sudo tail -f /var/log/nginx/error.log  # Nginxの場合
sudo tail -f /var/log/apache2/error.log  # Apacheの場合
```

### 3. パフォーマンス確認

```bash
# ページの読み込み速度を確認
curl -w "@curl-format.txt" -o /dev/null -s https://logishift.net

# curl-format.txt の内容:
# time_namelookup:  %{time_namelookup}\n
# time_connect:  %{time_connect}\n
# time_starttransfer:  %{time_starttransfer}\n
# time_total:  %{time_total}\n
```

---

## ⚠️ トラブルシューティング

### 問題1: テーマが表示されない

**原因:**
- パーミッションが正しくない
- `style.css`にエラーがある

**解決策:**
```bash
# パーミッションを再設定
sudo chown -R www-data:www-data /var/www/html/wp-content/themes/logishift/
sudo chmod -R 755 /var/www/html/wp-content/themes/logishift/

# style.cssの確認
head -20 /var/www/html/wp-content/themes/logishift/style.css
```

---

### 問題2: CSSが反映されない

**原因:**
- ブラウザキャッシュ
- サーバーキャッシュ
- CDNキャッシュ

**解決策:**
```bash
# サーバーキャッシュをクリア
wp cache flush
sudo systemctl reload nginx

# style.cssのバージョンを確認
grep "Version:" /var/www/html/wp-content/themes/logishift/style.css

# ブラウザで強制リロード: Cmd+Shift+R (Mac) / Ctrl+Shift+R (Windows)
```

---

### 問題3: 画像が表示されない

**原因:**
- 画像パスが間違っている
- パーミッションが正しくない

**解決策:**
```bash
# 画像ディレクトリのパーミッション確認
ls -la /var/www/html/wp-content/themes/logishift/assets/images/

# パーミッション修正
sudo chmod -R 644 /var/www/html/wp-content/themes/logishift/assets/images/*
```

---

### 問題4: PHPエラー

**原因:**
- PHPバージョンの違い
- 関数の互換性問題

**解決策:**
```bash
# PHPバージョン確認
php -v

# エラーログ確認
sudo tail -50 /var/log/nginx/error.log

# WordPressデバッグモードを有効化
# wp-config.phpに追加:
# define('WP_DEBUG', true);
# define('WP_DEBUG_LOG', true);
```

---

## 🔄 継続的なデプロイ戦略

### 開発フロー

```
ローカル開発 → Git Push → 自動テスト → 本番デプロイ
```

### 推奨ワークフロー

1. **ローカルで開発・テスト**
2. **Gitにコミット**
3. **ステージング環境でテスト**（任意）
4. **本番環境にデプロイ**
5. **動作確認**
6. **問題があればロールバック**

### ロールバック手順

```bash
# バックアップから復元
cd /var/www/html/wp-content/themes
sudo rm -rf logishift
sudo tar -xzf ~/backups/logishift-backup-YYYYMMDD-HHMMSS.tar.gz
sudo chown -R www-data:www-data logishift/
wp cache flush
```

---

## 📚 関連ドキュメント

- [git_partial_deploy.md](./git_partial_deploy.md) - Gitリポジトリから特定ディレクトリのみデプロイする詳細ガイド
- [theme_deploy_quick.md](./theme_deploy_quick.md) - logishift.net専用クイックガイド
- [production_deployment_guide.md](./production_deployment_guide.md) - 記事自動投稿の本番環境デプロイ
- [quick_start_production.md](./quick_start_production.md) - クイックスタートガイド
- [development_guidelines.md](./development_guidelines.md) - 開発ガイドライン

---

## ✅ まとめ

### 推奨デプロイフロー

```
1️⃣ 初回デプロイ（1回のみ）
   └─ Git Sparse Checkout
      └─ themes/logishift のみをサーバーにクローン

2️⃣ 日常の開発（自動化）
   └─ GitHub Actions
      └─ git push するだけで自動デプロイ

3️⃣ 緊急時（手動）
   └─ Git Archive
      └─ 即座にデプロイ可能
```

### デプロイ方法の選択

| 状況 | 推奨方法 | コマンド | 所要時間 |
|------|---------|---------|---------|
| **初回セットアップ** | Sparse Checkout | ワンライナーコマンド | 5分 |
| **日常の更新** | GitHub Actions | `git push` | 1分（自動） |
| **緊急デプロイ** | Git Archive | ワンライナーコマンド | 2分 |

### 重要なポイント

- ✅ **リポジトリ構成**: `automation/`, `docs/`, `themes/`を含むモノレポでOK
- ✅ **部分デプロイ**: `themes/logishift`だけをサーバーに反映
- ✅ **自動化**: GitHub Actionsで完全自動デプロイ
- ✅ **バックアップ**: デプロイ時に自動でバックアップ作成
- ✅ **パーミッション**: 自動で正しく設定（755/644）

---

## 🚀 次のステップ

### 1. 初回デプロイを実行

```bash
ssh tarunosuke@logishift.net << 'EOF'
mkdir -p ~/logishift-repo && cd ~/logishift-repo
git init && git remote add origin https://github.com/AkiraMatsumoto-github/logishift.git
git config core.sparseCheckout true
echo "themes/logishift/" >> .git/info/sparse-checkout
git pull origin main
sudo rsync -av --delete themes/logishift/ /var/www/html/wp-content/themes/logishift/
sudo chown -R www-data:www-data /var/www/html/wp-content/themes/logishift/
sudo chmod -R 755 /var/www/html/wp-content/themes/logishift/
sudo systemctl reload nginx
echo "✅ 初回デプロイ完了！"
EOF
```

### 2. GitHub Actionsをセットアップ

`.github/workflows/deploy-theme.yml`を作成して、自動デプロイを有効化

### 3. WordPress管理画面でテーマを有効化

https://logishift.net/wp-admin → **外観** → **テーマ** → **LogiShift** を有効化

---

**質問やトラブルがあれば、関連ドキュメントを参照してください。**

