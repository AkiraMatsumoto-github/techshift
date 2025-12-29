#!/usr/bin/env python3
"""
Market Data Collector for FinShift Risk Monitor
Fetches 1D, 1W, 1M performance for key assets using yfinance.
Saves data to themes/finshift/assets/data/risk_monitor.json
"""

import os
import json
import yfinance as yf
from datetime import datetime
import sys

# Define Assets to Track
ASSETS = {
    "indices": [
        {"symbol": "^GSPC", "name": "S&P 500", "region": "US"},
        {"symbol": "^IXIC", "name": "Nasdaq", "region": "US"},
        {"symbol": "^N225", "name": "Nikkei 225", "region": "JP"},
        {"symbol": "^NSEI", "name": "Nifty 50", "region": "IN"},
        {"symbol": "000001.SS", "name": "Shanghai Comp", "region": "CN"},
        {"symbol": "^JKSE", "name": "IDX Composite", "region": "ID"}, # Indonesia
    ],
    "commodities": [
        {"symbol": "GC=F", "name": "Gold", "region": "Global"},
        {"symbol": "CL=F", "name": "Crude Oil", "region": "Global"},
        # {"symbol": "HG=F", "name": "Copper", "region": "Global"},
    ],
    "crypto": [
        {"symbol": "BTC-USD", "name": "Bitcoin", "region": "Global"},
        {"symbol": "ETH-USD", "name": "Ethereum", "region": "Global"},
    ],
    "forex": [
        {"symbol": "USDJPY=X", "name": "USD/JPY", "region": "Global"},
        {"symbol": "CNY=X", "name": "USD/CNY", "region": "Global"},
    ]
}

# Output Paths
THEME_DATA_DIR = os.path.join(os.getcwd(), "themes/finshift/assets/data")
AUTOMATION_DATA_DIR = os.path.join(os.getcwd(), "automation/data")

def ensure_dirs():
    os.makedirs(THEME_DATA_DIR, exist_ok=True)
    os.makedirs(AUTOMATION_DATA_DIR, exist_ok=True)

def get_percentage_change(current, old):
    if not old or old == 0:
        return 0.0
    return ((current - old) / old) * 100

def fetch_data():
    """Fetch market data and calculate changes."""
    print("Fetching market data from Yahoo Finance...")
    
    # Flatten list of symbols for bulk fetch (efficient)
    all_symbols = []
    for category in ASSETS.values():
        for asset in category:
            all_symbols.append(asset["symbol"])
            
    # Fetch data (1mo history to calculate 1M change)
    # interval='1d' is standard.
    tickers = yf.Tickers(" ".join(all_symbols))
    
    results = {
        "updated_at": datetime.now().isoformat(),
        "data": {}
    }
    
    for category, assets in ASSETS.items():
        results["data"][category] = []
        for asset in assets:
            symbol = asset["symbol"]
            name = asset["name"]
            
            try:
                # Get history
                # We need at least 1mo of data. 
                # yfinance history() returns a DataFrame
                ticker = tickers.tickers[symbol]
                hist = ticker.history(period="1mo")
                
                if hist.empty:
                    print(f"Warning: No data for {symbol}")
                    continue
                
                # Current Price (Last available close)
                current_price = hist['Close'].iloc[-1]
                
                # 1 Day Ago (iloc[-2])
                price_1d = hist['Close'].iloc[-2] if len(hist) >= 2 else current_price
                
                # 1 Week Ago (approx 5 trading days)
                price_1w = hist['Close'].iloc[-6] if len(hist) >= 6 else hist['Close'].iloc[0]
                
                # 1 Month Ago (iloc[0])
                price_1m = hist['Close'].iloc[0]
                
                # Calculate Changes
                change_1d = get_percentage_change(current_price, price_1d)
                change_1w = get_percentage_change(current_price, price_1w)
                change_1m = get_percentage_change(current_price, price_1m)
                
                data_point = {
                    "symbol": symbol,
                    "name": name,
                    "price": round(current_price, 2),
                    "changes": {
                        "1d": round(change_1d, 2),
                        "1w": round(change_1w, 2),
                        "1m": round(change_1m, 2)
                    },
                    "last_close_date": hist.index[-1].strftime('%Y-%m-%d')
                }
                results["data"][category].append(data_point)
                print(f"Fetched {name}: {data_point['price']} ({data_point['changes']['1d']}%)")
                
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")
                
    return results

def save_json(data, filename="risk_monitor.json"):
    # Save to Theme Directory
    theme_path = os.path.join(THEME_DATA_DIR, filename)
    with open(theme_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved to {theme_path}")
    
    # Save to Automation Directory (Backup)
    backup_path = os.path.join(AUTOMATION_DATA_DIR, filename)
    with open(backup_path, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    ensure_dirs()
    data = fetch_data()
    save_json(data)
    print("Market data update complete.")

if __name__ == "__main__":
    main()
