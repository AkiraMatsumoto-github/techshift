import sys
import os
import json
import time

# Add automation directory to path
sys.path.append(os.path.join(os.getcwd(), 'automation'))

from collectors.collector import fetch_rss, DEFAULT_SOURCES
from collectors.url_reader import extract_content

def main():
    print("=== Visualizing Scraping Success Rates ===")
    
    results = {}
    
    # Test one URL from each source
    for source_key, rss_url in DEFAULT_SOURCES.items():
        print(f"\n--- Testing {source_key} ---")
        try:
            # 1. Fetch RSS to get a real URL
            articles = fetch_rss(rss_url, source_key)
            if not articles:
                print(f"Skipping {source_key}: No articles found in RSS.")
                results[source_key] = "RSS_EMPTY"
                continue
                
            target_article = articles[0]
            url = target_article['url']
            summary = target_article.get('summary', 'No Summary')
            
            print(f"Target URL: {url}")
            
            # 2. Try Scraping
            content_data = extract_content(url, source_key, rss_summary=summary)
            
            # 3. Analyze Result
            is_fallback = content_data.get('is_fallback', False)
            content_len = len(content_data.get('content', ''))
            
            if is_fallback:
                status = "FALLBACK (Scraping Failed)"
            elif content_len < 200:
                status = "WARNING (Content < 200 chars)"
            else:
                status = f"SUCCESS ({content_len} chars)"
                
            print(f"Result: {status}")
            results[source_key] = status
            
            time.sleep(1) # Be nice
            
        except Exception as e:
            print(f"Error testing {source_key}: {e}")
            results[source_key] = f"ERROR: {str(e)}"

    # Summary Reort
    print("\n\n=== Final Report ===")
    print(f"{'Source':<25} | {'Status':<30}")
    print("-" * 60)
    for source, status in results.items():
        print(f"{source:<25} | {status:<30}")

if __name__ == "__main__":
    main()
