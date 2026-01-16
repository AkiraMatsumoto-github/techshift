#!/usr/bin/env python3
"""
ForexFactory Calendar Collector
Fetches economic events from ForexFactory.com and saves them to the DB.
Extracts data from embedded JSON-like structures in the HTML.
"""

from curl_cffi import requests
import re
import json
import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path to import modules
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(base_dir)

from automation.db.client import DBClient

IMPORTANT_KEYWORDS = [
    "Fed", "FOMC", "Interest Rate", "Policy Rate",
    "GDP", "CPI", "PCE", "Inflation", "PPI",
    "NFP", "Non-Farm", "Unemployment", "Jobless",
    "ISM", "PMI", "Retail Sales", "Confidence",
    "BOJ", "ECB", "PBOC", "RBA", "RBNZ", "BOC", "BOE"
]

TARGET_CURRENCIES = ["USD", "EUR", "JPY", "GBP", "CHF", "CAD", "AUD", "NZD", "CNY", "INR"]

def fetch_and_save_calendar(days=14):
    """
    Fetch calendar data for today + days ahead.
    Note: ForexFactory 'calendar?day=xxx' fetches a single day unless valid range logic is used.
    Since we need a range, we might need to fetch multiple days or use a range view if possible.
    However, the standard efficient way is to fetch the 'month' view if we need many days, 
    or just iterate day by day if we need strict range.
    Given 'days=14', month view is safer if it works.
    Current URL: https://www.forexfactory.com/calendar?month=jan.2026 (example)
    """
    
    current_date = datetime.now()
    # Construct month string e.g. "jan.2026"
    month_str = current_date.strftime("%b.%Y").lower()
    
    # We might need next month too if we are at the end of the month
    next_month_date = current_date + timedelta(days=20)
    next_month_str = next_month_date.strftime("%b.%Y").lower()
    
    urls = [f"https://www.forexfactory.com/calendar?month={month_str}"]
    if month_str != next_month_str:
        urls.append(f"https://www.forexfactory.com/calendar?month={next_month_str}")
        
    db = DBClient()
    processed_count = 0
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1"
    }
    
    for url in urls:
        print(f"Fetching {url}...")
        try:
            resp = requests.get(url, headers=headers, timeout=15, impersonate="chrome")
            if resp.status_code != 200:
                print(f"Failed to fetch {url}: {resp.status_code}")
                continue
                
            # Regex Extraction of Event Objects
            # Finds strings starting with {"id": and containing "impactName"
            matches = re.finditer(r'(\{?"id":\d+,[^}]*?"impactName":"[^"]+"[^}]*?\})', resp.text)
            
            for m in matches:
                # Clean parsing
                try:
                    # The regex might catch "id":123 (unquoted id if sloppy), but FF seems to have quoted keys usually inside the object.
                    # We might need to ensure it's valid JSON.
                    # As we saw in debug, keys inside the objects ARE quoted.
                    # e.g. {"id":149849,"ebaseId":254,"name":"..."}
                    
                    obj_str = m.group(1)
                    if not obj_str.startswith('{'): obj_str = '{' + obj_str
                    
                    # Simple JSON load
                    data = json.loads(obj_str)
                    
                    # Process Event
                    if not validate_event(data):
                        continue
                        
                    save_event(db, data)
                    processed_count += 1
                    
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    print(f"Error processing event: {e}")
                    continue
                    
        except Exception as e:
            print(f"Request Error: {e}")
            
    print(f"Total Events Processed: {processed_count}")

def validate_event(data):
    # Filter by Currency
    curr = data.get('currency', '')
    if curr not in TARGET_CURRENCIES and 'CNY' not in curr: 
        return False
        
    # Get Impact
    impact = data.get('impactName', '').lower()
    event_name = data.get('name', '')
    
    # Logic:
    # 1. High Impact: Always Keep
    if impact == 'high':
        return True
        
    # 2. Medium Impact: Keep ONLY if it matches Important Keywords
    if impact == 'medium':
        if any(k.lower() in event_name.lower() for k in IMPORTANT_KEYWORDS):
            return True
        return False
            
    # 3. Low/Non Impact: Drop completely
    return False

def save_event(db, data):
    # Map fields
    # FF: name, country, actual, forecast, previous, dateline (timestamp)
    ts = data.get('dateline')
    if not ts: return
    
    dt = datetime.fromtimestamp(int(ts))
    date_str = dt.strftime('%Y-%m-%d')
    
    # Impact Mapping
    impact_map = {
        'high': 'High',
        'medium': 'Medium',
        'low': 'Low'
    }
    impact_val = impact_map.get(data.get('impactName', '').lower(), 'Low')
    
    # Clean up values (FF often has empty strings or html spans in values?)
    # "actual": "51.9", sometimes "<span class=...>"
    # Usually clean in JSON but let's be safe.
    
    # Description: FF List View doesn't have a text description. 
    # Since we strictly have 'actual', 'forecast', 'previous' columns now, 
    # we leave description empty rather than stuffing metrics here.
    desc = ""
    
    print(f"Saving: {date_str} [{data.get('country')}] {data.get('name')} ({impact_val})")
    
    db.save_economic_event(
        event_date=date_str,
        event_name=data.get('name'),
        country=data.get('country'),
        impact=impact_val,
        description=desc,
        source="forex_factory",
        actual=data.get('actual', ''),
        forecast=data.get('forecast', ''),
        previous=data.get('previous', '')
    )

if __name__ == "__main__":
    fetch_and_save_calendar()
