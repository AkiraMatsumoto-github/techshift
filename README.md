# LogiShift - 物流業界特化型SEOメディア

物流業界の課題解決（コスト削減、DX推進、2024年問題など）に貢献する高品質な情報を提供するSEOメディアです。
Gemini APIを活用した高度な記事自動生成システムを搭載し、最新の業界トレンドやノウハウを迅速に配信します。

## プロジェクト構成

```
.
├── themes/logishift/          # WordPressテーマ（独自開発）
├── automation/                # 記事自動生成・収集システム
│   ├── collector.py           # RSS/Sitemap収集
│   ├── scorer.py              # 記事スコアリング
│   ├── pipeline.py            # 自動化パイプライン（収集→生成）
│   ├── generate_article.py    # 記事生成メインスクリプト
│   ├── seo_optimizer.py       # SEO最適化（メタディスクリプション・タイトル）
│   └── ...
├── docs/                      # プロジェクトドキュメント
└── .github/workflows/         # GitHub Actions (CI/CD)
```

---

## 1. サーバー接続 & インフラ

本番環境は Xserver で運用されています。

### SSH接続情報

| 項目 | 値 |
|---|---|
| **ホスト** | `sv16718.xserver.jp` |
| **ポート** | `10022` (標準の22ではありません) |
| **ユーザー** | `xs937213` |
| **サイトURL** | `https://logishift.net` |

### 接続コマンド

```bash
# 基本的な接続
ssh -p 10022 xs937213@sv16718.xserver.jp

# または ~/.ssh/config 設定済みの場合
ssh xserver-logishift
```

---

## 2. デプロイ運用

GitHub Actions により、`main` ブランチへのプッシュで自動デプロイされます。

### A. WordPressテーマ (`themes/logishift/`)
- **自動デプロイ**: `themes/logishift/` 配下の変更を検知して実行。
- **手動デプロイ (緊急時)**:
  ```bash
  scp -P 10022 -r themes/logishift/ xs937213@sv16718.xserver.jp:~/logishift.net/public_html/wp-content/themes/
  ```

### B. Automationシステム (`automation/`)
- **自動デプロイ**: `automation/` 配下の変更を検知して実行。Pythonパッケージの更新も行います。
- **手動デプロイ (緊急時)**:
  ```bash
  scp -P 10022 -r automation/ xs937213@sv16718.xserver.jp:~/logishift-automation/
  ```

---

## 3. Automation System (記事自動生成)

### システム概要
1.  **Collector**: RSS/Sitemapから記事を収集（国内メディア、TechCrunch、WSJ等）。
2.  **Scorer**: Geminiで「物流への関連度」「有益性」をスコアリング。
3.  **Generator**: 高スコア記事からMarkdown記事・SEOメタデータ・画像を生成。
4.  **Poster**: WordPressへ投稿。

### 環境構築 (ローカル)

#### 必須要件
- Python 3.10+
- Docker (WordPressローカル環境用)

#### セットアップ手順

1.  **Python環境の準備**
    ```bash
    cd automation
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **環境変数の設定**
    `automation/.env` を作成:
    ```bash
    GEMINI_API_KEY=your_apiKey
    WORDPRESS_URL=http://localhost:8002
    WORDPRESS_USERNAME=admin
    WORDPRESS_APP_PASSWORD=your_appPassword
    ```

3.  **WordPress Basic Auth プラグイン (ローカル開発用)**
    ローカルのWordPressでREST API認証を行うために必要です。
    ```bash
    # プラグインのDLとインストール
    curl -L https://github.com/WP-API/Basic-Auth/archive/master.zip -o /tmp/basic-auth.zip
    unzip -q /tmp/basic-auth.zip -d /tmp/
    docker cp /tmp/Basic-Auth-master logishift-wp:/var/www/html/wp-content/plugins/basic-auth
    ```
    ※ 管理画面でプラグインを有効化してください。

### 実行コマンド詳細

#### 全自動パイプライン (`pipeline.py`)
収集から生成までを一貫して実行します。cron等での定期実行用です。

```bash
# 通常実行
python automation/pipeline.py

# データ収集範囲や生成数を調整
python automation/pipeline.py --days 2 --limit 3 --threshold 80

# ドライラン (AWS/WPへの書き込みなしで動作確認)
python automation/pipeline.py --dry-run
```

#### 個別モジュール実行

**Phase 1: 記事生成 (`generate_article.py`)**
```bash
# キーワード指定
python automation/generate_article.py --keyword "物流DX"

# 記事タイプ指定 (know/buy/do/news/global)
python automation/generate_article.py --keyword "AGV" --type buy

# スケジュール予約
python automation/generate_article.py --keyword "2024年問題" --schedule "2025-12-10 10:00"
```

#### 内部リンク自動提案機能 (Internal Link Suggester)
新規記事生成時に、既存のWordPress記事から関連性の高いものを自動抽出し、内部リンクとして埋め込む機能です。

- **仕組み**:
  1. WordPressから既存記事を取得（`InternalLinkSuggester`）
  2. Geminiが新規記事のテーマと既存記事の関連度をスコアリング
  3. 関連度の高い記事の”抜粋”を執筆プロンプトに追加指示として注入し、自然な形でリンク設置

- **設定（読み込み記事数）**:
  現在、参照する既存記事数は **最新50件** に設定されています。
  変更する場合は `automation/generate_article.py` の以下の箇所を修正してください：
  ```python
  # automation/generate_article.py
  candidates = linker.fetch_candidates(limit=50)  # この数値を変更
  ```

**Phase 2: 収集 (`collector.py`)**
```bash
# 全ソースから収集
python automation/collector.py --source all > articles.json

# 特定ソースのみ (例: TechCrunch)
python automation/collector.py --source techcrunch --days 3
```

**Phase 2: スコアリング (`scorer.py`)**
```bash
# ファイル入力でスコアリング
python automation/scorer.py --input articles.json --threshold 80 --output scored.json
```

**Phase 3: 固定ページ生成 (`generate_static_pages.py`)**
```bash
python automation/generate_static_pages.py --all
```

---

## 4. トラブルシューティング

### サーバー運用

#### gcloud 認証ができてない
```bash 
gcloud auth application-default login
```

#### パーミッションエラーでテーマが反映されない
```bash
ssh -p 10022 xs937213@sv16718.xserver.jp
chmod -R 755 ~/logishift.net/public_html/wp-content/themes/logishift
```

#### Automationスクリプトが動かない (依存関係)
Miniconda環境の再構築が必要な場合があります。
```bash
ssh -p 10022 xs937213@sv16718.xserver.jp
cd ~/logishift-automation/automation
conda install -c conda-forge lxml -y
pip install -r requirements.txt
```

#### GitHub Actions のデプロイ失敗
GitHub Secrets (`Settings > Secrets`) を確認してください：
- `SERVER_HOST`: sv16718.xserver.jp
- `SERVER_USER`: xs937213
- `SSH_PORT`: 10022
- `SSH_PRIVATE_KEY`: (正しい秘密鍵か)

### ローカル開発
#### 環境立ち上げ
```bash
source automation/venv/bin/activate
export GOOGLE_CLOUD_LOCATION=global   
```

#### 記事が生成されない (スコア不足)
`pipeline.py` の `--threshold` デフォルト値(85)が高すぎる可能性があります。`--threshold 60` 程度に下げてお試しください。

## 関連ドキュメント
- [テーマデプロイガイド](docs/00_meta/theme_deployment_guide.md)
- [本番環境デプロイガイド](docs/00_meta/production_deployment_guide.md)
