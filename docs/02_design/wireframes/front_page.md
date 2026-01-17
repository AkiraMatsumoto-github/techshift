# Front Page Wireframe (Global Dashboard)

**Device**: Mobile (iPhone 15 Pro size assumed)
**Role**: Global Command Center

```text
+-----------------------------+
| [=] TechShift      [Search] |  <-- Header: Logo + Menu/Search
+-----------------------------+
|                             |
|   TODAY'S SHIFT (Highlite)  |  <-- Hero: "What changed today?"
| +-------------------------+ |
| | ⚡️ AGI Roadmap           | |  <-- 1. Subject
| | **ACCELERATED BY 1 YR** | |  <-- 2. The Impact (Big Font)
| |                         | |
| | "New reasoning model    | |  <-- 3. The Reason
| |  breaks bottlenecks."   | |
| +-------------------------+ |
|                             |
|  [Latest Ticker Info...]    |
+-----------------------------+
+-----------------------------+
+-----------------------------+
|   SECTOR OVERVIEW (Cards)   |
|                             |
| [ 1. Space & Aero ]         |
| +-------------------------+ |
| | 🚀 Next: Mars Sample Rx | |  <-- 1. Next Milestone
| | 📅 2028 Q3  [==80%==] | |  <-- 2. Date & Confidence
| +-------------------------+ |
| � Latest: NASA awards...   |  <-- 3. Latest Article
|                             |
| [ 2. Advanced AI ]          |
| +-------------------------+ |
| | 🧠 Next: AGI Protocol   | |
| | 📅 2027 Q1  [==40%==] | |
| +-------------------------+ |
| 📰 Latest: Anthropic...     |
|                             |
| [ 3. Quantum Tech ]         |
| ...                         |
|                             |
| > Load All Sectors          |
+-----------------------------+
|                             |
|   GLOBAL IMPACT FEED        |
|  .  🚨 AGI: +1yr (Major)    |
|  .  ⚡️ Battery: -6mo       |
+-----------------------------+
|                             |
+-----------------------------+
| [Topics] [Alerts] [Menu]    |  <-- Sticky Bottom Nav (Optional)
+-----------------------------+
```

## Requirements
1.  **Today's Shift**: ユーザーが一番知りたいのは「今日、未来が近づいたのか？」という点。最もインパクトの大きかった変更（または「変化なし」という事実）をトップで宣言する。
2.  **Sector Cards**: 複雑なヒートマップではなく、セクターごとにカード化して整理する。
3.  **Speed**: 重い画像を避け、テキストとCSSシェイプ主体で構成する。
4.  **Scalability**: 30トピックあってもカード形式なら縦スクロールで自然に閲覧可能。
