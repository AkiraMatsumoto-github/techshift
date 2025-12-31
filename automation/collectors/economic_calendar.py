#!/usr/bin/env python3
"""
Economic Calendar Collector for FinShift
Fetches upcoming economic events from Yahoo Finance, iterates 1-by-1, and persists to WordPress via DBClient.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import os
import sys

# Add parent directory to path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

from automation.db.client import DBClient

# High Impact Keywords
IMPORTANT_KEYWORDS = [
    "Fed", "FOMC", "Interest Rate", "Policy Rate",
    "GDP", "Gross Domestic Product",
    "CPI", "Consumer Price Index", "PPI", "Producer Price", "PCE", "Inflation",
    "Non-Farm Payrolls", "Nonfarm Payrolls", "Unemployment Rate", "Jobless Claims",
    "ISM", "PMI", "Caixin", "Tankan",
    "Retail Sales",
    "Consumer Confidence",
    "Housing Starts",
    "BOJ", "Bank of Japan",
    "ECB", "European Central Bank",
    "PBOC", "People's Bank of China",
    "RBI", "Reserve Bank of India",
    "Trade Balance", "Export", "Import"
]

TARGET_REGIONS = ["US", "CN", "JP", "IN", "ID", "EU", "GB", "DE", "FR", "BR", "KR", "AU", "CA"]

def fetch_and_save_calendar(days=14):
    start_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    url = f"https://finance.yahoo.com/calendar/economic?from={start_date}&to={end_date}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }
    
    print(f"Fetching Economic Calendar from {start_date} to {end_date}...")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching calendar: {e}")
        return []

    soup = BeautifulSoup(response.content, 'lxml')
    db = DBClient()
    
    # Improved Date Parsing needed, but for now reverting to simplified logic or assuming "Next 14 days"
    # Actually, let's assume valid rows found.
    rows = soup.find_all('tr')
    
    current_date = start_date
    count = 0
    all_events = []
    
    for row in rows:
        # Date Header check
        th = row.find('th')
        if th and 'colspan' in th.attrs:
             dtext = th.get_text(strip=True)
             try:
                 dt = datetime.strptime(dtext, "%A, %B %d, %Y")
                 current_date = dt.strftime("%Y-%m-%d")
             except:
                 pass
             continue
        
        cols = row.find_all('td')
        if not cols or len(cols) < 4: continue
        
        region = cols[1].get_text(strip=True)
        event = cols[2].get_text(strip=True)
        
        # Keyword Filter
        if not any(kw.lower() in event.lower() for kw in IMPORTANT_KEYWORDS): continue
        # Region Filter
        if not any(r in region for r in TARGET_REGIONS) and "USD" not in region: continue
        
        impact = "High" if any(x in event for x in ["Fed", "FOMC", "GDP", "CPI", "Payrolls"]) else "Medium"
        description = row.get_text(" | ", strip=True) # Full row as desc
        
        # Add to return list
        all_events.append({
            "date": current_date,
            "region": region,
            "event": event,
            "impact": impact
        })
        
        print(f"Saving Event: {current_date} [{region}] {event}")
        
        db.save_economic_event(
            event_date=current_date,
            event_name=event,
            country=region,
            impact=impact,
            description=description,
            source="yahoo_finance"
        )
        count += 1
        
    print(f"Saved {count} events to DB.")
    return all_events

if __name__ == "__main__":
    fetch_and_save_calendar()
