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
        
    def classify_article(self, title, content_summary, excluded_categories=None):
        """
        Classify an article into FinShift Category and Tags.
        
        Args:
            title (str): Article title
            content_summary (str): Article summary
            excluded_categories (list): List of category slugs to exclude
        
        Returns:
            dict: {
                "category": "slug",
                "tags": ["slug1", "slug2"]
            }
        """
        
        # Define available categories
        categories = [
            {"name": "Market Analysis", "slug": "market-analysis", "desc": "毎日の市況、全体の流れ、トレンド分析"},
            {"name": "Featured News", "slug": "featured-news", "desc": "特定のニュース（決算、政策、M&A）の深掘り記事"},
            {"name": "Strategic Assets", "slug": "strategic-assets", "desc": "仮想通貨・コモディティの分析記事"},
            {"name": "Investment Guide", "slug": "investment-guide", "desc": "手法解説、ツール使い方、初心者向けガイド（ストック記事）"},
        ]
        
        # Filter categories
        if excluded_categories:
            categories = [c for c in categories if c['slug'] not in excluded_categories]
            
        # Build category prompt string
        category_prompt_str = ""
        for c in categories:
            category_prompt_str += f"- {c['name']} ({c['slug']}): {c['desc']}\n"
        
        prompt = f"""
        あなたは金融メディア「FinShift」の編集者です。
        以下の記事タイトルと概要を分析し、最も適切な「カテゴリ（1つ）」と「タグ（複数可）」を選択してください。
        
        ## 記事情報
        タイトル: {title}
        概要: {content_summary}
        
        ## 1. カテゴリ (必ず1つ選択)
{category_prompt_str}
        
        ## 2. タグ (該当するものを全て選択)
        【地域】
        - US Market (us-market): 米国株市場（S&P500, Nasdaq, NYダウ）
        - Japan Market (japan-market): 日本株市場（日経平均, TOPIX）
        - China Market (china-market): 中国・香港市場
        - India Market (india-market): インド市場
        - Indonesia Market (indonesia-market): インドネシア市場
        - Global (global): クロスボーダーな市場動向、世界経済
        
        【資産クラス】
        - Stock (stock): 個別銘柄の分析、決算、M&A
        - Crypto (crypto): 暗号資産（ビットコイン、イーサリアム）
        - Forex (forex): 為替市場（ドル円、ユーロドル）
        - Commodity (commodity): 金、原油、銅など商品市場
        
        【テーマ】
        - Tech & AI (tech-ai): 半導体、人工知能、SaaS、ハイテク株
        - EV & Auto (ev-auto): 電気自動車、バッテリー、自動運転
        - Energy (energy): 再生可能エネルギー、石油・ガス、インフラ
        - Earnings (earnings): 決算速報、ガイダンス修正
        - Central Bank (central-bank): FRB, 日銀, ECBなどの金融政策
        - Macro Economy (macro): マクロ経済、インフレ、GDP成長率
        - Geopolitics (geopolitics): 地政学リスク、戦争、貿易摩擦
        
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
