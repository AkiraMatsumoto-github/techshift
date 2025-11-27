#!/usr/bin/env python3
"""
Article Relevance Scorer for LogiShift

Evaluates articles using Gemini API based on LogiShift's editorial persona:
- DX Evangelist perspective
- Focus on cost reduction and feasibility
- Future potential evaluation
"""

import argparse
import json
import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found in .env file")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)

# Editorial Persona and Scoring Criteria
SCORING_PROMPT = """あなたは物流業界のDXエバンジェリストです。以下の記事が「LogiShift」というメディアで取り上げる価値があるかを評価してください。

【評価基準】
1. **物流業界へのインパクト** (0-40点)
   - 物流、サプライチェーン、倉庫管理に直接関連するか
   - 業界の課題解決に貢献するか

2. **DX/テクノロジー要素** (0-30点)
   - 最新技術（AI, IoT, ロボティクス, クラウドなど）が含まれるか
   - イノベーティブな要素があるか

3. **読者への有益性** (0-30点)
   - 経営層や現場管理者が意思決定に活用できる情報か
   - コスト削減や効率化のヒントになるか
   - 実現可能性があるか、または将来性があるか

【記事情報】
タイトル: {title}
要約: {summary}
ソース: {source}

【出力形式】
以下のJSON形式で出力してください:
{{
  "score": <0-100の整数>,
  "reasoning": "<評価理由を2-3文で簡潔に>",
  "relevance": "<high/medium/low>"
}}
"""

def score_article(article, model_name="gemini-2.5-flash"):
    """Score a single article using Gemini API."""
    
    model = genai.GenerativeModel(model_name)
    
    prompt = SCORING_PROMPT.format(
        title=article.get("title", ""),
        summary=article.get("summary", ""),
        source=article.get("source", "")
    )
    
    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Extract JSON from markdown code blocks if present
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(result_text)
        
        return {
            "title": article.get("title"),
            "url": article.get("url"),
            "source": article.get("source"),
            "score": result.get("score", 0),
            "reasoning": result.get("reasoning", ""),
            "relevance": result.get("relevance", "low")
        }
        
    except Exception as e:
        print(f"Error scoring article '{article.get('title', 'Unknown')}': {e}", file=sys.stderr)
        return {
            "title": article.get("title"),
            "url": article.get("url"),
            "source": article.get("source"),
            "score": 0,
            "reasoning": f"Error: {str(e)}",
            "relevance": "error"
        }

def main():
    parser = argparse.ArgumentParser(description="Score articles for relevance to LogiShift.")
    parser.add_argument("--input", type=str, help="Path to JSON file with articles (from collector.py)", required=True)
    parser.add_argument("--threshold", type=int, default=80, help="Minimum score to pass (default: 80)")
    parser.add_argument("--output", type=str, help="Output file for scored articles (optional)")
    parser.add_argument("--model", type=str, default="gemini-2.5-flash", help="Gemini model to use")
    
    args = parser.parse_args()
    
    # Load articles
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            articles = json.load(f)
    except Exception as e:
        print(f"Error loading input file: {e}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Scoring {len(articles)} articles using {args.model}...")
    
    scored_articles = []
    for i, article in enumerate(articles, 1):
        print(f"[{i}/{len(articles)}] Scoring: {article.get('title', 'Unknown')[:60]}...")
        scored = score_article(article, args.model)
        scored_articles.append(scored)
    
    # Filter by threshold
    high_score_articles = [a for a in scored_articles if a["score"] >= args.threshold]
    
    print(f"\n{'='*60}")
    print(f"Scoring complete!")
    print(f"Total articles: {len(articles)}")
    print(f"High-score articles (>={args.threshold}): {len(high_score_articles)}")
    print(f"{'='*60}\n")
    
    # Display high-score articles
    if high_score_articles:
        print("High-score articles:")
        for article in sorted(high_score_articles, key=lambda x: x["score"], reverse=True):
            print(f"\n[{article['score']}点] {article['title']}")
            print(f"  URL: {article['url']}")
            print(f"  理由: {article['reasoning']}")
    
    # Save output if specified
    if args.output:
        output_data = {
            "threshold": args.threshold,
            "total": len(articles),
            "high_score_count": len(high_score_articles),
            "articles": scored_articles,
            "high_score_articles": high_score_articles
        }
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {args.output}")

if __name__ == "__main__":
    main()
