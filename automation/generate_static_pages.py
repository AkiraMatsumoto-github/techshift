#!/usr/bin/env python3
"""
Static Pages Generator for LogiShift

Generate and publish static pages (privacy policy, about, contact) using Gemini API.
"""

import os
import sys
import argparse
import markdown
from gemini_client import GeminiClient
from wp_client import WordPressClient

# Page configurations
PAGE_CONFIGS = {
    "privacy": {
        "title": "プライバシーポリシー",
        "slug": "privacy-policy",
        "type": "privacy"
    },
    "about": {
        "title": "運営者情報",
        "slug": "about",
        "type": "about"
    },
    "contact": {
        "title": "お問い合わせ",
        "slug": "contact",
        "type": "contact"
    }
}

def generate_page(gemini_client, page_type):
    """
    Generate page content using Gemini API.
    
    Args:
        gemini_client: GeminiClient instance
        page_type: Type of page (privacy, about, contact)
    
    Returns:
        Tuple of (title, markdown_content)
    """
    print(f"\n{'='*60}")
    print(f"Generating {page_type} page...")
    print(f"{'='*60}\n")
    
    config = PAGE_CONFIGS[page_type]
    
    # Generate content with Gemini
    markdown_content = gemini_client.generate_static_page(config["type"])
    
    if not markdown_content:
        print(f"❌ Failed to generate {page_type} page")
        return None, None
    
    print(f"✅ Generated {page_type} page ({len(markdown_content)} characters)")
    
    return config["title"], markdown_content

def publish_page(wp_client, title, markdown_content, slug, dry_run=False):
    """
    Publish page to WordPress.
    
    Args:
        wp_client: WordPressClient instance
        title: Page title
        markdown_content: Page content in Markdown
        slug: URL slug
        dry_run: If True, only preview without publishing
    
    Returns:
        True if successful, False otherwise
    """
    # Convert Markdown to HTML
    html_content = markdown.markdown(
        markdown_content,
        extensions=['extra', 'nl2br', 'sane_lists']
    )
    
    if dry_run:
        print(f"\n{'='*60}")
        print(f"DRY RUN - Preview of {title}")
        print(f"{'='*60}\n")
        print(f"Title: {title}")
        print(f"Slug: {slug}")
        print(f"\nMarkdown Content (first 500 chars):")
        print(markdown_content[:500])
        print("\n...")
        print(f"\nHTML Content (first 500 chars):")
        print(html_content[:500])
        print("\n...")
        return True
    
    # Publish to WordPress
    print(f"\nPublishing {title} to WordPress...")
    result = wp_client.create_page(
        title=title,
        content=html_content,
        status="publish",
        slug=slug
    )
    
    if result:
        page_url = result.get('link', f"/{slug}/")
        print(f"✅ Successfully published: {page_url}")
        return True
    else:
        print(f"❌ Failed to publish {title}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Generate and publish static pages for LogiShift"
    )
    parser.add_argument(
        "--page",
        choices=["privacy", "about", "contact"],
        help="Generate a specific page"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate all pages"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview only, do not publish"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.page and not args.all:
        parser.error("Please specify --page or --all")
    
    # Initialize clients
    try:
        print("Initializing Gemini API client...")
        gemini_client = GeminiClient()
        print("✅ Gemini API client initialized")
        
        print("Initializing WordPress API client...")
        wp_client = WordPressClient()
        print("✅ WordPress API client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize clients: {e}")
        sys.exit(1)
    
    # Determine which pages to generate
    if args.all:
        pages_to_generate = ["privacy", "about", "contact"]
    else:
        pages_to_generate = [args.page]
    
    # Generate and publish pages
    success_count = 0
    fail_count = 0
    
    for page_type in pages_to_generate:
        try:
            # Generate content
            title, markdown_content = generate_page(gemini_client, page_type)
            
            if not markdown_content:
                fail_count += 1
                continue
            
            # Publish to WordPress
            config = PAGE_CONFIGS[page_type]
            success = publish_page(
                wp_client,
                title,
                markdown_content,
                config["slug"],
                dry_run=args.dry_run
            )
            
            if success:
                success_count += 1
            else:
                fail_count += 1
                
        except Exception as e:
            print(f"❌ Error processing {page_type} page: {e}")
            import traceback
            traceback.print_exc()
            fail_count += 1
    
    # Summary
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {fail_count}")
    
    if args.dry_run:
        print("\n⚠️  DRY RUN mode - No pages were published")
    
    sys.exit(0 if fail_count == 0 else 1)

if __name__ == "__main__":
    main()
