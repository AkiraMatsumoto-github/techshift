#!/usr/bin/env python3
"""
Daily Briefing Automation Controller
Orchestrates the N:1 article generation process.
"""

import argparse
import sys
import os
import json
import hashlib
import markdown
import time
from datetime import datetime, timedelta

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automation.db.client import DBClient
from automation.gemini_client import GeminiClient
from automation.wp_client import WordPressClient
from automation.collectors.collector import collect_articles
from automation.collectors import market_data
from automation.collectors import forex_factory
from automation.internal_linker import InternalLinkSuggester

def get_url_hash(url):
    return hashlib.sha256(url.encode('utf-8')).hexdigest()

def phase_1_collection(args):
    print("\n=== Phase 1: Global Data Collection ===")
    db = DBClient()
    gemini = GeminiClient()
    
    # Ensure DB Schema is up to date
    try:
        db.update_schema()
    except Exception as e:
        print(f"Schema update warning: {e}")

    # 1. News Collection
    print(">> Collecting News...")
    collect_region = "all" if args.region == "all" else args.region
    
    articles = collect_articles(region=collect_region, hours=args.hours)
    print(f"Fetched {len(articles)} raw articles.")
    
    today_date = datetime.now()
    
    # --- Optimization: Batch Deduplication ---
    print(">> Checking Database for duplicates (Batch)...")
    art_map = {}
    all_hashes = []
    
    for art in articles:
        u_hash = get_url_hash(art['url'])
        art['url_hash'] = u_hash
        all_hashes.append(u_hash)
        art_map[u_hash] = art
        
    known_hashes = db.check_known_hashes(all_hashes)
    print(f"Skipped {len(known_hashes)} existing articles.")
    
    new_articles = [art for art in articles if art['url_hash'] not in known_hashes]
    
    if not new_articles:
        print("No new articles to process.")
        # Proceed to market data anyway
    
    # --- Optimization: Batch Processing ---
    # from concurrent.futures import ThreadPoolExecutor, as_completed (Removed for Batch)

    if new_articles:
        print(f"Processing {len(new_articles)} new articles with Batch AI Check...")
        new_count = 0
        batch_size = 20
        
        for i in range(0, len(new_articles), batch_size):
            batch = new_articles[i:i+batch_size]
            print(f" >> Sending Batch {i//batch_size + 1}/{(len(new_articles)-1)//batch_size + 1} ({len(batch)} articles)...")
            
            # 1. Batch AI Check
            results_map = gemini.check_relevance_batch(batch)
            
            # 2. Process Results
            for art in batch:
                try:
                    u_hash = art['url_hash']
                    res = results_map.get(u_hash, {'is_relevant': False, 'reason': 'Batch Error/Missing'})
                    
                    is_relevant = res['is_relevant']
                    reason = res['reason']
                    
                    # Save
                    article_record = {
                        "url_hash": u_hash,
                        "title": art['title'],
                        "source": art['source'],
                        "region": art.get('region', 'Global'),
                        "published_at": art['published'],
                        "summary": art['summary'],
                        "is_relevant": is_relevant,
                        "relevance_reason": reason
                    }
                    if article_record['published_at'] == "Unknown":
                         article_record['published_at'] = today_date
                    
                    if args.dry_run:
                        print(f"[Dry-Run] Processed: {art['title'][:40]}... (Relevant: {is_relevant})")
                    else:
                         db.save_article(article_record)
                         print(f"Saved: {art['title'][:30]}... (Relevant: {is_relevant})")
                    
                    new_count += 1
                    
                except Exception as e:
                    print(f"Error processing {art['title'][:20]}...: {e}")
            
            # Small buffer between batches
            time.sleep(2)
                
        print(f"Finished processing {new_count} new articles.")

    # 2. Market Data
    # Always collect market data if we are in collection phase, as it's needed for analysis context
    print(">> Collecting Market Snapshot...")
    m_data = market_data.fetch_data()
    
    vix_obj = next((x for x in m_data['data']['indices'] if x['symbol'] == '^VIX'), None)
    vix = vix_obj['price'] if vix_obj else None
    
    spx_obj = next((x for x in m_data['data']['indices'] if x['symbol'] == '^GSPC'), None)
    spx = spx_obj['price'] if spx_obj else None
    
    tnx_obj = next((x for x in m_data['data']['bonds'] if x['symbol'] == '^TNX'), None)
    us10y = tnx_obj['price'] if tnx_obj else None
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    if not args.dry_run:
        db.save_market_snapshot(
            date_str=today_str,
            data_json=json.dumps(m_data),
            vix=vix,
            spx=spx,
            us10y=us10y
        )
        # Update WordPress Market Pages with new KPIs
        print(">> Updating WordPress Market Pages...")
        try:
             market_data.update_wp_market_pages(m_data)
        except Exception as e:
             print(f"Warning: Failed to update WP Market Pages: {e}")
             
    print("Market snapshot saved.")

    # 3. Economic Calendar
    # Always collect economic events as they impact all regions
    print(">> Collecting Economic Calendar...")
    if not args.dry_run:
        forex_factory.fetch_and_save_calendar(days=14)
    print("Economic calendar updated.")

def phase_2_analysis(args):
    print("\n=== Phase 2: Analysis & Generation ===")
    
    # Define Target Regions
    if args.region == "all":
        target_regions = ["US", "JP", "CN", "IN", "ID", "Crypto"]
    else:
        target_regions = [args.region]
        
    db = DBClient()
    gemini = GeminiClient()
    wp = WordPressClient()
    today_str = datetime.now().strftime('%Y-%m-%d')

    for region in target_regions:
        print(f"\n>> Processing Region: {region}")
        
        # 1. Get Context
        news = db.get_articles(region=region, hours=args.hours)
        market_snap = db.get_latest_market_snapshot()
        
        # Get Upcoming Events (Future 7 days)
        upcoming_events = db.get_upcoming_events(days=7)
        # Get Recent Events (Past 24-48h) for Context
        recent_events = db.get_recent_events(days=2) # Needed for "Review"
        
        # Get Previous Analysis for Continuity
        prev_analysis = db.get_latest_analysis_by_region(region)
        
        print(f"Context: {len(news)} articles, Market Data: {'Yes' if market_snap else 'No'}, "
              f"Events: {len(upcoming_events)} (Upcoming) / {len(recent_events)} (Recent)")
        
        if not news and not market_snap:
            print("Skipping due to lack of data.")
            continue
            
        # 2. Analyze
        print("Analyzing Market...")
        market_data_str = json.dumps(market_snap['data_json']) if market_snap and 'data_json' in market_snap else "No Data"
        
        # Format Events Strings
        events_str = "## Upcoming Economic Calendar (Next 7 Days)\n"
        events_str += "\n".join([f"- {e['event_date']}: {e['event_name']} ({e['impact']})" for e in upcoming_events])
        
        recent_events_str = "## Recent Economic Results (Past 48 Hours)\n"
        recent_events_str += "\n".join([
            f"- {e['event_date']} {e['event_name']}: Act {e.get('actual','?')} vs fcst {e.get('forecast','?')}" 
            for e in recent_events
        ])

        # Format Previous Analysis Context
        prev_context_str = ""
        if prev_analysis:
            scenarios = prev_analysis.get('scenarios')
            if not isinstance(scenarios, dict):
                scenarios = {}
                
            main_cond = scenarios.get('main', {}).get('condition', 'N/A')
            bull_cond = scenarios.get('bull', {}).get('condition', 'N/A')
            bear_cond = scenarios.get('bear', {}).get('condition', 'N/A')
            
            prev_context_str = f"""
            ## Yesterday's Analysis Context (verification target)
            - Market Regime: {prev_analysis.get('market_regime')}
            - Main Scenario (Base Case): {main_cond}
            - Bull Scenario: {bull_cond}
            - Bear Scenario: {bear_cond}
            """

        
        if args.dry_run:
            print(" [Dry-Run] Generating Analysis with Context...")
            print(f"   - Recent Events: {len(recent_events)} items")
            print(f"   - Prev Analysis: {'Available' if prev_analysis else 'None (404 expected if not deployed)'}")



        analysis = gemini.analyze_daily_market(
            news, 
            market_data_str, 
            events_str, 
            region, 
            extra_context=recent_events_str + "\n" + prev_context_str
        )
        
        if not analysis:
            print("Analysis failed.")
            continue
            
        print(f"Analysis Complete. Regime: {analysis.get('market_regime')}")
        
        # 2.5 Internal Linking Suggestions
        internal_links_context = ""
        try:
            print(">> Fetching Internal Link Suggestions...")
            linker = InternalLinkSuggester(wp, gemini)
            candidates = linker.fetch_candidates(limit=50)
            
            if candidates:
                # Context for scoring: Region + Market Regime + Main Scenario
                scen = analysis.get('scenarios', {}).get('main', {}).get('condition', '')
                scoring_context = f"Region: {region}\nMarket Regime: {analysis.get('market_regime')}\nKey Topics: {scen}"
                
                relevant_links = linker.score_relevance(f"{region} Market Analysis", scoring_context, candidates)
                
                if relevant_links:
                    print(f"   Found {len(relevant_links)} relevant articles.")
                    # candidates are already sorted by relevance_score in score_relevance
                    top_links = relevant_links[:5]
                    
                    for l in top_links:
                        internal_links_context += f"- ID: {l['id']} | Title: {l['title']} | URL: {l['url']}\n"
                else:
                    print("   No relevant links found.")
        except Exception as e:
            print(f"   Internal Linking Warning: {e}")

        # 3. Write Briefing
        print("Writing Briefing...")
        article_md = gemini.write_briefing(
            analysis, 
            region, 
            context_news=news, 
            market_data_str=market_data_str, 
            events_str=events_str,
            date_str=today_str,
            internal_links_context=internal_links_context
        )

        # SEO: Add Internal Link to Previous Analysis
        if prev_analysis and prev_analysis.get('article_url'):
            link_title = prev_analysis.get('article_title', '昨日の市場分析')
            link_url = prev_analysis.get('article_url')
            # Append to bottom
            article_md += f"\n\n---\n**前日の分析**: [{link_title}]({link_url})"
        if args.dry_run:
            print("\n[Dry-Run] Generated Briefing (Excerpt):")
            print("-" * 40)
            print(article_md[:500] + "...\n(truncated)")
            print("-" * 40)
            print("[Dry-Run] Skipping DB Save, File Save, and WordPress Post.")
            continue
        
        if not article_md:
            print("Writing failed.")
            continue
            
        # 4. Save to DB & Local File
        analysis_record = {
            "date": today_str,
            "region": region,
            "sentiment_score": analysis.get("sentiment_score"),
            "sentiment_label": analysis.get("sentiment_label"),
            "market_regime": analysis.get("market_regime"),
            "scenarios": analysis.get("scenarios"),
            "full_briefing_md": article_md
        }
        db.save_daily_analysis(analysis_record)
        print("Analysis & Article saved to DB.")
        
        # Save to local generated_articles
        output_dir = os.path.join(os.path.dirname(__file__), "generated_articles")
        os.makedirs(output_dir, exist_ok=True)
        
        filename_base = f"{today_str}_{region}_briefing"
        md_path = os.path.join(output_dir, f"{filename_base}.md")
        
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(article_md)
        print(f"Article saved locally to: {md_path}")
        
        # 5. Post to WordPress
        print("Posting to WordPress...")
        
        lines = article_md.strip().split('\n')
        
        # Extract title logic
        title_line = lines[0].strip()
        if title_line.startswith("#"):
            title = title_line.lstrip("#").strip()
            content_body_md = "\n".join(lines[1:]).strip()
        elif "Title:" in title_line or "**Title**:" in title_line:
            # Handle "Title: ..." or "**Title**: ..." or "1. Title: ..."
            parts = title_line.split("itle", 1)[1] # Split after 'itle'
            if ":" in parts:
                title = parts.split(":", 1)[1].strip(" *") # Remove : and bold markers
                content_body_md = "\n".join(lines[1:]).strip()
            else:
                 title = f"Daily Briefing ({region}) - {today_str}"
                 content_body_md = article_md
        else:
             # Fallback: Check if first line is short and looks like a title
             if len(title_line) < 100 and len(lines) > 1:
                 title = title_line.strip(" *#")
                 content_body_md = "\n".join(lines[1:]).strip()
             else:
                 title = f"Daily Briefing ({region}) - {today_str}"
                 content_body_md = article_md

        # Convert to HTML
        # Use extensions for better table and link support
        content_body_html = markdown.markdown(
            content_body_md, 
            extensions=['tables', 'fenced_code', 'nl2br']
        )
        
        # Feature Image Generation
        featured_media_id = None
        if not args.dry_run:
            try:
                print("Generating Feature Image...")
                img_prompt = gemini.generate_image_prompt(title, content_body_md[:2000], "market-analysis") # Use MD for context
                
                # Save image to generated_articles
                img_path = os.path.join(output_dir, f"{filename_base}.png")
                
                saved_img = gemini.generate_image(img_prompt, img_path)
                if saved_img:
                    print(f"Image saved locally to: {saved_img}")
                    print("Uploading Image to WordPress...")
                    media_res = wp.upload_media(saved_img, alt_text=title)
                    if media_res:
                        featured_media_id = media_res.get('id')
            except Exception as e:
                print(f"Image generation failed: {e}")

        # Get Categories/Tags
        cat_id = wp.get_category_id("market-analysis")
        if not cat_id:
             cat_id = wp.get_category_id("uncategorized")
        
        tag_ids = []
        reg_tag = wp.get_tag_id(region)
        if reg_tag: tag_ids.append(reg_tag)
        
        status = "publish" 
        
        # Prepare Post Meta regardless of dry-run for verification
        # Extract Scenarios
        scenarios = analysis.get("scenarios", {})
        main_data = scenarios.get("main", {})
        bull_data = scenarios.get("bull", {})
        bear_data = scenarios.get("bear", {})
        
        # Format Scenarios with Probability
        main_text = f"[{main_data.get('probability', 'Unknown')}] {main_data.get('condition', '')}"
        bull_text = f"[{bull_data.get('probability', 'Unknown')}] {bull_data.get('condition', '')}"
        bear_text = f"[{bear_data.get('probability', 'Unknown')}] {bear_data.get('condition', '')}"

        # Extract AI Structured Summary
        ai_structured_summary = analysis.get("ai_structured_summary", {})

        post_meta = {
            "_finshift_sentiment": analysis.get("sentiment_score"),
            "_finshift_regime": analysis.get("market_regime"),
            "_finshift_scenario_main": main_text,
            "_finshift_scenario_bull": bull_text,
            "_finshift_scenario_bear": bear_text,
            "_ai_structured_summary": json.dumps(ai_structured_summary, ensure_ascii=False)
        }

        if not args.dry_run:
            res = wp.create_post(
                title=title,
                content=content_body_html, # Send HTML
                status=status,
                categories=[cat_id] if cat_id else [],
                tags=tag_ids,
                featured_media=featured_media_id,
                meta=post_meta
            )
            
            if res:
                print(f"Posted to WordPress (ID: {res.get('id')}). Status: {status}")
                # Update DB with the public URL for future linking
                # Update DB with the public URL using FULL SAVE to prevent overwriting scenarios
                if res.get('link'):
                    analysis_record['article_url'] = res.get('link')
                    db.save_daily_analysis(analysis_record)
                    print(f"Updated DB with Article URL: {res.get('link')}")
            else:
                print("Failed to post to WordPress.")

        else:
            print(f"[Dry-Run] Would post: {title}")
            print(f"[Dry-Run] With Meta: {json.dumps(post_meta, ensure_ascii=False)}")
            print(f"[Dry-Run] Image ID: {featured_media_id}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["collect", "analyze", "all"], default="all", help="Execution phase")
    parser.add_argument("--region", default="all", help="Target region (US, JP, etc) or 'all'")
    parser.add_argument("--hours", type=int, default=24, help="Lookback hours for news")
    parser.add_argument("--dry-run", action="store_true")
    
    args = parser.parse_args()
    
    if args.phase in ["collect", "all"]:
        phase_1_collection(args)
        
    if args.phase in ["analyze", "all"]:
        phase_2_analysis(args)

if __name__ == "__main__":
    main()
