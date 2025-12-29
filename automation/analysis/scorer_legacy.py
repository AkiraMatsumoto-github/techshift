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
try:
    from automation.gemini_client import GeminiClient
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from automation.gemini_client import GeminiClient

# Editorial Persona and Scoring Criteria
# Editorial Persona and Scoring Criteria
SHARED_CRITERIA = """あなたは物流業界のDXエバンジェリスト「LogiShift編集長」です。
ターゲット読者である「物流倉庫の管理者」「3PL企業の経営層」にとって、以下の記事（または記事リスト）が有益かどうかを評価してください。

【ターゲットペルソナ】
- 属性: 物流現場の責任者、または経営層
- 課題: 2024年問題（人手不足）、コスト削減、アナログ管理からの脱却
- 関心: 業界動向、効率化手法、他社の事例、最新技術（自動化・ロボット）

【評価基準】（合計100点）
1. **物流業界への関連性と影響** (0-35点)
   - 物流、サプライチェーン、倉庫管理に関連する内容か？
   - 業界に影響を与える、または参考になる情報か？
   - 物流業界特有の文脈や課題に触れているか？

2. **DX・テクノロジー・効率化** (0-25点)
   - 最新技術（AI, IoT, ロボット, 自動倉庫など）の活用が含まれるか？
   - 効率化や改善の可能性がある取り組みか？
   - 海外の先進事例など、日本企業が参考にできる視点があるか？

3. **読者への実用性** (0-25点)
   - 読者が自社の業務に活かせるヒントがあるか？
   - 意思決定（ツール導入や戦略変更）の参考になる情報か？
   - 業界トレンドの理解に役立つか？

4. **情報の新鮮さ・話題性** (0-15点)
   - 最新の業界動向や注目すべきニュースか？
   - 大手企業や業界リーダーの動きか？
   - 市場トレンドや今後の展望に関する情報か？
"""

SCORING_PROMPT = SHARED_CRITERIA + """
【記事情報】
タイトル: {title}
要約: {summary}
ソース: {source}

【出力形式】
以下のJSON形式で出力してください:
{{
  "score": <0-100の整数>,
  "reasoning": "<評価理由をターゲット読者の視点で2-3文で簡潔に>",
  "relevance": "<high/medium/low>"
}}
"""

BATCH_SCORING_PROMPT = SHARED_CRITERIA + """
【記事リスト】
{articles_text}

【出力形式】
以下のJSON配列形式のみで出力してください。Markdownコードブロックは不要です。
[
  {{
    "id": <記事ID(整数)>,
    "score": <0-100の整数>,
    "reasoning": "<評価理由をターゲット読者の視点で2-3文で簡潔に>",
    "relevance": "<high/medium/low>"
  }}
]
"""

def score_article(article, model_name="gemini-3-pro-preview", client=None):
    """Score a single article using Gemini API."""
    
    if client is None:
        try:
            client = GeminiClient()
        except Exception as e:
            print(f"Error initializing GeminiClient: {e}", file=sys.stderr)
            return {
                "title": article.get("title"),
                "url": article.get("url"),
                "source": article.get("source"),
                "summary": article.get("summary", ""),
                "score": 0,
                "reasoning": f"Initialization Error: {str(e)}",
                "relevance": "error"
            }
    
    prompt = SCORING_PROMPT.format(
        title=article.get("title", ""),
        summary=article.get("summary", ""),
        source=article.get("source", "")
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
        
        return {
            "title": article.get("title"),
            "url": article.get("url"),
            "source": article.get("source"),
            "summary": article.get("summary", ""),
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
            "summary": article.get("summary", ""),
            "score": 0,
            "reasoning": f"Error: {str(e)}",
            "relevance": "error"
        }

def score_articles_batch(articles, model_name="gemini-3-pro-preview", client=None, start_id=0):
    """Score a batch of articles using Gemini API."""
    if not articles:
        return []

    if client is None:
        try:
            client = GeminiClient()
        except Exception as e:
            print(f"Error initializing GeminiClient: {e}", file=sys.stderr)
            return []

    articles_text = ""
    for i, article in enumerate(articles):
        # Assign a temporary ID for matching (relative to batch, but we could use start_id if needed for logging)
        # Using simple index 0..N for the batch prompt is usually safer for the LLM to understand.
        articles_text += f"\nID: {i}\nタイトル: {article.get('title')}\n要約: {article.get('summary', 'なし')}\nソース: {article.get('source')}\n---\n"

    prompt = BATCH_SCORING_PROMPT.format(articles_text=articles_text)

    try:
        response = client.generate_content(prompt, model=model_name)
        
        if not response:
            raise Exception("No response from Gemini API")

        result_text = response.text.strip()
        
        # Extract JSON from markdown code blocks if present
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        # Cleanup potential invalid JSON (sometimes ends with comma)
        if result_text.endswith(","):
             result_text = result_text[:-1]

        results = json.loads(result_text)
        
        if not isinstance(results, list):
            print(f"Error: Batch response is not a list: {results}", file=sys.stderr)
            return []

        # Map back to articles
        scored_articles = []
        for res in results:
            idx = res.get('id')
            if isinstance(idx, int) and 0 <= idx < len(articles):
                original = articles[idx]
                scored_articles.append({
                    "title": original.get("title"),
                    "url": original.get("url"),
                    "source": original.get("source"),
                    "summary": original.get("summary", ""),
                    "score": res.get("score", 0),
                    "reasoning": res.get("reasoning", ""),
                    "relevance": res.get("relevance", "low")
                })
        
        # Sort by index to maintain order? Or simply return what we got.
        # It's safer to return a list of same length if possible, filling missing with 0 scores?
        # For simplicity, let's just return what matched.
        return scored_articles
        
    except Exception as e:
        print(f"Error batch scoring: {e}", file=sys.stderr)
        return []

def main():
    parser = argparse.ArgumentParser(description="Score articles for relevance to LogiShift.")
    parser.add_argument("--input", type=str, help="Path to JSON file with articles (from collector.py)", required=True)
    parser.add_argument("--threshold", type=int, default=80, help="Minimum score to pass (default: 80)")
    parser.add_argument("--output", type=str, help="Output file for scored articles (optional)")
    parser.add_argument("--model", type=str, default="gemini-3-pro-preview", help="Gemini model to use")
    
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
