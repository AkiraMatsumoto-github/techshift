#!/usr/bin/env python3
"""
SEO Optimizer for LogiShift Articles

Generates SEO metadata including:
- Meta descriptions (150-160 characters)
- OGP (Open Graph Protocol) tags
- JSON-LD structured data
"""

import re
import json
from datetime import datetime
try:
    from automation.gemini_client import GeminiClient
except ImportError:
    from gemini_client import GeminiClient


class SEOOptimizer:
    def __init__(self):
        self.gemini = GeminiClient()
    
    def generate_meta_description(self, title, content, keyword):
        """
        Generate a compelling meta description (150-160 chars).
        
        Args:
            title: Article title
            content: Article content (markdown)
            keyword: Target keyword
            
        Returns:
            str: Meta description
        """
        prompt = f"""以下の記事のメタディスクリプションを作成してください。

タイトル: {title}
キーワード: {keyword}
本文（抜粋）: {content[:500]}

【要件】
- 文字数: 150-160文字（厳守）
- 検索ユーザーのクリックを誘う魅力的な文章
- キーワードを自然に含める
- 記事の核心的な価値を伝える

メタディスクリプションのみを出力してください（前置きや説明は不要）。
"""
        
        try:
            response = self.gemini.model.generate_content(prompt)
            meta_desc = response.text.strip()
            
            # Ensure length is within bounds
            if len(meta_desc) > 160:
                meta_desc = meta_desc[:157] + "..."
            elif len(meta_desc) < 120:
                # Too short, try again with a more specific prompt
                meta_desc = self._generate_fallback_description(title, keyword)
            
            return meta_desc
        except Exception as e:
            print(f"Warning: Failed to generate meta description: {e}")
            return self._generate_fallback_description(title, keyword)
    
    def _generate_fallback_description(self, title, keyword):
        """Generate a simple fallback meta description."""
        return f"{keyword}について解説。{title}をわかりやすく説明します。物流DX・倉庫管理の最新情報をお届けします。"[:160]
    
    def create_json_ld(self, article_data):
        """
        Create JSON-LD structured data for the article.
        
        Args:
            article_data: Dict containing:
                - title: Article title
                - content: Article content (text)
                - url: Article URL
                - date_published: ISO 8601 date string
                - date_modified: ISO 8601 date string (optional)
                - image_url: Featured image URL (optional)
                
        Returns:
            str: JSON-LD as string
        """
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": article_data.get("title", ""),
            "author": {
                "@type": "Organization",
                "name": "LogiShift編集部"
            },
            "publisher": {
                "@type": "Organization",
                "name": "LogiShift",
                "logo": {
                    "@type": "ImageObject",
                    "url": article_data.get("site_logo", "https://logishift.example.com/logo.png")
                }
            },
            "datePublished": article_data.get("date_published", datetime.now().isoformat()),
            "dateModified": article_data.get("date_modified", article_data.get("date_published", datetime.now().isoformat())),
        }
        
        # Add URL if provided
        if article_data.get("url"):
            schema["url"] = article_data["url"]
            schema["mainEntityOfPage"] = {
                "@type": "WebPage",
                "@id": article_data["url"]
            }
        
        # Add image if provided
        if article_data.get("image_url"):
            schema["image"] = article_data["image_url"]
        
        # Add description if provided
        if article_data.get("description"):
            schema["description"] = article_data["description"]
        
        return json.dumps(schema, ensure_ascii=False, indent=2)
    
    def create_ogp_data(self, title, description, url=None, image_url=None):
        """
        Create OGP (Open Graph Protocol) metadata.
        
        Args:
            title: Article title
            description: Meta description
            url: Article URL (optional)
            image_url: Featured image URL (optional)
            
        Returns:
            dict: OGP metadata key-value pairs
        """
        ogp = {
            "og:type": "article",
            "og:title": title,
            "og:description": description,
            "og:site_name": "LogiShift",
            "og:locale": "ja_JP",
            
            # Twitter Card
            "twitter:card": "summary_large_image",
            "twitter:title": title,
            "twitter:description": description,
        }
        
        if url:
            ogp["og:url"] = url
        
        if image_url:
            ogp["og:image"] = image_url
            ogp["twitter:image"] = image_url
        
        return ogp
    
    def optimize_title(self, title):
        """
        Optimize title for SEO (ensure it's within 60 chars for SERPs).
        
        Args:
            title: Original title
            
        Returns:
            str: Optimized title
        """
        if len(title) <= 60:
            return title
        
        # If too long, try to shorten intelligently
        # Remove subtitle after colon or dash
        if "：" in title:
            main_title = title.split("：")[0]
            if len(main_title) >= 30:
                return main_title
        
        if "｜" in title:
            main_title = title.split("｜")[0]
            if len(main_title) >= 30:
                return main_title
        
        # If still too long, truncate
        return title[:57] + "..."


if __name__ == "__main__":
    # Test
    optimizer = SEOOptimizer()
    
    test_title = "物流DXを加速する自動倉庫とロボット：導入事例から学ぶ成功戦略"
    test_keyword = "自動倉庫 ロボット"
    test_content = "物流業界において、自動倉庫とロボットの導入は..."
    
    # Test meta description
    meta_desc = optimizer.generate_meta_description(test_title, test_content, test_keyword)
    print(f"Meta Description ({len(meta_desc)} chars):")
    print(meta_desc)
    print()
    
    # Test JSON-LD
    article_data = {
        "title": test_title,
        "url": "https://logishift.example.com/article",
        "date_published": "2025-11-27T10:00:00+09:00"
    }
    json_ld = optimizer.create_json_ld(article_data)
    print("JSON-LD:")
    print(json_ld)
