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
                print(f"DEBUG: Processing {symbol}...")
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
                
                # 3. Volatility (HV - Historical Volatility)
                # Annualized Standard Deviation of Log Returns (20-day window usually)
                # Using simple percentage change for approximation if simpler, but log returns are standard.
                # HV = std(ln(P_t / P_t-1)) * sqrt(252) * 100
                
                # Using pct_change() as a close proxy for log returns for small changes, or actual log returns.
                # Let's use simple pct_change std dev for robustness with minimal deps if numpy not heavy used, 
                # but standard is:
                import numpy as np
                log_returns = np.log(hist['Close'] / hist['Close'].shift(1))
                # 20-day rolling standard deviation
                volatility_window = 20
                rolling_std = log_returns.rolling(window=volatility_window).std()
                # Annualize (assuming 252 trading days)
                annualized_vol = rolling_std * np.sqrt(252) * 100
                current_vol = annualized_vol.iloc[-1]

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
                    "region": asset.get("region", "Global"),
                    "price": round(current_price, 2),
                    "changes": {
                        "1d": round(change_1d, 2),
                        "1w": round(change_1w, 2),
                        "1m": round(change_1m, 2)
                    },
                    "technical": {
                        "rsi": round(current_rsi, 1) if not pd.isna(current_rsi) else None,
                        "sma_50_dev": round(sma_dev, 2) if not pd.isna(sma_dev) else None,
                        "volatility": round(current_vol, 1) if not pd.isna(current_vol) else 0.0
                    },
                    "last_close_date": hist.index[-1].strftime('%Y-%m-%d')
                }
                results["data"][category].append(data_point)
                print(f"Fetched {name}: {data_point['price']} (RSI: {data_point['technical']['rsi']}, HV: {data_point['technical']['volatility']}%)")
                
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")
                
    return results

def update_wp_market_pages(data):
    """
    Update WordPress Market Pages with fetched metrics.
    Maps regions to page slugs and updates meta.
    """
    print("\n--- Updating WordPress Market Pages ---")
    try:
        from automation.wp_client import WordPressClient
        wp = WordPressClient()
    except ImportError:
        # Fallback for running from different dir
        sys.path.append(os.path.join(os.getcwd()))
        try:
            from automation.wp_client import WordPressClient
            wp = WordPressClient()
        except ImportError:
            print("WordPressClient not found. Skipping WP update.")
            return

    # Map Regions to specific index symbols for metrics
    # usage: Region -> Symbol in fetched data to use for Page Metrics
    REGION_MAP = {
        "us-market": "^GSPC",    # US Market Page uses S&P 500 metrics
        "japan-market": "^N225", # JP Market Page uses Nikkei 225
        "india-market": "^NSEI", # India Market Page uses Nifty 50
        "china-market": "000001.SS", # China uses Shanghai Composite
        "indonesia-market": "^JKSE", # Indonesia uses IDX Composite
        "crypto": "BTC-USD",  # Crypto uses Bitcoin
    }

    # Flatten data for easy lookup by symbol
    flat_data = {}
    for cat, items in data["data"].items():
        for item in items:
            flat_data[item["symbol"]] = item

    for region_slug, symbol in REGION_MAP.items():
        if symbol not in flat_data:
            print(f"Skipping {region_slug}: Data for {symbol} not found.")
            continue
            
        metric_data = flat_data[symbol]
        
        # Prepare Meta Data
        # Mapping:
        # _metric_trend -> 1 Month Change % (Formatted as string with % and sign)
        # _metric_rsi   -> RSI (Formatted as string)
        # _metric_mom   -> Momentum/SMA Dev (Formatted with % and sign)
        
        trend_val = metric_data["changes"]["1m"]
        rsi_val = metric_data["technical"]["rsi"]
        mom_val = metric_data["technical"]["sma_50_dev"]
        vol_val = metric_data["technical"]["volatility"]
        
        meta_update = {
            "_metric_trend": f"{trend_val:+.2f}%" if trend_val is not None else "",
            "_metric_rsi": str(rsi_val) if rsi_val is not None else "",
            "_metric_mom": f"{mom_val:+.2f}%" if mom_val is not None else "",
            "_metric_volatility": f"{vol_val:.1f}%" if vol_val is not None else ""
        }
        
        # Find Page
        print(f"Updating {region_slug} with data from {symbol}...")
        pages = wp.get_pages_by_meta("market_region_tag", region_slug)
        
        if not pages:
            print(f"  No page found for tag: {region_slug}")
            continue
            
        for page in pages:
            print(f"  Found page: {page['title']['rendered']} (ID: {page['id']})")
            # Update Meta
            # Note: updating 'meta' via REST API requires keys to be registered or using specific endpoint.
            # Our custom metabox saves to post_meta. 
            # The standard 'meta' field in REST API needs 'show_in_rest' => true in register_meta.
            # If not registered, we might need a custom endpoint or authenticated update might work if schema allows.
            # Let's try standard update first.
            result = wp.update_resource('pages', page['id'], {"meta": meta_update})
            
            if result:
                print(f"  ✅ Updated metadata for {page['title']['rendered']}")
            else:
                print(f"  ❌ Failed to update {page['title']['rendered']}")

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
    
    # Push to WordPress
    try:
        update_wp_market_pages(data)
    except Exception as e:
        print(f"Error updating WordPress: {e}")
        
    print("Market data update complete.")

if __name__ == "__main__":
    main()
