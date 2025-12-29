# FinShift 開発実装計画 (Phase 1)

FinShiftの立ち上げに向けた、初期開発フェーズ（Phase 1）の詳細計画書です。
Logishiftの既存資産をベースに、金融メディア特有の機能を実装します。

### Related Documents
- **Media Strategy**: [finshift_media_plan.md](../00_project/finshift_media_plan.md) - コンセプト、ターゲット、収益化戦略
- **System Architecture**: [system_architecture.md](../01_architecture/system_architecture.md) - 詳細なシステム構成図とデータフロー
- **Site Map**: [sitemap.md](../01_architecture/sitemap.md) - URL設計とカテゴリ構造
- **Wireframes**: [docs/02_design/wireframes/](../02_design/wireframes/) - モバイルファースト画面設計一式
- **Weekly Summary Spec**: [weekly_summary_feature.md](../02_design/weekly_summary_feature.md) - 週次集計機能の仕様
- **Component Design**: [component_design.md](../02_design/component_design.md) - UIコンポーネント詳細

## 1. 決定・確認事項 (User Review Required)

### Q1. 開発環境の構成
- **決定**: **B案 (ポート8002 & DB分離)**
    - ポート `8002` で別コンテナを立ち上げ、データベースも Logishift とは完全に分離します。
    - これにより、カテゴリ・タグ構造の違いによる衝突を防ぎます。

### Q2. Gitリポジトリ構成
- **決定**: **B案 (別リポジトリ)**
    - FinShift用に新しいGitリポジトリを作成します。
    - 理由: 共通化できる部分が少なく、独自機能（金融API、シナリオ生成）でファイルが肥大化するため。
    - **対応**: 
        1. 現在のフォルダ構成から必要なファイル（`docker-compose`の雛形、一部の汎用スクリプト）のみをコピーして新規リポジトリを開始します。
        2. `/Users/matsumotoakira/Documents/Private_development/finshift` (仮) などの別ディレクトリを作成して作業します。

### Q3. スクレイピングのリスク対策
- **現状のLogishiftの仕組み**:
    1.  **RSS取得 (`collector.py`)**: `feedparser` を使用し、登録されたRSSフィードから記事リスト（タイトル、URL）を取得。これが入口。
    2.  **本文抽出 (`url_reader.py`)**: 取得したURLに対し、`requests` + `BeautifulSoup` でアクセス。
        - サイトごとに定義されたセレクタ（例: `div.article-content`）で本文をピンポイントで抽出。
        - 取得できない場合は「フォールバック」として、ページ内の全テキストを取得する等の処理が動く。
- **FinShiftでの方針**:
    - 基本はこの仕組みを踏襲します。
    - **変更点**: 金融系サイトはスクレイピング対策が強い場合があるため、`BeautifulSoup` で取れない場合は即座に **「RSSの概要文 (Summary) のみを使う」** モードに切り替える処理を追加します。深追いはしません。

---

## 2. 実装詳細 (Implementation Details)

### 2.1. 新規リポジトリ構築 (`finshift`)
- **方針**: 現在のディレクトリ (`/Users/matsumotoakira/Documents/Private_development/finshift`) はLogishiftのコピーであるため、**既存ファイルを上書き・整理して** FinShift用の構成に作り変えます。

- **ディレクトリ構成案**:
```text
finshift/ (Current Dir)
├── docker-compose.yml   # Port: 8002, DB: finshift_db
├── automation/          # Python Scripts
│   ├── collectors/      # RSS & Scraper
│   ├── analysis/        # AI Analysis
│   ├── pipeline.py
│   └── ...
└── themes/
    └── finshift/        # Custom WP Theme
```

### 2.2. Python Automation 環境 (`/automation`)
金融メディア用のデータ収集・分析モジュールを追加します。

#### [NEW] `collectors/` (データ収集)
- [x] **`collector.py`**: RSSフィードからのヘッドライン収集（旧名維持）。Yahoo Finance (Global/JP), CNBC, SCMP, Mint, Jakarta Post, Crypto等のフィード定義実装済み。
- [x] **`url_reader.py`**: 特定サイトの本文抽出・スクレイピング（旧名維持）。金融サイト (Yahoo, CNBC, 36Kr, Economic Times等) の構造に対応。RSS Summaryによるフォールバック実装済み。
- [x] **`market_data.py`**: 株価・指数データ (`yfinance`) および Risk Monitor用データ (1D/1W/1M変化率) の取得・保存 (JSON出力) 実装済み。

#### [NEW] `analysis/` (AI分析)
- **`scenario_generator.py`**: Gemini API用プロンプト。「ニュース事実」を入力し、「強気/弱気シナリオ」と「発生確率」を出力。
- **`sentiment_analyzer.py`**: Fear & Greed Index等の数値化ロジック。

#### [NEW] `tools/` (運用ツール)
- **`batch_generate_2025.py`**: SEOキーワードリストに基づく記事一括生成スクリプト（手動実行用）。


#### [MODIFY] `pipeline.py` (実行管理)
- **ハイブリッド投稿戦略 (SEO対策)**:
    1. **Daily Briefing (Daily Flow)**:
        - 地域ごとの市況まとめ記事。1日1回生成。
        - ターゲット: リピーター、日々の市況確認。「日付 + インド株」等の検索狙い。
    2. **Featured News (Stock Content)**:
        - スコアリングで **閾値（例: 80点）を超えた重要ニュース** は、別途「個別記事」としても生成。
        - ターゲット: 特定銘柄指名買い検索（例: "Tata Motors 業績", "中国 不動産対策"）。
        - デイリー記事内に個別記事への内部リンクを自動生成し、回遊性を高める。
    3. **Long-tail SEO (Manual Asset)**:
        - **`batch_generate_2025.py`** を活用 (Manual Trigger)。
        - 運用安定期（Phase 2以降目安）に入力キーワードリスト等からストック記事を一括生成。
        - 検索ボリュームのある用語（例: "インドETF 比較", "中国株 買い方"）の流入獲得を狙う。
    4.  **Weekly Summary (Review & Forecast)**:
        - **`workflows/weekly_summary.yml`**: 毎週日曜夜に実行。
        - 直近1週間の「地域別デイリー記事」やニュース記事の内容を集計し、翌週の市場展望をまとめる。
        - 「先週の振り返り」+「翌週の注目イベント/シナリオ」の構成。

- 実行コマンド例: `python pipeline.py --region india --mode daily` (まとめ) / `--mode news` (個別)

#### [NEW] Workflows (地域別実行)
- RSS一括取得・スコアリング方式（Logishift型）ではなく、**国ごとのデイリー・ブリーフィング**を目指します。
- **Phase 1 対象地域**: 米国、中国、インド、**日本、インドネシア**（これら5地域を初期実装）。
- 将来的には欧州、ベトナムなども同様の仕組みで追加可能。
- **`workflows/us_daily.yml`**: 米国市場 (NY Close後)
- **`workflows/china_daily.yml`**: 中国市場 (CST 終了後)
- **`workflows/india_daily.yml`**: インド市場 (IST 終了後)
- **`workflows/japan_daily.yml`**: 日本市場 (大引け後)
- **`workflows/indonesia_daily.yml`**: インドネシア市場 (JKT 終了後)
- **`workflows/market_ticker.yml`**: **[NEW] Risk Monitor更新用**
    - 実行頻度: 20分おき (毎時 00, 20, 40分)。
    - 動作: `market_data.py` を実行し、主要資産の1D/1W/1M騰落率をWordPressにPush。

### 2.3. WordPress テーマ開発 (`/themes`)
#### [NEW] `themes/finshift/`
- **デザインコンセプト**: "Financial Terminal" (Bloomberg/Reuters風)。ダークモード基調、情報密度高め。

#### **A. フロントページ (`front-page.php`)**
- **First View (Market Dashboard)**:
    - **Global Ticker**: 主要指数（S&P500, Nasdaq, Nikkei, Nifty50, Shanghai Comp）のリアルタイムレート (TradingView Widget利用)。
    - **Market Sentiment**: Automationが集計した「本日の市場センチメント(Fear & Greed)」を表示。
        - *Automation要件*: `wp_options` または専用CPTにセンチメント数値を保存する処理が必要。
- **Daily Briefing Section**:
    - 各国（US, CN, IN, JP, ID）の「最新のデイリー記事」をカード表示。
    - 「今日のシナリオ」を要約表示（カスタムフィールド `scenario_summary` を利用）。
- **Latest News Feed**:
    - タブ切り替え（All / Stocks / Crypto / FX）。

#### **B. 市場別ランディングページ (`page-market.php`)**
- **Template Hierarchy**: `page-india.php`, `page-usa.php` 等、スラッグで分岐または共通テンプレートでクエリ制御。
- **Components**:
    - **Regional Chart**: その国の代表指数のTradingViewチャート (Large size)。
    - **Key Metrics**: PER, PBR, 配当利回りなどの国別平均指標（手動更新またはAutomationで取得）。
    - **Related Articles**: その地域タグ (`India`) が付いた記事のみを表示。

#### **C. 記事詳細ページ (`single.php`)**
- **Sidebar**:
    - 関連銘柄のミニチャート表示（記事内の銘柄コード `TATA.NS` 等を自動検出してWidget化）。
    - *Automation要件*: 記事生成時に銘柄コードを抽出・タグ保存するロジック (`tags` or `custom_field`)。

### 2.4. Automationへの追加要件 (Feedback from Theme Specs)
テーマ側のリッチな表示を実現するために、以下のデータ保持ロジックが必要です：
1.  **センチメント保存**: `automation/analysis/sentiment_analyzer.py` の結果を WP Options API に POST する機能。
2.  **シナリオ要約**: 記事本文とは別に、トップページ表示用の「3行まとめ」を生成し、カスタムフィールド `scenario_summary` に保存。
3.  **銘柄コード抽出**: 記事生成時に登場するティッカーシンボル（例: $NVDA, $TSLA）を抽出し、メタデータとして保存。

## 3. 検証計画 (Verification Plan)

### 自動テスト
- `pytest` を導入し、データ収集から記事下書き作成までのフローをテスト。
- AI生成テキストに「免責文言」が含まれているかを自動チェック。

### 手動確認手順
1.  **ローカル環境 (localhost:8002)**:
    - トップページのTradingViewウィジェットが正しく表示されるか。
    - 別リポジトリとして立ち上げた環境で、WordPressが正常に動作するか。
2.  **記事品質**:
    - 生成されたシナリオが、元ニュースの内容と整合しているか。
