# ワイヤーフレーム: 記事詳細ページ

## 概要
- **ファイル名**: `single.php`
- **役割**: 記事コンテンツを読みやすく提供し、読者の課題解決とコンバージョン（回遊、CTA）につなげる。
- **デザイン方針**: Mobile-First, Flat Design (No Shadows/Gradients).

## レイアウト (Desktop / Mobile)

### Desktop (> 768px)
```text
+-----------------------------------------------------------------------+
| [Header]                                                              |
+-----------------------------------------------------------------------+
| [Breadcrumb] Home > カテゴリ > 記事タイトル                           |
+-----------------------------------------------------------------------+
| [Main Content] (Left/Center)        | [Sidebar] (Right)               |
|                                     |                                 |
|  [Article Header]                   | [Search Widget] (Flat Input)    |
|  [Category Label] (Flat Badge)      |                                 |
|  <h1>記事タイトル:                  | [Table of Contents] (Sticky)    |
|      物流コスト削減の5つの手順</h1> | (Border-left style)             |
|  Date: ...  Update: ...             |                                 |
|                                     | [Popular Posts]                 |
|  [Eye Catch Image] (No Shadow)      |                                 |
|                                     | [CTA Banner]                    |
|  [Lead Text]                        |                                 |
|                                     |                                 |
|  [Table of Contents] (In-article)   |                                 |
|  (Background: #F8F9FA, Flat)        |                                 |
|                                     |                                 |
|  <h2>1. 見出し</h2>                 |                                 |
|  本文テキスト...                    |                                 |
|                                     |                                 |
|  [CTA Box] (Border only)            |                                 |
|                                     |                                 |
|  [Share Buttons] (Flat, No gap)     |                                 |
|                                     |                                 |
|  [Related Posts] (Grid Layout)      |                                 |
+-----------------------------------------------------------------------+
| [Footer]                                                              |
+-----------------------------------------------------------------------+
```

### Mobile (< 768px)
- **特徴**: サイドバーなし、メインコンテンツ100%幅。
```text
+---------------------------------------+
| [Header] Logo      [Hamburger Menu =] |
+---------------------------------------+
| [Breadcrumb] (Scrollable or Short)    |
+---------------------------------------+
| [Main Content] (Full Width)           |
|                                       |
|  [Category Label]                     |
|  <h1>記事タイトル (24px)</h1>         |
|  Date: ...                            |
|                                       |
|  [Eye Catch Image]                    |
|                                       |
|  [Lead Text]                          |
|                                       |
|  [Table of Contents] (Accordion?)     |
|                                       |
|  <h2>1. 見出し</h2>                   |
|  本文テキスト...                      |
|                                       |
|  [CTA Box] (Stack Layout)             |
|                                       |
|  [Share Buttons] (Fixed Bottom?)      |
|  or (Inline Bottom)                   |
|                                       |
|  [Author Box]                         |
|                                       |
|  [Related Posts] (Stack Layout)       |
|  +--------------------------------+   |
|  | [Thumb] Title...               |   |
|  +--------------------------------+   |
|  +--------------------------------+   |
|  | [Thumb] Title...               |   |
|  +--------------------------------+   |
|                                       |
+---------------------------------------+
| [Footer]                              |
+---------------------------------------+
```
