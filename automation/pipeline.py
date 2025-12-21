#!/usr/bin/env python3
"""
LogiShift Automation Pipeline

Orchestrates the flow:
1. Collection (collector.py)
2. Scoring (scorer.py)
3. Selection (Filter high scores)
4. Generation (generate_article.py)
"""

import argparse
import json
import os
import sys
import subprocess
from datetime import datetime

# Source to Content Type Mapping
SOURCE_TYPE_MAPPING = {
    # Global Sources
    "techcrunch": "global",
    "wsj_logistics": "global",
    "supply_chain_dive": "global",
    "logistics_mgmt": "global",
    "robot_report": "global",
    "supply_chain_brain": "global",
    "supply_chain_brain": "global",
    "freightwaves": "global",
    "robotics_automation_news": "global",
    "36kr_japan": "global",
    "pandaily": "global",
    
    # Domestic Sources
    "lnews": "news",
    "logistics_today": "news",
    "logi_biz": "news",
}

def run_command(command):
    """Run a shell command and return output."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {command}")
        print(result.stderr)
        return None
    return result.stdout

def main():
    parser = argparse.ArgumentParser(description="LogiShift Automation Pipeline")
    parser.add_argument("--days", type=int, help="Days to look back for collection")
    parser.add_argument("--hours", type=int, default=3, help="Hours to look back for collection (overrides --days)")
    parser.add_argument("--threshold", type=int, default=85, help="Score threshold for generation")
    parser.add_argument("--limit", type=int, default=2, help="Max articles to generate per run")
    parser.add_argument("--score-limit", type=int, default=0, help="Max articles to score (0 for all)")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode (no posting)")
    
    args = parser.parse_args()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    articles_file = os.path.join(base_dir, "collected_articles.json")
    scored_file = os.path.join(base_dir, "scored_articles.json")
    
    # 1. Collection
    print("\n=== Step 1: Collection ===")
    
    # Import modules directly
    sys.path.append(os.path.dirname(base_dir))
    from automation.collector import fetch_rss, DEFAULT_SOURCES
    from automation.scorer import score_article
    from automation.url_reader import extract_content
    from automation.summarizer import summarize_article
    from automation.classifier import ArticleClassifier
    from automation.wp_client import WordPressClient
    from automation.gemini_client import GeminiClient
    
    collected_articles = []
    if args.hours:
        print(f"Collecting articles from last {args.hours} hours...")
    else:
        print(f"Collecting articles from last {args.days} days...")
    for name, url in DEFAULT_SOURCES.items():
        # Note: fetch_rss in collector.py currently has hardcoded 2 days logic inside?
        # Let's check.
        # It has `if (now - published_parsed).days <= 2:`
        # We should probably update collector.py to accept days param in fetch_rss.
        # For now, let's assume 2 days is fine or just filter later.
        fetched = fetch_rss(url, name, days=args.days, hours=args.hours)
        collected_articles.extend(fetched)
        
    print(f"Collected {len(collected_articles)} articles.")
    
    # 2. Scoring
    print("\n=== Step 2: Scoring ===")
    scored_articles = []
    
    articles_to_score = collected_articles
    if args.score_limit > 0:
        print(f"Limiting scoring to first {args.score_limit} articles.")
        articles_to_score = collected_articles[:args.score_limit]
    
    for i, article in enumerate(articles_to_score):
        print(f"[{i+1}/{len(articles_to_score)}] Scoring: {article['title'][:30]}...")
        scored = score_article(article)
        scored_articles.append(scored)
        
    # Filter
    high_score_articles = [a for a in scored_articles if a["score"] >= args.threshold]
    high_score_articles.sort(key=lambda x: x["score"], reverse=True)
    
    print(f"\nFound {len(high_score_articles)} articles above threshold {args.threshold}.")
    
    # 3. Generation
    print("\n=== Step 3: Generation ===")
    count = 0
    
    # Schedule logic removed - defaulting to immediate publish
    
    # Initialize Classifier & Clients
    classifier = ArticleClassifier()
    gemini_client = GeminiClient()
    wp_client = WordPressClient()

    # Fetch existing posts for deduplication
    print("Fetching recent posts for deduplication check...")
    existing_titles = []
    try:
        # Fetch more posts to be safe, e.g., last 30
        recent_posts = wp_client.get_posts(limit=30, status="publish")
        if recent_posts:
            existing_titles = [p['title']['rendered'] for p in recent_posts]
            print(f"Loaded {len(existing_titles)} existing post titles.")
        else:
            print("No existing posts found or failed to fetch.")
    except Exception as e:
        print(f"Warning: Failed to fetch existing posts: {e}")

    generated_titles_this_run = []

    for article in high_score_articles:
        if count >= args.limit:
            break
            
        print(f"Generating article for: {article['title']}")
        print(f"Score: {article['score']}")
        print(f"Reason: {article['reasoning']}")
        
        # --- Deduplication Check ---
        print("Checking for duplicates...")
        # Combine existing WP titles and locally processed titles
        comparison_pool = existing_titles + generated_titles_this_run
        
        duplicate_of = gemini_client.check_duplication(article['title'], article.get('summary', ''), comparison_pool)
        
        if duplicate_of:
            print(f"SKIP: Duplicate detected! '{article['title']}' is a duplicate of '{duplicate_of}'")
            continue
            
        print("No duplicate found. Proceeding...")
        generated_titles_this_run.append(article['title'])
        # ---------------------------
        
        # Determine Type
        source = article.get("source", "")
        # Use dynamic classification
        article_type = classifier.classify_type(article['title'], article['summary'], source)
        print(f"Type: {article_type}")
        
        # Generate keyword
        keyword = article['title']
        
        # Base command
        cmd = [
            "python", os.path.join(base_dir, "generate_article.py"),
            "--keyword", keyword,
            "--type", article_type
        ]
        
        # News/Global articles: Context-based generation (URL reading + summarization)
        if article_type in ["news", "global"]:
            print("\n--- Context-based generation (URL reading + summarization) ---")
            
            try:
                # Step 2.5-A: URL reading and summarization
                article_content = extract_content(article['url'], article['source'])
                
                if article_content['content'] and "Error" not in article_content['title']:
                    summary_data = summarize_article(article_content['content'], article['title'])
                    
                    # Pass context as JSON string
                    context_json = json.dumps(summary_data, ensure_ascii=False)
                    cmd.extend(["--context", context_json])
                    print(f"Context created: {len(summary_data['summary'])} chars summary, {len(summary_data['key_facts'])} key facts")
                else:
                    print("Warning: Failed to extract content, falling back to keyword-based generation")
            except Exception as e:
                print(f"Error during context creation: {e}")
                print("Falling back to keyword-based generation")
        else:
            print("\n--- Keyword-based generation (traditional) ---")
            # Know/Buy/Do articles: No context (maintain current behavior)
        
        if args.dry_run:
            cmd.append("--dry-run")
        
        # print(f"Scheduled for: {schedule_datetime}")

            
        subprocess.run(cmd)
        count += 1
        print("-" * 40)

if __name__ == "__main__":
    main()
