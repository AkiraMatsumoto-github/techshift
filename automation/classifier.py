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
        ※ 海外の動向や事例に関する記事は、必ず「ニュース・海外 (news-global)」を選択してください。
        
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

        ## 4. 地域タグ (海外記事の場合のみ選択、該当なければ空)
        - アメリカ (usa)
        - ヨーロッパ (europe)
        - 中国 (china)
        - 東南アジア (southeast-asia)
        
        ## 出力フォーマット (JSONのみ)
        {{
            "category": "slug",
            "industry_tags": ["slug1", "slug2"],
            "theme_tags": ["slug1", "slug2"],
            "region_tags": ["slug1"]
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
                "theme_tags": [],
                "region_tags": []
            }

            
    def classify_type(self, title, summary, source=""):
        """
        Classify the article type based on title and summary.
        
        Args:
            title: Article title
            summary: Article summary
            source: Source identifier (optional)
            
        Returns:
            str: One of [know, buy, do, news, global]
        """
        
        # 1. Check for Global/News based on source/content first (Low cost)
        if source in ["techcrunch", "wsj_logistics", "supply_chain_dive", "freightwaves", "36kr_japan", "pandaily"]:
            return "global"
            
        # 2. Use Gemini for semantic classification (High accuracy)
        prompt = f"""
        あなたは物流メディアの編集長です。
        以下の記事企画を、読者にとって最も価値のある5つの記事タイプ（フォーマット）のいずれかに分類してください。

        記事タイトル: {title}
        記事概要: {summary}

        ## 選択肢 (以下のいずれか1つを選んでください)
        1. know  (解説記事: 「WMSとは」「物流DXの仕組み」など、基礎知識や定義を解説)
        2. buy   (比較記事: 「WMS比較」「おすすめ10選」「選び方」など、製品選定を支援)
        3. do    (実践/事例: 「導入事例」「成功ノウハウ」「誤出荷ゼロへの道」など、具体的なハウツー)
        4. news  (国内ニュース: 最新の行政動向、企業のプレスリリース、人事情報など速報値・時事性があるもの)
        5. global (海外情報: 海外のトレンド、海外企業の事例、日本未上陸の技術)

        ## 判定ルール
        - 海外の国名や海外企業の話であれば「global」
        - 「比較」「選定」「おすすめ」なら「buy」
        - 「事例」「成功」「実践」なら「do」
        - 「とは」「仕組み」「メリット」などの基礎解説なら「know」
        - 特定の日付や「速報」などの時事性が強ければ「news」
        
        出力はタイプ名（know, buy, do, news, global）のみを小文字で返してください。
        """

        try:
            response = self.gemini.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config={
                    'response_mime_type': 'text/plain'
                }
            )
            result = response.text.strip().lower()
            
            # Validation
            valid_types = ["know", "buy", "do", "news", "global"]
            found_type = "news" # default
            
            for t in valid_types:
                if t in result:
                    found_type = t
                    break
            
            print(f"  > Classification result: {found_type} (Raw: {result})")
            return found_type

        except Exception as e:
            print(f"Type classification failed: {e}")
            return "news" # Safe fallback
if __name__ == "__main__":
    # Test
    classifier = ArticleClassifier()
    sample_title = "最新の自動倉庫システム導入でピッキング効率が30%向上"
    sample_summary = "A社は最新のシャトル型自動倉庫を導入し、EC物流センターのピッキング作業を自動化。人手不足を解消しつつ、誤出荷ゼロを達成した。"
    print(json.dumps(classifier.classify_article(sample_title, sample_summary), indent=2, ensure_ascii=False))
