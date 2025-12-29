# Wireframe: Common Elements (Global)

## 1. Header & Navigation (Sticky)

### Mobile
```text
+--------------------------------------------------+
| [≡]  FINSHIFT (Logo)                     [🔍]    |
+--------------------------------------------------+
| [Risk Monitor Bar (Sticky)]                      |
| BTC: +2.1% ▲ | Gold: -0.5% ▼ | Oil: +1.2% ▲      |
+--------------------------------------------------+
```
*   **Hamburger Menu [≡]**:
    *   **Markets**: India, China, USA, Japan, Indonesia
    *   **Categories**: Crypto, Global News, How-to
    *   **Pages**: About, Contact

*   **Risk Monitor**:
    *   **Components**: Bitcoin, Gold, WTI Crude Oil.
    *   **Data Source**: `automation/collectors/market_data.py` (via GitHub Actions every 20 mins).
    *   **Data Structure**: JSON saved in `wp_options`. Contains 1D, 1W, 1M change %.
    *   **Display Logic**:
        *   **Sticky Bar**: Show 1D Change % by default.
        *   **Interaction**: Click to show popup with 1W/1M trends.
    *   **Color**: Green (>0%), Red (<0%), Grey (0%).

### Desktop
```text
+----------------------------------------------------------------------------------+
| [FINSHIFT]  [Markets v]  [News v]  [Strategies]  [How-to]           [🔍] [Sub]   |
+----------------------------------------------------------------------------------+
| [Risk Monitor Ticker (Sparklines)]                                               |
| [BTC Graph] +2.1%  |  [Gold Graph] -0.5%  |  [Oil Graph] +1.2%                   |
+----------------------------------------------------------------------------------+
```

## 2. Footer

```text
+--------------------------------------------------+
| [Logo] FinShift                                  |
| "Market Shift for Swing Traders"                 |
|                                                  |
| [Links]                                          |
| About | Contact | Privacy | Disclaimer           |
|                                                  |
| [Social Icons] X (Twitter) | RSS                 |
|                                                  |
| (c) 2025 FinShift / Akira Matsumoto              |
+--------------------------------------------------+
```

## 3. UI Components

*   **Cards**: Flat design, 1px border (`#333` on Dark Mode), No dropshadow.
*   **Typography**: Inter, Roboto (English), Noto Sans JP (Japanese).
*   **Colors**:
    *   Background: Dark (`#121212`, `#1E1E1E`)
    *   Text: White (`#E0E0E0`), Muted (`#A0A0A0`)
    *   Bullish: Green (`#00C853`)
    *   Bearish: Red (`#FF1744`)
