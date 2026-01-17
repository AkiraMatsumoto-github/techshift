# TechShift 開発実装計画 (Phase 1)

**メディアコンセプトシート (Version 2.0)** に基づく、初期立ち上げフェーズの詳細実装計画です。
「動的ロードマップ」を実現するための「WordPressテーマ改修」と「オートメーションロジック刷新」に焦点を当てます。

## 1. 開発環境・構成

*   **Repository Name**: `techshift` (New)
*   **Base Architecture**:
    *   **CMS**: WordPress (Port: 8003)
    
## 2. 実装スコープ (Phase 1 Priorities)

### 2.1. WordPress Theme (`/themes/techshift`)
標準的なブログテーマではなく、ロードマップ表示に特化したUIを構築します。

*   **A. 固定ページテンプレート (`page-roadmap.php`)**
    *   **役割**: 各トピック（例: `/roadmap/solid-state-battery`）の親ページ。
    *   **実装要素 (V4 Content-First)**:
        *   **Official Roadmap**: 公式予定表（Baseline）の静的表示。
        *   **Signal Timeline**: 関連ニュースの時系列リスト。
        *   **Forecast**: 編集部による独自見解（テキストメイン）。

*   **B. 記事詳細テンプレート (`single.php`)**
    *   **役割**: 個別のニュース記事表示。
    *   **実装要素**:
        *   **Impact Context**: 記事冒頭に「このニュースがロードマップに与えた影響（Daily Briefing転用）」を表示。
        *   **Related Roadmap**: 親トピックへのバックリンク。

### 2.2. Automation Logic (`/automation`)

*   **A. Collector & Scorer (`collector.py` / `scorer.py`) [Phase 1]**
    *   **Input**: RSS feeds.
    *   **Process**: 記事収集および重要度スコアリング（下書き生成の前処理）。
    *   **Output**: WordPress下書き記事。

*   **B. Impact Analyzer (`impact_analyzer.py`) [Phase 2]**
    *   **Input**: ニュース記事テキスト。
    *   **Output**: 自動ロードマップ更新（JSON）。

*   **C. Setup Taxonomy (`setup_taxonomy.py`) [Phase 1]**
    *   概念シートの「重点3トピック」+「全30カテゴリ」をWordPressに自動登録・設定するスクリプト。

## 3. タスク詳細 (Action Items)

## 3. タスク詳細 (Action Items)

### Step 1: Baseline Setup (Infrastructure)
*   [ ] **Docker Environment**
    *   [ ] `docker-compose.yml`: WordPress, MySQL, Python (Automation) のコンテナ定義。
    *   [ ] `automation/Dockerfile`: Python環境（lib: `feedparser`, `google-generativeai`, `requests`）。
    *   [ ] `.env`: DBパスワード, Gemini API Key 管理。
    *   [ ] Volume Mounts: `themes/techshift` をホストと同期設定。
*   **WordPress Initialization**
    *   [ ] Install WordPress & Login.
    *   [ ] `fs_` テーブル群 (`fs_roadmap_nodes`, `fs_impact_assessments`) の作成SQL実行。
    *   [ ] Permalinks 設定 (Post name)。
*   **Theme Skeleton**
    *   [ ] `style.css`: Theme Header定義。
    *   [ ] `functions.php`: 基本設定, CSS/JS読み込み, カスタム投稿タイプ定義。
    *   [ ] Tailwind CSS (CDN版) の導入（開発スピード優先）。

### Step 2: Automation Implementation (Phase 1 MVP)
*   **Taxonomy Setup**
    *   [ ] `automation/tools/setup_taxonomy.py`:
        *   [ ] WP REST API 認証処理 (`wp_client.py`)。
        *   [ ] 重点3トピック + 全30カテゴリの登録ロジック。
*   **Collector (News Fetcher)**
    *   [ ] `automation/collectors/collector.py`:
        *   [ ] Target RSS List 定義 (Top 3 Priorities)。
        *   [ ] `feedparser` による記事取得 & 重複チェック (`url_hash`)。
        *   [ ] WPへの「下書き(Draft)」投稿機能。
*   **Scorer (Drafting Support)**
    *   [ ] `automation/analysis/scorer.py`:
        *   [ ] Gemini Prompt作成（"Extract Fact & Impact for TechShift"）。
        *   [ ] JSON Output Parser (Title, Summary, Impact Context)。

### Step 3: Frontend Implementation (V4 Content-First)
*   **Front Page (`front-page.php`)**
    *   [ ] **Daily Shift Hero**: 最新の "Daily Briefing" 記事からカスタムフィールド (`_hero_impact_text`) を取得して表示。
    *   [ ] **Sector Cards**: 各カテゴリの最新記事とマイルストーンを表示するカードループ。
*   **Roadmap Page (`page-roadmap.php`)**
    *   [ ] **Data Query**: `$wpdb` を使用し `fs_roadmap_nodes` から該当トピックのノードを取得。
    *   [ ] **View Components**:
        *   [1] Official Baseline (List View)
        *   [2] Signal Timeline (List View linked to `fs_impact_assessments`)
        *   [3] Forecast Text (Static HTML or Block)
*   **Article Page (`single.php`)**
    *   [ ] **Impact Header**: 記事本文の前に `_techshift_impact_context` を表示するBoxコンポーネント。
    *   [ ] **Back Link**: 親ロードマップへの導線設置。

## 4. 検証基準 (Definition of Done)

1.  **データ整合性**:
    *   ニュース記事更新時に、親ロードマップページの「最終更新日」や「予測データ」が正しく書き換わること（Event-Driven Update）。
2.  **UI/UX**:
    *   スマホでロードマップを見た際、スクロールで未来へスムーズに移動できること。
    *   文字ばかりでなく、視覚的に「進捗」がわかること。
