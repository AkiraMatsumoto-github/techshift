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
from automation.collectors.url_reader import extract_content
from concurrent.futures import ThreadPoolExecutor, as_completed

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
            
            # 0.5 Fetch Full Content (Parallel)
            print(f"    Fetching full content for {len(batch)} articles...")
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_art = {executor.submit(extract_content, art['url'], art['source'], rss_summary=art.get('summary')): art for art in batch}
                for future in as_completed(future_to_art):
                    art = future_to_art[future]
                    try:
                        extracted = future.result()
                        # Update summary with full content if available
                        if extracted and extracted.get('content') and len(extracted.get('content')) > 200:
                            # Truncate to reasonable length for Gemini (e.g. 3000 chars)
                            # Enough for relevance check and analysis, but not too huge for DB
                            art['summary'] = extracted['content'][:4000]
                            # art['is_full_content'] = True # usage flag if needed
                    except Exception as exc:
                        print(f"    Content fetch failed for {art['title'][:20]}...: {exc}")

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
        # Consolidated Global Briefing Mode
        # Iterate all sectors to gather data, but produce ONE analysis/article
        target_regions = ["AI", "Quantum", "Green", "Robotics", "General"]
        primary_region_label = "Global"
    else:
        # Legacy/Single Region Mode
        target_regions = [args.region]
        primary_region_label = args.region
        
    db = DBClient()
    gemini = GeminiClient()
    wp = WordPressClient()
    today_str = datetime.now().strftime('%Y-%m-%d')

    # Data Collection Container
    all_news = []
    full_str_context = ""
    seen_urls = set()
    
    internal_links_context = ""

    print(f">> Consolidating News from: {target_regions}")

    # 1. Iterate Sub-regions to collect CONTEXT
    for region in target_regions:
        print(f"   [Collecting] {region}...")
        
        # Get News
        news = db.get_articles(region=region, hours=args.hours)
        if news:
            for n in news:
                # Deduplicate
                # Try url_hash, fallback to title if API not updated yet
                unique_key = n.get('url_hash') or n.get('title')
                
                if unique_key and unique_key not in seen_urls:
                    n['sub_region'] = region # Tag source region
                    all_news.append(n)
                    seen_urls.add(unique_key)
        
        # Get Deep Dives (Created Today)
        created_articles = db.get_todays_generated_articles(region=region)
        if created_articles:
             full_str_context += f"\n## {region} Deep Dives (Must Feature/Link)\n"
             for art in created_articles:
                 art_info = f"- [{region}] Title: {art.get('title')}\n  URL: {art.get('article_url')}\n  Summary: {art.get('summary', '')[:100]}...\n"
                 full_str_context += art_info

    # 2. Get High-Level Context (Prev Analysis from "Global" or generic)
    # Ideally checking previous "Global" analysis
    prev_analysis = db.get_latest_analysis_by_region(primary_region_label) # e.g. "Global"
    
    print(f"Context: {len(all_news)} articles total.")
    
    if not all_news:
        print("Skipping due to lack of data.")
        return # Exit function

    # 3. Analyze (Global Scope)
    print(f"Analyzing Market ({primary_region_label})...")
    
    # Format Previous Analysis Context
    prev_context_str = ""
    if prev_analysis:
        scenarios = prev_analysis.get('scenarios')
        if not isinstance(scenarios, dict):
            scenarios = {}
            
        main_cond = scenarios.get('main', {}).get('condition', 'N/A')
        prev_context_str = f"""
        ## Yesterday's Analysis Context (verification target)
        - Market Regime: {prev_analysis.get('market_regime')}
        - Main Scenario: {main_cond}
        """

    full_context = prev_context_str + "\n" + full_str_context

    # Call Generic Analysis Method with "Global" (or primary label)
    analysis = gemini.analyze_tech_impact(
        all_news, 
        primary_region_label, 
        extra_context=full_context
    )
    
    if not analysis:
        print("Analysis failed.")
        return

    print(f"Analysis Complete (Hero Topic: {analysis.get('hero_topic', 'N/A')})")
    
    # Extract variables for later use (default to None for DB NULL)
    evolution_phase = analysis.get('evolution_phase')
    timeline_impact = analysis.get('timeline_impact')
    scenarios_data = analysis.get('scenarios')

    # 4. Internal Linking Suggestions (Global Scope)
    try:
        print(">> Fetching Internal Link Suggestions...")
        linker = InternalLinkSuggester(wp, gemini)
        candidates = linker.fetch_candidates(limit=50)
        
        if candidates:
            # Context: Global + The Shift
            scoring_context = f"Region: {primary_region_label}\nShift: {evolution_phase}"
            
            relevant_links = linker.score_relevance(f"{primary_region_label} Tech Impact Analysis", scoring_context, candidates)
            
            if relevant_links:
                print(f"   Found {len(relevant_links)} relevant articles.")
                top_links = relevant_links[:5]
                for l in top_links:
                    internal_links_context += f"- ID: {l['id']} | Title: {l['title']} | URL: {l['url']}\n"
            else:
                print("   No relevant links found.")
    except Exception as e:
        print(f"   Internal Linking Warning: {e}")

    # 5. Write Briefing
    print("Writing Briefing...")
    # Add deep dive links to linking context so writer knows they are internal assets
    full_links_context_addendum = "\n\n## Today's Deep Dive Articles (Priority Links)\n" + full_str_context

    article_md = gemini.write_briefing(
        analysis, 
        primary_region_label, 
        context_news=all_news, 
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
        return
        
    # 6. Save to DB & Local File
    analysis_record = {
        "date": today_str,
        "region": primary_region_label,
        "timeline_impact": timeline_impact,
        "impact_label": "Shift",
        "evolution_phase": evolution_phase[:50] if evolution_phase else None,
        "hero_topic": analysis.get("hero_topic"),
        "scenarios": scenarios_data, 
        "ai_structured_summary": analysis.get("ai_structured_summary"),
        "full_briefing_md": article_md
    }
    
    if not args.dry_run:
        db.save_daily_analysis(analysis_record)
        print("Analysis & Article saved to DB.")
    
    # Save to local generated_articles
    output_dir = os.path.join(os.path.dirname(__file__), "generated_articles")
    os.makedirs(output_dir, exist_ok=True)
    filename_base = f"{today_str}_{primary_region_label}_briefing"
    md_path = os.path.join(output_dir, f"{filename_base}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(article_md)
    print(f"Article saved locally to: {md_path}")
    
    # 7. Post to WordPress
    print("Posting to WordPress...")
    lines = article_md.strip().split('\n')
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
                title = f"Daily Briefing ({primary_region_label}) - {today_str}"
                content_body_md = article_md
    else:
            if len(title_line) < 100 and len(lines) > 1:
                title = title_line.strip(" *#")
                content_body_md = "\n".join(lines[1:]).strip()
            else:
                title = f"Daily Briefing ({primary_region_label}) - {today_str}"
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
    post_meta = {
        "_ai_structured_summary": json.dumps(analysis.get("ai_structured_summary", {}), ensure_ascii=False)
    }

    if not args.dry_run:
        # Get Categories
        cat_id = wp.get_category_id("summary")
        tag_ids = []
        
        # Add 'Daily' tag
        daily_tag = wp.get_tag_id("daily")
        if daily_tag: tag_ids.append(daily_tag)
        
        reg_tag = wp.get_tag_id(primary_region_label) # "Global" tag might need to be created?
        if reg_tag: 
            tag_ids.append(reg_tag)
        else:
            # Maybe fall back to General if Global tag doesn't exist, or just skip
            pass
        
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
