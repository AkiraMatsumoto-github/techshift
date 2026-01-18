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

    # 2. Market Data & Economic Calendar (Deprecated/Removed)
    print(">> Market Data & Economic Calendar collection skipped (Modules removed).")

def phase_2_analysis(args):
    print("\n=== Phase 2: Analysis & Generation ===")
    
    # Define Target Regions (TechShift Domains)
    if args.region == "all":
        target_regions = ["AI", "Quantum", "Green", "General"]
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
        # market_snap = db.get_latest_market_snapshot() # Deprecated
        
        # Get Upcoming Events (Future 7 days)
        # upcoming_events = db.get_upcoming_events(days=7) # Deprecated
        # Get Recent Events (Past 24-48h) for Context
        # recent_events = db.get_recent_events(days=2) # Needed for "Review"
        
        # Get Previous Analysis for Continuity
        prev_analysis = db.get_latest_analysis_by_region(region)
        
        print(f"Context: {len(news)} articles")
        
        if not news:
            print("Skipping due to lack of data.")
            continue
            
        # 2. Analyze
        print("Analyzing Market...")
        market_data_str = "N/A (Market Data Module Removed)"
        
        # Format Events Strings
        events_str = "No Economic Events Data"
        recent_events_str = ""

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
            print(f"   - Prev Analysis: {'Available' if prev_analysis else 'None'}")

        # 1.5 Fetch Today's Created Articles (Deep Dives)
        # This ensures we link to articles created by pipeline.py earlier today
        created_articles = db.get_todays_generated_articles(region=region)
        created_articles_str = ""
        full_links_context_addendum = ""
        
        if created_articles:
            print(f"   - Found {len(created_articles)} Deep Dive articles created today.")
            created_articles_str = "## Today's Deep Dives (MUST FEATURE/LINK)\n"
            full_links_context_addendum = "\n\n## Today's Featured Articles (Priority Links)\n"
            for art in created_articles:
                 art_info = f"- Title: {art.get('title')}\n  URL: {art.get('article_url')}\n  Summary: {art.get('summary', '')[:100]}...\n"
                 created_articles_str += art_info
                 full_links_context_addendum += art_info
        
        # Add to extra_context for Analysis
        full_context = recent_events_str + "\n" + prev_context_str + "\n" + created_articles_str

        analysis = gemini.analyze_tech_impact(
            news, 
            market_data_str, 
            events_str, 
            region, 
            extra_context=full_context
        )
        
        if not analysis:
            print("Analysis failed.")
            continue
            
        # --- Map TechShift Analysis to DB Schema ---
        # DB expects: timeline_impact, evolution_phase, scenarios (json)
        # New Output: shift_score, shift_analysis {the_shift, catalyst, next_wall, signal}
        
        timeline_impact = analysis.get('shift_score', 50)
        # Evolution Phase -> "The Shift" textual summary
        evolution_phase = analysis.get('shift_analysis', {}).get('the_shift', 'N/A')
        # Scenarios -> Full Shift Analysis JSON
        scenarios_data = analysis.get('shift_analysis', {})
        
        print(f"Analysis Complete. Shift Score: {timeline_impact}")
        
        # 2.5 Internal Linking Suggestions
        internal_links_context = ""
        try:
            print(">> Fetching Internal Link Suggestions...")
            linker = InternalLinkSuggester(wp, gemini)
            candidates = linker.fetch_candidates(limit=50)
            
            if candidates:
                # Context: Region + The Shift
                scoring_context = f"Region: {region}\nShift: {evolution_phase}"
                
                relevant_links = linker.score_relevance(f"{region} Tech Impact Analysis", scoring_context, candidates)
                
                if relevant_links:
                    print(f"   Found {len(relevant_links)} relevant articles.")
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
            internal_links_context=internal_links_context + full_links_context_addendum
        )

        # SEO: Add Internal Link to Previous Analysis
        if prev_analysis and prev_analysis.get('article_url'):
            link_title = prev_analysis.get('article_title', '昨日の分析')
            link_url = prev_analysis.get('article_url')
            article_md += f"\n\n---\n**前日の分析**: [{link_title}]({link_url})"
            
        if args.dry_run:
            print("\n[Dry-Run] Generated Briefing (Excerpt):")
            print("-" * 40)
            print(article_md[:500] + "...\n(truncated)")
            print("-" * 40)
            
        if not article_md:
            print("Writing failed.")
            continue
            
        # 4. Save to DB & Local File
        analysis_record = {
            "date": today_str,
            "region": region,
            "timeline_impact": timeline_impact,
            "impact_label": "Shift", # Fixed label for TechShift
            "evolution_phase": evolution_phase[:255], # Truncate if needed for DB
            "hero_topic": analysis.get("hero_topic"),
            "scenarios": scenarios_data, # Save full shift analysis structure
            "ai_structured_summary": analysis.get("ai_structured_summary"),
            "full_briefing_md": article_md
        }
        
        if not args.dry_run:
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
        # (Title extraction logic remains same, simplified here for context match)
        title_line = lines[0].strip()
        if title_line.startswith("#"):
            title = title_line.lstrip("#").strip()
            content_body_md = "\n".join(lines[1:]).strip()
        elif "Title:" in title_line or "**Title**:" in title_line:
             parts = title_line.split("itle", 1)[1]
             if ":" in parts:
                 title = parts.split(":", 1)[1].strip(" *")
                 content_body_md = "\n".join(lines[1:]).strip()
             else:
                 title = f"Daily Briefing ({region}) - {today_str}"
                 content_body_md = article_md
        else:
             if len(title_line) < 100 and len(lines) > 1:
                 title = title_line.strip(" *#")
                 content_body_md = "\n".join(lines[1:]).strip()
             else:
                 title = f"Daily Briefing ({region}) - {today_str}"
                 content_body_md = article_md

        content_body_html = markdown.markdown(content_body_md, extensions=['tables', 'fenced_code', 'nl2br'])
        
        featured_media_id = None
        if not args.dry_run:
            try:
                print("Generating Feature Image...")
                img_prompt = gemini.generate_image_prompt(title, content_body_md[:2000], "daily-briefing")
                img_path = os.path.join(output_dir, f"{filename_base}.png")
                saved_img = gemini.generate_image(img_prompt, img_path)
                if saved_img:
                    media_res = wp.upload_media(saved_img, alt_text=title)
                    if media_res: featured_media_id = media_res.get('id')
            except Exception as e:
                print(f"Image generation failed: {e}")

        # Post Meta - Map TechShift keys to Custom Fields
        # Re-purpose the legacy scenario fields for the new structure
        shift_analysis = analysis.get("shift_analysis", {})
        
        post_meta = {
            "_techshift_impact": timeline_impact,
            "_techshift_phase": evolution_phase[:255],
            # Mapping Scenarios to Shift Structure for Frontend Display
            "_techshift_scenario_main": f"[The Shift] {shift_analysis.get('the_shift', '')}",
            "_techshift_scenario_bull": f"[Next Wall] {shift_analysis.get('next_wall', '')}",
            "_techshift_scenario_bear": f"[Signal] {shift_analysis.get('signal', '')}",
            "_ai_structured_summary": json.dumps(analysis.get("ai_structured_summary", {}), ensure_ascii=False)
        }

        if not args.dry_run:
            # Get Categories
            cat_id = wp.get_category_id("market-analysis")
            tag_ids = []
            reg_tag = wp.get_tag_id(region)
            if reg_tag: tag_ids.append(reg_tag)
            
            res = wp.create_post(
                title=title,
                content=content_body_html,
                status="publish",
                categories=[cat_id] if cat_id else [],
                tags=tag_ids,
                featured_media=featured_media_id,
                meta=post_meta
            )
            if res:
                print(f"Posted to WordPress (ID: {res.get('id')}). Status: publish")
                if res.get('link'):
                    analysis_record['article_url'] = res.get('link')
                    db.save_daily_analysis(analysis_record)
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
