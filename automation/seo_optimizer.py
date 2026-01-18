#!/usr/bin/env python3
"""
SEO Optimizer for TechShift Articles

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
    def __init__(self, client=None):
        if client:
            self.gemini = client
        else:
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
本文（抜粋）: {content[:1000]}

【TechShiftのトーン＆マナー】
- 未来予測（Foresight）と技術的インパクト（Impact）を重視する。
- 投資家やビジョナリーに向けて、この記事が「なぜ重要か」を伝える。

【要件】
- 文字数: 150-160文字（厳守）
- 検索ユーザー（投資家・技術者）のクリックを誘う知的で魅力的な文章
- キーワードを自然に含める
- 「〜とは？」のような初心者向け解説ではなく、インサイトを強調する

メタディスクリプションのみを出力してください（前置きや説明は不要）。
"""
        
        try:
            response = self.gemini.generate_content(prompt)
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
        return f"{keyword}の最新技術動向と社会的インパクトを解説。{title}がもたらす未来の変革と投資シナリオについて、TechShift独自の視点でお届けします。"[:160]
    
    def create_json_ld(self, article_data, schema_type="Article"):
        """
        Create JSON-LD structured data for the article.
        
        Args:
            article_data: Dict containing article details
            schema_type: "Article" or "NewsArticle" (default: "Article")
            
        Returns:
            str: JSON-LD as string
        """
        schema = {
            "@context": "https://schema.org",
            "@type": schema_type,
            "headline": article_data.get("title", ""),
            "author": {
                "@type": "Organization",
                "name": "TechShift編集部"
            },
            "publisher": {
                "@type": "Organization",
                "name": "TechShift",
                "logo": {
                    "@type": "ImageObject",
                    "url": article_data.get("site_logo", "https://techshift.net/logo.png")
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
            "og:site_name": "TechShift",
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
    
    test_title = "TechShift: 全固体電池の量産化がもたらすエネルギー革命"
    test_keyword = "全固体電池 エネルギー"
    test_content = "トヨタと出光興産が全固体電池の量産パイロットラインを稼働。EV市場のゲームチェンジャーとなるか。TechShift独自の分析によるインパクト予測..."
    
    # Test meta description
    try:
        meta_desc = optimizer.generate_meta_description(test_title, test_content, test_keyword)
        print(f"Meta Description ({len(meta_desc)} chars):")
        print(meta_desc)
        print()
    except Exception as e:
        print(f"Meta generation failed (likely no API key in env): {e}")

    # Test JSON-LD
    article_data = {
        "title": test_title,
        "url": "https://techshift.net/article/solid-state-battery",
        "date_published": "2026-05-20T10:00:00+09:00"
    }
    json_ld = optimizer.create_json_ld(article_data)
    print("JSON-LD:")
    print(json_ld)
