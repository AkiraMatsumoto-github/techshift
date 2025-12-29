# AI Scenario Generation Logic for FinShift

スイングトレーダー（数日〜数週間の保有）に最適な「アクションにつながる」シナリオ生成ロジックを定義します。

## 1. 基本方針: "Dynamic Dual-Track" (Main vs Risk)

固定的な「強気・中立・弱気」の3パターン出力は行いません。
代わりに、**「市場の優勢な方向性（Main）」** と **「それが崩れる条件（Risk）」** の2軸で構成します。
これにより、トレーダーにとって不可欠な「エントリー根拠」と「損切りライン（撤退基準）」を明確に提示します。

### 構造
1.  **Market Sentiment Check (判定)**: ニュースが強気(Bullish)か、弱気(Bearish)か、不透明(Neutral/Mixed)かをまず判定。
2.  **Scenario Construction (構成)**:
    - **Case A: 明確なトレンドがある場合 (Bullish/Bearish)**
        - **Main Scenario (順張り)**: トレンドに従うシナリオ。目標価格やアップサイドの余地。（発生確率: 高）
        - **Risk Scenario (逆張り)**: 前提が崩れるリスク要因。ここを割ったら撤退というライン。（発生確率: 低）
    - **Case B: 不透明な場合 (Mixed)**
        - **Scenario 1 (Breakout)**: 上値抵抗線を抜けたら強気入り。（条件付き強気）
        - **Scenario 2 (Breakdown)**: 下値支持線を割ったら弱気入り。（条件付き弱気）

---

## 2. プロンプト設計 (System Prompt Design)

Geminiに与える役割と出力フォーマット定義。

**Role**:
You are a professional market strategist for swing traders.
Analyze the provided news/market data and generate a trading scenario.

**Output Structure (JSON)**:

```json
{
  "market_snetiment": "Bullish" | "Bearish" | "Mixed",
  "confidence_score": 0.85, // AIの自信度
  "main_scenario": {
    "direction": "Bullish",
    "probability": "70%",
    "headline": "好決算を背景に一段高へ、次は$150を目指す展開",
    "rationale": "EPSが予想を上回り、ガイダンスも強気であるため...",
    "key_levels": "Support: $140, Resistance: $155"
  },
  "risk_scenario": {
    "direction": "Bearish", 
    "probability": "30%",
    "headline": "地合い悪化による利食い売り先行なら$135まで調整も",
    "rationale": "全体相場（S&P500）が調整局面にあるため、連れ安するリスク...",
    "invalidation_level": "$138 (このラインを割ったら撤退)"
  },
  "action_plan": {
    "recommendation": "Buy on Dip",
    "timeframe": "1-2 weeks"
  }
}
```

---

## 3. なぜこの方式か (Rationale)

| 方式 | 特徴 | FinShiftへの適用 |
| :--- | :--- | :--- |
| **3パターン (Bull/Neutral/Bear)** | 網羅的だが「中立」によりがち。 | **△** どっちつかずの記事はトレーダーに嫌われる。 |
| **2パターン固定 (Bull vs Bear)** | 常に両論併記。 | **△** 明らかな好材料の時に「無理やり作った弱気シナリオ」はノイズになる。 |
| **Dynamic (Main + Risk)** | **「基本路線」と「リスク」**。 | **◎ 推奨** プロのトレーダーの思考プロセスに最も近い。 |

## 4. UI/UX イメージ

記事ページでは以下のように表示します。

- **ヘッダー**: 「AI強気シグナル点灯 (確度70%)」のようなバッジ。
- **シナリオセクション**:
    - **Main**: 背景色（緑/赤）で目立たせる。「これがメインシナリオです」
    - **Risk**: 警告色（黄色/グレー）で補足。「ただし、このリスクに注意」
