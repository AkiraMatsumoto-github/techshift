# TechShift テーマ実装仕様書

## 概要
TechShiftの独自テーマは、ブログというよりも「インタラクティブなロードマップ・アプリケーション」として実装します。
`front-page.php` は最新の動的ロードマップを表示し、`single.php` はその変化の根拠（Impact Analysis）を提示します。

## 1. ページ構造

### A. トップページ (`front-page.php`) - Global Dashboard
サイト全体の「司令室」。全トピックの最新状況と、グローバルな技術トレンドを俯瞰するハブ。

1.  **Global Heatmap / Topic Picker**
    *   30の技術トピックをグリッドまたはリストで表示。
    *   各トピックの現在のフェーズと、直近のImpact（加速/遅延）をヒートマップ的に可視化。
    *   **Action**: クリックすると各トピックの「ロードマップ詳細ページ」へ遷移。
2.  **Latest Impact Stream**
    *   トピックを横断して、直近で発生した「Impact（予測変更）」のタイムラインを表示。
    *   "Global Alert: AGl Roadmap accelerated by 2 years due to Model X release." みたいなニュース速報。

### B. トピック別ロードマップ (`page-roadmap.php`)
個別技術（例: Generative AI, Commercial Space）の詳細な未来地図を表示するページ。
*URL構造: `techshift.net/roadmap/{slug}/`*

1.  **Roadmap Header**
    *   トピック名 (H1)
    *   **Current Phase**: 現在のフェーズ（例: "Phase 2: Multimodal Reasoning"）。
    *   **Next Milestone**: 次に来る大きなノードと、その予測時期 (カウントダウン)。
2.  **Vertical Timeline (Main)**
    *   過去・現在・未来のノードを縦軸に沿ってレンダリング。
    *   **Impact Indicators**: 最近のニュースで予測が変わったノードには、色付きのインジケータ（緑/赤）を表示。
3.  **Related Alerts (Sidebar)**
    *   このトピックに関連するImpact Analysis記事へのリンク。

### C. 記事詳細 (`single.php` - Impact Analysis)
ロードマップ更新の「証拠」となる分析レポート。

1.  **Impact Header**
    *   普通のアイキャッチではなく、**「Impact Dashboard」**を表示。
    *   **Affected Node**: どのノードに関する話か。
    *   **Score**: 大きく表示 (-5 ~ +5)。
    *   **Shift**: 予測時期の変化（例: 2028 Q1 → 2027 Q3）。
2.  **Logic Chain Section**
    *   本文の前に、AIが生成した論理フロー図（Event -> Mechanism -> Outcome）を挿入。
    *   忙しい読者はここだけ見て理解できる。
3.  **Analysis Body**
    *   Markdown本文。
    *   用語解説や背景知識へのリンクを豊富に含む（Topic Cluster構造）。

## 2. データ連携 (Data Binding)

Automation (Python) から WordPress へのデータマッピング定義。

| データ項目 | ソース (Python) | WordPress 保存先 | 表示コンポーネント |
|---|---|---|---|
| **Impact Score** | `impact_analyzer` | Meta: `_techshift_impact_score` | Header Badge, Timeline Dot |
| **Logic Chain** | `impact_analyzer` | Meta: `_techshift_logic_chain` (JSON) | Logic Chain Block (React component) |
| **Target Node** | `impact_analyzer` | Meta: `_techshift_target_node_id` | Article Header, Sidebar Link |
| **Prediction Drift** | `impact_analyzer` | Meta: `_techshift_date_drift` (Days) | Header "Shift" Indicator |
| **Node Phase** | `db_sync` | Custom Field (Page) | Roadmap Header |

## 3. 推奨実装順序

1.  **Custom Fields & Post Types**:
    *   固定ページ (`page`) にロードマップ用のカスタムフィールド定義。
    *   投稿 (`post`) にImpact Analysis用のメタボックス追加。
2.  **Static Logic Chain**:
    *   まずはJSONデータを単純なHTMLリストとして表示するショートコードを作成。
    *   後にReact/SVGでのリッチな図解へアップデート。
3.  **Timeline View**:
    *   CSS Grid/Flexboxを使った、レスポンシブな縦型タイムラインの実装。
    *   最初は静的なHTMLでモックアップを作成し、WPループに組み込む。

## 4. テクニカル要件
*   **CSS Framework**: Tailwind CSS (Utility-first) を推奨。
    *   カスタムカラー (`slate-950`, `emerald-500` etc) を `tailwind.config.js` に定義。
*   **Icons**: Heroicons (Outline) or Phosphor Icons.
*   **Animations**: CSS Transitions for hover states. Keyframes for "Pulse" effects on active nodes.
