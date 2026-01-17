# Automation Python Scripts Overview

`automation/` ディレクトリ内のPythonスクリプトの役割と機能についての解説です。
TechShiftでは、既存の収集・分析パイプラインを「技術ロードマップの更新」という目的に特化させています。

> [!NOTE]
> **Phase Strategy**
> *   **Phase 1 (MVP)**: `collector.py` (News Fetching) と `scorer.py` (Drafting Pre-process) を使用し、編集者による手動分析を支援します。
> *   **Phase 2 (Automation)**: `impact_analyzer.py` (Deep Analysis) などの高度な推論ロジックを実装します。

## 🛠️ Data Collection (`automation/collectors/`)

生データを外部ソースから取得し、正規化して保存するモジュール群です。

### `collector.py`
- **役割**: RSSヘッドライン収集 (News Aggregator)
- **機能**:
    - 指定されたRSSフィード（TechCrunch, VentureBeat, NASA, Nature等）から最新記事を収集。
    - **TechShift特有**: 重点3トピック（Multi-Agent, PQC, Solid-State Battery）に関連するソースを優先的にクロールします。

### `url_reader.py`
- **役割**: 全文記事スクレイピング (Content Extractor)
- **機能**:
    - 記事URLから本文、タイトル、著者情報を抽出。
    - **Fallback**: スクレイピング失敗時やブロック時は、RSSのSummaryを代用してエラーを回避するロバスト性を持っています。

---

## 🧠 AI Analysis (`automation/analysis/`)

収集したデータに対し、Geminiを用いて洞察（インサイト）を付与するモジュール群です。

### `impact_analyzer.py` [Phase 2] (New: Replaces `scenario_generator.py`)
- **役割**: ロードマップ影響度分析
- **機能**:
    - ニュース記事（事実）が、既存の技術ロードマップに与える影響（Impact）を判定。
    - **Logic Chain**: Fact -> Analysis -> Impact -> Conclusion の3段階論理で「時期の前倒し/遅延」や「ボトルネック解消」を導出します。

### `sentiment_analyzer.py` [Phase 2]
- **役割**: 技術トレンドセンチメント分析
- **機能**:
    - その技術に対する社会的な期待値（Hype Cycle上の位置）を推定します。

### `scorer.py` [Phase 1 (Drafting)]
- **役割**: 記事重要度評価スコアラー
- **機能**:
    - ニュースが「技術的ブレイクスルー」を含んでいるかを評価。
    - 単なる新製品発表（スマホの機種変など）は低スコア、基礎研究の進展は高スコアと判定します。

---

## ⚙️ Core Pipeline & Generators

### `pipeline.py`
- **役割**: 実行オーケストレーター
- **機能**:
    - Collection -> Analysis -> WordPress Post の一連の流れを制御します。
    - **Event-Driven Update**: 重要なニュース（High Impact）が検出された場合、即座に「ロードマップ親ページ」の更新トリガーを引きます。

### `generate_article.py`
- **役割**: 記事生成実行スクリプト
- **機能**:
    - 分析結果を元に、WordPress投稿用HTMLを作成。
    - **Vertical Timeline**: 記事内に縦型タイムラインコンポーネントを埋め込み、そのニュースがロードマップ上のどこに位置するかを視覚化します。

---

## 🔌 Clients & Helpers (Common Infrastructure)

### `gemini_client.py`
- **役割**: Gemini API Interface (Vertex AI / Studio)
- **機能**: 記事・画像生成、構造化データ抽出（JSON）。TechShift専用のプロンプト（Connecting Dots / Reality Check）を管理。

### `wp_client.py`
- **役割**: WordPress REST API Client
- **機能**: 記事投稿、カスタムフィールド（予測時期データ）の更新。

### `sns_client.py`
- **役割**: X (Twitter) API Client
- **機能**: "Shift Alert"（予測変更通知）の自動投稿。

### `seo_optimizer.py`
- **役割**: SEO最適化
- **機能**: トピッククラスターモデルに基づき、親ページ（ロードマップ）への内部リンクを自動生成。
