# Wireframe: Front Page (Dashboard)

## 概要
- **ファイル名**: `front-page.php`
- **役割**: "Pocket Bloomberg" - 3秒で世界市場の現在地と、今日のリスクテイク方針を伝える。
- **デザインコンセプト**: Dark Mode, High Density, Red/Green Data Colors.

## Layout (Mobile First)

```text
+--------------------------------------------------+
| [Header (Sticky)]                                |
| [≡]  FINSHIFT  [🔍]                              |
| ------------------------------------------------ |
| [Risk Monitor Bar (Sticky)]                      |
| BTC: +2.1% ▲ | Gold: -0.5% ▼ | Oil: +1.2% ▲      |
+--------------------------------------------------+
| [Global Indices Ticker (Auto Scroll)]            |
| US500: 4,780 (+0.5%) | NK225: 38,500 (-0.2%) ... |
+--------------------------------------------------+
| [Market Sentiment Meter]                         |
|      FEAR <---[ 65 GREED ]--->                   |
|      "Bullish Scenario Dominant"                 |
+--------------------------------------------------+
| [Daily Compass (Vertical Stack)]                 |
| 各国の「今日の結論」をカード化                   |
|                                                  |
| +----------------------------------------------+ |
| | 🇮🇳 INDIA BRIEFING (Dec 29)             [>] | |
| | [BS: Bullish (80%)]  [Sentiment: Greed]      | |
| | "TATA Motors決算好感、SENSEX最高値更新"      | |
| +----------------------------------------------+ |
|                                                  |
| +----------------------------------------------+ |
| | 🇨🇳 CHINA BRIEFING (Dec 29)             [>] | |
| | [BS: Bearish (60%)]  [Sentiment: Fear]       | |
| | "不動産刺激策への失望売り、上海指数続落"     | |
| +----------------------------------------------+ |
|                                                  |
| +----------------------------------------------+ |
| | 🇺🇸 USA BRIEFING (Dec 29)               [>] | |
| | [BS: Neutral]        [Sentiment: Neutral]    | |
| | "FOMC待ちで小動き、ハイテク株は利食い優勢"   | |
| +----------------------------------------------+ |
| ... (JP, ID)                                     |
+--------------------------------------------------+
| [Featured News (Tabs)]                           |
| [ Global ] [ Crypto ] [ Stocks ]                 |
|                                                  |
| 20:30  米雇用統計、予想上回る強い数字            |
| 18:15  ビットコイン、10万ドルの壁を再トライ      |
| 15:00  ソニーG、インド事業の統合完了を発表       |
| ...                                              |
| [View All News >]                                |
+--------------------------------------------------+
| [Footer]                                         |
| [Terms] [Privacy] [Disclaimer(Important)]        |
+--------------------------------------------------+
```

## Desktop Layout (> 768px)
- **3 Column Layout**:
    - **Left**: Daily Compass (Vertical List)
    - **Center**: Main Dashboard (Charts & News)
    - **Right**: Market Data & Rankings (Top Gainers/Losers)
- **Header**: Risk Monitor expands to show sparkline charts (mini graphs).
