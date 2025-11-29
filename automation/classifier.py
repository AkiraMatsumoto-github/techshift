import json
import re
try:
    from automation.gemini_client import GeminiClient
except ImportError:
    from gemini_client import GeminiClient

class ArticleClassifier:
    def __init__(self):
        self.gemini = GeminiClient()
        
    def classify_article(self, title, content_summary):
        """
        Classify an article into Category, Industry Tags, and Theme Tags.
        
        Returns:
            dict: {
                "category": "slug",
                "industry_tags": ["slug1", "slug2"],
                "theme_tags": ["slug1", "slug2"]
            }
        """
        
        prompt = f"""
        あなたは物流メディア「LogiShift」の編集者です。
        以下の記事タイトルと概要を分析し、最も適切な「カテゴリ（1つ）」と「タグ（複数可）」を選択してください。
        
        ## 記事情報
        タイトル: {title}
        概要: {content_summary}
        
        ## 1. カテゴリ (必ず1つ選択)
        - 物流DX・トレンド (logistics-dx)
        - 倉庫管理・WMS (warehouse-management)
        - 輸配送・TMS (transportation)
        - マテハン・ロボット (material-handling)
        - サプライチェーン (supply-chain)
        - 事例・インタビュー (case-studies)
        - ニュース・海外 (news-global)
        
        ## 2. 業種タグ (該当するものがあれば複数選択可、なければ空)
        - 製造業 (manufacturing)
        - 小売・流通 (retail)
        - EC・通販 (ecommerce)
        - 3PL・倉庫 (3pl-warehouse)
        - 食品・飲料 (food-beverage)
        - アパレル (apparel)
        - 医薬品・医療 (medical)
        
        ## 3. テーマタグ (該当するものがあれば複数選択可、なければ空)
        - コスト削減 (cost-reduction)
        - 人手不足対策 (labor-shortage)
        - 品質向上・誤出荷防止 (quality-improvement)
        - 環境・SDGs (environment-sdgs)
        - 安全・BCP (safety-bcp)
        - 補助金・助成金 (subsidy)
        
        ## 出力フォーマット (JSONのみ)
        {{
            "category": "slug",
            "industry_tags": ["slug1", "slug2"],
            "theme_tags": ["slug1", "slug2"]
        }}
        """
        
        try:
            response = self.gemini.client.models.generate_content(
                model='gemini-2.5-pro',
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
                "category": "logistics-dx",
                "industry_tags": [],
                "theme_tags": []
            }

if __name__ == "__main__":
    # Test
    classifier = ArticleClassifier()
    sample_title = "最新の自動倉庫システム導入でピッキング効率が30%向上"
    sample_summary = "A社は最新のシャトル型自動倉庫を導入し、EC物流センターのピッキング作業を自動化。人手不足を解消しつつ、誤出荷ゼロを達成した。"
    print(json.dumps(classifier.classify_article(sample_title, sample_summary), indent=2, ensure_ascii=False))
