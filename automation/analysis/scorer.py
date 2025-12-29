#!/usr/bin/env python3
"""
Article Relevance Scorer for FinShift
Evaluates articles using Gemini API based on FinShift's persona (Market Strategist).
"""

import argparse
import json
import os
import sys
import textwrap

# Add parent directory to path to import GeminiClient
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from automation.gemini_client import GeminiClient

# Editorial Persona and Scoring Criteria for FinShift
SHARED_CRITERIA = """あなたは金融市場の戦略家「FinShiftチーフストラテジスト」です。
ターゲット読者である「スイングトレーダー（数日〜数週間の短期売買）」にとって、以下の記事が有益かどうかを評価してください。

【ターゲットペルソナ】
- 属性: 個人投資家（兼業）、スイングトレーダー
- 対象市場: 米国株、日本株、インド株、中国株、仮想通貨、コモディティ
- ニーズ: 「今日買うべきか、売るべきか」の判断材料、トレンドの転換点、予兆

【評価基準】（合計100点）
1. **価格への直接的インパクト** (0-40点)
    - そのニュースで株価・指数・レートが動くか？
    - 決算サプライズ、中央銀行の政策変更、大型M&A、規制強化などは高得点。
    - 単なる「解説記事」や「アナリストの個人的見解」は低得点。

2. **スイングトレード適性** (0-30点)
    - 数日〜数週間のトレンドを作り出す材料か？
    - デイトレ（数分）でも長期投資（数年）でもなく、「中間的な波」に乗れるか。

3. **地域・セクターの重要性** (0-20点)
    - FinShiftの注力領域（インド、中国、テック、半導体、Crypto）に関連するか？
    - グローバルな波及効果があるか（例: 米国の金利 -> 新興国通貨への影響）。

4. **具体性と新規性** (0-10点)
    - 具体的な数値（売上高、EPS、目標株価）が含まれているか。
    - 既知の事実の焼き直しではなく、新しい事実か。
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
  "reasoning": "<評価理由をトレーダー視点で2-3文で簡潔に>",
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
    "reasoning": "<評価理由>",
    "relevance": "<high/medium/low>"
  }}
]
"""

class ArticleScorer:
    def __init__(self):
        try:
            self.client = GeminiClient()
        except Exception as e:
            print(f"Error initializing GeminiClient: {e}", file=sys.stderr)
            self.client = None

    def score_article(self, article, model_name="gemini-3-pro-preview"):
        """Score a single article."""
        if not self.client:
            return {**article, "score": 0, "reasoning": "Client Init Failed"}

        prompt = SCORING_PROMPT.format(
            title=article.get("title", ""),
            summary=article.get("summary", ""),
            source=article.get("source", "")
        )

        try:
            response = self.client.generate_content(prompt, model=model_name)
            if not response: raise Exception("No response")
            
            text = self._clean_json(response.text)
            result = json.loads(text)
            
            # Merge result
            article['score'] = result.get('score', 0)
            article['reasoning'] = result.get('reasoning', '')
            article['relevance'] = result.get('relevance', 'low')
            return article
            
        except Exception as e:
            print(f"Scoring error {article.get('title')}: {e}")
            return {**article, "score": 0, "reasoning": f"Error: {e}"}

    def score_articles_batch(self, articles, model_name="gemini-3-pro-preview", start_id=0):
        """Score a batch of articles."""
        if not articles or not self.client:
            return []

        articles_text = ""
        for i, article in enumerate(articles):
            articles_text += f"\nID: {i}\nタイトル: {article.get('title')}\n要約: {article.get('summary', 'なし')}\nソース: {article.get('source')}\n---\n"

        prompt = BATCH_SCORING_PROMPT.format(articles_text=articles_text)

        try:
            response = self.client.generate_content(prompt, model=model_name)
            if not response: raise Exception("No response")
            
            text = self._clean_json(response.text)
            results = json.loads(text)
            
            scored_articles = []
            for res in results:
                idx = res.get('id')
                if isinstance(idx, int) and 0 <= idx < len(articles):
                    original = articles[idx].copy()
                    original['score'] = res.get('score', 0)
                    original['reasoning'] = res.get('reasoning', '')
                    original['relevance'] = res.get('relevance', 'low')
                    scored_articles.append(original)
            
            return scored_articles

        except Exception as e:
            print(f"Batch scoring error: {e}")
            return []

    def _clean_json(self, text):
        text = text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        if text.endswith(","): text = text[:-1]
        return text

# Legacy function aliases for compatibility if needed
def score_article(article, client=None):
    scorer = ArticleScorer()
    if client: scorer.client = client
    return scorer.score_article(article)

def score_articles_batch(articles, client=None, start_id=0):
    scorer = ArticleScorer()
    if client: scorer.client = client
    return scorer.score_articles_batch(articles, start_id=start_id)

if __name__ == "__main__":
    # Test
    scorer = ArticleScorer()
    test_article = {
        "title": "Fed likely to hold rates steady, signals patience",
        "source": "CNBC",
        "summary": "Powell emphasizes data dependency."
    }
    print(json.dumps(scorer.score_article(test_article), indent=2, ensure_ascii=False))
