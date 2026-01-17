# TechShift デザインガイドライン

## 1. デザインコンセプト
**「Intelligent Reality (知性ある現実)」**

TechShiftは、単なるニュースメディアでも、無機質なデータベースでもありません。
「未来の地図（Roadmap）」を動的に描き直す、**未来のナビゲーション・コンソール**です。
ユーザーが「今、歴史のどの地点にいるのか」を直感的に把握できる、没入感と知性を兼ね備えたUIを目指します。

*   **Keywords**: Immersive, Temporal (時間軸), Structured.

## 2. カラーパレット

### Brand Identity
*   **Deep Space (`#020617` - Slate 950)**:
    *   背景のベースカラー。無限の宇宙や未知の領域を表現。
*   **TechShift Blue (`#38BDF8` - Sky 400)**:
    *   アクセントカラー。知性とテクノロジーの象徴。
*   **Timeline Gray (`#334155` - Slate 700)**:
    *   ロードマップの軸線やコネクターに使用。

### Impact Colors (Timeline Dynamics)
ニュースがロードマップに与える「力」を色で表現します。
*   **Accelerate (加速)**: `#10B981` (Emerald 500) - Vivid Green.
*   **Delay (遅延)**: `#F43F5E` (Rose 500) - Vivid Red.
*   **Neutral (不変)**: `#94A3B8` (Slate 400).

### Text Colors
*   **Primary**: `#F8FAFC` (Slate 50) - 純白に近い白。
*   **Secondary**: `#CBD5E1` (Slate 300) - 読みやすいグレー。
*   **Muted**: `#64748B` (Slate 500) - タイムスタンプなどのメタ情報。

## 3. タイポグラフィ

### Font Family
*   **English (Headings / Numbers)**: `Outfit` (Google Fonts)
    *   モダンでジオメトリックなサンセリフ。未来的な印象を与える。
*   **Japanese (Body)**: `Noto Sans JP`
    *   可読性重視。

### Hierarchy
*   **Display (Roadmap Nodes)**: 1.25rem ~ 2rem (Bold). タイムライン上のマイルストーン。
*   **H1 (Article Title)**: 2.5rem (Bold).
*   **Body**: 1rem (16px). 行間は広め (1.8) に取り、知的な余白を持たせる。
*   **Data (Impact Score)**: 等幅フォント (`JetBrains Mono` or `Roboto Mono`) を使用し、計測機器のような精密さを演出。

## 4. スペーシング & 構造

### Vertical Rhythm
TechShiftのUIは「時間軸（縦方向の流れ）」が支配します。
*   **Timeline Axis**: 画面中央（モバイルでは左端）に一本の「軸」を通し、全てのコンテンツがその軸に紐づくレイアウトを採用。
*   **Connectors**: カードと軸を繋ぐラインを明示的に描画する。

### Glassmorphism (Minimal)
*   カードやパネルには、ごく薄い背景色 (`rgba(30, 41, 59, 0.7)`) と `backdrop-filter: blur(10px)` を適用。
*   背景の「Deep Space」が透けて見えることで、奥行きと先進性を表現。
