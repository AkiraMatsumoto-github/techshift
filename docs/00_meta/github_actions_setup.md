# GitHub Actions 自動実行設定ガイド

## 概要

GitHub Actionsを使用して、`pipeline.py`を6時間ごとに自動実行する設定を行います。

## ワークフローファイル

**場所**: `.github/workflows/article-pipeline.yml`

### 実行スケジュール

- **Cron**: `0 */6 * * *` (6時間ごと)
- **UTC時間**: 0:00, 6:00, 12:00, 18:00
- **日本時間**: 9:00, 15:00, 21:00, 3:00

### 手動実行

GitHub ActionsのUIから手動で実行することも可能です：
1. GitHubリポジトリの「Actions」タブを開く
2. 「Article Generation Pipeline」を選択
3. 「Run workflow」ボタンをクリック

## 必要なシークレット設定

GitHubリポジトリの設定で以下のシークレットを追加する必要があります。

### 設定手順

1. GitHubリポジトリページを開く
2. **Settings** → **Secrets and variables** → **Actions** に移動
3. **New repository secret** をクリック
4. 以下のシークレットを追加

### 必須シークレット一覧

| シークレット名 | 説明 | 例 |
|--------------|------|-----|
| `GEMINI_API_KEY` | Gemini APIキー | `AIza...` |
| `GOOGLE_CLOUD_PROJECT` | Google CloudプロジェクトID | `231503280916` |
| `GOOGLE_CLOUD_LOCATION` | Google Cloudリージョン | `us-central1` |
| `WP_URL` | WordPress サイトURL | `https://logishift.net` |
| `WP_USER` | WordPress ユーザー名 | `admin` |
| `WP_APP_PASSWORD` | WordPress アプリケーションパスワード | `xxxx xxxx xxxx xxxx` |

### シークレット取得方法

#### 1. Gemini API Key
- [Google AI Studio](https://aistudio.google.com/app/apikey) で取得

#### 2. Google Cloud Project & Location
- [Google Cloud Console](https://console.cloud.google.com/) で確認
- プロジェクトIDとリージョンを取得

#### 3. WordPress App Password
1. WordPress管理画面にログイン
2. **ユーザー** → **プロフィール** に移動
3. **アプリケーションパスワード** セクションまでスクロール
4. 新しいアプリケーション名（例: "GitHub Actions"）を入力
5. **新しいアプリケーションパスワードを追加** をクリック
6. 生成されたパスワードをコピー（スペース込み）

## ワークフローの動作

### 実行内容

1. **リポジトリのチェックアウト**
2. **Python 3.11のセットアップ**
3. **依存関係のインストール** (`requirements.txt`)
4. **Pipeline実行**:
   ```bash
   python pipeline.py --hours 6 --threshold 85 --limit 3
   ```
   - 過去6時間の記事を収集
   - スコア85以上の記事を選択
   - 最大3記事を生成

### 失敗時の対応

ワークフローが失敗した場合、以下のファイルがアーティファクトとして保存されます（7日間保持）：
- `collected_articles.json`
- `scored_articles.json`

アーティファクトのダウンロード方法：
1. **Actions** タブを開く
2. 失敗したワークフロー実行をクリック
3. **Artifacts** セクションから `pipeline-logs` をダウンロード

## ワークフローの確認

### 実行履歴の確認

1. GitHubリポジトリの **Actions** タブを開く
2. 「Article Generation Pipeline」を選択
3. 実行履歴が表示される

### ログの確認

1. 実行履歴から特定の実行をクリック
2. 各ステップのログを展開して確認

## トラブルシューティング

### よくあるエラー

#### 1. シークレットが設定されていない
```
Error: Missing WordPress credentials in .env
```
**解決策**: GitHubのシークレット設定を確認

#### 2. API制限エラー
```
Quota exceeded (429)
```
**解決策**: 
- Gemini APIの利用制限を確認
- `--limit` パラメータを減らす

#### 3. WordPress接続エラー
```
Error creating post: 401
```
**解決策**:
- WordPress URLが正しいか確認
- アプリケーションパスワードが有効か確認

### デバッグ方法

手動実行でテストする：
```bash
# ローカルで実行
cd automation
python pipeline.py --hours 6 --threshold 85 --limit 1 --dry-run
```

## カスタマイズ

### 実行頻度の変更

`.github/workflows/article-pipeline.yml` の `cron` を変更：

```yaml
# 3時間ごと
- cron: '0 */3 * * *'

# 毎日9時（UTC 0時）
- cron: '0 0 * * *'

# 平日のみ9時（UTC 0時）
- cron: '0 0 * * 1-5'
```

### パラメータの調整

`pipeline.py` の実行パラメータを変更：

```yaml
run: |
  cd automation
  python pipeline.py --hours 12 --threshold 80 --limit 5
```

## 本番環境への適用

### 1. ワークフローファイルをコミット

```bash
git add .github/workflows/article-pipeline.yml
git commit -m "feat: GitHub Actions workflow for article pipeline"
git push
```

### 2. シークレットを設定

GitHubリポジトリの設定で必要なシークレットを追加

### 3. ワークフローを有効化

- 自動的に有効化される
- 次回のスケジュール時刻に実行開始

### 4. 初回実行のテスト

手動実行で動作確認：
1. **Actions** タブを開く
2. 「Article Generation Pipeline」を選択
3. **Run workflow** をクリック

## 監視とメンテナンス

### 通知設定

GitHub Actionsの失敗通知を受け取る：
1. **Settings** → **Notifications** に移動
2. **Actions** の通知を有効化

### 定期的な確認

- 週1回、実行履歴を確認
- エラーログをチェック
- 生成された記事の品質を確認

## まとめ

✅ **設定完了後の動作**:
- 6時間ごとに自動実行
- 記事の収集・スコアリング・生成を自動化
- WordPressに自動投稿（予約投稿）

🎉 **完全自動化達成！**
