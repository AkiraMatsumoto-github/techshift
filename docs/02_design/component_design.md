# LogiShift 共通パーツ設計 (Component Design)

## 1. ボタン (Buttons)

### Primary Button (CTA)
- **用途**: 「記事を読む」「お問い合わせ」など、主要なアクション。
- **スタイル**:
    - 背景: `Tech Blue (#00B4D8)` (Solid)
    - 文字: `White (#FFFFFF)`
    - 角丸: `4px`
    - ボーダー: なし (Shadowなし)
    - ホバー: 背景色を少し濃くする (`#0096B4`)。

- **サイズ**:
    - パディング: `12px 32px`

### Secondary Button (Outline)
- **用途**: 「もっと見る」「キャンセル」など、副次的なアクション。
- **スタイル**:
    - 背景: 透明
    - ボーダー: `1px solid Tech Blue`
    - 角丸: `4px`
    - 文字: `Tech Blue`
    - ホバー: 背景を `Tech Blue` (opacity 10%) に、文字はそのまま。 or 背景 `Tech Blue` + 文字 `White`。

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
    - ボーダー: `1px solid Border Gray`
    - 影 (Shadow): なし (`none`)
    - 角丸: `8px`
    - トランジション: ホバー時にボーダー色を `Tech Blue` に変化、または背景色をわずかに `Light Gray` へ。浮き上がり(Lift)は廃止。

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
    - 影 (Shadow): なし (`none`)
    - 角丸: `4px`
    - パディング: `12px`
    - フォーカス時: `Tech Blue` の太めのボーダー (`2px`)。Glow効果は廃止。

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
