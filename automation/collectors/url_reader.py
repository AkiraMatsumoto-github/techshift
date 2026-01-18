#!/usr/bin/env python3
"""
URL Content Extractor for FinShift

Extracts article content from URLs using BeautifulSoup.
Supports major logistics news sources with fallback to Gemini URL reading.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import sys

# Content selectors for each source
# Content selectors for FinShift sources
CONTENT_SELECTORS = {
    # --- TechShift Sources (Added) ---
    "mit_tech_review": {
        "content": ".piano__post_body, #content-body, .story-body, main",
        "title": "h1",
        "author": "span.byline__author, a.author",
    },
    "techcrunch_ai": {
        "content": "div.article-content, div.entry-content, article",
        "title": "h1.article__title",
        "author": "div.article__byline",
    },
    "techcrunch_transport": {
        "content": "div.article-content, div.entry-content, article",
        "title": "h1.article__title",
        "author": "div.article__byline",
    },
    "wired_science": {
        "content": "div.body__content, article.article, main",
        "title": "h1.content-header__row",
        "author": "span.byline__name",
    },
    "venturebeat_ai": {
        "content": "div.article-content, div.entry-content, article",
        "title": "h1.article-title",
        "author": "span.author",
    },
    "nvidia_blog": {
        "content": "div.entry-content",
        "title": "h1.entry-title",
        "author": "span.entry-author",
    },
    "google_ai": {
        "content": "div.post-content, div.entry-content",
        "title": "h1",
        "author": "span.author",
    },
    "microsoft_ai": {
        "content": "div.entry-content, div.post-content",
        "title": "h1.entry-title",
        "author": "a.author",
    },
    "huggingface_blog": {
        "content": "div.prose, main article",
        "title": "h1",
        "author": "div.author",
    },
    "quantum_daily": {
        "content": "div.entry-content, div.td-post-content, main, article",
        "title": "h1.entry-title, h1",
        "author": "div.td-post-author-name, span.author",
    },
    "cleantechnica": {
        "content": "div.entry-content, article, main",
        "title": "h1.entry-title",
        "author": "div.entry-meta",
    },
    "energy_storage_news": {
        "content": "div.elementor-widget-theme-post-content, div.elementor-widget-text-editor, article",
        "title": "h1.elementor-heading-title, h1",
        "author": "span.elementor-icon-list-text, span.author",
    },
    "ieee_spectrum_energy": {
        "content": "div.article-body, section.article-content",
        "title": "h1.widget__headline",
        "author": "div.widget__author",
    },
    "y_combinator": {
        "content": "div.post-content, div.entry-content, article, div.content",
        "title": "h1.entry-title, h1",
        "author": "span.author, a.author",
    },
    "therobotreport": {
        "content": "div.entry-content, article, div.post-content",
        "title": "h1.entry-title",
        "author": "span.author a",
    },
    "electrek": {
        "content": "div.entry-content, div.post-content, article, main",
        "title": "h1.entry-title, h1.post-title",
        "author": "div.author-name, span.author",
    },
}


def extract_content(url: str, source: str, rss_summary: Optional[str] = None) -> Dict[str, str]:
    """
    Extract article content from URL.
    
    Args:
        url: Article URL
        source: Source name (e.g., 'techcrunch', 'lnews')
        rss_summary: Optional RSS summary to use as fallback
    
    Returns:
        Dictionary with keys: title, content, author, url, is_fallback
    """
    print(f"Extracting content from {source}: {url}")
    
    # Get selectors for this source
    selectors = CONTENT_SELECTORS.get(source)
    
    if not selectors:
        print(f"Warning: No selectors defined for source '{source}', using generic extraction")
        selectors = {
            "content": "article, div.content, div.post-content, div.entry-content",
            "title": "h1",
            "author": "span.author, a.author, span.author-name",
        }
    
    try:
        # Fetch URL
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,ja;q=0.8,zh-CN;q=0.7,zh;q=0.6,id;q=0.5,hi;q=0.4",
            "Referer": "https://www.google.com/",
            "Upgrade-Insecure-Requests": "1",
        }
        response = requests.get(url, headers=headers, timeout=10)
        # response.raise_for_status() # Don't raise immediately, handle 403/404 with fallback

        if response.status_code != 200:
             print(f"Error fetching URL: Status {response.status_code}")
             if rss_summary:
                 print("Using RSS summary fallback.")
                 return {
                     "title": "RSS Summary (Fetch Error)",
                     "content": rss_summary,
                     "author": "Unknown",
                     "url": url,
                     "is_fallback": True
                 }
             raise requests.RequestException(f"Status {response.status_code}")
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Extract title
        title_elem = soup.select_one(selectors["title"])
        title = title_elem.get_text(strip=True) if title_elem else "No Title"
        
        # Extract content
        content_elem = soup.select_one(selectors["content"])
        if content_elem:
            # Remove script and style tags
            for tag in content_elem.find_all(['script', 'style', 'nav', 'aside', 'iframe', 'ads']):
                tag.decompose()
            content = content_elem.get_text(separator='\n', strip=True)
        else:
             content = None # Explicitly set to None for check below
        
        # If content selector found nothing or text is empty, try fallback
        if not content:
            print(f"Warning: Content selector '{selectors['content']}' yielded empty result.")
            if rss_summary:
                 print("Using RSS summary fallback.")
                 return {
                     "title": title,
                     "content": rss_summary, # Use RSS summary
                     "author": "Unknown",
                     "url": url,
                     "is_fallback": True
                 }
            
            # Last resort fallback: get all paragraphs
            print("Using all <p> tags fallback.")
            paragraphs = soup.find_all('p')
            content = '\n'.join([p.get_text(strip=True) for p in paragraphs])
        
        # Extract author
        author_elem = soup.select_one(selectors["author"])
        author = author_elem.get_text(strip=True) if author_elem else "Unknown"
        
        result = {
            "title": title,
            "content": content,
            "author": author,
            "url": url,
            "is_fallback": False
        }
        
        print(f"Successfully extracted: {len(content)} chars")
        return result
        
    except Exception as e:
        print(f"Error extracting content: {e}")
        if rss_summary:
             print("Using RSS summary fallback due to exception.")
             return {
                 "title": "RSS Summary (Exception)",
                 "content": rss_summary,
                 "author": "Unknown",
                 "url": url,
                 "is_fallback": True
             }
        return {
            "title": "Error",
            "content": f"Failed to fetch content: {str(e)}",
            "author": "Unknown",
            "url": url,
            "is_fallback": True # Treated as fallback/error
        }


def main():
    """Test URL extraction"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract content from URL")
    parser.add_argument("--url", type=str, required=True, help="URL to extract")
    parser.add_argument("--source", type=str, required=True, help="Source name")
    
    args = parser.parse_args()
    
    result = extract_content(args.url, args.source)
    
    print("\n=== Extraction Result ===")
    print(f"Title: {result['title']}")
    print(f"Author: {result['author']}")
    print(f"Content Length: {len(result['content'])} chars")
    print(f"\nContent Preview:\n{result['content'][:500]}...")


if __name__ == "__main__":
    main()
