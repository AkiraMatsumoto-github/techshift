#!/usr/bin/env python3
"""
Article Relevance Scorer for TechShift
Evaluates articles using Gemini API based on TechShift's persona (TechShift Lead Analyst).
"""

import argparse
import json
import os
import sys
import textwrap

# Add parent directory to path to import GeminiClient
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from automation.gemini_client import GeminiClient

# Editorial Persona and Scoring Criteria for TechShift
SHARED_CRITERIA = """あなたは「TechShift Lead Analyst」です。
未来の実践者 (Visionary Practitioner) と 未来への投資家 (Macro Investor) にとって、以下の記事が「未来のロードマップを変える重要なシグナル」かどうかを評価してください。

【ターゲットペルソナ】
- 属性: エンジニア、R&Dリーダー、VC、長期投資家
- 関心領域: AI (AGI, Multi-Agent), Quantum (PQC), Green Tech (Fusion, Battery)
- ニーズ: 「技術がいつ実用化されるか」「ロードマップがどう変わるか」「どの技術が勝つか」

【評価基準】（合計100点）
1. **Technological Breakthrough (技術的確変)** (0-40点)
    - 0->1の革新、または既存の限界を突破するスケーリングか？
    - 単なる「新製品発表」ではなく、「アーキテクチャの進化」や「科学的発見」か。
    - 論文、コード、ベンチマークなどの裏付けがあるか。

2. **Cross-Domain Synergy (領域横断シナジー)** (0-30点)
    - AIが科学（Green/Quantum）を加速させる、あるいはその逆のシナジーがあるか？
    - 単一領域に留まらない波及効果。

3. **Business/Social Implication (社会実装・コスト)** (0-30点)
    - コスト1/10化、規制の壁の突破、主要プレイヤーの戦略転換など。
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
  "reasoning": "<評価理由をアナリスト視点で2-3文で簡潔に。技術的確変、横断シナジー、社会実装・コストを中心に>",
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
    def __init__(self, client=None):
        if client:
             self.client = client
        else:
            try:
                self.client = GeminiClient()
            except Exception as e:
                print(f"Error initializing GeminiClient: {e}", file=sys.stderr)
                self.client = None

    def score_article(self, article, model_name="gemini-3-flash-preview"):
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

    def score_articles_batch(self, articles, model_name="gemini-3-flash-preview", start_id=0):
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
    scorer = ArticleScorer(client=client)
    return scorer.score_article(article)

def score_articles_batch(articles, client=None, start_id=0):
    scorer = ArticleScorer(client=client)
    return scorer.score_articles_batch(articles, start_id=start_id)

if __name__ == "__main__":
    # Test
    scorer = ArticleScorer()
    test_article = {
        "title": "Google DeepMind unveils localized scaling laws for AGI",
        "source": "TechCrunch AI",
        "summary": "New paper suggests training compute can be reduced by 50% with new architecture."
    }
    print(json.dumps(scorer.score_article(test_article), indent=2, ensure_ascii=False))
