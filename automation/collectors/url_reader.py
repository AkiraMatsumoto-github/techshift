#!/usr/bin/env python3
"""
URL Content Extractor for LogiShift

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
    # --- Global ---
    "yahoo_finance_top": {
        "content": "div.caas-body",
        "title": "h1",
        "author": "span.caas-author-byline-collapse-link",
    },
    "yahoo_jp_business": {
        "content": "div.article_body",
        "title": "h1.sc-bqyKva, h1.article_title",
        "author": ".article_body b",
    },
    "cnbc_world": {
        "content": "div.ArticleBody-articleBody",
        "title": "h1.ArticleHeader-headline",
        "author": "div.Author-authorName",
    },
    "wsj_markets": {
        "content": "div.article-content", # Often Paywalled, need fallback
        "title": "h1.wsj-article-headline",
        "author": "span.author-name",
    },
    
    # --- Asia Giants ---
    "36kr_china": {
        "content": "div.article-content, div.common-width-content",
        "title": "h1.article-title",
        "author": "a.author",
    },
    "sina_finance_focus": {
        "content": "div.article, div#artibody", 
        "title": "h1.main-title",
        "author": ".date-source .source",
    },
    "mint_top": {
        "content": "div.mainArea",
        "title": "h1.headline",
        "author": "span.author",
    },
    "mint_markets": {
        "content": "div.mainArea",
        "title": "h1.headline",
        "author": "span.author",
    },
    "economictimes": {
        "content": "div.artText",
        "title": "h1.artTitle",
        "author": "a.auth_name",
    },
    "antara_news_biz": {
        "content": "div.post-content",
        "title": "h1.post-title",
        "author": "span.text-muted",
    },
    "jakarta_globe": {
        "content": "div.content-body",
        "title": "h1.title-large",
        "author": "div.name-author",
    },

    # --- Crypto ---
    "coindesk": {
        "content": "div.at-text",
        "title": "h1.at-headline",
        "author": "div.at-authors",
    },
    "cointelegraph": {
        "content": "div.post-content",
        "title": "h1.post__title",
        "author": "div.post-meta__author-name",
    },
    "bitcoin_magazine": {
        "content": "div.m-detail--body",
        "title": "h1.m-detail--title",
        "author": "div.m-detail--author a",
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
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
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
