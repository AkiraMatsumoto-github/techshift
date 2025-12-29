# FinShift System Architecture

## 1. System Overview

本システムは、世界中の金融ニュース・市況データを自動収集し、AIによる分析・示唆を付加してWebメディアに公開する完全自動化パイプラインです。
FinShiftでは、Logishiftの基盤を拡張し、**「国別デイリー・ブリーフィング（フロー）」** と **「重要ニュース個別深掘り（ストック）」** のハイブリッド戦略を採用します。

```mermaid
graph TD
    subgraph "Data Sources (Global)"
        S1[Global News<br/>(Reuters, Bloomberg, SCMP, Mint)] -->|RSS| RSSFetcher
        S2[Market Data<br/>(Yahoo Finance)] -->|API| MarketData
        S3[Sentiment/Events<br/>(CNN, Investing.com)] -->|Scraping| Scraper
    end

    subgraph "Automation Core (Python)"
        RSSFetcher & MarketData & Scraper --> RawDB[(Raw Data Store)]
        RawDB --> Pipeline{Pipeline Orchestrator<br/>(Daily/Weekly/News)}
        
        Pipeline -->|Analyze| Analyzer[AI Analyzer<br/>(Gemini)]
        Analyzer -->|Generate Scenario| ScenarioGen[Scenario Generator]
        Analyzer -->|Calc Sentiment| Sentiment[Sentiment Analyzer]
        
        ScenarioGen & Sentiment --> Drafter[Article Drafter]
    end

    subgraph "Presentation (WordPress)"
        Drafter -->|Post via API| WP[WordPress Site]
        WP -->|Display| Page[Front Page / Market Page]
        WP -->|Store| Meta[Custom Fields<br/>(Sentiment/Scenario)]
    end
```

## 2. Component Design

### 2.1. Collectors (`automation/collectors/`)
外部データ収集を担当するモジュール群。
- **`rss_fetcher.py`**: 
    - 各国（US, CN, IN, JP, ID）の主要メディアRSSを取得。
    - コンテンツ全文が取れない場合は、概要(Summary)のみを取得してAIに渡すフォールバック機能を実装。
- **`scraper.py`**: 
    - 特定サイト（恐怖指数、経済指標カレンダー）からのスクレイピング。
    - RSSで取得できない独自ソース（中国現地サイト等）の補完。
- **`market_data.py`**: 
    - `yfinance` 等を利用し、各国の主要指数・為替・コモディティ価格を取得。
    - **Risk Monitor用データ**: BTC, Gold, Oilについて「1日(1D), 1週間(1W), 1ヶ月(1M)」の騰落率を計算し、WP Options APIに保存。
- **`market_ticker.yml`**:
    - 各国市場の主要指数、為替、コモディティのティッカーシンボルと表示名を定義する設定ファイル。

### 2.2. AI Analysis (`automation/analysis/`)
取得データに「金融的付加価値」を与えるコアロジック。
- **`scenario_generator.py`**: 
    - 入力: ニュース群 + 市況データ
    - 出力: 「強気シナリオ」「弱気シナリオ」「横ばい」の3パターンとその発生確率。
    - **Disclaimer**: 生成テキストに必ず投資助言ではない旨の免責を注入。
- **`sentiment_analyzer.py`**:
    - 入力: ニュースのトーン + VIX/Fear&Greed指数
    - 出力: 市場センチメントスコア (0-100) および「Greed/Fear」のラベル。
- **`scorer_legacy.py`**: 
    - ニュースの重要度（Impact）を0-100で採点し、80点以上を「個別記事」候補とする。

### 2.3. Tools (`automation/tools/`)
- **`batch_generate_2025.py`**: SEOキーワードリストに基づき、ストック型記事（解説記事など）を一括生成する手動ツール。

## 3. Workflow & Pipeline

### 3.1. Daily Briefing (Regional)
国・地域ごとに1日1回実行されるメインフロー。
- **Trigger**: 各市場のクローズ後 (Cronでスケジュール)。
- **Flow**:
    1.  指定地域 (`--region india` 等) のニュースを収集。
    2.  市況データ（指数、騰落率）を取得。
    3.  AIが「本日の市況概況」と「注目ニュース3選」を要約。
    4.  「明日のシナリオ」を生成。
    5.  1本の記事としてWordPressに投稿。

### 3.2. Featured News (High Impact)
スイングトレードに影響を与える重要ニュースの個別速報。
- **Trigger**: 6時間ごとの定期ポーリング時に判定。
- **Logic**: スコアリング > 80点 のニュースのみを対象に独立した記事を生成。デイリー記事から内部リンクされる。

### 3.3. Weekly Summary
週末に行う振り返りと来週の展望。
- **Trigger**: 日曜夜。
- **Flow**: 過去7日間のDBデータを利用し、週次のトレンド変化と翌週の「Watch List」を作成。

## 4. WordPress Architecture (`themes/finshift`)

### 4.1. Theme Structure
- **Design**: "Financial Terminal" スタイル。ダークモード推奨。
- **`front-page.php`**: 
    - **TradingView Widget**: ヘッダー下にGlobal Ticker。
    - **Market Sentiment**: `automation` から送られたセンチメント値を表示。
    - **Daily Compass**: 各国の最新ブリーフィングへのナビゲーション。
- **`page-market.php`**: `page-india.php` 等、国別のランディングページ。
- **`single.php`**: 記事詳細。関連銘柄のミニチャートをWidget表示。

### 4.2. Data Integration
Automationとテーマの連携用データ。
- **Custom Fields**:
    - `scenario_summary`: トップページ表示用の3行要約。
    - `bull_scenario` / `bear_scenario`: 記事内のタブ表示用詳細テキスト。
- **Options API**:
    - `finshift_market_sentiment`: 現在の市場センチメント値。

## 5. Directory Structure

```text
/finshift
├── automation/
│   ├── collectors/         # RSS, Scraper, Market Data
│   ├── analysis/           # Scenario, Sentiment, Scorer
│   ├── tools/              # Manual SEO Batch Generator
│   ├── workflows/          # GitHub Actions (Daily/Weekly)
│   └── pipeline.py         # Main Entry Point
├── themes/
│   └── finshift/           # Custom WP Theme
│       ├── front-page.php
│       ├── page-market.php
│       └── ...
└── docs/
    ├── 00_project/         # Project Management
    ├── 01_architecture/    # System Design
    └── 02_design/          # UI/Feature Specs
```
