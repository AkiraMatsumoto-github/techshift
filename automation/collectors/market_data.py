#!/usr/bin/env python3
"""
Market Data Collector for FinShift Risk Monitor
Fetches 1D, 1W, 1M performance for key assets using yfinance.
Saves data to themes/finshift/assets/data/risk_monitor.json
"""

import os
import json
import yfinance as yf
import pandas as pd
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
        {"symbol": "^HSI", "name": "Hang Seng Index", "region": "CN"},
        {"symbol": "^JKSE", "name": "IDX Composite", "region": "ID"}, # Indonesia
        {"symbol": "^VIX", "name": "VIX", "region": "Global"}, # Volatility Index
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
        {"symbol": "INR=X", "name": "USD/INR", "region": "Global"},
        {"symbol": "IDR=X", "name": "USD/IDR", "region": "Global"},
    ],
    "bonds": [
        {"symbol": "^TNX", "name": "US 10Y Yield", "region": "US"}
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
                # We need at least 3mo of data for 50-day SMA and 14-day RSI
                ticker = tickers.tickers[symbol]
                hist = ticker.history(period="3mo")
                
                if hist.empty:
                    print(f"Warning: No data for {symbol}")
                    continue
                
                # --- Technical Analysis ---
                # 1. RSI (14-day)
                delta = hist['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                current_rsi = rsi.iloc[-1]
                
                # 2. SMA (50-day) and Deviation
                sma_50 = hist['Close'].rolling(window=50).mean()
                current_sma = sma_50.iloc[-1]
                current_price = hist['Close'].iloc[-1]
                
                sma_dev = 0.0
                if not pd.isna(current_sma) and current_sma != 0:
                    sma_dev = ((current_price - current_sma) / current_sma) * 100
                
                # --- Price Changes ---
                
                # 1 Day Ago (iloc[-2])
                price_1d = hist['Close'].iloc[-2] if len(hist) >= 2 else current_price
                
                # 1 Week Ago (approx 5 trading days)
                price_1w = hist['Close'].iloc[-6] if len(hist) >= 6 else hist['Close'].iloc[0]
                
                # 1 Month Ago (approx 20 trading days)
                price_1m = hist['Close'].iloc[-21] if len(hist) >= 21 else hist['Close'].iloc[0]
                
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
                    "technical": {
                        "rsi": round(current_rsi, 1) if not pd.isna(current_rsi) else None,
                        "sma_50_dev": round(sma_dev, 2) if not pd.isna(sma_dev) else None
                    },
                    "last_close_date": hist.index[-1].strftime('%Y-%m-%d')
                }
                results["data"][category].append(data_point)
                print(f"Fetched {name}: {data_point['price']} (RSI: {data_point['technical']['rsi']})")
                
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
