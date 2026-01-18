# TechShift - 未来予測メディア

世界のテクノロジー進化（AI, Quantum, Green Tech等）を追跡し、スイングトレーダーやビジョナリー向けに「未来への羅針盤 (Dynamic Navigation Chart)」を提供する情報メディアです。
Gemini APIを活用した高度な自動生成システムにより、客観的な技術インパクト分析と投資シナリオを迅速に配信します。

## プロジェクト構成

```
.
├── themes/techshift/          # WordPressテーマ（独自開発）
├── automation/                # 自動化システム
│   ├── collectors/            # データ収集モジュール (News Streams)
│   ├── daily_briefing.py      # デイリーブリーフィング生成 (TechShift Domains)
│   ├── pipeline.py            # 記事生成パイプライン (Topic Focus)
│   ├── gemini_client.py       # Gemini APIクライアント
│   └── ...
├── docs/                      # プロジェクトドキュメント
└── .github/workflows/         # GitHub Actions (CI/CD)
```

---

## 1. Automation System

TechShiftの自動化システムは、ニュース収集からインパクト分析、記事生成、WordPress投稿までを一貫して行います。

### セットアップ (ローカル)

#### 必須要件
- Python 3.10+
- Gemini API Key

#### 手順

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
    WORDPRESS_URL=http://localhost:8003 # or https://techshift.net
    # WP_USER / WP_APP_PASSWORD
    WORDPRESS_USERNAME=admin
    WORDPRESS_APP_PASSWORD=your_appPassword
    ```

### 実行ガイド

#### A. デイリーブリーフィング (`daily_briefing.py`)
TechShiftの主要4ドメイン（AI, Quantum, Green, General）のニュースを分析し、ブリーフィング記事を生成します。

```bash
# 全ドメインの分析・生成 (AI, Quantum, Green, General)
python automation/daily_briefing.py --region all --phase analyze

# ドライラン (投稿・保存なし、ログ出力のみ)
python automation/daily_briefing.py --region all --phase analyze --dry-run

# 特定ドメインのみ実行
python automation/daily_briefing.py --region AI --phase analyze
python automation/daily_briefing.py --region Green --phase analyze
```

#### B. 汎用記事パイプライン (`pipeline.py`)
特定のトピック深掘り記事を生成します。

```bash
# 基本実行
python automation/pipeline.py --hours 12 --threshold 75 --limit 2

# 全ソースから収集
python automation/collector.py --source all > articles.json
```

#### C. タクソノミー同期 (`setup_taxonomy.py`)
WordPressのカテゴリ・タグ設定を同期します。環境セットアップ時に実行してください。

```bash
python automation/setup_taxonomy.py
```

---

## 4. トラブルシューティング

### サーバー運用

#### gcloud 認証
```bash 
gcloud auth application-default login
```

#### パーミッションエラー修正
```bash
ssh -p 10022 [user]@[host]
chmod -R 755 ~/techshift.net/public_html/wp-content/themes/techshift
```

#### GitHub Actions のデプロイ失敗
GitHub Secrets (`Settings > Secrets`) を確認してください：
- `SERVER_HOST`: (Server Host)
- `SERVER_USER`: (User)
- `SSH_PORT`: 10022
- `WP_URL`: (WordPress URL)
- `GEMINI_API_KEY`: (API Key)

### ローカル開発
#### 環境立ち上げ
```bash
source automation/venv/bin/activate
export GOOGLE_CLOUD_LOCATION=global   
```

## 関連ドキュメント
- [テーマデプロイガイド](docs/00_meta/theme_deployment_guide.md)
- [本番環境デプロイガイド](docs/00_meta/production_deployment_guide.md)
