#!/usr/bin/env python3
"""
Article Summarizer for FinShift

[USAGE ROLE]: Input Processing
This script is used to summarize **EXTERNAL** source articles (from Web, RSS, etc.) *BEFORE* generation.
The output (summary + key facts) is fed into the GeminiClient.generate_article() as 'context'.
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

SUMMARIZATION_PROMPT = """あなたはテクノロジーメディア「TechShift」のシニア・テックアナリストです。
以下の記事（外部ソース）を要約し、技術責任者や事業責任者にとって重要な「産業構造へのインパクト」を抽出してください。

【元記事】
タイトル: {title}
本文: {content}

【出力形式】
以下のJSON形式で出力してください:
{{
  "summary": "記事の要約（300文字程度）。事実関係（5W1H）を正確に。",
  "key_facts": [
    "技術性能（スペック、効率、速度、精度など）",
    "市場規模予測・導入社数・成長率",
    "具体的な企業名・製品名・技術規格"
  ],
  "techshift_view": "アナリストとしての見解（150文字程度）。この記事が「技術ロードマップ」や「産業構造」にどのような影響を与えるか（加速/破壊/停滞など）をコメントする。"
}}

【注意事項】
- key_factsは技術判断に直結する定量的数値を優先する
- techshift_viewは現象の解説だけでなく、具体的な未来予測（〜という技術が陳腐化する、〜の普及が3年モデル前倒しになる、など）を提示する
"""


def summarize_article(content: str, title: str, model_name: str = "gemini-3-flash-preview", client=None) -> dict:
    """
    Summarize article content and extract key facts for Context.
    
    Args:
        content: Article content
        title: Article title
        model_name: Gemini model to use
        client: GeminiClient instance (optional)
    
    Returns:
        Dictionary with keys: summary, key_facts, techshift_view
    """
    print(f"Summarizing article: {title[:50]}...")
    
    if client is None:
        try:
            client = GeminiClient()
        except Exception as e:
            print(f"Error initializing GeminiClient: {e}")
            return {
                "summary": f"要約生成に失敗しました: {str(e)}",
                "key_facts": [],
                "techshift_view": "分析できませんでした。"
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
            "techshift_view": "分析できませんでした。"
        }
    except Exception as e:
        print(f"Error summarizing article: {e}")
        return {
            "summary": f"要約生成に失敗しました: {str(e)}",
            "key_facts": [],
            "techshift_view": "分析できませんでした。"
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
