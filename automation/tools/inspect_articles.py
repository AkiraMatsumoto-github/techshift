#!/usr/bin/env python3
import sys
import os
import json
from datetime import datetime

# Add parent dir to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.client import DBClient
from dotenv import load_dotenv

# Force load .env from automation dir
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
print(f"DEBUG: Loading .env from {env_path}")
load_dotenv(env_path, override=True)

import requests

def list_articles():
    # Print what is in env AFTER loading
    print(f"DEBUG: Env Var WP_APP_PASSWORD starts with: {os.getenv('WP_APP_PASSWORD', '')[:2]}")

    db = DBClient()
    print(f"DEBUG: Target WP_URL = {db.wp_url}")
    print(f"DEBUG: Target API_URL = {db.api_url}")
    print(f"DEBUG: DBClient Auth User = {db.auth[0]}")
    mask_pass = db.auth[1][:2] + "*" * 5 + db.auth[1][-2:] if db.auth[1] else "None"
    print(f"DEBUG: Password loaded: '{mask_pass}' (Length: {len(db.auth[1])})")
    
    # 1. Test Auth against Standard Endpoint (to rule out Custom API issues)
    print("\n[Auth Check] Testing standard WP API (/wp/v2/users/me)...")
    try:
        # Manually construct request for standard API
        std_url = f"{db.wp_url}/?rest_route=/wp/v2/users/me"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        resp = requests.get(std_url, auth=db.auth, headers=headers)
        if resp.status_code == 200:
            user_data = resp.json()
            print(f"✅ Auth Success! Logged in as: {user_data.get('name')} (ID: {user_data.get('id')})")
        else:
            print(f"❌ Auth Failed! Status: {resp.status_code}")
            print(f"Response: {resp.text[:200]}")
            # If 401, and user says password is correct -> Header Stripping Issue
    except Exception as e:
        print(f"Auth check error: {e}")

    print(f"\nChecking articles from: {db.api_url}")
    
    # Get articles from last 72 hours to ensure we get 50
    print("Fetching articles (limit 50)...")
    articles = db.get_articles(hours=72, limit=50)
    
    if not articles:
        print("No articles found (or API error).")
        return

    # Write to file
    output_file = "docs/04_data/collected_articles_dump.md"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Collected Articles Data Dump (Detailed)\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Source:** Database (fs_articles) via API\n")
        f.write(f"**Count:** {len(articles)}\n\n")
        f.write("---\n")

        for i, art in enumerate(articles):
            title = art.get('title', 'No Title').strip()
            source = art.get('source', 'Unknown')
            region = art.get('region', 'Unknown')
            pub = art.get('published_at', 'Unknown')
            summary = art.get('summary', '').strip()
            is_relevant = art.get('is_relevant')
            is_relevant_str = "Yes" if is_relevant in [1, True, '1'] else "No"
            reason = art.get('relevance_reason', '') 
            
            f.write(f"\n## {i+1}. {title}\n")
            f.write(f"- **Region**: {region}\n")
            f.write(f"- **Source**: {source}\n")
            f.write(f"- **Published**: {pub}\n")
            f.write(f"- **Relevance**: {is_relevant_str}\n")
            if reason:
                f.write(f"- **Reason**: {reason}\n")
            f.write(f"- **Summary**:\n")
            f.write(f"> {summary}\n")
            f.write("\n---\n")
    
    print(f"Successfully wrote {len(articles)} articles to {output_file}")

if __name__ == "__main__":
    list_articles()
