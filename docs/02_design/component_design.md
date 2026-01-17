# TechShift 共通パーツ設計 (Component Design)

## 1. ロードマップ・ノード (Roadmap Nodes)
TechShiftの最も重要な構成要素。タイムライン上に配置されるマイルストーン。

### Node Card
*   **状態**:
    *   **Achieved (到達済)**: Solid Background (`Slate 800`), Opacity 100%. Check icon.
    *   **Active (現在)**: Border Glow (`TechShift Blue`), Pulsing Animation.
    *   **Future (未来)**: Dashed Border, Opacity 70%.
*   **配置**: タイムライン軸の左右（PC）または右側（SP）に配置。

### Vertical Line & Connector
*   **Line**: width 2px, Solid (`Slate 700`). 上下を貫く。
*   **Dot**: width 12px, height 12px. ノード発生地点に配置。
    *   Impact発生時は、Dotの色が変化（Green/Red）し、波紋エフェクト（Ripple）が出る。

## 2. インパクト・バッジ (Impact Badge)
ニュース記事やノード更新時に表示される、影響度のスコア。

### Design
*   **Shape**: Pill型 (角丸完全)。
*   **Content**: アイコン (Arrow Up/Down/Right) + スコア数値 (+3, -1, 0)。
*   **Variants**:
    *   **Major Acceleration (+3 ~ +5)**: Bg `Emerald 500 alpha 20%`, Text `Emerald 400`, Border `Emerald 500`.
    *   **Minor Acceleration (+1 ~ +2)**: Text `Emerald 400`.
    *   **Neural (0)**: Text `Slate 400`.
    *   **Major Delay (-3 ~ -5)**: Bg `Rose 500 alpha 20%`, Text `Rose 400`.

## 3. ロジック・チェーン (Logic Chain Visualization)
記事詳細ページで「なぜその結論に至ったか」を図示するフローチャート。

### Flow Structure
横並び（PC）または縦積み（SP）のブロック図。

`[ Event ]` --(mechanism)--> `[ Outcome ]`

*   **Event Block**: 背景 `Slate 800`. アイコン「⚡️」。
*   **Arrow**: 矢印。Impactの色を反映。
*   **Outcome Block**: 背景 `Slate 800` + Impact Color Border. アイコン「🏁」。

## 4. カード (Article Integration)

### Impact Alert Card
通常の記事カードとは異なり、Impactを強調する。
*   **Header**: Impact Badgeを右上に配置。
*   **Title**: 記事タイトル。
*   **Footer**: 関連するRoadmap Node名へのリンク。

## 5. ナビゲーション
*   ヘッダーは最小限にし、コンテンツへの没入を妨げない。
*   **Topic Switcher**: 画面下部またはサイドに「AI」「Space」「Bio」などのトピック切り替えドックを配置（OSのドックのようなUI）。
