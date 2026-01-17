import argparse
import feedparser
import requests
import json
import os
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import time

# TechShift RSS Sources
# Focus: AI (Multi-Agent, LLM), Quantum (PQC), Green (Battery, Fusion)
DEFAULT_SOURCES = {
    # --- Top Tier Tech (General) ---
    "techcrunch_ai": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "wired_science": "https://www.wired.com/feed/category/science/latest/rss",
    "mit_tech_review": "https://www.technologyreview.com/feed/",
    "venturebeat_ai": "https://venturebeat.com/category/ai/feed/",

    # --- Deep Tech / Research ---
    # Note: Some corporate blogs might not have simple RSS, using proxies or aggregators if needed.
    # For MVP, we stick to accessible feeds.
    
    # AI & Compute
    "nvidia_blog": "https://blogs.nvidia.com/feed/", 
    "google_ai": "https://blog.google/technology/ai/rss/",
    "microsoft_ai": "https://blogs.microsoft.com/ai/feed/",
    "huggingface_blog": "https://huggingface.co/blog/feed.xml",

    # Quantum & Computing
    "quantum_daily": "https://thequantuminsider.com/feed/", 
    # "quanta_magazine": "https://www.quantamagazine.org/feed/", # Excellent for foundation

    # Green & Energy (Batteries, Fusion)
    # Green & Energy (Batteries, Fusion)
    "cleantechnica": "https://cleantechnica.com/feed/",
    "energy_storage_news": "https://energy-storage.news/feed", # Added for solid-state
    "ieee_spectrum_energy": "https://spectrum.ieee.org/feeds/topic/energy.rss", # Fixed URL

    # --- Startups &VC ---
    "y_combinator": "https://blog.ycombinator.com/feed/",
}

# Domain Mapping
REGION_MAPPING = {
    # We repurpose "Region" as "Technology Domain" for TechShift
    "AI": ["techcrunch_ai", "venturebeat_ai", "nvidia_blog", "google_ai", "microsoft_ai", "huggingface_blog", "y_combinator"],
    "Quantum": ["quantum_daily", "wired_science", "mit_tech_review"], # MIT/Wired cover quantum often
    "Green": ["cleantechnica", "ieee_spectrum_energy", "energy_storage_news"], # Added new sources
    "General": ["mit_tech_review", "wired_science"]
}

def fetch_rss(url, source_name, days=None, hours=None):
    """Fetches and parses an RSS feed."""
    print(f"Fetching {source_name} from {url}...")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/rss+xml, application/xml, text/xml, */*"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            print(f"Error fetching {url}: Status {resp.status_code}")
            return []
            
        feed = feedparser.parse(resp.content)
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

    articles = []
    
    if feed.bozo:
        print(f"Warning: Error parsing feed {source_name}: {feed.bozo_exception}")

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
        
        is_recent = False
        if published_parsed:
             # Make timezone-aware comparison
             if published_parsed.tzinfo is not None:
                 now = datetime.now(published_parsed.tzinfo)
             else:
                 now = datetime.now()
                 
             if hours:
                 cutoff = timedelta(hours=hours)
             elif days:
                 cutoff = timedelta(days=days)
             else:
                 cutoff = timedelta(days=2) # Default

             if (now - published_parsed) <= cutoff:
                 is_recent = True
        else:
            # If no date, include cautiously or skip. Including for now.
            is_recent = True

        if is_recent:
            # Determine primary domain
            domain = "General"
            for d, sources in REGION_MAPPING.items():
                if source_name in sources:
                    domain = d
                    break
            
            articles.append({
                "title": entry.title,
                "url": entry.link,
                "published": str(published_parsed) if published_parsed else "Unknown",
                "source": source_name,
                "summary": entry.summary if hasattr(entry, 'summary') else "",
                "region": domain # Mapping "Region" field to Domain for schema compatibility
            })
            
    return articles

def collect_articles(region=None, days=None, hours=None):
    """
    Collect articles for a specific domain (region) or all.
    """
    targets = {}
    if region and region in REGION_MAPPING:
        source_keys = REGION_MAPPING[region]
        for key in source_keys:
            if key in DEFAULT_SOURCES:
                targets[key] = DEFAULT_SOURCES[key]
    elif region == "all" or region is None:
        targets = DEFAULT_SOURCES
    else:
        print(f"Domain/Region {region} not found in mapping.")
        return []
        
    all_articles = []
    for name, url in targets.items():
        articles = fetch_rss(url, name, days=days, hours=hours)
        all_articles.extend(articles)
        time.sleep(1) # Polite delay
        
    return all_articles

def main():
    parser = argparse.ArgumentParser(description="Collect articles from RSS feeds.")
    parser.add_argument("--source", type=str, help="Comma-separated list of source keys or 'all'", default=None)
    parser.add_argument("--region", type=str, help="Domain (AI, Quantum, Green) or 'all'", default="all")
    parser.add_argument("--days", type=int, help="Filter articles published within last N days")
    parser.add_argument("--hours", type=int, help="Filter articles published within last N hours")

    args = parser.parse_args()

    all_articles = []
    
    if args.source:
        target_sources = {}
        if args.source == "all":
            target_sources = DEFAULT_SOURCES
        else:
            keys = args.source.split(",")
            for key in keys:
                key = key.strip()
                if key in DEFAULT_SOURCES:
                    target_sources[key] = DEFAULT_SOURCES[key]
        
        for name, url in target_sources.items():
            articles = fetch_rss(url, name, days=args.days, hours=args.hours)
            all_articles.extend(articles)
            time.sleep(1)
            
    else:
        all_articles = collect_articles(args.region, days=args.days, hours=args.hours)

    print(f"\nFound {len(all_articles)} articles.")
    print(json.dumps(all_articles, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
