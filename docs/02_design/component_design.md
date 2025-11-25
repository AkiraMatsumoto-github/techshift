# LogiShift 共通パーツ設計 (Component Design)

## 1. ボタン (Buttons)

### Primary Button (CTA)
- **用途**: 「記事を読む」「お問い合わせ」など、主要なアクション。
- **スタイル**:
    - 背景: `Tech Blue (#00B4D8)`
    - 文字: `White (#FFFFFF)`
    - 角丸: `4px`
    - ホバー: 明度を少し下げる or オパシティを下げる。
- **サイズ**:
    - パディング: `12px 32px`

### Secondary Button (Outline)
- **用途**: 「もっと見る」「キャンセル」など、副次的なアクション。
- **スタイル**:
    - 背景: 透明
    - ボーダー: `2px solid Tech Blue`
    - 文字: `Tech Blue`
    - ホバー: 背景を `Tech Blue` に、文字を `White` に反転。

### Text Link
- **用途**: 文中のリンク、控えめな誘導。
- **スタイル**:
    - 文字: `Tech Blue`
    - 下線: ホバー時に表示。

## 2. カード (Cards)

### 記事カード (Article Card)
- **構成**:
    - サムネイル画像 (アスペクト比 16:9)
    - カテゴリラベル (画像左上 or タイトル上)
    - タイトル (H3相当)
    - メタ情報 (日付)
- **スタイル**:
    - 背景: `White`
    - 影 (Shadow): `0 4px 6px rgba(0,0,0,0.05)` (通常時) -> `0 8px 12px rgba(0,0,0,0.1)` (ホバー時)
    - トランジション: ホバー時に少し浮き上がる (`transform: translateY(-4px)`)。

## 3. ラベル・バッジ (Labels & Badges)

### カテゴリラベル
- **用途**: 記事のカテゴリを表示。
- **スタイル**:
    - 背景: `Navy Blue` (基本) または カテゴリごとの色分け（要検討）。
    - 文字: `White`
    - フォントサイズ: `0.75rem`
    - 角丸: `2px`
    - パディング: `4px 8px`

## 4. フォーム要素 (Forms)

- **Input / Textarea**:
    - 背景: `White`
    - ボーダー: `1px solid Border Gray`
    - 角丸: `4px`
    - パディング: `12px`
    - フォーカス時: `Tech Blue` のボーダーと淡いグロー効果。

## 5. ナビゲーション (Navigation)

### ヘッダーナビ
- **PC**: テキストリンクの横並び。ホバーで下線アニメーション。
- **SP**: ハンバーガーメニュー。展開時にドロワーメニューを表示。

### パンくずリスト (Breadcrumbs)
- **用途**: 現在位置の明示。
- **スタイル**:
    - 文字: `Medium Gray`
    - 区切り文字: `>` (Chevron Right icon)
    - 現在地: `Dark Gray` (太字なし)

## 6. アイコン (Icons)
- **ライブラリ**: `Phosphor Icons` または `Heroicons` (SVG) を使用。
- **スタイル**: ライン（アウトライン）スタイルで統一し、洗練された印象にする。
