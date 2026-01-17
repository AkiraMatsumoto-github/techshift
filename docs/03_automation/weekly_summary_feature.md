# Weekly Shift Recap (Feature Design)

> [!NOTE]
> **Status**: Phase 2 (Future)
> **Role**: Aggregation of Phase 1 "Daily Briefings".

## Overview
Automated generation of a "Weekly Shift Report" released every Friday. It aggregates the 7 "Daily Briefings" of the week to provide a high-level view of the global technology shift.

## Architecture

### 1. Data Retrieval
*   **Source**: WordPress contents.
*   **Filter**: Articles posted in the last 7 days with `category: daily-briefing` (or identified as Hero).
*   **Input**: The "Hero Text" and "Impact Score" from each day.

### 2. Logic (Gemini 2.0)
*   **Prompt**: "Analyze the 7 daily shifts of this week. Identify the single dominant vector (e.g., 'AI accelerated while Space stagnated')."
*   **Structure**:
    1.  **Macro Trend**: The one-line summary of the week.
    2.  **The Winners**: Technologies that accelerated.
    3.  **The Losers**: Technologies that hit bottlenecks.

### 3. Output
*   **Format**: Article with "Weekly Recap" tag.
*   **Distribution**: Email Newsletter & X Thread.
