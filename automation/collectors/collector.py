import argparse
import feedparser
import json
import os
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import time

# Default RSS Sources
DEFAULT_SOURCES = {
    # --- Global News (Base) ---
    "yahoo_finance_top": "https://finance.yahoo.com/news/rssindex",
    "cnbc_world": "https://www.cnbc.com/id/100727362/device/rss/rss.html",
    # "wsj_markets": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml", # RSS Empty

    # --- Asia Strategy (Source of Competitive Advantage) ---
    # China (Native Sources - Deep Dive)
    "36kr_china": "https://36kr.com/feed", # Tech & Startups (Unicorns) -> SUCCESS
    # "sina_finance_focus": "http://rss.sina.com.cn/news/allnews/finance.xml", # XML Error
    # "china_daily_biz": "http://www.chinadaily.com.cn/rss/bizchina_rss.xml", # XML Error
    # "xinhua_biz": "http://english.news.cn/rss/business.xml", # XML Error

    # India 
    # "mint_top": "https://www.livemint.com/rss/news", # Fallback only
    # "mint_markets": "https://www.livemint.com/rss/markets", # Fallback only
    "economictimes": "https://economictimes.indiatimes.com/rssfeedsdefault.cms", # SUCCESS

    # Indonesia
    "antara_news_biz": "https://en.antaranews.com/rss/business-investment.xml", # SUCCESS
    # "jakarta_globe": "https://jakartaglobe.id/rss/news", # XML Error
    
    # --- Japan Market ---
    "yahoo_jp_business": "https://news.yahoo.co.jp/rss/categories/business.xml", # SUCCESS
    
    # --- Crypto & Assets (Strategic Indicators) ---
    "coindesk": "https://www.coindesk.com/arc/outboundfeeds/rss/", # SUCCESS
    # "cointelegraph": "https://cointelegraph.com/rss", # Fallback only
    "bitcoin_magazine": "https://bitcoinmagazine.com/.rss/full/",
}

def fetch_rss(url, source_name, days=None, hours=None):
    """Fetches and parses an RSS feed."""
    print(f"Fetching {source_name} from {url}...")
    feed = feedparser.parse(url)
    articles = []
    
    if feed.bozo:
        print(f"Warning: Error parsing feed {source_name}: {feed.bozo_exception}")
        # Continue anyway as feedparser often returns usable data even with errors

    for entry in feed.entries:
        # Parse published date
        published_parsed = None
        if hasattr(entry, 'published'):
             try:
                published_parsed = date_parser.parse(entry.published)
             except:
                pass
        elif hasattr(entry, 'updated'):
             try:
                published_parsed = date_parser.parse(entry.updated)
             except:
                pass
        
        # Filter by date (last 24 hours) - Optional, can be a flag
        # For now, let's just collect everything and let the scorer/filter handle it, 
        # or maybe just last 48 hours to be safe.
        is_recent = False
        if published_parsed:
             # Make offset-naive for comparison if needed, or handle timezones properly
             # Simple check: if within last 2 days
             if published_parsed.tzinfo is not None:
                 now = datetime.now(published_parsed.tzinfo)
             else:
                 now = datetime.now()
                 
             # Determine cutoff
             if hours:
                 cutoff = timedelta(hours=hours)
             elif days:
                 cutoff = timedelta(days=days)
             else:
                 cutoff = timedelta(days=2) # Default to 2 days

             if (now - published_parsed) <= cutoff:
                 is_recent = True
        else:
            # If no date, assume it's recent enough or skip? Let's include for now.
            is_recent = True

        if is_recent:
            articles.append({
                "title": entry.title,
                "url": entry.link,
                "published": str(published_parsed) if published_parsed else "Unknown",
                "source": source_name,
                "summary": entry.summary if hasattr(entry, 'summary') else ""
            })
            
    return articles

def main():
    parser = argparse.ArgumentParser(description="Collect articles from RSS feeds.")
    parser.add_argument("--source", type=str, help="Comma-separated list of source keys (e.g., techcrunch,wsj_logistics) or 'all'", default="all")
    parser.add_argument("--dry-run", action="store_true", help="Print results to stdout instead of saving (currently only prints)")
    parser.add_argument("--days", type=int, help="Filter articles published within last N days")
    parser.add_argument("--hours", type=int, help="Filter articles published within last N hours")

    args = parser.parse_args()

    target_sources = {}
    if args.source == "all":
        target_sources = DEFAULT_SOURCES
    else:
        keys = args.source.split(",")
        for key in keys:
            key = key.strip()
            if key in DEFAULT_SOURCES:
                target_sources[key] = DEFAULT_SOURCES[key]
            else:
                print(f"Warning: Source '{key}' not found in defaults.")

    all_articles = []
    for name, url in target_sources.items():
        articles = fetch_rss(url, name, days=args.days, hours=args.hours)
        all_articles.extend(articles)
        time.sleep(1) # Be nice to servers

    # Output results
    print(f"\nFound {len(all_articles)} articles.")
    print(json.dumps(all_articles, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
