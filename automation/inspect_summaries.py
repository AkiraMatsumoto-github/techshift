#!/usr/bin/env python3
"""
Inspect AI Summaries

Fetches recent posts and displays their stored AI structured summaries.
"""
import sys
import json
import textwrap
try:
    from automation.wp_client import WordPressClient
except ImportError:
    from wp_client import WordPressClient

def main():
    print("--- Inspecting AI Structured Summaries ---\n")
    
    try:
        wp = WordPressClient()
    except Exception as e:
        print(f"Failed to initialize WP client: {e}")
        sys.exit(1)
        
    # Get recent posts with context=edit to ensure meta is returned
    import requests
    url = f"{wp.api_url}/posts"
    params = {
        "per_page": 20,
        "status": "publish,draft,future",
        "context": "edit" 
        # 'edit' context returns all fields including registered meta.
        # Note: Basic Auth is required for 'edit' context, which wp.auth provides.
    }
    
    try:
        response = requests.get(url, params=params, auth=wp.auth)
        response.raise_for_status()
        posts = response.json()
    except Exception as e:
        print(f"Failed to fetch posts: {e}")
        return

    if not posts:
        print("No posts found.")
        return

    count = 0
    for post in posts:
        post_id = post['id']
        title = post['title']['rendered']
        
        # safely get meta
        meta = post.get('meta', {})
        
        summary_raw = meta.get('ai_structured_summary')
        
        if summary_raw:
            count += 1
            print(f"[{post_id}] {title}")
            try:
                data = json.loads(summary_raw)
                # JSON loads successfully
                
                # Use simple slicing for display as textwrap fails on Japanese text (no spaces)
                summary_text = data.get('summary', '')
                display_summary = (summary_text[:100] + '...') if len(summary_text) > 100 else summary_text
                
                print(f"  Summary: {display_summary}")
                print(f"  Topics: {', '.join(data.get('key_topics', []))}")
                print(f"  Entities: {', '.join(data.get('entities', []))}")
                print("-" * 60)
            except json.JSONDecodeError:
                print("  [ERROR] Invalid JSON data in summary field.")
        else:
            print(f"[{post_id}] {title} - [NO SUMMARY DATA]")
            
    print(f"\nFound summaries for {count}/{len(posts)} posts.")

if __name__ == "__main__":
    main()
