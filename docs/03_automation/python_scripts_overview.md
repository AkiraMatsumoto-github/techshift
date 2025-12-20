# Automation Python Scripts Overview

`automation/` ディレクトリ内のPythonスクリプトの役割と機能についての解説です。

## 🛠️ 主要実行スクリプト (Executables)

これらは直接実行してタスクを行うためのスクリプトです。

### `pipeline.py`
- **役割**: 記事生成の全自動パイプラインのオーケストレーター
- **主なフロー**:
    1. **収集 (Collection)**: `collector.py` でRSSから記事を収集
    2. **スコアリング (Scoring)**: `scorer.py` で記事の関連度を評価
    3. **選定 (Selection)**: スコアが高い記事を選定
    4. **生成 (Generation)**: `generate_article.py` を呼び出して記事を生成
- **引数**:
    - `--days`: 遡る日数
    - `--threshold`: 生成対象とするスコアの閾値
    - `--limit`: 生成する記事数の上限

### `generate_article.py`
- **役割**: 単一の記事を生成してWordPressに投稿するメインスクリプト
- **機能**:
    - Geminiを使用して記事本文を執筆
    - SEO向上のためのメタデータ（タイトル、説明文）生成
    - アイキャッチ画像の生成
    - WordPressへのドラフト/公開投稿
    - X (Twitter) への自動投稿
- **引数**:
    - `--keyword`: ターゲットキーワード
    - `--type`: 記事タイプ (`know`, `buy`, `do`, `news`, `global`)

### `generate_weekly_summary.py`
- **役割**: 週間サマリー記事の自動生成
- **機能**:
    - 直近1週間の記事をWordPressから全文取得
    - 業界動向を構造化・抽象化してサマリー記事を生成
    - 内部リンクを豊富に含んだ「インデックス記事」として機能
    - ローカルへのMDファイル保存およびWordPressへの投稿
- **引数**:
    - `--days`: 遡る日数（デフォルト: 7）
    - `--dry-run`: 投稿せずにローカル生成のみ行う

### `batch_generate_2025.py`
- **役割**: 2025年のSEOターゲットキーワードリストに基づいた一括生成
- **機能**: Defines markdown list (`seo_target_keywords_2025.md`) からキーワードを読み込み、順次 `generate_article.py` を実行します。

### `generate_static_pages.py`
- **役割**: 固定ページ（プライバシーポリシー、運営者情報、お問い合わせ）の自動生成
- **機能**: サイトの基本情報を基に、法的に適切な文言やフォーマットで固定ページを作成します。

### `setup_taxonomy.py`
- **役割**: WordPressのカテゴリとタグの初期設定
- **機能**: 戦略ドキュメントに基づき、カテゴリとタグ（説明文含む）を自動作成または更新します。

---

## 🔌 APIクライアント (Clients)

外部サービスとの通信を担うクラス群です。

### `gemini_client.py`
- **役割**: Google Gemini API (Vertex AI / Studio) とのインターフェース
- **機能**:
    - `generate_article`: 記事執筆プロンプトの管理と生成
    - `generate_image`: 画像生成 (Imagen 3 / Gemini Flash)
    - `classify_content`: コンテンツの分類
    - `generate_structured_summary`: 内部リンク用構造化データの生成

### `wp_client.py`
- **役割**: WordPress REST API とのインターフェース
- **機能**:
    - 記事の投稿 (`create_post`)
    - メディアのアップロード (`upload_media`)
    - カテゴリ・タグの取得と作成

### `sns_client.py`
- **役割**: X (旧Twitter) API とのインターフェース
- **機能**: 生成された記事のシェア投稿を行います。

---

## 🧩 支援モジュール (Helpers)

特定のタスク処理を担うモジュール群です。

### `collector.py`
- **役割**: 情報収集
- **機能**: 指定されたRSSフィードリストから最新の記事を収集します。

### `scorer.py`
- **役割**: 記事選定（スコアリング）
- **機能**: 収集した記事が「LogiShift」の読者にとって有益かどうかをGeminiを使って0-100点で評価します。

### `classifier.py`
- **役割**: 記事分類
- **機能**: 記事の内容に基づいて、適切なカテゴリ、業種タグ、テーマタグ、記事タイプ（解説/比較/事例/ニュース/海外）を判定します。

### `summarizer.py`
- **役割**: 要約生成
- **機能**: ニュース記事などの長文コンテンツを要約し、重要な事実（Key Facts）と編集部の独自視点（LogiShift Angle）を抽出します。

### `seo_optimizer.py`
- **役割**: SEO最適化
- **機能**:
    - 検索意図に基づいたメタディスクリプションの生成
    - JSON-LD構造化データの作成
    - OGPタグの生成

### `internal_linker.py`
- **役割**: 内部リンク提案
- **機能**: WordPress内の過去記事を検索し、新しく書く記事に関連するものを提案・評価して、本文内にリンクを挿入する指示を作成します。

### `url_reader.py`
- **役割**: Webコンテンツ抽出
- **機能**: 指定されたURLのHTMLを解析し、本文、タイトル、著者を抽出します。主要な物流メディアサイトごとのセレクタ定義を持っています。

### `inspect_summaries.py`
- **役割**: デバッグ・確認用
- **機能**: WordPressに保存された記事の「AI構造化要約」データを確認するためのスクリプトです。
