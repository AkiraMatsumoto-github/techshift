# Automation Python Scripts Overview

`automation/` ディレクトリ内のPythonスクリプトの役割と機能についての解説です。
FinShiftでは、Logishiftの既存資産（SEO最適化、WordPress連携など）を最大限活用しつつ、金融特化の「収集」と「分析」モジュールを拡張しています。

## 🛠️ Data Collection (`automation/collectors/`)

生データを外部ソースから取得し、正規化して保存するモジュール群です。

### `collector.py`
- **役割**: RSSヘッドライン収集 (News Aggregator)
- **機能**:
    - 指定されたRSSフィード（Yahoo Finance, CNBC, 36Kr等）から最新記事を収集。
    - 重複除外、日付フィルタリングを行い、記事リストを生成します。

### `url_reader.py`
- **役割**: 全文記事スクレイピング (Content Extractor)
- **機能**:
    - 記事URLから本文、タイトル、著者情報を抽出。
    - **FinShift特有機能**: 金融メディア（Yahoo, SCMP等）固有のHTML構造に対応。
    - **Fallback**: スクレイピング失敗時やブロック時は、RSSのSummaryを代用してエラーを回避するロバスト性を持っています。

### `market_data.py`
- **役割**: 市場データ収集 (Market Ticker)
- **機能**:
    - `yfinance` を使用して、主要指数（S&P500, Nikkei, Gold, BTC等）の価格データを取得。
    - 1日(1D), 1週間(1W), 1ヶ月(1M) の騰落率を計算。
    - フロントエンド表示用にJSONファイル (`themes/finshift/assets/data/risk_monitor.json`) を生成・保存します。

---

## 🧠 AI Analysis (`automation/analysis/`)

収集したデータに対し、Geminiを用いて洞察（インサイト）を付与するモジュール群です。

### `scenario_generator.py` (Completed)
- **役割**: シナリオ分析・記事生成
- **機能**:
    - ニュース記事（事実）を入力として受け取る。
    - Geminiに「強気シナリオ」「弱気シナリオ」を生成させる。
    - 投資家向けの「Action Plan」を含む構造化された記事本文を作成します。

### `sentiment_analyzer.py` (Completed)
- **役割**: 市場センチメント分析
- **機能**:
    - ニュースのヘッドラインと市場データ（VIX/モメンタム）から、現在の市場心理（Fear & Greed）を数値化します。

### `scorer_legacy.py` (Reuse)
- **役割**: 記事関連度評価スコアラー
- **機能**:
    - ニュース記事が「スイングトレード記事」として適しているかを0-100点で評価。
    - FinShift用にプロンプト（評価基準）を調整して利用予定。

### `classifier_legacy.py` (Reuse)
- **役割**: カテゴリ・タグ分類
- **機能**:
    - 記事内容から適切なWordPressタグ（Region: `India`, Sector: `Tech` 等）を推奨します。

---

## ⚙️ Core Pipeline & Generators

### `pipeline.py` (Updated)
- **役割**: 実行オーケストレーター
- **機能**:
    - Collection -> Analysis -> WordPress Post の一連の流れを制御します。
    - 引数によって「特定地域のデイリーまとめ」や「速報ニュース」の生成モードを切り替えます。

### `generate_article.py` (Reuse/Update)
- **役割**: 記事生成実行スクリプト
- **機能**:
    - 分析結果を元に、WordPress投稿用HTMLを作成。
    - アイキャッチ画像生成 (`gemini_client`呼び出し)、メタデータ設定を行い、`wp_client`経由で投稿します。

### `generate_weekly_summary.py` (Reuse/Update)
- **役割**: 週間サマリー記事生成
- **機能**:
    - 過去1週間の記事を集計し、翌週の市場展望記事を生成します。

### `generate_static_pages.py` (Reuse)
- **役割**: 固定ページ生成
- **機能**: 
    - 利用規約、免責事項、プライバシーポリシー等を自動生成します。

---

## 🔌 Clients & Helpers (Common Infrastructure)

Logishiftからそのまま流用・共通化されるインフラモジュール群です。

### `gemini_client.py`
- **役割**: Gemini API Interface (Vertex AI / Studio)
- **機能**: 記事・画像生成、要約、翻訳など、全てのAI処理の窓口。

### `wp_client.py`
- **役割**: WordPress REST API Client
- **機能**: 記事投稿、画像アップロード、タグ管理。

### `sns_client.py`
- **役割**: X (Twitter) API Client
- **機能**: 記事公開時の自動ポスト。

### `seo_optimizer.py` (Reuse)
- **役割**: SEO最適化
- **機能**: 検索意図に基づいたMeta Description生成、構造化データ(JSON-LD)作成。

### `internal_linker.py` (Reuse)
- **役割**: 内部リンク最適化
- **機能**: 過去記事データベースから関連用語を検索し、記事内に内部リンクを自動挿入。

### `summarizer.py` (Reuse)
- **役割**: コンテキスト圧縮・要約 (Context Pre-processor)
- **機能**: 
    - 過去記事や長文ニュースを要約し、**内部リンク提案 (`internal_linker`)** の検索対象として最適化します。
    - 新記事生成時にGeminiへ渡す「参考情報（Context）」を圧縮し、精度の向上とトークン節約を行います。

### `setup_taxonomy.py` (Reuse)
- **役割**: 初期セットアップ
- **機能**: WordPressのカテゴリ・タグ構造を定義ファイル（`finshift_media_plan`等）に基づいて自動構築します。

---

## 🧰 Operation Tools (`automation/tools/`)

手動実行やメンテナンス目的で使用する補助ツール群です。

### `batch_summarize.py`
- **役割**: 過去記事のAI要約・メタデータ付与
- **機能**:
    - 既存のWordPress投稿をスキャンし、AI構造化サマリーが未生成の記事に対して生成・保存を行います。
    - **SEO効果**: `internal_linker` が正確な内部リンクを提案するための「インデックス作り」として機能します。

### `batch_generate_2025.py` (Planned)
- **役割**: ストック記事一括生成
- **機能**: 
    - キーワードリスト（CSV）を読み込み、「初心者ガイド」や「口座解説」などの普遍的な記事を一括生成します。
