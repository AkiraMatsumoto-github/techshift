# TechShift Content Automation Strategy

## 1. Objective
Build the world's first "Dynamic Navigation Chart" for technology. Use automation to collect global signals and manual curation to ensure high-quality impact analysis.

## 2. Content Types

### A. Daily Briefing (The Core)
*   **Role**: The single most important daily update.
*   **Format**: Cross-Sectional Highlight.
*   **Selection**: One "Hero Topic" selected from all reported news.
*   **Logic**:
    1.  **Collector**: Fetches 100+ articles.
    2.  **Scorer**: Filters top 5 "Must Read" candidates.
    3.  **Editor**: Selects ONE as "The Shift" and writes the briefing.

### B. Roadmap Updates (The Stock)
*   **Role**: Maintaining the "Source of Truth" for prediction dates.
*   **Trigger**: Event-driven (when a Daily Briefing implies a shift).
*   **Process**: Manual update of `fs_roadmap_nodes` (e.g., 2026 Q1 -> 2025 Q4).

## 3. Taxonomy Strategy (30 Categories)
Defined in `automation/tools/setup_taxonomy.py`.

*   **Priority 1 (Launch Phase)**:
    *   Multi-Agent Systems (AI)
    *   Post-Quantum Cryptography (Quantum)
    *   Solid-State Batteries (Energy)
*   **Priority 2 (Phase 3)**:
    *   Space (Reusable Rockets)
    *   Bio (AI Drug Discovery)
    *   ...and remaining 25 categories.

## 4. Phase 1 Workflow (Manual Curation Hybrid)
1.  **News Fetching**: `collector.py` runs every 6 hours.
2.  **Scoring**: `scorer.py` assigns 0-100 score based on "Technology Breakthrough".
3.  **Drafting**: Top 5 articles are drafted as private posts in WP.
4.  **Curation**: Human editor reviews drafts, picks the Hero, and publishes the Daily Briefing.

## 5. Phase 2 Workflow (Full Automation)
*   **Impact Analyzer**: `impact_analyzer.py` calculates roadmap delta (-1 year, etc.).
*   **Auto-Update**: Roadmap nodes are updated automatically if confidence is > 90%.
*   **Weekly Recap**: AI aggregates 7 daily briefings into a Friday Summary.
