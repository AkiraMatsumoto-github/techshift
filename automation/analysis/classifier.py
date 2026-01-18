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
           - reusable-rockets (再使用型ロケット): SpaceX StarshipやNew Glennに代表される、完全再使用型ロケット技術と打ち上げコスト破壊。
           - mega-constellations (衛星コンステレーション): Starlinkなどの低軌道衛星群による地球規模の通信インフラ構築と宇宙空間の混雑問題。
           - lunar-exploration (月面開発・アルテミス計画): NASAアルテミス計画、月面基地建設、月資源（水・ヘリウム3）の利用に向けた有人宇宙探査の最前線。
           - osam-debris (軌道上サービス・宇宙デブリ): 軌道上での衛星修理・燃料補給(OSAM)技術と、ADR（アクティブデブリ除去）による持続可能な宇宙環境。
           - supersonic-hypersonic (超音速・極超音速技術): マッハ5を超える極超音速ミサイル技術や、静粛超音速旅客機(SST)の商用化に向けた開発動向。
           
        **2. Quantum (quantum)**
           - quantum-gate-computing (量子ゲート型コンピュータ): 超伝導、イオントラップ、光方式など、誤り耐性型量子コンピュータ(FTQC)実現に向けたハードウェア開発競争。
           - quantum-annealing (量子アニーリング): 組合せ最適化問題に特化した量子アニーリング技術の物流、金融、創薬分野への産業応用事例。
           - post-quantum-cryptography (耐量子暗号 PQC): 量子コンピュータによる暗号解読脅威に対抗する、NIST標準化PQCアルゴリズムとシステム移行ガイドライン。
           - quantum-sensing (量子センシング): ダイヤモンドNVセンタなどを用いた超高感度計測技術と、医療・GPS・資源探査への応用。
           - quantum-internet (量子通信・インターネット): 量子もつれを利用した盗聴不可能な量子暗号通信(QKD)と、地球規模の量子インターネット構築構想。
           
        **3. Advanced AI (advanced-ai)**
           - foundation-models (基盤モデル LLM/SLM): GPT-4, Claude, Geminiなどの大規模言語モデル(LLM)と、特定領域に特化した小規模言語モデル(SLM)の進化と推論能力。
           - multi-agent-systems (マルチエージェント自律システム): 複数のAIエージェントが協調して複雑なタスクを完遂する自律型AIシステムの設計と実装パターン。
           - edge-ai (オンデバイス・エッジAI): クラウドを介さずスマートフォンやPCローカルで動作するAIモデルの軽量化技術とプライバシー保護。
           - ai-native-dev (AIネイティブ開発 No-Code): 自然言語等のプロンプトだけでアプリケーションを構築するAIネイティブ開発と、エンジニアリングの未来。
           - digital-provenance (デジタル・プロヴェナンス): C2PAなどのコンテンツ来歴証明技術による、生成AIコンテンツの真正性保証とディープフェイク対策。
           
        **4. Robotics (robotics)**
           - humanoid-robots (ヒューマノイドロボット): 工場労働から家事支援まで、人間の動作を模倣・代替する汎用人型ロボットのハードウェアと制御AIの進化。
           - autonomous-driving (自動運転): 特定条件下での完全無人運転（レベル4）の商用化、Robotaxiの社会実装、法規制と安全性の課題。
           - delivery-robots (ラストワンマイル配送ロボ): 物流の最終拠点を担う自動配送ロボット、ドローン配送の技術課題と都市インフラとの連携。
           - spatial-computing (空間コンピューティング XR): Vision Proに代表されるMR/ARデバイス、空間OS、デジタルツインによる物理とデジタルの融合体験。
           - bci (ブレイン・コンピュータ I/F): Neuralinkなどの侵襲・非侵襲型BCIデバイスによる、脳とコンピュータの直接接続技術と医療応用。
           
        **5. Life Science (life-science)**
           - ai-drug-discovery (AI創薬): AlphaFoldなどの構造予測AIを活用した、新薬候補物質の探索・スクリーニング高速化と開発コスト削減。
           - gene-editing (ゲノム編集・遺伝子治療): CRISPR-Cas9などのゲノム編集技術を用いた難病治療、農作物改良、および倫理的課題。
           - protein-structure (タンパク質構造予測): アミノ酸配列からの3次元構造予測技術の進展と、酵素設計・ドラッグデザインへの応用。
           - regenerative-medicine (再生医療・オルガノイド): iPS細胞やオルガノイド（ミニ臓器）を用いた組織再生、移植医療、動物実験代替法の開発動向。
           - longevity (老化制御・長寿研究): 老化を「治療可能な疾患」と捉えるLongevity研究、老化細胞除去、エピジェネティック時計の解析。
           
        **6. Green Tech (green-tech)**
           - fusion-energy (核融合発電): 「地上の太陽」を実現する核融合発電（トカマク型・レーザー型など）の点火実験進捗と商用炉ロードマップ。
           - solid-state-batteries (全固体電池・次世代蓄電): EVの航続距離と安全性を飛躍させる全固体電池、ナトリウムイオン電池などの次世代エネルギー貯蔵技術。
           - direct-air-capture (直接空気回収 DAC): 大気中のCO2を直接回収・貯留するDAC技術のコスト削減、スケーリング、炭素除去クレジット市場。
           - smr (小型モジュール炉): 安全性と経済性を高めた小型原子炉(SMR)の開発、次世代炉（高温ガス炉等）、分散型エネルギー源としての活用。
           - hydrogen-new-fuels (水素・次世代燃料): グリーン水素の製造・輸送チェーン、アンモニア燃料、e-fuelなどの脱炭素合成燃料の社会実装。
           
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
