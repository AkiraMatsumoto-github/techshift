# Refactor: Replace Direct DB Connection with REST API

To avoid complex network configurations (SSH Tunnels) and improve security/portability, we will expose the necessary database operations for "Data Collection" and "Analysis" via custom WordPress REST API endpoints. This allows the automation scripts to run anywhere (GitHub Actions, local, etc.) using standard HTTP requests.

## User Review Required
> [!NOTE]
> This change modifies `functions.php` to add new API endpoints. This is a "WordPress-native" approach.
> No new secrets are required (uses existing `WP_APP_PASSWORD`).

## Proposed Changes

### WordPress Theme (Server-Side)
#### [MODIFY] [functions.php](file:///Users/matsumotoakira/Documents/Private_development/finshift/themes/finshift/functions.php)
- **Add Table Initialization**: Ensure `fs_articles` table creation is included in `finshift_initialize_tables`.
- **Register New Endpoints**:
    - `POST /finshift/v1/articles/check`: Checks if a list of `url_hash` exists.
    - `POST /finshift/v1/articles`: Saves a new article to `fs_articles`.
    - `GET /finshift/v1/articles`: Retrieves articles (with filtering by region/time) for context generation.

### Automation (Client-Side)
#### [MODIFY] [automation/db/client.py](file:///Users/matsumotoakira/Documents/Private_development/finshift/automation/db/client.py)
- **Deprecate `mysql.connector`**: Remove direct MySQL connection logic.
- **Integrate `WPClient`**: Update `DBClient` to wrap `WordPressClient` (or simpler, have `DBClient` make HTTP requests using the same credentials).
- **Refactor Methods**:
    - `check_article_exists(hash)` -> Calls `POST .../check`
    - `save_article(article)` -> Calls `POST .../articles`
    - `get_articles(...)` -> Calls `GET .../articles`
    - `save_market_snapshot`, `save_daily_analysis`, `save_economic_event` -> Already have endpoints, just need to update client to use them instead of SQL.

#### [MODIFY] [automation/daily_briefing.py](file:///Users/matsumotoakira/Documents/Private_development/finshift/automation/daily_briefing.py)
- No major changes expected if `DBClient` interface remains compatible, but we will verify.

#### [MODIFY] [daily-briefing.yml](file:///Users/matsumotoakira/Documents/Private_development/finshift/.github/workflows/daily-briefing.yml)
- **Remove MySQL Requirement**: No need for `services: mysql` or SSH tunneling.
- Ensure `WP_URL`, `WP_USER`, `WP_APP_PASSWORD` are available (already are).

## Verification Plan

### Automated Tests
1.  **Local Verification**:
    - Update `functions.php` on local WP.
    - Run `automation/daily_briefing.py --dry-run` (or a small test script) locally to verify it can talk to the local API.
2.  **Workflow Verification**:
    - Push changes.
    - The workflow should run purely over HTTP.

### Manual Verification
- Check `/wp-json/finshift/v1/articles` output in browser (if public/auth allowed).
