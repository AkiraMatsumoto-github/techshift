#!/usr/bin/env python3
"""
FinShift Automation Pipeline

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
import random

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
    parser = argparse.ArgumentParser(description="FinShift Automation Pipeline")
    parser.add_argument("--days", type=int, help="Days to look back for collection")
    parser.add_argument("--hours", type=int, help="Hours to look back for collection (overrides --days, default: 6)")
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
    from automation.collectors.collector import fetch_rss, DEFAULT_SOURCES
    from automation.analysis.scorer import score_article, score_articles_batch
    from automation.collectors.url_reader import extract_content
    from automation.summarizer import summarize_article
    from automation.analysis.classifier import ArticleClassifier
    from automation.wp_client import WordPressClient
    from automation.gemini_client import GeminiClient
    
    collected_articles = []
    
    # Determine lookback
    lookback_hours = None
    lookback_days = None
    
    if args.hours is not None:
        lookback_hours = args.hours
        print(f"Collecting articles from last {lookback_hours} hours...")
    elif args.days is not None:
        lookback_days = args.days
        print(f"Collecting articles from last {lookback_days} days...")
    else:
        # Default behavior
        lookback_hours = 6
        print(f"Collecting articles from last {lookback_hours} hours (default)...")
        
    # Shuffle sources to randomize fetch order (User Request)
    source_items = list(DEFAULT_SOURCES.items())
    random.shuffle(source_items)

    for name, url in source_items:
        # fetch_rss accepts both, prioritizes hours if set not None
        fetched = fetch_rss(url, name, days=lookback_days, hours=lookback_hours)
        collected_articles.extend(fetched)
        
    print(f"Collected {len(collected_articles)} articles.")
    
    # 2. Scoring
    print("\n=== Step 2: Scoring ===")
    scored_articles = []
    
    articles_to_score = collected_articles
    if args.score_limit > 0:
        print(f"Limiting scoring to first {args.score_limit} articles.")
        articles_to_score = collected_articles[:args.score_limit]
    
    
    # Initialize Gemini Client once
    gemini_client = GeminiClient()
    
    import time
    batch_size = 10
    print(f"Scoring in batches of {batch_size}...")
    
    # Early Exit Logic
    high_score_count = 0
    early_exit_threshold = int(args.limit * 2) # Updated to 2x buffer
    # Ensure at least 1
    if early_exit_threshold < 1:
        early_exit_threshold = 1
    
    print(f"Early Exit Threshold configured: Stop if {early_exit_threshold} high-score articles found.")

    for i in range(0, len(articles_to_score), batch_size):
        batch = articles_to_score[i:i + batch_size]
        print(f"[{i+1}-{min(i+batch_size, len(articles_to_score))}/{len(articles_to_score)}] Processing batch...")
        
        try:
            batch_results = score_articles_batch(batch, client=gemini_client, start_id=i)
            
            if batch_results:
                scored_articles.extend(batch_results)
                 # Simple progress indication & Count High Scores
                for res in batch_results:
                     score = res.get('score', 0)
                     print(f"  - Scored: {res.get('title', 'Unknown')[:40]}... -> {score} pts")
                     if score >= args.threshold:
                         high_score_count += 1
            else:
                print("Warning: Batch failed or returned no results. Falling back to individual scoring...")
                for article in batch:
                    print(f"  Fallback Scoring: {article['title'][:30]}...")
                    # Pass client to score_article as well
                    scored = score_article(article, client=gemini_client)
                    scored_articles.append(scored)
                    if scored.get('score', 0) >= args.threshold:
                        high_score_count += 1
            
            # Check for Early Exit
            if high_score_count >= early_exit_threshold:
                print(f"\n🚀 Early Exit: Found {high_score_count} candidate articles (Target >= {early_exit_threshold}). Stopping scoring.")
                break
                
        except Exception as e:
            print(f"Error processing batch: {e}")
                
        time.sleep(2) # Rate limit protection
        
    # Filter
    high_score_articles = [a for a in scored_articles if a["score"] >= args.threshold]
    high_score_articles.sort(key=lambda x: x["score"], reverse=True)
    
    print(f"\nFound {len(high_score_articles)} articles above threshold {args.threshold}.")
    
    # 3. Generation
    # 3. Generation
    print("\n=== Step 3: Generation ===")
    
    if not high_score_articles:
        print("No articles to generate. Exiting.")
        return

    count = 0
    
    # Initialize Classifier & Clients
    print("Initializing clients for generation...")
    # gemini_client is already initialized
    classifier = ArticleClassifier(client=gemini_client)
    
    # Initialize WP Client
    wp_client = None
    try:
        wp_client = WordPressClient()
    except Exception as e:
         print(f"Warning: Failed to initialize WP Client: {e}")

    # Imports for generation (moved from top level to avoid circular imports if any, though generated_article imports pipeline? No.)
    # Actually, import at top level is fine in Python usually unless circular.
    # But let's import here or at top.
    from automation.generate_article import run_generation_task
    
    # Fetch existing posts for deduplication
    print("Fetching recent posts for deduplication check...")
    existing_titles = []
    if wp_client:
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
    else:
        print("Skipping deduplication check (WP Client not available).")

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
        
        # Determine Category & Type
        classification = classifier.classify_article(article['title'], article['summary'], excluded_categories=['market-analysis'])
        category_slug = classification.get('category', 'featured-news')
        article_type = category_slug
            
        print(f"Category: {category_slug} -> Type: {article_type}")
        
        # Prepare arguments for task
        # We need a namespace or mock object appropriately since run_generation_task expects argparse.Namespace
        class TaskArgs:
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)
                
        task_args_dict = {
            "keyword": article['title'],
            "type": article_type,
            "category": category_slug,
            "dry_run": args.dry_run,
            "schedule": None, # Default immediate
            "context": None
        }
        
        # Context Generation
        if article_type in ["news", "global", "market-analysis", "featured-news", "strategic-assets"]:
            print("\n--- Context-based generation (URL reading + summarization) ---")
            
            try:
                article_content = extract_content(article['url'], article['source'])
                
                if article_content['content'] and "Error" not in article_content['title']:
                    summary_data = summarize_article(article_content['content'], article['title'], client=gemini_client)
                    task_args_dict["context"] = json.dumps(summary_data, ensure_ascii=False)
                    print(f"Context created: {len(summary_data['summary'])} chars summary, {len(summary_data['key_facts'])} key facts")
                else:
                    print("Warning: Failed to extract content, falling back to keyword-based generation")
            except Exception as e:
                print(f"Error during context creation: {e}")
                print("Falling back to keyword-based generation")
        else:
             print("\n--- Keyword-based generation (traditional) ---")
             
        # Execute Generation Task
        task_args = TaskArgs(**task_args_dict)
        
        try:
             success = run_generation_task(task_args, gemini_client=gemini_client, wp_client=wp_client)
             if success:
                 count += 1
        except Exception as e:
             print(f"Error executing generation task: {e}")

        print("-" * 40)

if __name__ == "__main__":
    main()
