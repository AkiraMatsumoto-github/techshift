import json
import re
import sys
import os
import textwrap

# Add parent directory to path to import GeminiClient
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from automation.gemini_client import GeminiClient
except ImportError:
    # Use relative import if running from automation dir
    from gemini_client import GeminiClient

class ArticleClassifier:
    def __init__(self, client=None):
        if client:
            self.gemini = client
        else:
            self.gemini = GeminiClient()
        
    def classify_article(self, title, content_summary, excluded_categories=None):
        """
        Classify an article into TechShift Category (Topic) and Tags.
        
        Args:
            title (str): Article title
            content_summary (str): Article summary
            excluded_categories (list): List of category slugs to exclude
        
        Returns:
            dict: {
                "category": "slug_of_child_topic",  # e.g., 'solid-state-batteries'
                "tags": ["slug1", "slug2"]          # e.g., ['technology', 'japan']
            }
        """
        
        prompt = textwrap.dedent(f"""
        You are the Chief Editor of "TechShift", a future foresight media.
        Classify the following article into the appropriate **Technical Topic (Category)** and **Context Tags**.
        
        ## Article Info
        Title: {title}
        Summary: {content_summary}
        
        ## 1. Category (Select ONE specific Topic Slug)
        
        **Target: Choose the most specific sub-category (Topic) from the hierarchy below.**
        
        **1. Space & Aero (space-aero)**
           - reusable-rockets (再使用型ロケット)
           - mega-constellations (衛星コンステレーション)
           - lunar-exploration (月面開発・アルテミス計画)
           - osam-debris (軌道上サービス・宇宙デブリ)
           - supersonic-hypersonic (超音速・極超音速技術)
           
        **2. Quantum (quantum)**
           - quantum-gate-computing (量子ゲート型コンピュータ)
           - quantum-annealing (量子アニーリング)
           - post-quantum-cryptography (耐量子暗号 PQC)
           - quantum-sensing (量子センシング)
           - quantum-internet (量子通信・インターネット)
           
        **3. Advanced AI (advanced-ai)**
           - foundation-models (基盤モデル LLM/SLM)
           - multi-agent-systems (マルチエージェント自律システム)
           - edge-ai (オンデバイス・エッジAI)
           - ai-native-dev (AIネイティブ開発 No-Code)
           - digital-provenance (デジタル・プロヴェナンス)
           
        **4. Robotics (robotics)**
           - humanoid-robots (ヒューマノイドロボット)
           - l4-autonomous-driving (レベル4 自動運転)
           - delivery-robots (ラストワンマイル配送ロボ)
           - spatial-computing (空間コンピューティング XR)
           - bci (ブレイン・コンピュータ I/F)
           
        **5. Life Science (life-science)**
           - ai-drug-discovery (AI創薬)
           - gene-editing (ゲノム編集・遺伝子治療)
           - protein-structure (タンパク質構造予測)
           - regenerative-medicine (再生医療・オルガノイド)
           - longevity (老化制御・長寿研究)
           
        **6. Green Tech (green-tech)**
           - fusion-energy (核融合発電)
           - solid-state-batteries (全固体電池・次世代蓄電)
           - direct-air-capture (直接空気回収 DAC)
           - smr (小型モジュール炉)
           - hydrogen-new-fuels (水素・次世代燃料)
           
        *(If none fit perfectly, choose the closest Section Parent slug)*
        
        ## 2. Tags (Select ALL relevant slugs)
        
        **Layer (Focus Area)**
        - regulation (規制・法整備・政策)
        - technology (技術開発・R&D, スペック向上)
        - market (市場・ビジネス・M&A・資金調達)
        
        **Region (Comparison)**
        - global-general (世界トレンド)
        - us (米国市場)
        - europe (欧州市場)
        - china (中国市場)
        - asia (アジア新興国)
        - japan (日本国内)
        
        **Priority**
        - hero-topic (Top Story of the day, Major Breakthrough)
        - strategic-asset (Key National Strategy)
        
        ## Output Format (JSON Only)
        {{
            "category": "slug_of_selected_topic",
            "tags": ["tag_slug_1", "tag_slug_2", ...]
        }}
        """)
        
        try:
            response = self.gemini.client.models.generate_content(
                model='gemini-2.0-flash-exp', # Use Flash for classification speed
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
                "category": "advanced-ai", # Default to AI
                "tags": ["global-general"]
            }

if __name__ == "__main__":
    # Test
    classifier = ArticleClassifier()
    sample_title = "トヨタ、全固体電池の量産化へ一歩前進"
    sample_summary = "トヨタ自動車は出光興産と提携し、全固体電池の量産パイロットラインを稼働させた。2027年の実用化を目指す。"
    print(json.dumps(classifier.classify_article(sample_title, sample_summary), indent=2, ensure_ascii=False))
