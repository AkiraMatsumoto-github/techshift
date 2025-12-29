import json
import re
import sys
import os

# Add parent directory to path to import GeminiClient
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from automation.gemini_client import GeminiClient
except ImportError:
    # Use relative import if running from automation dir
    from gemini_client import GeminiClient

class ArticleClassifier:
    def __init__(self):
        self.gemini = GeminiClient()
        
    def classify_article(self, title, content_summary):
        """
        Classify an article into FinShift Category and Tags.
        
        Returns:
            dict: {
                "category": "slug",
                "tags": ["slug1", "slug2"]
            }
        """
        
        prompt = f"""
        あなたは金融メディア「FinShift」の編集者です。
        以下の記事タイトルと概要を分析し、最も適切な「カテゴリ（1つ）」と「タグ（複数可）」を選択してください。
        
        ## 記事情報
        タイトル: {title}
        概要: {content_summary}
        
        ## 1. カテゴリ (必ず1つ選択)
        - Market Analysis (market-analysis): 毎日の市況、全体の流れ、トレンド分析
        - Featured News (featured-news): 特定のニュース（決算、政策、M&A）の深掘り記事
        - Strategic Assets (strategic-assets): 仮想通貨・コモディティの分析記事
        - Investment Guide (investment-guide): 手法解説、ツール使い方、初心者向けガイド（ストック記事）
        
        ## 2. タグ (該当するものを全て選択)
        【地域】
        - US Market (us-market)
        - Japan Market (japan-market)
        - China Market (china-market)
        - India Market (india-market)
        - Indonesia Market (indonesia-market)
        - Global (global)
        
        【資産クラス】
        - Stock (stock)
        - Crypto (crypto)
        - Forex (forex)
        - Commodity (commodity)
        
        【テーマ】
        - Tech & AI (tech-ai)
        - EV & Auto (ev-auto)
        - Energy (energy)
        - Earnings (earnings)
        - Central Bank (central-bank)
        
        ## 出力フォーマット (JSONのみ)
        {{
            "category": "slug",
            "tags": ["slug1", "slug2", "slug3"]
        }}
        """
        
        try:
            response = self.gemini.client.models.generate_content(
                model='gemini-3-pro-preview',
                contents=prompt,
                config={
                    'response_mime_type': 'application/json'
                }
            )
            response_text = response.text
            # Clean up JSON markdown if present (though response_mime_type should handle it)
            response_text = re.sub(r'```json\n|\n```', '', response_text).strip()
            result = json.loads(response_text)
            return result
        except Exception as e:
            print(f"Classification failed: {e}")
            # Default fallback
            return {
                "category": "market-analysis",
                "tags": ["global"]
            }

            


if __name__ == "__main__":
    # Test
    classifier = ArticleClassifier()
    sample_title = "インド株SENSEXが最高値更新、タタ・モーターズが牽引"
    sample_summary = "インド市場は自動車セクターの好調により続伸。外国人投資家の買い越しが続く。"
    print(json.dumps(classifier.classify_article(sample_title, sample_summary), indent=2, ensure_ascii=False))
