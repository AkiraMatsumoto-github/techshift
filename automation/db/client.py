import os
import json
import requests
from datetime import datetime, date
from dotenv import load_dotenv

# Load env from parent directory
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

class DBClient:
    def __init__(self):
        self.wp_url = os.getenv("WP_URL")
        self.wp_user = os.getenv("WP_USER")
        self.wp_password = os.getenv("WP_APP_PASSWORD")
        
        # Fallback for WP_URL if ending in slash
        if self.wp_url and self.wp_url.endswith('/'):
            self.wp_url = self.wp_url[:-1]

        self.auth = (self.wp_user, self.wp_password)
        self.api_url = f"{self.wp_url}/?rest_route=/finshift/v1"

    def _post(self, endpoint, data):
        try:
            # Json serialize helper for dates
            def json_serial(obj):
                if isinstance(obj, (datetime, date)):
                    return obj.isoformat()
                raise TypeError ("Type %s not serializable" % type(obj))

            resp = requests.post(
                f"{self.api_url}/{endpoint}", 
                data=json.dumps(data, default=json_serial), 
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                },
                auth=self.auth
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"API Error (POST {endpoint}): {e}")
            if isinstance(e, requests.exceptions.HTTPError):
                 # Log only first 200 chars to avoid dumping full HTML
                 error_preview = e.response.text[:200] + ("..." if len(e.response.text) > 200 else "")
                 print(f"Response: {error_preview}")
            return None

    def _get(self, endpoint, params=None):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            resp = requests.get(f"{self.api_url}/{endpoint}", params=params, headers=headers, auth=self.auth)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"API Error (GET {endpoint}): {e}")
            return None

    # --- Reimplemented Methods ---

    def check_article_exists(self, url_hash):
        res = self._post("articles/check", {"hashes": [url_hash]})
        if res and "exists" in res:
             return url_hash in res["exists"]
        return False

    def save_article(self, article):
        """
        Save an article via API.
        """
        # Ensure dict keys match API expectation
        # API expects: url_hash, title, source, region, published_at, summary, is_relevant, relevance_reason
        # article dict usually has these.
        res = self._post("articles", article)
        if res and res.get('success'):
            print(f"Saved Article: {article.get('title', '')[:30]}...")
        else:
            print(f"Failed to save article: {article.get('title', '')[:30]}...")

    def save_economic_event(self, event_date, event_name, country, impact, description, source):
        data = {
            "event_date": event_date,
            "event_name": event_name,
            "country": country,
            "impact": impact,
            "description": description,
            "source": source
        }
        self._post("economic-events", data)

    def save_market_snapshot(self, date_str, data_json, vix, spx, us10y):
        # API expects { date, data: {...} } where data is the json object
        # but data_json arg here is string.
        try:
            data_obj = json.loads(data_json)
        except:
            data_obj = {}
            
        payload = {
            "date": date_str,
            "data": data_obj 
            # Note: API callback extracts sp500/us10y from 'data' automatically
        }
        self._post("market-snapshots", payload)

    def get_articles(self, region=None, hours=24, limit=50):
        params = {
            "hours": hours,
            "limit": limit
        }
        if region:
            params["region"] = region
            
        res = self._get("articles", params)
        return res if res else []

    def get_latest_market_snapshot(self):
        # Get list limit 1
        res = self._get("market-snapshots", {"limit": 1})
        if res and len(res) > 0:
            # The API returns list of objects.
            # Client code expects a specific dict structure?
            # Existing code: snapshot['data_json'] (as dict), snapshot['date']...
            # The API returns `data_json` as OBJECT already (decoded in PHP callback)
            # wait, `finshift_api_get_market_snapshots`:
            # foreach ($results as $row) { $row->data_json = json_decode( $row->data_json ); }
            # So JSON response has `data_json` as an object/dict.
            
            # Legacy code expected what?
            # daily_briefing.py: 
            # market_data_str = json.dumps(market_snap['data_json']) if market_snap and 'data_json' in market_snap else "No Data"
            
            # Since requests .json() decodes the whole response, `res[0]['data_json']` will be a dict.
            # So `json.dumps(res[0]['data_json'])` will work.
            return res[0]
        return None

    def get_upcoming_events(self, days=7):
        # API supports start_date (default today) and days
        res = self._get("economic-events", {"days": days})
        return res if res else []

    def save_daily_analysis(self, analysis_record):
        # API expects: date, region, sentiment_score, ...
        # analysis_record matches.
        self._post("daily-analysis", analysis_record)

    def update_schema(self):
        """Trigger remote DB schema update/initialization."""
        self._get("update-schema")

