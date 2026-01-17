# Shift Alert: SNS Automation Setup

> [!NOTE]
> **Status**: Phase 2 (Future)

## Overview
"Shift Alert" automatically posts to X (Twitter) whenever a significant roadmap update occurs.

## 1. X (Twitter) API Setup

### Requirements
1.  **X Developer Account**: Free tier is sufficient for "Write-only" bots (1,500 tweets/month).
2.  **App Permissions**: Must be **Read and Write**.

### Configuration
Update `.env` in `automation/` container:

```bash
X_API_KEY="your_api_key"
X_API_SECRET="your_api_secret"
X_ACCESS_TOKEN="your_access_token"
X_ACCESS_TOKEN_SECRET="your_access_token_secret"
```

## 2. Trigger Logic
*   **Event**: When `impact_analyzer.py` detects a `delta != 0` (e.g., Timeline shifted by 3 months).
*   **Content**:
    > "🚨 **SHIFT ALERT**
    > [Solid-State Battery] Mass Production Roadmap ACCELERATED by 1 Year.
    > Reason: Toyota's new breakthrough on sulfide electrolytes.
    > #TechShift #Battery #Future"

## 3. Threads API (Optional)
Defer to Phase 3 due to lower priority and higher API complexity.
