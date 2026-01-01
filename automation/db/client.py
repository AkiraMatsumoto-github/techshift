import os
import json
import mysql.connector
from dotenv import load_dotenv

# Load env from parent directory
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

class DBClient:
    def __init__(self):
        # Default to localhost:3308 for local dev (mapped in docker-compose)
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", 3308))
        self.user = os.getenv("DB_USER", "wordpress")
        self.password = os.getenv("DB_PASSWORD", "password")
        self.database = os.getenv("DB_NAME", "wordpress")

    def get_connection(self):
        try:
            conn = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return conn
        except mysql.connector.Error as err:
            print(f"Error connecting to DB: {err}")
            raise

    def execute_query(self, query, params=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            return cursor
        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
            
    def fetch_all(self, query, params=None):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            return cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error fetching data: {err}")
            raise
        finally:
            cursor.close()
            conn.close()

    def fetch_one(self, query, params=None):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            return cursor.fetchone()
        except mysql.connector.Error as err:
            print(f"Error fetching data: {err}")
            raise
        finally:
            cursor.close()
            conn.close()

    # --- Specific Data Access Methods ---

    def check_article_exists(self, url_hash):
        query = "SELECT id FROM fs_articles WHERE url_hash = %s"
        result = self.fetch_one(query, (url_hash,))
        return result is not None

    def save_article(self, article):
        """
        Save an article to fs_articles.
        article: dict with title, url_hash, source, region, published_at, summary, is_relevant, relevance_reason
        """
        query = """
        INSERT INTO fs_articles 
        (url_hash, title, source, region, published_at, summary, is_relevant, relevance_reason)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            article['url_hash'],
            article['title'],
            article.get('source'),
            article.get('region'),
            article.get('published_at'), # Should be datetime object or string
            article.get('summary'),
            article.get('is_relevant', True),
            article.get('relevance_reason', "")
        )
        try:
            self.execute_query(query, params)
            print(f"Saved Article: {article['title'][:30]}...")
        except mysql.connector.Error as err:
            if err.errno == 1062: # Duplicate entry
                print(f"Duplicate article skipped: {article['title'][:20]}...")
            else:
                print(f"Error saving article: {err}")

    def save_economic_event(self, event_date, event_name, country, impact, description, source):
        """
        Save economic event.
        """
        query = """
        INSERT INTO fs_economic_events (event_date, event_name, country, impact, description, source)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (event_date, event_name, country, impact, description, source)
        self.execute_query(query, params)

    def save_market_snapshot(self, date_str, data_json, vix, spx, us10y):
        """
        Save market snapshot.
        date_str: YYYY-MM-DD
        data_json: json string
        """
        query = """
        INSERT INTO fs_market_snapshots (date, data_json, vix_close, spx_close, us10y_yield)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            data_json = VALUES(data_json),
            vix_close = VALUES(vix_close),
            spx_close = VALUES(spx_close),
            us10y_yield = VALUES(us10y_yield)
        """
        params = (date_str, data_json, vix, spx, us10y)
        self.execute_query(query, params)

    def get_articles(self, region=None, hours=24, limit=50):
        """
        Get relevant articles for context.
        If region is specified, filters by region + Global.
        """
        # Logic: 
        # - Published within last `hours`
        # - is_relevant = 1
        # - Region matches OR Region='Global' (if region provided)
        
        query = """
        SELECT title, summary, source, region, published_at 
        FROM fs_articles 
        WHERE is_relevant = 1 
        AND published_at >= DATE_SUB(NOW(), INTERVAL %s HOUR)
        """
        params = [hours]
        
        if region and region != "Global":
            query += " AND (region = %s OR region = 'Global')"
            params.append(region)
        elif region == "Global":
            # For Global briefing, maybe include everything? or specific sources?
            # Let's say Global includes everything for now, or major markets.
            pass
            
        query += " ORDER BY published_at DESC LIMIT %s"
        params.append(limit)
        
        return self.fetch_all(query, tuple(params))

    def get_latest_market_snapshot(self):
        query = "SELECT * FROM fs_market_snapshots ORDER BY date DESC LIMIT 1"
        return self.fetch_one(query)

    def get_upcoming_events(self, days=7):
        query = """
        SELECT * FROM fs_economic_events 
        WHERE event_date BETWEEN CURRENT_DATE AND DATE_ADD(CURRENT_DATE, INTERVAL %s DAY)
        ORDER BY event_date ASC
        """
        return self.fetch_all(query, (days,))

    def save_daily_analysis(self, analysis_record):
        """
        Save daily analysis result.
        """
        query = """
        INSERT INTO fs_daily_analysis 
        (date, region, sentiment_score, sentiment_label, market_regime, scenarios_json, full_briefing_md)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            sentiment_score = VALUES(sentiment_score),
            sentiment_label = VALUES(sentiment_label),
            market_regime = VALUES(market_regime),
            scenarios_json = VALUES(scenarios_json),
            full_briefing_md = VALUES(full_briefing_md)
        """
        params = (
            analysis_record['date'],
            analysis_record['region'],
            analysis_record.get('sentiment_score'),
            analysis_record.get('sentiment_label'),
            analysis_record.get('market_regime'),
            json.dumps(analysis_record.get('scenarios', {})), # Ensure JSON string
            analysis_record.get('full_briefing_md')
        )
        self.execute_query(query, params)


