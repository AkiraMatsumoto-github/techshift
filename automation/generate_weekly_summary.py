#!/usr/bin/env python3
import json
import os
import sys
import argparse
from datetime import datetime, timedelta
import re
import markdown

# Add parent directory to path to allow imports from automation package if run directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from automation.gemini_client import GeminiClient
    from automation.wp_client import WordPressClient
    from automation.seo_optimizer import SEOOptimizer
except ImportError:
    # Fallback for local run
    import gemini_client
    from gemini_client import GeminiClient
    from wp_client import WordPressClient
    from seo_optimizer import SEOOptimizer

def parse_article_content(text):
    """
    Parse the generated text to extract title and content.
    Extracts the first Markdown heading (# Title) as the title.
    """
    lines = text.split('\n')
    title = "Weekly Summary"
    content_start_index = 0
    
    for i, line in enumerate(lines):
        clean_line = line.strip()
        if clean_line.startswith('#'):
            title = clean_line.lstrip('#').strip()
            content_start_index = i + 1
            break
            
    content = "\n".join(lines[content_start_index:]).strip()
    return title, content

def main():
    parser = argparse.ArgumentParser(description="Generate Weekly Summary Article")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode (no posting)")
    parser.add_argument("--days", type=int, default=7, help="Days to look back (default: 7)")
    args = parser.parse_args()
    
    print(f"=== Starting Weekly Summary Generation (Lookback: {args.days} days) ===")
    
    # 1. Initialize Clients
    try:
        wp = WordPressClient()
        gemini = GeminiClient()
        print("Clients initialized.")
    except Exception as e:
        print(f"Error initializing clients: {e}")
        sys.exit(1)
        
    # 2. Fetch Articles from Last Week
    end_date = datetime.now()
    start_date = end_date - timedelta(days=args.days)
    start_date_iso = start_date.isoformat()
    
    print(f"Fetching posts published after: {start_date_iso}")
    
    posts = wp.get_posts(limit=20, after=start_date_iso, status="publish") # Fetch enough posts
    
    if not posts:
        print("No posts found in the last week. Exiting.")
        return
        
    print(f"Found {len(posts)} posts.")
    
    # 3. Format Context for Gemini
    context_summaries = []
    for post in posts:
        # Strip HTML from excerpt and content
        title = post['title']['rendered']
        link = post['link']
        
        # Simple HTML strip (regex)
        content_html = post['content']['rendered']
        clean_content = re.sub('<[^<]+?>', '', content_html).strip()
        # Reduce multiple newlines
        clean_content = re.sub(r'\n\s*\n', '\n', clean_content)
        
        context_summaries.append({
            "title": title,
            "url": link,
            "content": clean_content
        })
        print(f"- {title}")
        
    # Create context string
    context_str = ""
    for item in context_summaries:
        context_str += f"""
[Title] {item['title']}
[URL] {item['url']}
[Content] {item['content']}
-------------------
"""

    context_data = {
        "summary": context_str,
        "key_facts": [f"Total articles: {len(posts)}", f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"]
    }
    
    # 4. Generate Content
    print("\nGenerating weekly summary content...")
    keyword = f"Weekly LogiShift {start_date.strftime('%m/%d')}-{end_date.strftime('%m/%d')}"
    
    generated_text = gemini.generate_article(
        keyword=keyword,
        article_type="weekly_summary",
        context=context_data
    )
    
    if not generated_text:
        print("Failed to generate content.")
        sys.exit(1)
        
    title, content = parse_article_content(generated_text)
    print(f"\nGenerated Title: {title}")
    
    # 5. SEO Optimization (Meta Description)
    optimizer = SEOOptimizer()
    meta_desc = optimizer.generate_meta_description(title, content, keyword)
    print(f"Meta Description: {meta_desc}")
    
    # 6. Generate Hero Image
    print("\nGenerating hero image...")
    image_prompt = f"Abstract digital art representing logistics trends, summary, data visualization, connectivity, futuristic blue and white tones, high quality, 4k"
    
    output_dir = os.path.join(os.path.dirname(__file__), "generated_articles")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    date_str = datetime.now().strftime("%Y-%m-%d")
    image_filename = f"{date_str}_weekly_summary_hero.png"
    image_path = os.path.join(output_dir, image_filename)
    
    generated_image_path = gemini.generate_image(image_prompt, image_path, aspect_ratio="16:9")
    
    # Save local markdown file
    markdown_filename = f"{date_str}_weekly_summary.md"
    markdown_path = os.path.join(output_dir, markdown_filename)
    
    file_content = f"""---
title: {title}
date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
keyword: {keyword}
---

{content}
"""
    try:
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(file_content)
        print(f"Saved local copy to: {markdown_path}")
    except Exception as e:
        print(f"Warning: Failed to save local file: {e}")

    if args.dry_run:
        print("\n=== Dry Run Preview ===")
        print(f"Title: {title}")
        print(f"Content Preview:\n{content[:500]}...")
        if generated_image_path:
            print(f"Hero Image Generated: {image_path}")
        return
        
    # 7. Post to WordPress
    print("\nPosting to WordPress...")
    
    # Upload Image
    featured_media_id = None
    if generated_image_path and os.path.exists(generated_image_path):
        print(f"Uploading hero image: {image_filename}")
        media_result = wp.upload_media(generated_image_path, alt_text=title)
        if media_result and 'id' in media_result:
            featured_media_id = media_result['id']
    
    # Convert Markdown to HTML
    html_content = markdown.markdown(content, extensions=['extra', 'nl2br', 'tables'])
    
    # Create Post
    # Assuming category 'Weekly Report' exists or we just use default/uncategorized for now
    # Ideally find or create a category. For now let's leave uncategorized or use 'News' if available?
    # Let's search for a category "Weekly" or "News"
    cat_id = None
    weekly_cat = wp.get_category_id("weekly-report")
    if weekly_cat:
        cat_id = [weekly_cat]
    else:
        # Fallback to News
        news_cat = wp.get_category_id("news")
        if news_cat:
            cat_id = [news_cat]

    result = wp.create_post(
        title=title,
        content=html_content,
        status="publish",
        categories=cat_id,
        featured_media=featured_media_id,
        excerpt=meta_desc,
        meta={"_yoast_wpseo_metadesc": meta_desc} if meta_desc else None
    )
    
    if result:
        print(f"Successfully posted: {result.get('link')}")
    else:
        print("Failed to post to WordPress.")

if __name__ == "__main__":
    main()
