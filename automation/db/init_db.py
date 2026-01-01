from client import DBClient

def init_tables():
    db = DBClient()
    
    queries = [
        # 1. Articles Table
        """
        CREATE TABLE IF NOT EXISTS fs_articles (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            url_hash CHAR(64) UNIQUE NOT NULL,
            title VARCHAR(512) NOT NULL,
            source VARCHAR(100),
            region VARCHAR(20),
            published_at DATETIME,
            fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            summary TEXT,
            is_relevant BOOLEAN DEFAULT TRUE,
            relevance_reason TEXT,
            sentiment_score INT,
            INDEX idx_region (region),
            INDEX idx_published (published_at)
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        """,
        
        # 2. Market Snapshots
        """
        CREATE TABLE IF NOT EXISTS fs_market_snapshots (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            date DATE UNIQUE NOT NULL,
            data_json JSON,
            vix_close FLOAT,
            spx_close FLOAT,
            us10y_yield FLOAT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_date (date)
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        """,
        
        # 3. Economic Events
        """
        CREATE TABLE IF NOT EXISTS fs_economic_events (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            event_date DATE,
            country VARCHAR(50),
            event_name VARCHAR(255),
            impact VARCHAR(20),
            description TEXT,
            source VARCHAR(50),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_event_date (event_date),
            INDEX idx_country (country)
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        """,
        
        # 4. Daily Analysis
        """
        CREATE TABLE IF NOT EXISTS fs_daily_analysis (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            date DATE,
            region VARCHAR(20),
            sentiment_score INT,
            sentiment_label VARCHAR(50),
            market_regime VARCHAR(50),
            scenarios_json JSON,
            full_briefing_md MEDIUMTEXT,
            wp_post_id BIGINT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY uk_date_region (date, region)
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        """
    ]
    
    print("Initializing Database Tables...")
    try:
        for q in queries:
            print(f"Executing: {q.strip().splitlines()[0]}...")
            db.execute_query(q)
        print("Database initialization complete.")
    except Exception as e:
        print(f"Initialization failed: {e}")

if __name__ == "__main__":
    init_tables()
