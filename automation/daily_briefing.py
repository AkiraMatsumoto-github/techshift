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
from datetime import datetime, timedelta

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automation.db.client import DBClient
from automation.gemini_client import GeminiClient
from automation.wp_client import WordPressClient
from automation.collectors.collector import collect_articles
from automation.collectors import market_data
from automation.collectors import economic_calendar

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
    
    new_count = 0
    for art in articles:
        u_hash = get_url_hash(art['url'])
        if db.check_article_exists(u_hash):
            continue
            
        # Relevance Check (AI)
        # To save cost/time in dry-run or verification, one might skip this, but let's run it.
        # Note: In collect_articles, we might want to batch this? But 1-by-1 is safer for now.
        is_relevant, reason = gemini.check_relevance(art['title'], art['summary'])
        
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
             article_record['published_at'] = datetime.now()
        
        if params_dry_run := args.dry_run:
            print(f"[Dry-Run] Would save: {art['title']} (Relevant: {is_relevant})")
        else:
             db.save_article(article_record)
             new_count += 1
        
    print(f"Saved {new_count} new articles.")

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
    print("Market snapshot saved.")

    # 3. Economic Calendar
    if args.region == "all" or args.region == "Global":
        print(">> Collecting Economic Calendar...")
        # Note: economic_calendar script writes directly. We can't easily suppress it for dry-run 
        # unless we modify it. For now, we just run it if not dry-run.
        if not args.dry_run:
            economic_calendar.fetch_and_save_calendar(days=14)
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
        events = db.get_upcoming_events(days=7)
        
        print(f"Context: {len(news)} articles, Market Data: {'Yes' if market_snap else 'No'}, Events: {len(events)}")
        
        if not news and not market_snap:
            print("Skipping due to lack of data.")
            continue
            
        if args.dry_run:
            print("[Dry-Run] Skipping AI Analysis & Writing.")
            continue

        # 2. Analyze
        print("Analyzing Market...")
        market_data_str = json.dumps(market_snap['data_json']) if market_snap and 'data_json' in market_snap else "No Data"
        events_str = "\n".join([f"{e['event_date']}: {e['event_name']} ({e['impact']})" for e in events])
        
        analysis = gemini.analyze_daily_market(news, market_data_str, events_str, region)
        
        if not analysis:
            print("Analysis failed.")
            continue
            
        print(f"Analysis Complete. Regime: {analysis.get('market_regime')}")
        
        # 3. Write Briefing
        print("Writing Briefing...")
        article_md = gemini.write_briefing(
            analysis, 
            region, 
            context_news=news, 
            market_data_str=market_data_str, 
            events_str=events_str,
            date_str=today_str
        )
        
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
        
        status = "draft" 
        
        # Prepare Post Meta regardless of dry-run for verification
        # Extract Scenarios
        scenarios = analysis.get("scenarios", {})
        bull_data = scenarios.get("bull", {})
        bear_data = scenarios.get("bear", {})
        
        # Format Scenarios with Probability
        bull_text = f"[{bull_data.get('probability', 'Unknown')}] {bull_data.get('condition', '')}"
        bear_text = f"[{bear_data.get('probability', 'Unknown')}] {bear_data.get('condition', '')}"

        # Extract AI Structured Summary
        ai_structured_summary = analysis.get("ai_structured_summary", {})

        post_meta = {
            "_finshift_sentiment": analysis.get("sentiment_score"),
            "_finshift_regime": analysis.get("market_regime"),
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
