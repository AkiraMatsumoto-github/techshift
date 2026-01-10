# -*- coding: utf-8 -*-
import os
import base64
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
import time
import random
import textwrap


load_dotenv(override=True)

class GeminiClient:
    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = os.getenv("GOOGLE_CLOUD_LOCATION")
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None
        self.use_vertex = False

        # Prioritize Vertex AI initialization
        if self.project_id and self.location:
            try:
                print(f"Initializing Gemini with Vertex AI (Project: {self.project_id}, Location: {self.location})")
                self.client = genai.Client(vertexai=True, project=self.project_id, location=self.location)
                self.use_vertex = True
            except Exception as e:
                print(f"Warning: Vertex AI initialization failed: {e}, falling back to API Key.")
                self.use_vertex = False
        
        # Fallback to API Key if Vertex AI is not available
        if not self.use_vertex:
            if self.api_key:
                print("Initializing Gemini with API Key (google-genai)")
                self.client = genai.Client(api_key=self.api_key)
            else:
                raise ValueError("Missing Gemini credentials. Set GOOGLE_CLOUD_PROJECT/LOCATION or GEMINI_API_KEY in .env")

    def _retry_request(self, func, *args, **kwargs):
        """
        Retry a function call with exponential backoff if a quota error occurs.
        """
        max_retries = 5
        base_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_str = str(e).lower()
                # Check for rate limit/quota errors
                if "429" in error_str or "quota" in error_str or "exhausted" in error_str:
                    if attempt == max_retries - 1:
                        print(f"Max retries ({max_retries}) exceeded for quota error.")
                        raise e
                    
                    delay = (base_delay * (2 ** attempt)) + (random.random() * 1)
                    print(f"Quota exceeded (429). Retrying in {delay:.2f}s... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                else:
                    # Not a quota error, raise immediately
                    raise e

    def generate_content(self, prompt, model='gemini-3-pro-preview', config=None):
        """
        Generic method to generate content with retry logic.
        """
        try:
            response = self._retry_request(
                self.client.models.generate_content,
                model=model,
                contents=prompt,
                config=config
            )
            return response
        except Exception as e:
            print(f"Error generating content: {e}")
            return None

    def generate_article(self, keyword, article_type="know", context=None, extra_instructions=None, category=None):
        """
        Generate a full blog article in Markdown format based on the keyword and type (or category).
        """
        print(f"Generating article for keyword: {keyword} (Type: {article_type}, Category: {category})")
        
        context_section = ""
        if context:
            context_section = f"""
            ## Context Information
            The following external information is relevant to the topic. Use it to ensure accuracy and freshness.
            Summary: {context.get('summary', '')}
            Key Facts: {', '.join(context.get('key_facts', []))}
            Analyst View: {context.get('finshift_view', '')}
            """
            
        prompts = {
            # --- FinShift Specific Prompts ---
            
            # [Standard Pipeline] Used for generating individual articles (1:1) based on a specific keyword/topic.
            # This is NOT used for the Daily Briefing aggregation.
            "market-analysis": textwrap.dedent(f"""
            {context_section}あなたは金融市場のシニア・ストラテジスト（元ヘッジファンド運用者）です。
            本日の市場ニュースを統合し、投資家向けの「市況分析（Daily Briefing）」を執筆してください。
            
            キーワード/テーマ: {keyword}
            
            ## ターゲット
            - 日々の市場動向をチェックし、短期〜中期の売買判断を行うスイングトレーダー
            - 「なぜ動いたか」だけでなく「明日どうなるか」を知りたい個人投資家
            
            ## 構成案
            1. **【市場概況】 (Market Overview)**:
               - 本日の市場全体のムード（Risk-on / Risk-off）を一言で定義。
               - 最も影響力のあったドライバー（材料）を端的に提示。
            2. **【詳細分析】 (Deep Dive)**:
               - {keyword} に関するニュースを深掘り。
               - 「市場参加者がこれをどう解釈したか（織り込み度合い）」を分析。
            3. **【注目ライン】 (Key Levels)**:
               - 関連指数や銘柄の重要な価格帯（サポート/レジスタンス）に到達したか、意識されているかを解説。
            4. **【シナリオ分析】**:
               - **強気 (Bull)**: 上昇継続のための条件。
               - **弱気 (Bear)**: 下落リスク・警戒点。
            5. **【投資戦略】 (Actionable Insights)**:
               - 「様子見」「押し目買い」「利益確定」など、具体的なスタンスを提案。
            
            ## 執筆ルール
            - **見出し**: 全て日本語を使用すること（例：## 市場概況）。
            - **トーン**: 冷静、客観的、プロフェッショナル。「です・ます」調で統一し、読みやすさを重視。
            - **専門性**: 金融用語を適切に使用しつつ、論理的なつながりを明確にする。
            - **データ重視**: 数値（株価、騰落率、金利）を必ず引用する。
            
            ## フォーマット
            - Markdown形式
            - 4000文字程度
            - **重要な数値データはMarkdownテーブルで整理する**
            - HTMLタグ使用禁止

            ## タイトル作成ルール
            1. **文字数**: 32文字程度（検索結果で省略されない長さ）
            2. **キーワード**: 「{keyword}」から**最も重要な単語（企業名やテーマ）**を抜き出して含める
            3. **引き**: 読者がクリックしたくなる「転換点」「急騰」「警告」などの強い言葉を使う
            4. **形式**: Markdownの見出しとして出力（# タイトル）
            5. **例**: 「(抽出語句)急騰：FRB利下げ観測で変わる潮目と今後の戦略」
            """),

            "featured-news": textwrap.dedent(f"""
            {context_section}あなたは株式市場の専門アナリスト（Equity Analyst）です。
            特定の重要ニュース（{keyword}）について、個別銘柄やセクターへの「インパクト」を深掘り分析する記事を執筆してください。
            
            キーワード/対象銘柄: {keyword}
            
            ## ターゲット
            - その銘柄/セクターを既に保有している、または購入を検討している投資家
            - ニュースの表面的な内容ではなく、「株価への具体的な影響」を知りたい層
            
            ## 構成案
            1. **Impact Summary (インパクト要約)**:
               - このニュースが「買い材料」なのか「売り材料」なのか、短期/中長期の視点で結論を提示（例: 短期はポジティブだが長期的には懸念あり）。
            2. **News Breakdown (ニュースの核心)**:
               - 何が起きたか（What）、なぜ重要か（Why）。
               - 決算数値、M&A、新製品発表などの事実関係を正確に記述。
            3. **Valuation & Fundamentals (企業価値への影響)**:
               - 業績（EPS、売上高）への貢献度予測。
               - 競合他社との比較優位性の変化。
            4. **Chart Analysis (テクニカル)**:
               - 現在の株価位置（高値圏/安値圏）と、ニュースによるトレンド変化の可能性。
            5. **Conclusion (投資判断)**:
               - ターゲットプライスやエントリーのタイミングについての示唆。
               - 具体的な「買い」推奨は避けつつ、判断材料を提供。
            
            ## 執筆ルール
            - **客観性重視**: エモーショナルな煽りは厳禁。ロジックと数字で語る。
            - **比較視点**: 同業他社（Peers）や過去の類似事例との比較を含めると良い。
            
            ## フォーマット
            - Markdown形式
            - 3000文字程度
            - 財務データ等はテーブルを活用
            - HTMLタグ使用禁止

            ## タイトル作成ルール
            1. **文字数**: 32文字程度（スマホ検索で切れにくい長さ）
            2. **キーワード**: 「{keyword}」から**主要な銘柄名やテーマ**を抽出して前半に含める
            3. **具体性**: 「大幅上昇」「暴落」ではなく「15%急騰」「底割れ」など数字や具体的表現を入れる
            4. **形式**: Markdownの見出しとして出力（# タイトル）
            """),

            "strategic-assets": textwrap.dedent(f"""
            {context_section}あなたは暗号資産（Crypto）およびコモディティ（Gold/Oil）の市場ストラテジストです。
            以下のキーワードについて、テクニカル分析とマクロ経済環境を重視した分析記事を執筆してください。
            
            キーワード/資産: {keyword}
            
            ## ターゲット
            - ビットコイン、イーサリアム、ゴールド等をトレードするアクティブ投資家
            - ボラティリティ（変動）を利益に変えたいスペキュレーター
            
            ## 構成案
            1. **Asset Status (現在の局面)**:
               - トレンド定義（上昇トレンド、レンジ、調整局面）。
            2. **Macro Correlation (マクロ環境との相関)**:
               - 米金利（Fed政策）、ドル指数（DXY）、株価指数との連動性を分析。
               - 「デジタルゴールドとしてのBTC」や「インフレヘッジとしてのGold」などのナラティブ分析。
            3. **On-chain / Supply Data (需給データ)**:
               - ※仮想通貨の場合：ハッシュレート、ETFフロー、クジラ（大口）の動向。
               - ※コモディティの場合：在庫統計、地政学リスク、生産コスト。
            4. **Technical Setup (チャート分析)**:
               - 重要な水平線、移動平均線、RSI/MACDなどのオシレーター分析。
               - 具体的なアップサイド/ダウンサイドの目処。
            5. **Strategy (トレード戦略)**:
               - 短期的なエントリーポイントと損切り（Stop Loss）の目安。
            
            ## 執筆ルール
            - **専門用語**: オンチェーンデータ、半減期、OI（建玉）、ファンディングレート等の専門用語を適切に使用。
            - **リスク警告**: ボラティリティが高い資産であることを前提に、リスク管理の重要性を必ず添える。
            
            ## フォーマット
            - Markdown形式
            - 3000文字程度
            - HTMLタグ使用禁止

            ## タイトル作成ルール
            1. **文字数**: 32文字以内推奨
            2. **対比**: 「ビットコインvsゴールド」のような対立構造を入れる（{keyword}から要素を抽出）
            3. **キーワード**: 「{keyword}」の主要要素を含める
            4. **形式**: Markdownの見出しとして出力（# タイトル）
            """),

            "investment-guide": textwrap.dedent(f"""
            あなたは金融教育のプロフェッショナル（フィナンシャル・アドバイザー）です。
            以下のキーワードについて、初心者〜中級者の投資家が正しく理解し、実践できるような「ガイド記事（Educational）」を執筆してください。
            
            キーワード: {keyword}
            
            ## ターゲット
            - 投資を始めたばかりの初心者、または知識を体系化したい中級者
            - 新しい手法（CFD、オプション、特定ツール）を学びたい人
            
            ## 構成案
            1. **Introduction (導入)**:
               - なぜ今、この知識（ツール/手法）を知っておく必要があるのか？
               - 読者のメリット（利益向上、リスク低減）を提示。
            2. **Basic Concept (基礎知識)**:
               - {keyword} の定義。専門用語を使わず、例え話などを用いて平易に解説。
            3. **How-to / Mechanism (仕組みとやり方)**:
               - 具体的な手順、操作方法、計算式など。ステップバイステップで説明。
            4. **Pros & Cons (メリット・デメリット)**:
               - 良い面だけでなく、リスクや注意点（手数料、税金、損失リスク）を公平に解説。
            5. **Best Practice (活用事例)**:
               - 「こういう時に使うと効果的」という実践的なケーススタディ。
            6. **Summary (まとめ)**:
               - 復習と次のステップ。
            
            ## 執筆ルール
            - **平易さ**: 難解な言い回しは避け、親しみやすい「ですので」「ましょう」調（です・ます）を使用。
            - **図解意識**: 「以下の図のように〜」といった、図解を挿入しやすい構成にする（実際の画像生成は別プロセスだが、意識した文章にする）。
            - **教育的価値**: 単なる情報羅列ではなく、「読者が自力で判断できるようになること」をゴールにする。
            
            ## フォーマット
            - Markdown形式
            - 3500文字程度
            - 手順や比較はMarkdownテーブルで整理
            - HTMLタグ使用禁止

            ## タイトル作成ルール
            1. **文字数**: 32文字前後
            2. **ターゲット**: 初心者が「自分に関係ある」と思える疑問形や「完全ガイド」等の表現
            3. **キーワード**: 「{keyword}」から核心となる単語を抜き出して含める
            4. **形式**: Markdownの見出しとして出力（# タイトル）
            """),

            # --- Future / Weekly Summary (To be refined) ---
            # "weekly_summary": textwrap.dedent(f"""
            # {context_section}あなたは物流業界の専門メディア「LogiShift」の編集長です。
            # 今週公開された以下の記事（タイトルと要約）をもとに、業界の動きを構造化・抽象化し、深い示唆（インサイト）を提供する「週間サマリー」を作成してください。
            # 
            # ## 対象期間
            # - 直近1週間
            # 
            # ## ターゲット読者
            # - 経営層、物流部門長、DX推進リーダー
            # - 単なるニュースの羅列ではなく、「その事象が業界にとって何を意味するのか」という深い解釈を求めている人
            # 
            # ## 構成案
            # 1. **今週の潮流（The Weekly Macro View）**:
            #    - 個別のニュースを俯瞰し、今週の物流業界が「どのようなフェーズにあったか」を抽象化して一言で定義する。（例：「AIの実装が『実験』から『実利』へシフトした1週間」など）
            #    - その背景にある業界構造の変化について簡潔に触れる。
            # 
            # 2. **業界構造の変化と示唆（Key Movements & Insights）**:
            #    - 記事を単にトピックごとに分類するのではなく、「業界のどのような構造的変化・動きか」という観点で2〜3つのまとまり（H2）を作る。
            #    - **構成要素**:
            #      - **現象（What）**: 具体的にどのようなニュースがあったか（記事リンク必須）。
            #      - **深層（Why/So What）**: なぜその動きが起きているのか？そこから読み取れる業界の課題やチャンスは何か？読者はどう捉えるべきか？という「独自の示唆」を必ず加える。
            #    - **記事リンク**: 関連する記事へのリンク（`[記事タイトル](URL)`）を文脈の中で自然に、かつ必ず埋め込むこと。
            # 
            # 3. **来週以降の視点（Strategic Outlook）**:
            #    - 今週の動きを踏まえ、来週以降、読者が注目すべき具体的なポイントを提言する。
            #    - 抽象的な話で終わらせず、「どの技術の進展を見るべきか」「どのプレイヤー（企業群）の動きを注視すべきか」「規制や市場環境はどう動くか」など、具体的な「ウォッチポイント」を提示する。
            # 
            # ## 執筆ルール
            # - **思考の深さ**: 記事の要約で終わらせない。「つまり、これは〇〇という大きな流れの一部である」という構造化・抽象化を行うこと。
            # - **トーン＆マナー**: 知的で洞察に満ちたトーン。評論家にならず、実務家に寄り添った視点を持つ。
            # - **リンク（最重要）**: 
            #     - **可能な限り多くの記事を紹介すること。** 少なくとも10記事以上への言及・リンクを目指す。
            #     - 単にリスト化するのではなく、文脈の中で自然に複数の記事を引用する。（例：「A社（リンク）やB社（リンク）の事例に見られるように...」）
            #     - すべての主張の根拠として、提供された記事へのリンクを使用すること。
            # 
            # ## フォーマット
            # - Markdown形式
            # - 記事リンク必須
            # - 記事量はしっかり語るため **4000〜5000文字程度** を目指す。
            # 
            # ## タイトル生成ルール
            # - **フォーマット**: 【週間サマリー】MM/DD〜MM/DD｜[今週の最大の潮流・抽象化したテーマ]
            # - **例**: 【週間サマリー】12/13〜12/20｜「点」のDXから「線」の連携へ、物流構造改革の胎動
            # """)
        }
        
        # Priority: Category -> Type -> Default
        if category and category in prompts:
            prompt = prompts[category]
        else:
            # Fallback for legacy types or missing category
            type_map = {
                "know": "investment-guide", 
                "do": "investment-guide",
                "buy": "investment-guide",
                "news": "featured-news",
                "global": "market-analysis"
            }
            mapped_cat = type_map.get(article_type, "market-analysis")
            prompt = prompts[mapped_cat]
        
        if extra_instructions:
            prompt += f"\n\n{extra_instructions}\n"
        
        # Add common formatting instruction
        # Add common formatting instruction
        prompt += textwrap.dedent("""
        
        ## 出力形式
        必ず以下の形式で出力してください：
        
        1行目: # [生成したタイトル]
        2行目: 空行
        3行目以降: 記事本文（導入から始める）
        
        **見出しレベル:**
        - タイトル: # (H1) ← 記事の主題
        - 大見出し: ## (H2) ← 記事の主要な構成要素（章）
        - 中見出し: ### (H3) ← 章を構成する具体的なトピック（節）
        - 小見出し: #### (H4) ← トピックの詳細。情報の粒度を細かくし、可読性を高めるために活用する。
        
        **【重要】Markdown記述ルール:**
        - **リスト（箇条書き）の前には必ず空行を入れること。** 空行がないと正しくリストとして認識されないため厳守する。
        - **ネスト（入れ子）したリストのインデントは必ず半角スペース4つ（4 spaces）を使用すること。** 2スペースでは構造が崩れる場合がある。
        
        **【重要】見出しの禁止事項:**
        - **「具体的な効果」「メリット」「ポイント」といった汎用的な単語だけの見出しを、H3やH4で繰り返し使用することを禁止する。**
        - OK例: `#### 自動見積もりによるコスト削減`
        - NG例: `#### 具体的な効果`
        - 目次を見ただけで内容が伝わる具体的な見出しにすること。
        
        例:
        # 【決算速報】NVIDIA (NVDA) 3Q決算：AIブームは終わらない？市場予想を凌駕する「データセンター」の爆発的成長

        ## 1. Executive Summary
        11月20日に発表されたNVIDIAの第3四半期決算は、売上高・EPSともに市場コンセンサスを大幅に上回った。
        特に注目すべきは、データセンター部門の売上が前年同期比+279%という驚異的な伸びを見せた点だ。これは、生成AIへの設備投資（CAPEX）が依然として加速傾向にあることを示唆している。

        投資家にとっての結論はシンプルだ。**「AI半導体相場は第2章に入った」**。

        ## 2. Key Metrics（主要数値）
        今回の決算におけるハイライトは以下の通りである。

        | 項目 | 結果 | 市場予想 | 前年同期比 |
        | :--- | :--- | :--- | :--- |
        | 売上高 | $18.12B | $16.18B | +206% |
        | EPS (Non-GAAP) | $4.02 | $3.37 | +593% |
        | データセンター売上 | $14.51B | $12.97B | +279% |

        ## 3. シナリオ分析
        ### Bull Case (強気シナリオ)
        *   **新製品への期待:** 次世代GPU「H200」および「Blackwell」アーキテクチャへの移行がスムーズに進み、ASP（平均販売単価）が上昇する。
        *   **中国規制の回避:** 中国向け特化チップの投入により、輸出規制の影響を最小限に留める。

        ### Bear Case (弱気シナリオ)
        *   **供給制約:** CoWoSパッケージング工程のボトルネックが解消されず、バックログ（受注残）の消化が遅れる。
        
        ...
        """)
        
        try:
            response = self._retry_request(
                self.client.models.generate_content,
                model='gemini-3-pro-preview',
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Error generating content: {e}")
            return None

    def generate_image(self, prompt, output_path, aspect_ratio="16:9"):
        """
        Generate an image using Gemini 2.5 Flash Image (Primary) or Imagen 3.0 (Fallback).
        """
        # 1. Try Gemini 2.5 Flash Image (API Key supported)
        try:
            print(f"Generating image with Gemini 2.5 Flash Image for prompt: {prompt}")
            
            # Use google-genai SDK (v1beta) for API Key support and aspect ratio control
            # We need a dedicated client for v1beta to ensure aspect_ratio works
            client_v1beta = genai.Client(api_key=self.api_key, vertexai=False, http_options={'api_version': 'v1beta'})
            
            response = client_v1beta.models.generate_content(
                model='gemini-2.5-flash-image',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    image_config=types.ImageConfig(
                        aspect_ratio=aspect_ratio,
                    )
                )
            )
            
            # Extract image from response (Gemini 2.5 Flash)
            if response.parts:
                for part in response.parts:
                    # Check if part has inline_data (image)
                    if part.inline_data is not None:
                        image_bytes = part.inline_data.data
                        with open(output_path, 'wb') as f:
                            f.write(image_bytes)
                        print(f"Image saved to: {output_path}")
                        return output_path
            
            print("No image found in Gemini 2.5 response, trying fallback...")
            
        except Exception as e:
            print(f"Gemini 2.5 Flash Image failed ({e}), falling back to Imagen 3.0...")

        # 2. Fallback to Imagen 3.0 (Vertex AI only)
        try:
            print(f"Generating image with Imagen 3.0 (Fallback) for prompt: {prompt}")
            
            response = self._retry_request(
                self.client.models.generate_images,
                model='imagen-3.0-generate-001',
                prompt=prompt,
                config={
                    'aspect_ratio': aspect_ratio
                }
            )
            
            # Extract image from response (Imagen 3.0)
            if response.generated_images:
                image_bytes = response.generated_images[0].image.image_bytes
                with open(output_path, 'wb') as f:
                    f.write(image_bytes)
                print(f"Image saved to: {output_path}")
                return output_path
            
            print("No image generated in Imagen 3.0 response.")
            return None
                
        except Exception as e:
            print(f"Failed to generate image with Imagen 3.0: {e}")
            return None


    def generate_image_prompt(self, title, content_summary, article_type="market-analysis"):
        """
        Generate an optimized English image prompt based on article title and content.
        
        Args:
            title: Article title
            content_summary: Brief summary or first paragraph of the article
            article_type: Type of article (market-analysis, featured-news, strategic-assets, investment-guide)
        
        Returns:
            English image prompt optimized for Imagen 3.0
        """
        prompt = textwrap.dedent(f"""
        You are an expert at creating image generation prompts for Imagen 3.0.
        
        Based on the following article information, create a detailed English image prompt that:
    1. Captures the main theme and context of the article (Financial Markets, Investment, Economy)
    2. **Visual Metaphors**: Use diverse metaphors beyond just animals. Consider:
       - **Cityscapes**: Futuristic financial districts, glowing networks.
       - **Kinetic**: Moving gears, rising/falling tides, accelerating lights.
       - **Animals**: Use Bull/Bear ONLY if explicitly fitting, but prefer subtler symbolism.
    3. **Style**: Premium, Financial Professional, Bloomberg/WallStreetJournal style.
    4. **Lighting**: Clean Corporate.
    5. Avoids text, human faces, or complex diagrams.
    
    Article Title: {title}
    Article Type: {article_type}
    Content Summary: {content_summary[:2000]}
    
    Generate a single, detailed English image prompt (max 100 words) that would create a compelling hero image for this article.
    Output ONLY the prompt text, no explanations.
        """)
        
        try:
            response = self._retry_request(
                self.client.models.generate_content,
                model='gemini-3-pro-preview',
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error generating image prompt: {e}")
            # Fallback to simple prompt
            return f"Professional logistics warehouse scene related to {title}, photorealistic, high quality, 4k"



    def generate_static_page(self, page_type):
        """
        Generate static page content (privacy policy, about, contact).
        
        Args:
            page_type: "privacy", "about", or "contact"
        
        Returns:
            Generated markdown content
        """
        prompts = {
            "privacy": textwrap.dedent("""
            あなたは法務に詳しいコンテンツライターです。
            以下の情報を基に、日本の個人情報保護法に準拠したプライバシーポリシーを作成してください。
            
            【サイト情報】
            - サイト名: FinShift（フィンシフト）
            - 運営者: FinShift編集部
            - 設立: 2025年12月
            - 目的: 金融市場の分析・投資情報の提供
            - 使用技術: Googleアナリティクス、Cookie
            - お問い合わせ: info@finshift.jp
            
            ## 含めるべき項目
            1. 個人情報の取り扱いについて
            2. 収集する情報の種類（アクセスログ、Cookie等）
            3. 利用目的（サイト改善、統計分析等）
            4. 第三者提供（Googleアナリティクス等）
            5. Cookie・アクセス解析ツールについて
            6. 免責事項（投資助言業務ではない旨を明記）
            7. 個人情報の開示・訂正・削除について
            8. お問い合わせ先
            9. 制定日・改定日
            
            ## 出力形式
            - Markdown形式で出力
            - 見出しはH2（##）とH3（###）を使用
            - 箇条書きや表を適宜使用
            - 法的に正確で、かつ読みやすい文章
            - 最後に「制定日: 2025年12月1日」を記載
            
            ## 注意点
            - 専門用語は分かりやすく説明
            - **投資判断は自己責任**であるという免責を必ず含める
            - 連絡先を明記
            """),
            
            "about": textwrap.dedent("""
            あなたはコーポレートコミュニケーションの専門家です。
            以下の情報を基に、FinShiftの運営者情報ページを作成してください。
            
            【サイト情報】
            - サイト名: FinShift（フィンシフト）
            - 運営者: FinShift編集部
            - 設立: 2025年12月
            - お問い合わせ: info@finshift.jp
            
            【ミッション】
            個人投資家に「機関投資家レベルの洞察」を提供し、健全な資産形成をサポートする。
            「情報の非対称性」を解消し、誰でもプロ並みの分析にアクセスできる世界を目指す。
            
            【主なコンテンツ】
            - 世界の市況速報・トレンド分析
            - 決算速報と株価インパクト分析
            - 暗号資産・コモディティの戦略的資産運用
            - 投資教育・ツール活用ガイド
            
            【ターゲット読者】
            - スイングトレーダー、中長期投資家
            - テクニカル分析・ファンダメンタルズ分析を学びたい個人投資家
            
            ## 含めるべき項目
            1. FinShiftについて（サイトの目的・ビジョン）
            2. 基本情報（サイト名、運営者、設立年、お問い合わせ先）をテーブル形式で
            3. ミッション・ビジョン
            4. 主なコンテンツカテゴリの紹介
            5. 想定読者
            6. お問い合わせ先
            
            ## 出力形式
            - Markdown形式で出力
            - 見出しはH2（##）とH3（###）を使用
            - 基本情報はMarkdownテーブルで整理
            - 信頼感があり、かつエネルギッシュな文章
            - 金融市場への情熱が伝わる内容
            """),
            
            "contact": textwrap.dedent("""
            あなたはカスタマーサポートの専門家です。
            以下の情報を基に、FinShiftのお問い合わせページを作成してください。
            
            【サイト情報】
            - サイト名: FinShift（フィンシフト）
            - 運営者: FinShift編集部
            - お問い合わせ: info@finshift.jp
            - 対応時間: 平日 10:00-18:00（土日祝日を除く）
            
            ## 含めるべき項目
            1. お問い合わせについて（導入文）
            2. お問い合わせ方法（メールアドレス）
            3. 対応時間
            4. お問い合わせ内容の例（記事の内容、広告掲載、取材依頼など）
            5. 返信までの目安時間
            6. 注意事項（個人情報の取り扱い、投資相談は受け付けていない旨など）
            
            ## 出力形式
            - Markdown形式で出力
            - 見出しはH2（##）とH3（###）を使用
            - 箇条書きを適宜使用
            - 丁寧で分かりやすい文章
            - お問い合わせしやすい雰囲気
            
            ## 注意点
            - メールアドレスは必ず記載
            - 対応時間を明記
            - **個別の投資相談や推奨銘柄の問い合わせには回答できない**旨を明記
            - プライバシーポリシーへのリンクを案内（「詳しくは[プライバシーポリシー](/privacy-policy/)をご覧ください」）
            """)
        }
        
        prompt = prompts.get(page_type)
        if not prompt:
            raise ValueError(f"Invalid page_type: {page_type}. Must be 'privacy', 'about', or 'contact'")
        
        try:
            response = self._retry_request(
                self.client.models.generate_content,
                model='gemini-3-pro-preview',
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Error generating static page: {e}")
            return None


    def generate_structured_summary(self, content):
        """
        Generate a structured JSON summary of the article for internal linking relevance.
        
        [USAGE ROLE]: Output Processing
        This method is used *AFTER* generation to extract metadata from the **INTERNAL** article.
        The result is saved in WordPress 'ai_structured_summary' field.
        """
        prompt = textwrap.dedent(f"""
        You are an expert content analyst. Analyze the following article and generate a structured summary in JSON format.
        This summary will be used by an AI system to identify relevant internal links.
        IMPORTANT: The content is Japanese, so the 'summary' and 'key_topics' MUST be written in Japanese.

        Article Content:
        {content[:4000]}... (truncated)

        Output JSON format (Strictly JSON only):
        {{
            "summary": "Detailed summary of the article content (300-500 chars) in Japanese. Mention specific methods, technologies, or case studies discussed.",
            "key_topics": ["list", "of", "specific", "sub-topics", "covered", "(in Japanese)"],
            "entities": ["list", "of", "companies", "products", "or", "tools", "mentioned", "(preserve original names)"],
            "bull_scenario": "Brief description of the bullish scenario (if applicable) in Japanese.",
            "bear_scenario": "Brief description of the bearish scenario (if applicable) in Japanese."
        }}
        """)
        
        try:
            response = self._retry_request(
                self.client.models.generate_content,
                model='gemini-3-pro-preview',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            import json
            return json.loads(response.text)
        except Exception as e:
            print(f"Structured summary generation failed: {e}")
            return None

    def generate_sns_content(self, title, content, article_type="market-analysis"):
        """
        Generate engaging SNS (Twitter/X) post content.
        Output is JSON: {"hook": "...", "summary": "...", "hashtags": ["#tag1", ...]}
        """
        # Truncate content for efficiency
        truncated_content = content[:3000]
        
        prompt = textwrap.dedent(f"""
        You are an expert social media manager for a financial media site "FinShift".
        Create an engaging X (Twitter) post content based on the following article.
        
        Target Audience: Swing traders, individual investors, market analysts.
        Goal: Maximize CTR and Engagement by appealing to "Profit Opportunity" or "Risk Management".
        
        Article Title: {title}
        Article Type: {article_type}
        Content (excerpt):
        {truncated_content}
        
        Requirements:
        1. **Hook**: A strong, catchy opening line. Use a number, a price target, or a provocative question.
           - MUST include 1 relevant emoji (📈, 📉, 💰, 🚨, etc.).
           - Max 50 chars.
        2. **Summary**: A compelling teaser. Do NOT just summarize. Explain "How this affects their wallet" or "What the next move is".
           - Focus on price action, sector trends, or earning surprises.
           - Max 100 chars.
        3. **Hashtags**: 3-5 relevant hashtags.
           - **CRITICAL**: Use specific Ticker Symbols (e.g., $NVDA, $BTC, $USDJPY) if mentioned.
           - Use standard finance tags like #米国株 #日経平均 #仮想通貨.
        
        4. Language: Japanese. 
        5. **Tone**: Professional, Insightful, slightly urgent ("Now or Never"). 
        
        Output JSON format (Strictly JSON only):
        {{
            "hook": "� NVIDIA決算、予想を上回るも時間外で下落？",
            "summary": "「材料出尽くし」か「押し目買い」か、プロの分析で見極める。AIセクターの第2章はここから始まる。",
            "hashtags": ["#FinShift", "$NVDA", "#米国株", "#AI関連"]
        }}
        """)
        
        try:
            response = self._retry_request(
                self.client.models.generate_content,
                model='gemini-3-pro-preview',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            import json
            return json.loads(response.text)
        except Exception as e:
            print(f"SNS content generation failed: {e}")
            # Fallback
            return {
                "hook": f"【新着記事】{title}",
                "summary": "最新の市場動向を分析しました。投資判断の参考にしてください。",
                "hashtags": ["#FinShift", "#投資", "#株"]
            }

    def check_duplication(self, new_title, new_summary, existing_titles):
        """
        Check if a new article title semantically matches any existing titles.
        
        Args:
            new_title: The title of the potential new article
            new_summary: The summary of the potential new article
            existing_titles: List of existing article titles (WP posts + currently generated)
            
        Returns:
            The matching existing title if duplicate found, or None.
        """
        if not existing_titles:
            return None
            
        # Optimization: Don't check against massive lists if unnecessary.
        # But for now, we assume existing_titles is reasonably sized (e.g., < 50).
        
        prompt = f"""
        You are a duplicate content detector for a logistics news site.
        Determine if the "New Article" covers the **same specific news topic** as any of the "Existing Articles".
        
        Rule:
        - Return the EXACT title of the existing article ONLY if they are about the same specific news event or announcement.
        - If the new article is just a general topic match (e.g. both are about "RFID") but different specific news, return "None".
        - If the new article is a "Summary" or "Compilation" and the existing one is a single news, they are different -> return "None".
        - Different companies doing similar things are DIFFERENT -> return "None".
        - Same company doing the same thing (reported by different sources) are DUPLICATES -> return the existing title.
        
        New Article:
        Title: "{new_title}"
        Summary: "{new_summary}"
        
        Existing Articles:
        {json.dumps(existing_titles, ensure_ascii=False, indent=2)}
        
        Output JSON format:
        {{
            "is_duplicate": true/false,
            "duplicate_of": "Exact Title of Existing Article" (or null if false),
            "reason": "Brief explanation"
        }}
        """
        
        try:
            response = self._retry_request(
                self.client.models.generate_content,
                model='gemini-2.0-flash-exp',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            result = json.loads(response.text)
            
            if result.get("is_duplicate"):
                print(f"Duplicate detected! '{new_title}' is duplicate of '{result.get('duplicate_of')}'")
                print(f"Reason: {result.get('reason')}")
                return result.get("duplicate_of")
            
            return None
            
            return None
            
        except Exception as e:
            print(f"Duplication check failed: {e}")
            return None

    # --- Daily Briefing Methods ---



    def check_relevance_batch(self, articles):
        """
        Check relevance for a batch of articles (list of dicts).
        Each dict must have 'url_hash', 'title', 'summary'.
        
        Returns: Dict mapping url_hash -> {'is_relevant': bool, 'reason': str}
        """
        if not articles:
            return {}
            
        # Prepare input list for prompt
        input_list = []
        for art in articles:
            input_list.append({
                "id": art.get('url_hash', 'unknown'),
                "title": art.get('title', ''),
                "summary": art.get('summary', '')[:500] # Truncate summary for token efficiency
            })
            
        prompt = f"""
        You are a financial news filter. 
        Analyze the following list of articles and determine if EACH one is relevant to **financial markets, economy, business, or investment**.
        
        Criteria for "Relevant":
        - Reports on stock markets, companies, earnings, economic indicators (GDP, CPI), central banks.
        - Discusses commodities, crypto, forex, or trade policies.
        - Covers major geopolitical events affecting markets.
        
        Criteria for "Not Relevant" (Noise):
        - Lifestyle insights, health tips, pure entertainment/celebrity gossip.
        - Sports scores (unless business related).
        - Shopping guides/reviews (unless significant for retail sector).
        - Career advice, HR tips, general "how to be productive".
        
        Input Articles:
        {json.dumps(input_list, ensure_ascii=False, indent=2)}
        
        Output JSON:
        A list of objects, one for each input article:
        [
            {{
                "id": "article_id_from_input",
                "is_relevant": true/false,
                "reason": "Brief explanation"
            }},
            ...
        ]
        """
        
        try:
            response = self._retry_request(
                self.client.models.generate_content,
                model='gemini-2.0-flash-exp', 
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            res_json = json.loads(response.text)
            
            # Map back to url_hash
            result_map = {}
            for res in res_json:
                u_hash = res.get('id')
                if u_hash:
                    result_map[u_hash] = {
                        'is_relevant': res.get('is_relevant', False),
                        'reason': res.get('reason', 'Unknown')
                    }
            return result_map
            
        except Exception as e:
            print(f"Batch relevance check failed: {e}")
            # Fallback: Mark all as Relevant with error note (to be safe)
            fallback_map = {}
            for art in articles:
                fallback_map[art.get('url_hash')] = {
                    'is_relevant': True,
                    'reason': f"Batch AI Check Failed: {e}"
                }
            return fallback_map

    def analyze_daily_market(self, context_news_list, market_data_str, economic_events_str, region, extra_context=""):
        """
        Analyze multiple news and market data to generate market insights.
        Returns: JSON with sentiment, regime, drivers, scenarios.
        """
        news_text = "\n".join([f"- [{art['published_at']}] {art['title']}: {art['summary'][:200]}" for art in context_news_list])
        
        prompt = textwrap.dedent(f"""
        You are a Senior Market Strategist. Analyze the provided data for the **{region}** market.
        
        ## Input Data
        
        ### 1. Market Data (Snapshot)
        {market_data_str}
        
        ### 2. Economic Calendar (Upcoming)
        {economic_events_str}
        
        ### 3. Key News (Last 24h)
        {news_text}
        
        ### 4. Context & Continuity (Important)
        {extra_context}
        
        ## Analysis Tasks
        1. **Market Regime**: Define the current mood in **Japanese**.
        2. **Sentiment Score**: 0 (Extreme Fear) to 100 (Extreme Greed).
        3. **Primary Driver**: What single factor is driving prices today?
           - **Consistency Check**: Reference the "Context & Continuity" section. Did yesterday's Bull/Bear scenario play out? Did recent economic results match forecasts? Explicitly mention this in your reasoning/driver logic if relevant.
         4. **Reflect on Previous Scenarios**: Reference the "Context & Continuity" section. Did yesterday's **Main/Bull/Bear** scenario play out?
            - **CRITICAL**: You MUST accurately compare the "Yesterday's Analysis Context" with today's "Key News" and "Raw Data".
            - If yes, specifically mention which scenario (Main/Bull/Bear) was hit.
            - If no (surprise), what unexpected factor intervened?

        5. **Scenarios**:
           - **Main Scenario (Base Case)**: The most likely outcome. Write in **Japanese**. **Format**: "Condition -> Result (Specific Marker Change)". Example: "US CPI matches expectation -> S&P500 maintains 6000 level / USDJPY stays at 155".
           - **Bull Case**: Condition for upside. Write in **Japanese**. **Format**: "Condition -> Result (Specific Marker Change)". Example: "Job data cools -> Yields drop to 4.2%, S&P500 rises to 6050".
           - **Bear Case**: Condition for downside. Write in **Japanese**. **Format**: "Condition -> Result (Specific Marker Change)". Example: "Inflation spike -> Yields jump to 4.5%, S&P500 falls below 5900".
           - **Probability Requirement**: Assign a percentage probability (e.g. "60%", "20%", "20%") to Main, Bull, and Bear scenarios. **The sum MUST be 100%.**
           - **Mid-term Outlook (1-2 weeks)**: General trend and key events.
        
        6. **AI Structured Summary**:
           - **summary**: A concise summary (max 200 chars) in **Japanese**.
           - **key_topics**: List of 3-5 key entities in **Japanese**.

        ## Output JSON
        {{
            "market_regime": "リスクオン",
            "sentiment_score": 75,
            "sentiment_label": "Greed",
            "primary_driver": "...",
            "scenarios": {{
                "review": "Verification of yesterday's scenario. e.g., 'Yesterday's Bull case was realized due to...'",
                "main": {{ "condition": "...", "probability": "60%", "target": "..." }},
                "bull": {{ "condition": "...", "probability": "20%", "target": "..." }},
                "bear": {{ "condition": "...", "probability": "20%", "target": "..." }},
                "mid_term": {{ 
                    "view": "Bullish/Neutral/Bearish", 
                    "events": "FOMC (Day X), Earnings (Company Y)", 
                    "risk": "Inflation data..." 
                }}
            }},
            "ai_structured_summary": {{
                "summary": "...",
                "key_topics": ["...", "..."]
            }},
            "reasoning": "Brief reasoning for the score"
        }}
        """)
        
        try:
            response = self._retry_request(
                self.client.models.generate_content,
                model='gemini-3-pro-preview', # High reasoning model
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            result = json.loads(response.text)
            if isinstance(result, list):
                if len(result) > 0:
                    return result[0]
                else:
                    return {}
            return result
        except Exception as e:
            print(f"Market analysis failed: {e}")
            return None

    def write_briefing(self, analysis_result, region, context_news=None, market_data_str=None, events_str=None, date_str=None, internal_links_context=None):
        """
        [Daily Briefing Pipeline]
        Write the final Daily Briefing article in Markdown based on the analysis and raw context.
        This method aggregates multiple data sources (N:1) into a single comprehensive report.
        """
        # Prepare context strings if provided
        news_text = ""
        if context_news:
             news_text = "\n".join([f"- {art['title']}" for art in context_news[:10]]) # Limit to top 10 for context

        prompt = textwrap.dedent(f"""
        You are a Senior Market Analyst at a top-tier Hedge Fund. Write a "Daily Briefing" for the **{region}** market.
        
        ## Input Data
        
        ### 1. Strategy & Analysis (AI Derived)
        {json.dumps(analysis_result, ensure_ascii=False, indent=2)}
        
        ### 2. Market Snapshot (Raw Data)
        {market_data_str if market_data_str else "N/A"}
        
        ### 3. Key News Headlines
        {news_text if news_text else "N/A"}
        
        ### 4. Upcoming Events
        {events_str if events_str else "N/A"}

        ### 5. Internal Link Candidates (Suggestion)
        {internal_links_context if internal_links_context else "N/A"}
        
        ## Goal
        Create a **highly practical, data-dense, and readable** report for Swing Traders. 
        Avoid generic statements. Explain "Why" things moved using specific correlations (e.g., "Yields up -> Tech down").
        
        ## Tone & Style
        - **Professional & Insightful**: Like a Bloomberg terminal note or a bank's morning note.
        - **Japanese Language**: Natural, sophisticated financial Japanese.
        - **Data-First**: Cite specific prices, % changes, and levels from the Raw Data.
        
        ## Structure & Requirements (Japanese Headers Only)
        
        1. **Title**: Catchy, specific, includes the primary driver. (e.g. "CPIショックでハイテク急落；VIXは20台へ")
        
        2. **【{date_str if date_str else 'YYYY/MM/DD'}の市況概要】 (Market Pulse)**
           - **Bold** key numbers.
           - Explain the "Big Picture".
        
        3. **【相場変動の主因】 (Key Drivers)**
           - Analyze the primary driver. Connect it to asset moves.
           - *Must* cite specific news or data points from Input.
           - Explain the mechanism.
            - **Scenario Continuity (CRITICAL)**:
              - Create a subsection `### 昨日のシナリオ検証` (Verification of Previous Scenario).
              - Explicitly state: "Yesterday's Main Scenario (Condition: ...) was [Hit/Missed] because..."
              - Analyze the cause of the outcome (Hit/Miss) specifically as a **primary factor of market fluctuation** (e.g., "The miss was caused by unexpected CPI data," or "The hit was driven by tech sector momentum").
              - **Format Rule**: ALWAYS use `### 昨日のシナリオ検証` as the header. Do NOT use numbered lists or bold text for the header itself.

        
        4. **【注目アセット】 (Asset Watch)**
           - Markdown table summarizing key asset moves.
           - Columns: 資産 (Asset), 価格 (Price), 変化 (Change), コメント (Comment).
           - Select 3-4 relevant assets.
        
        5. **【シナリオ分析】 (Scenarios)**
           - **短期シナリオ (Short-term: 24-48h)**:
             - **メイン (Main)**: Most likely path. (from `scenarios.main`)
             - **アップサイド (Bull)**: Trigger & Target. (from `scenarios.bull`)
             - **ダウンサイド (Bear)**: Trigger & Risk level. (from `scenarios.bear`)
             - **着目イベント**: Specific economic indicator or event to watch in the next 48h.
           
           - **中期シナリオ (Mid-term: 1-2 Weeks)**:
             - **見通し**: Bullish/Neutral/Bearish. (from `scenarios.mid_term.view`)
             - **重要イベント**: Upcoming key events (e.g. FOMC, Earnings). (from `scenarios.mid_term.events`)
             - **リスク**: What could derail the trend? (from `scenarios.mid_term.risk`)
        
        6. **【投資戦略】 (Outlook)**
           - Conclude with clear stance: "押し目買い (Buy Dips)", "戻り売り (Sell Rallies)", "様子見 (Wait)".
           - Provide concrete "Risk Level" (Support/Resistance).

        ## Internal Linking Instructions
        - Use "Internal Link Candidates" (Input 5) if they are highly relevant to the context (e.g. "As detailed in [Title]...").
        - **Format**: `[Title](URL)`
        - **Prioritize**: Links that explain specific concepts, recent analyses, or related themes mentioned in your report.
        - **Natural Integration**: Do not list them blindly. Integrate them into the text or put them as "Reference" at the end of relevant sections.
        
        ## タイトル作成ルール
        1. **文字数**: 32文字程度（検索結果で省略されない長さ）
        2. **キーワード**: 「{region}市場」のような大きな単語は避け、「NVIDIA」「米雇用統計」「ドル円」など、その日最も注目された**具体的な固有名称**を主語にする。
        3. **引き**: 「急騰」「暴落」「転換点」などの強い言葉を使う
        4. **形式**: Markdownの見出しとして出力（# タイトル）
        5. **例**: 「NVIDIA決算で潮目変化：{region}市場のハイテク戦略とドル円の行方」

        ## Format Rules
        - 日本語で4000文字程度
        - Use standard Markdown.
        - **First line MUST be the Title generated by the rules above** (prefixed with `#`).
        - HTML tags are NOT allowed.
        - **DO NOT** use generic titles like "Daily Briefing" or "Market Analysis".
        - **DO NOT** include metadata like "Date:", "Author:", or "Created by" at the top. Start directly with the Title.
        - Use H2 for sections (e.g., ## 【市場概況】).
        - **Use Japanese for ALL Section Headers.**
        - Use Tables where requested.
        """)
        
        try:
            response = self._retry_request(
                self.client.models.generate_content,
                model='gemini-3-pro-preview',
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Briefing writing failed: {e}")
            return None

if __name__ == "__main__":
    # Test generation
    try:
        client = GeminiClient()
        print("GeminiClient initialized successfully.")
    except Exception as e:
        print(f"Initialization failed: {e}")
