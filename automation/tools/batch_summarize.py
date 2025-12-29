#!/usr/bin/env python3
"""
Batch Summarizer for LogiShift

Iterates through all existing WordPress posts and generates structured AI summaries
if they are missing. Stores the result in the `_ai_structured_summary` custom field.
"""
import sys
import json
import time
from typing import List, Dict

try:
    from automation.gemini_client import GeminiClient
    from automation.wp_client import WordPressClient
except ImportError:
    from gemini_client import GeminiClient
    from wp_client import WordPressClient

def main():
    print("--- Batch Summarizer Started ---")
    
    # Initialize Clients
    try:
        gemini = GeminiClient()
        wp = WordPressClient()
    except Exception as e:
        print(f"Failed to initialize clients: {e}")
        sys.exit(1)
        
    # Get all published posts
    print("Fetching all posts from WordPress...")
    posts = wp.get_posts(limit=100, status="publish") # Adjust limit as needed
    print(f"Found {len(posts)} posts.")
    
    updated_count = 0
    skipped_count = 0
    
    for post in posts:
        post_id = post['id']
        title = post['title']['rendered']
        print(f"\nProcessing ID: {post_id} | Title: {title}")
        
        # Check if summary already exists
        # Note: We need a method to get meta fields. 
        # Since get_posts result usually doesn't include all meta unless specified,
        # we might need to rely on the fact that if we use wp.get_post(id), we get meta.
        # But for efficiency, we can just fetch meta or try to update blindly if we want to refresh.
        # Here we will try to fetch the specific post details to be sure, or check if we can get meta from the list.
        # Standard WP API 'posts' endpoint usually requires '?context=edit' to see meta, which requires auth.
        # Our WP client uses Basic Auth so it should be possible.
        
        # Let's inspect the post object keys to see if meta is there
        # If not, we fetch the single post with context=edit
        
        # Optimization: Just check if we should regenerate. 
        # For now, let's assume we want to backfill missing ones.
        
        try:
            # 1. Fetch full content and meta
            # We need the pure content for summarization (rendered content is HTML)
            content = post['content']['rendered']
            
            # Check for existing meta (we might need a dedicated call if not in list response)
            # For simplicity in this script, we'll generate and update. 
            # If you want to skip, we'd need to check the meta first.
            # Let's try to fetch meta first.
            
            # For this MVP, we will RE-GENERATE for all targets to ensure quality, 
            # unless a specific flag is set. 
            # Or we can check if 'meta' is in the post object.
            
            meta = post.get('meta', {})
            if 'ai_structured_summary' in meta and meta['ai_structured_summary']:
                print("  - Summary already exists. Skipping.")
                skipped_count += 1
                continue
            
            # 2. Generate Summary
            print("  - Generating structured summary...")
            # Strip HTML from content for token efficiency
            import re
            text_content = re.sub('<[^<]+?>', '', content)
            
            summary_json = gemini.generate_structured_summary(text_content)
            
            if summary_json:
                # 3. Update Post Meta
                print("  - Updating WordPress post meta...")
                
                # Convert JSON dict to string for storage
                meta_value = json.dumps(summary_json, ensure_ascii=False)
                
                # Update post
                # We need a method in WP Client to update meta.
                # Since create_post can update if ID is provided, or we can use a new method.
                # Let's see if we can use create_post or if we need to add update_post.
                # Actually, verify if wp.create_post supports updating by ID?
                # Looking at wp_client.py (I can't see it now, but standard logic):
                # Usually create_post makes a NEW post. 
                # We should add an 'update_post_meta' or usage of 'posts/<id>' endpoint.
                
                # For now, we will assume we need to use the requests object directly from wp client 
                # or add a method. Let's try to use a direct request here for flexibility.
                
                # Use api_url which corresponds to /wp/v2
                url = f"{wp.api_url}/posts/{post_id}"
                data = {
                    "meta": {
                        "ai_structured_summary": meta_value
                    }
                }
                
                # We need to manually add authentication since we are using requests directly via session if available, 
                # or just requests.post with auth. The wp_client instance has .auth tuple.
                import requests
                response = requests.post(url, json=data, auth=wp.auth)
                
                if response.status_code == 200:
                    print("  - Success: Meta updated.")
                    updated_count += 1
                else:
                    print(f"  - Failed to update meta: {response.status_code} {response.text}")
                    
            else:
                print("  - Failed to generate summary (Gemini returned None).")
                
            # Sleep to avoid rate limits
            time.sleep(2)
            
        except Exception as e:
            print(f"  - Error processing post {post_id}: {e}")

    print(f"\n--- Batch Complete ---")
    print(f"Updated: {updated_count}")
    print(f"Skipped: {skipped_count}")

if __name__ == "__main__":
    main()
