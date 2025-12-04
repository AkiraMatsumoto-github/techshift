#!/usr/bin/env python3
"""
Article Summarizer for LogiShift

Summarizes article content and extracts key facts using Gemini API.
Adds LogiShift perspective (DX Evangelist viewpoint).
"""

import os
import sys
import json
from dotenv import load_dotenv
try:
    from automation.gemini_client import GeminiClient
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from automation.gemini_client import GeminiClient

SUMMARIZATION_PROMPT = """あなたは物流業界のDXエバンジェリスト「LogiShift編集長」です。
以下の記事を要約し、LogiShift読者（物流担当者・経営層）向けに重要な情報を抽出してください。

【元記事】
タイトル: {title}
本文: {content}

【出力形式】
以下のJSON形式で出力してください:
{{
  "summary": "記事の要約（300文字程度）。読者が「何が起きたか」「なぜ重要か」を理解できるように。",
  "key_facts": [
    "重要な数値（例: コスト削減率、導入企業数など）",
    "固有名詞（企業名、製品名、技術名など）",
    "主要な主張や結論"
  ],
  "logishift_angle": "LogiShift視点のコメント（150文字程度）。DXエバンジェリストとして、この情報が日本の物流業界にどう影響するか、どう活かすべきかを語る。"
}}

【注意事項】
- key_factsは3〜5個程度に絞る
- 数値は正確に記載する
- logishift_angleは「ふーん」で終わらず、「やってみたい」と思わせる視点を
"""


def summarize_article(content: str, title: str, model_name: str = "gemini-2.5-flash") -> dict:
    """
    Summarize article content and extract key facts.
    
    Args:
        content: Article content
        title: Article title
        model_name: Gemini model to use
    
    Returns:
        Dictionary with keys: summary, key_facts, logishift_angle
    """
    print(f"Summarizing article: {title[:50]}...")
    
    # Truncate content if too long (max 10000 chars)
    if len(content) > 10000:
        print(f"Content too long ({len(content)} chars), truncating to 10000 chars")
        content = content[:10000] + "..."
    
    try:
        client = GeminiClient()
    except Exception as e:
        print(f"Error initializing GeminiClient: {e}")
        return {
            "summary": f"要約生成に失敗しました: {str(e)}",
            "key_facts": [],
            "logishift_angle": "分析できませんでした。"
        }
    
    prompt = SUMMARIZATION_PROMPT.format(
        title=title,
        content=content
    )
    
    try:
        # Use GeminiClient's generate_content which has retry logic
        response = client.generate_content(prompt, model=model_name)
        
        if not response:
            raise Exception("No response from Gemini API")
        
        result_text = response.text.strip()
        
        # Extract JSON from markdown code blocks if present
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(result_text)
        
        print(f"Summary: {result['summary'][:100]}...")
        print(f"Key facts: {len(result['key_facts'])} items")
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        print(f"Response text: {result_text}")
        return {
            "summary": f"要約生成に失敗しました: {str(e)}",
            "key_facts": [],
            "logishift_angle": "分析できませんでした。"
        }
    except Exception as e:
        print(f"Error summarizing article: {e}")
        return {
            "summary": f"要約生成に失敗しました: {str(e)}",
            "key_facts": [],
            "logishift_angle": "分析できませんでした。"
        }


def main():
    """Test summarization"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Summarize article content")
    parser.add_argument("--title", type=str, required=True, help="Article title")
    parser.add_argument("--content", type=str, required=True, help="Article content")
    parser.add_argument("--model", type=str, default="gemini-2.0-flash-exp", help="Gemini model")
    
    args = parser.parse_args()
    
    result = summarize_article(args.content, args.title, args.model)
    
    print("\n=== Summarization Result ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
