# Weekly Summary Generation Feature Design

## Overview
This feature automatically generates a weekly "Year-in-Review" style article that summarizes the content published on LogiShift during the past week. It aims to provide value to readers who have missed individual updates by offering a structured, insight-driven analysis of the week's trends.

## Objectives
1.  **Abstract & Structure**: Go beyond simple summaries; define the "phase" or "macro-trend" the industry is currently in.
2.  **Provide Insights**: Explain "Why" these events are happening and "What" they mean for the industry structure.
3.  **Maximize Connectivity**: Act as a hub by linking to numerous internal articles (target 10+) to encourage deeper reading.
4.  **Look Ahead**: Provide concrete, actionable outlooks for the coming week.

## Architecture

### 1. Data Retrieval
- **Source**: WordPress API (via `wp_client.py`).
- **Filter**: Articles published in the last 7 days (`after` parameter).
- **Fields**: Title, URL, **Full Content** (`content['rendered']`).
    - *Note: Full text is used to ensure the AI has sufficient context for deep analysis.*

### 2. Prompt Engineering
The prompt for Gemini (`weekly_summary` type) uses a sophisticated structure:

**Role**: LogiShift Editor-in-Chief (Intellectual, Insightful, Practical).
**Input**: List of articles (Title, URL, **Full Content**).
**Structure**:
1.  **The Weekly Macro View (今週の潮流)**:
    - Abstract the week's news into a single definition (e.g., "From Experimentation to Implementation").
    - Brief commentary on the background industry shifts.
2.  **Key Movements & Insights (業界構造の変化と示唆)**:
    - Group news not just by topic, but by "Structural Change".
    - For each group:
        - **Phenomenon (What)**: The specific news events.
        - **Deep Dive (Why/So What)**: The structural implication or opportunity.
    - **Links**: Must embed natural links to related articles (aiming for 10+ total).
3.  **Strategic Outlook (来週以降の視点)**:
    - Concrete watch points for the immediate future (specific technologies, companies, or regulations).
    - Avoid vague platitudes.

### 3. Execution Flow
- **Script**: `automation/generate_weekly_summary.py`
- **Process**:
    1.  Calculate date range (Last 7 days).
    2.  Fetch all published posts from WordPress.
    3.  Clean HTML from content to reduce token usage slightly (while keeping text).
    4.  Generate Article Markdown via Gemini.
    5.  Generate Hero Image via Vertex AI.
    6.  **Save Local Copy**: Checks `automation/generated_articles/YYYY-MM-DD_weekly_summary.md` (Crucial for review).
    7.  **Post to WordPress**: Uploads image and creates draft/published post.

## Usage
- **Manual (Dry Run)**: `python automation/generate_weekly_summary.py --dry-run`
    - Generates Markdown and Image, saves locally, does **not** post to WP.
- **Production**: `python automation/generate_weekly_summary.py`
    - Posts directly to WordPress.

## Future Improvements
- **Analytics Integration**: Incorporate GA4 data to highlight "Most Read" articles.
- **Newsletter**: Automatically dispatch the generated summary as an email.
