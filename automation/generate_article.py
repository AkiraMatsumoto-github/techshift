import argparse
import sys
import re
import markdown
from datetime import datetime
from automation.gemini_client import GeminiClient
from automation.wp_client import WordPressClient

def parse_article_content(text):
    """
    Parse the generated text to extract title and content.
    Assumes format:
    タイトル: [Title]
    
    [Content]
    """
    lines = text.split('\n')
    title = "無題"
    content_start_index = 0
    
    for i, line in enumerate(lines):
        if line.strip().startswith("タイトル:"):
            title = line.replace("タイトル:", "").strip()
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

def main():
    parser = argparse.ArgumentParser(description="Generate and post an article to WordPress.")
    parser.add_argument("--keyword", required=True, help="Keyword for the article")
    parser.add_argument("--dry-run", action="store_true", help="Generate content but do not post to WordPress")
    parser.add_argument("--schedule", help="Schedule post for future publication (format: 'YYYY-MM-DD HH:MM')")
    
    args = parser.parse_args()
    
    args = parser.parse_args()
    
    print(f"Starting article generation for keyword: {args.keyword}")
    
    # 1. Initialize Gemini Client
    try:
        gemini = GeminiClient()
    except Exception as e:
        print(f"Failed to initialize Gemini Client: {e}")
        sys.exit(1)
        
    # 2. Generate Content
    print("Generating content with Gemini...")
    generated_text = gemini.generate_article(args.keyword)
    
    if not generated_text:
        print("Failed to generate content.")
        sys.exit(1)
        
    title, content = parse_article_content(generated_text)
    
    print(f"Generated Title: {title}")
    print(f"Content Length: {len(content)} chars")
    
    if args.dry_run:
        print("Dry run mode. Skipping WordPress posting.")
        print("--- Preview ---")
        print(content[:500] + "...")
        return

    # 3. Post to WordPress
    print("Posting to WordPress...")
    try:
        wp = WordPressClient()
        # Convert Markdown to HTML
        html_content = markdown.markdown(content, extensions=['extra', 'nl2br'])
        
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
            date=schedule_date
        )
        
        if result:
            print(f"Successfully created draft post. ID: {result.get('id')}")
            print(f"Link: {result.get('link')}")
        else:
            print("Failed to create post.")
    except Exception as e:
        print(f"Failed to post to WordPress: {e}")

if __name__ == "__main__":
    main()
