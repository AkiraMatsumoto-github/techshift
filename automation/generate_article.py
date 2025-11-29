import argparse
import sys
import re
import markdown
from datetime import datetime
try:
    from automation.gemini_client import GeminiClient
    from automation.wp_client import WordPressClient
    from automation.classifier import ArticleClassifier
except ImportError:
    import gemini_client
    from gemini_client import GeminiClient
    from wp_client import WordPressClient
    from classifier import ArticleClassifier

def parse_article_content(text):
    """
    Parse the generated text to extract title and content.
    Extracts the first Markdown heading (# Title) as the title.
    """
    lines = text.split('\n')
    title = "無題"
    content_start_index = 0
    
    for i, line in enumerate(lines):
        clean_line = line.strip()
        
        # Check if line starts with # (Markdown heading)
        if clean_line.startswith('#'):
            # Extract title by removing # and whitespace
            title = clean_line.lstrip('#').strip()
            content_start_index = i + 1
            break
            
    content = "\n".join(lines[content_start_index:]).strip()
    return title, content

def parse_schedule_date(schedule_str):
    """
    Parse schedule string to ISO 8601 format for WordPress.
    Accepts formats:
    - "2025-11-27 10:00"
    - "2025-11-27 10:00:00"
    Returns ISO 8601 format: "2025-11-27T10:00:00"
    """
    try:
        # Try parsing with seconds
        dt = datetime.strptime(schedule_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            # Try parsing without seconds
            dt = datetime.strptime(schedule_str, "%Y-%m-%d %H:%M")
        except ValueError:
            raise ValueError(f"Invalid date format: {schedule_str}. Use 'YYYY-MM-DD HH:MM' or 'YYYY-MM-DD HH:MM:SS'")
    
    # Convert to ISO 8601 format
    return dt.strftime("%Y-%m-%dT%H:%M:%S")

def save_to_file(title, content, keyword):
    import os
    
    output_dir = os.path.join(os.path.dirname(__file__), "generated_articles")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    date_str = datetime.now().strftime("%Y-%m-%d")
    safe_keyword = re.sub(r'[\\/*?:\"<>| ]', '_', keyword)
    filename = f"{date_str}_{safe_keyword}.md"
    filepath = os.path.join(output_dir, filename)
    
    file_content = f"""---
title: {title}
date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
keyword: {keyword}
---

{content}
"""
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(file_content)
        print(f"Saved local copy to: {filepath}")
    except Exception as e:
        print(f"Warning: Failed to save local file: {e}")

def main():
    parser = argparse.ArgumentParser(description="Generate and post an article to WordPress.")
    parser.add_argument('--keyword', type=str, required=True, help='Keyword for the article')
    parser.add_argument('--type', type=str, default='know', choices=['know', 'buy', 'do', 'news', 'global'], help='Article type')
    parser.add_argument('--dry-run', action='store_true', help='Generate content but do not post to WordPress')
    parser.add_argument('--schedule', type=str, help='Schedule date (YYYY-MM-DD HH:MM or YYYY-MM-DD HH:MM:SS)')
    
    args = parser.parse_args()
    
    # Define output directory
    import os
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "generated_articles")
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    print(f"Starting article generation for keyword: {args.keyword} (Type: {args.type})")
    
    # 1. Initialize Clients
    try:
        gemini = GeminiClient()
        if not args.dry_run:
            wp = WordPressClient()
        else:
            wp = None
    except Exception as e:
        print(f"Failed to initialize Gemini Client: {e}")
        sys.exit(1)
        
    # 2. Generate Content
    print("Generating content with Gemini...")
    generated_text = gemini.generate_article(args.keyword, article_type=args.type)
    
    if not generated_text:
        print("Failed to generate content.")
        sys.exit(1)
        
    title, content = parse_article_content(generated_text)
    
    print(f"Generated Title: {title}")
    print(f"Content Length: {len(content)} chars")
    
    # 3. Generate SEO Metadata
    print("Generating SEO metadata...")
    try:
        from seo_optimizer import SEOOptimizer
    except ImportError:
        from automation.seo_optimizer import SEOOptimizer
    
    # 2.5 Generate Hero Image
    # if gemini.use_vertex: # Allow for both Vertex and API Key
    print("Generating hero image...")
    image_prompt = f"Futuristic and professional visualization of {args.keyword} in a logistics warehouse context. High quality, photorealistic, 4k."
    
    import os
    output_dir = os.path.join(os.path.dirname(__file__), "generated_articles")
    date_str = datetime.now().strftime("%Y-%m-%d")
    safe_keyword = re.sub(r'[\\/*?:\"<>| ]', '_', args.keyword)
    image_filename = f"{date_str}_{safe_keyword}_hero.png"
    image_path = os.path.join(output_dir, image_filename)
    
    generated_image_path = gemini.generate_image(image_prompt, image_path, aspect_ratio="16:9")
    
    if generated_image_path:
        # Insert image at the top of the content
        image_markdown = f"![{args.keyword} Image]({image_filename})\n\n"
        content = image_markdown + content
        # Re-save the file with the image
        save_to_file(title, content, args.keyword)
        print(f"Article updated with hero image: {image_filename}")
    
    # 3. Classify Content
    print("Classifying content...")
    category_id = None
    tag_ids = []
    
    try:
        classifier = ArticleClassifier()
        classification = classifier.classify_article(title, content[:1000])
        print(f"Classification Result: {classification}")
        
        # Resolve IDs if not dry-run (or even in dry-run if we want to test lookup, but let's skip for speed)
        # Actually, let's resolve them to verify logic if we have a client.
        # But we initialize wp_client later. Let's initialize it earlier if needed.
        # Or just do it in the posting block.
        # Let's do it here if we want to print them in dry run?
        # No, let's keep it simple. Just pass the classification dict to the posting block?
        # No, create_post expects IDs.
        # Let's initialize WP client here if we are going to post.
        
    except Exception as e:
        print(f"Classification failed: {e}")
        classification = {}

    if args.dry_run:
        print("Dry run mode. Skipping WordPress posting.")
        print("--- Preview ---")
        print(content[:500] + "...")
        return

    # 5. Post to WordPress
    print("Posting to WordPress...")
    try:
        wp = WordPressClient()
        
        # Resolve Categories and Tags
        if classification:
            cat_slug = classification.get("category")
            if cat_slug:
                cat_id = wp.get_category_id(cat_slug)
                if cat_id:
                    category_id = [cat_id]
                    print(f"Resolved Category: {cat_slug} -> {cat_id}")
            
            t_slugs = classification.get("industry_tags", []) + classification.get("theme_tags", [])
            for t_slug in t_slugs:
                t_id = wp.get_tag_id(t_slug)
                if t_id:
                    tag_ids.append(t_id)
            print(f"Resolved Tags: {t_slugs} -> {tag_ids}")

        # Upload hero image to WordPress if it exists
        image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        image_matches = re.findall(image_pattern, content)
        
        for alt_text, image_filename in image_matches:
            # Check if it's a local file (not a URL)
            if not image_filename.startswith('http'):
                image_path = os.path.join(OUTPUT_DIR, image_filename)
                if os.path.exists(image_path):
                    print(f"Uploading image to WordPress: {image_filename}")
                    media_result = wp.upload_media(image_path, alt_text=alt_text or keyword)
                    if media_result and 'source_url' in media_result:
                        # Replace local path with WordPress URL
                        content = content.replace(f']({image_filename})', f']({media_result["source_url"]})')
                        print(f"Image uploaded successfully: {media_result['source_url']}")
                    else:
                        print(f"Failed to upload image: {image_filename}")

        # Convert Markdown to HTML
        html_content = markdown.markdown(content, extensions=['extra', 'nl2br', 'tables'])
        
        # Determine status and date
        if args.schedule:
            try:
                schedule_date = parse_schedule_date(args.schedule)
                status = "future"
                print(f"Scheduling post for: {schedule_date}")
            except ValueError as e:
                print(f"Error: {e}")
                sys.exit(1)
        else:
            schedule_date = None
            status = "draft"
        
        result = wp.create_post(
            title=title, 
            content=html_content, 
            status=status,
            date=schedule_date,
            categories=category_id,
            tags=tag_ids
        )
        
        if result:
            print(f"Successfully created draft post. ID: {result.get('id')}")
            print(f"Link: {result.get('link')}")
        else:
            print("Failed to create post.")
    except Exception as e:
        print(f"Failed to post to WordPress: {e}")

def save_to_file(title, content, keyword):
    """Save the article to a local markdown file."""
    import os
    
    # Create directory if not exists
    output_dir = os.path.join(os.path.dirname(__file__), "generated_articles")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Format filename: YYYY-MM-DD_keyword.md
    date_str = datetime.now().strftime("%Y-%m-%d")
    safe_keyword = re.sub(r'[\\/*?:"<>| ]', '_', keyword)
    filename = f"{date_str}_{safe_keyword}.md"
    filepath = os.path.join(output_dir, filename)
    
    # Add frontmatter
    file_content = f"""---
title: {title}
date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
keyword: {keyword}
---

{content}
"""
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(file_content)
        print(f"Saved local copy to: {filepath}")
    except Exception as e:
        print(f"Warning: Failed to save local file: {e}")

if __name__ == "__main__":
    main()
