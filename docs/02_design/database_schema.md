# FinShift データベース・スキーマ設計

本ドキュメントは、FinShiftの市場分析データを保存するためのデータベーススキーマ定義書です。
WordPressで使用している既存の **MySQL 8.0** インスタンスに相乗りし、`fs_` プレフィックスを付けた専用テーブル群を作成して管理します。

## 1. 概要

**目的:**
ニュース記事、市場データ、AI分析結果を永続化（保存）することで、以下の高度な分析を実現します。
1.  **トレンド分析**: センチメントや市場レジーム（Risk-On/Off）の時系列変化を追跡。
2.  **コンテキスト再利用**: 「Global」の分析結果を、各リージョンのブリーフィングで使い回し、APIコストと処理時間を削減。
3.  **予実管理**: 過去のシナリオ（Bull/Bear）と実際の市場変動を比較し、分析精度を評価・改善する。

**接続情報:**
- **Host**: `db` (Docker service name)
- **Port**: `3306` (Internal)
- **Database**: `wordpress` (WPと同じDBを使用)
- **User/Pass**: `wordpress` / `password`

## 2. テーブル定義

### 2.1. 記事データ (`fs_articles`)
RSSフィードから収集した生のニュース記事データを格納します。
**統合ワークフロー (Unified Workflow)** において、最初に一括取得した記事をここに保存し、後続の各リージョンごとの記事生成ループで参照します。

*   **目的**:
    1.  **APIコスト削減**: 全リージョンで共通のグローバルニュース（USなど）を一度だけ取得・要約し、使い回す。
    2.  **一貫性の担保**: 全リージョンの記事が「同じソースデータのセット」に基づいていることを保証する。
*   **更新スクリプト**: `automation/daily_briefing.py` (Global Collection Phase)

| カラム名 | データ型 | 説明 |
| :--- | :--- | :--- |
| `id` | `BIGINT AUTO_INCREMENT` | プライマリキー |
| `url_hash` | `CHAR(64)` | URLのSHA256ハッシュ (ユニーク制約)。重複排除に使用。 |
| `title` | `VARCHAR(512)` | 記事タイトル |
| `source` | `VARCHAR(100)` | ソースID (例: `yahoo_finance_top`) |
| `region` | `VARCHAR(10)` | 推定リージョン (US, JP, CN, etc.)。ソース元から判定。 |
| `published_at` | `DATETIME` | 記事の公開日時 |
| `fetched_at` | `DATETIME` | システムが取得した日時 |
| `summary` | `TEXT` | RSSサマリー または スクレイピングした要約 |
| `is_relevant` | `BOOLEAN` | AIによるRelevance Check結果 (1=市場に関連, 0=ノイズ) |
| `relevance_reason` | `TEXT` | AIが判定した理由 (デバッグ・精度改善用) |
| `sentiment_score` | `INT` | (Optional) 簡易センチメントスコア (0-100) |

### 2.2. 市場スナップショット (`fs_market_snapshots`)
分析時点での市場データ（指数、為替、商品、金利など）の断面データを格納します。

*   **目的**: 「その時、市場はどうだったか」を記録し、後からAI分析の根拠として参照する。また、前日比などの計算に使用。
*   **更新スクリプト**: `automation/daily_briefing.py` (Market Data Fetchフェーズ) が `market_data.py` の結果を保存。

| カラム名 | データ型 | 説明 |
| :--- | :--- | :--- |
| `id` | `BIGINT AUTO_INCREMENT` | プライマリキー |
| `date` | `DATE` | 市場データの日付 (ユニーク制約)。1日1レコードを基本とする。 |
| `data_json` | `JSON` | `market_data.py` が取得した全データ (Indices, Forex, Crypto等) のJSONダンプ。 |
| `vix_close` | `FLOAT` | VIX指数 (検索・インデックス用) |
| `spx_close` | `FLOAT` | S&P 500指数 (検索・インデックス用) |
| `us10y_yield` | `FLOAT` | 米10年債利回り (検索・インデックス用) |
| `created_at` | `DATETIME` | レコード作成日時 |

### 2.3. 経済指標カレンダー (`fs_economic_events`)
重要イベントを格納するテーブル。**1イベント1レコード**で管理する（日付重複可）。

| カラム名 | データ型 | 説明 |
| :--- | :--- | :--- |
| `id` | `BIGINT AUTO_INCREMENT` | プライマリキー |
| `event_date` | `DATE` | イベント日 |
| `country` | `VARCHAR(50)` | 対象国 (例: US, JP) |
| `event_name` | `VARCHAR(255)` | イベント名 (例: CPI, FOMC議事録) |
| `impact` | `VARCHAR(20)` | 重要度 (High/Medium/Low) |
| `description` | `TEXT` | 詳細や予測値など (Optional) |
| `source` | `VARCHAR(50)` | データソース (yahoo, rss_extract) |
| `created_at` | `DATETIME` | レコード作成日時 |

### 2.4. AI分析結果 (`fs_daily_analysis`)
AI（Gemini）によって生成された、リージョンごとの分析結果やシナリオを格納します。

*   **目的**: 過去の分析結果（センチメント、シナリオ）の蓄積。Webサイト表示や、次回の分析時のコンテキスト（「昨日はこう予測した」）として利用。
*   **更新スクリプト**: `automation/daily_briefing.py` (Generationフェーズ)

| カラム名 | データ型 | 説明 |
| :--- | :--- | :--- |
| `id` | `BIGINT AUTO_INCREMENT` | プライマリキー |
| `date` | `DATE` | 分析対象日 |
| `region` | `VARCHAR(10)` | 対象リージョン (US, JP, CN, IN, ID) |
| `sentiment_score` | `INT` | Fear & Greedスコア (0-100) |
| `sentiment_label` | `VARCHAR(20)` | 例: "Extreme Greed", "Neutral" |
| `market_regime` | `VARCHAR(50)` | 例: "Goldilocks", "Risk-Off" |
| `scenarios_json` | `JSON` | 生成されたシナリオデータ。構造: `{ "bull": {...}, "bear": {...} }` |
| `full_briefing_md` | `MEDIUMTEXT` | 生成された記事のMarkdown全文 |
| `wp_post_id` | `BIGINT` | WordPressに投稿された記事ID (連携用) |
| `created_at` | `DATETIME` | レコード作成日時 |

## 3. 実装ステップ

1.  **依存ライブラリ**: `mysql-connector-python` をインストール。
2.  **初期化**: `automation/db/init_db.py` を作成し、上記テーブルが存在しなければ作成する処理を実装。
3.  **データ保存の実装**: `automation/daily_briefing.py` を改修し、各フェーズでデータをDBにインサートする処理を追加。
