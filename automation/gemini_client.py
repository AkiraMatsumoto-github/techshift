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

    def generate_article(self, keyword, article_type="topic-focus", context=None, extra_instructions=None, category=None):
        """
        Generate a full blog article in Markdown format.
        
        Args:
            keyword: Main topic or title.
            article_type: "topic-focus" (Deep Dive) is the primary type.
        """
        print(f"Generating article for keyword: {keyword} (Type: {article_type}, Category: {category})")
        
        # Normalize type: 'featured-news' -> 'topic-focus'
        if article_type == 'featured-news':
            article_type = 'topic-focus'
            
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
            # --- TechShift Primary Prompt ---
            # [Topic Deep Dive] Single article focus.
            "topic-focus": textwrap.dedent(f"""
            {context_section}あなたは専門技術アナリスト（Tech Analyst）です。
            特定の技術トピック（{keyword}）について、ロードマップへの影響を深掘りする解説記事を執筆してください。
            
            キーワード: {keyword}
            
            ## ターゲット
            - その技術の実用化時期を真剣に追っているエンジニアや投資家
            
            ## 執筆ロジック (Level 2 Granularity)
            - 単に「実用化」だけでなく、「技術的絶対条件 (Prerequisites)」の達成度にフォーカスする。
            - 例: "全固体電池の実用化" ではなく "電解質伝導率 10mS/cm の達成" に注目。
            
            ## 構成案
            1. **Impact Assessment (影響評価)**:
               - このニュースはロードマップを「加速」させたか、「遅延」させたか、それとも「維持」か。
               - 結論を最初に提示。
            2. **Technical Deep Dive (技術的詳細)**:
               - 具体的に何のスペックが向上したのか（精度、速度、コスト、耐久性）。
               - 従来技術（SOTA）との比較。
            3. **Bottleneck Analysis (ボトルネック分析)**:
               - 次に残されている課題は何か（量産性、法規制、電力消費など）。
            4. **Revised Timeline (予測修正)**:
               - この成果により、実用化予想時期がどう変動するか。
               - "2028 Q3" のように具体的に記述。
            
            ## 執筆ルール
            - **一次情報主義**: 論文や公式リリースに基づく事実のみを扱う。噂レベルは除外。
            - **冷静な評価**: "革命的" "破壊的" といった形容詞を避け、数値で語る。
            
            ## フォーマット
            - Markdown形式
            - 3000文字程度
            - 技術仕様はテーブルで比較
            - HTMLタグ使用禁止
            
            ## タイトル作成ルール
            - **形式**: [技術名] [動詞/状態]：[影響]
            - **例**: 全固体電池の電解質劣化問題を解決：2027年量産への道筋
            """)
        }
        
        # Select prompt
        prompt = prompts.get(article_type, prompts["topic-focus"])
        
        if extra_instructions:
            prompt += f"\n\n{extra_instructions}\n"
        
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
        
        **【重要】Markdown記述ルール:**
        - **リスト（箇条書き）の前には必ず空行を入れること。**
        - **ネスト（入れ子）したリストのインデントは必ず半角スペース4つ（4 spaces）を使用すること。**
        
        例:
        # 【技術解説】次世代半導体パッケージング技術の突破口
        
        ## 1. Executive Summary
        MITの研究チームが発表した新しい...
        
        ## 2. Technical Spec
        | 項目 | 今回の成果 | 従来技術 |
        | :--- | :--- | :--- |
        | 配線密度 | ... | ... |
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


    def generate_image_prompt(self, title, content_summary, article_type="topic-focus"):
        """
        Generate an optimized English image prompt based on article title and content.
        
        Args:
            title: Article title
            content_summary: Brief summary
            article_type: Type of article (topic-focus, daily-briefing)
        
        Returns:
            English image prompt optimized for Imagen 3.0/Gemini 2.5
        """
        prompt = textwrap.dedent(f"""
        You are an expert at creating image generation prompts for Imagen 3.0.
        
        Based on the following article information, create a detailed English image prompt that:
    1. **Theme**: "Future Technology", "Innovation", "Cyberpunk/High-Tech Sci-Fi".
    2. **Visual Metaphors**: 
       - **Futuristic**: Neon lights, data streams, holograms, advanced robotics, space exploration.
       - **Abstract**: Geometric patterns, circuit boards, glowing nodes connecting (representing networks).
    3. **Style**: Premium, Editorial, "Wired Magazine" or "The Verge" feature image style. High contrast, vibrant colors (Cyan, Magenta, Deep Blue).
    4. **Lighting**: Cinematic, Volumetric lighting, Ray tracing vibes.
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
            return f"Futuristic technology background related to {title}, cyberpunk style, high quality, 4k"



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
            - サイト名: TechShift（テックシフト）
            - 運営者: TechShift編集部
            - 設立: 2026年1月
            - 目的: 技術ロードマップの可視化・予測情報の提供
            - 使用技術: Googleアナリティクス、Cookie
            - お問い合わせ: info@finshift.net
            
            ## 含めるべき項目
            1. 個人情報の取り扱いについて
            2. 収集する情報の種類（アクセスログ、Cookie等）
            3. 利用目的（サイト改善、統計分析等）
            4. 第三者提供（Googleアナリティクス等）
            5. Cookie・アクセス解析ツールについて
            6. 免責事項（本サイトの情報は予測であり、正確性を保証するものではない旨）
            7. 個人情報の開示・訂正・削除について
            8. お問い合わせ先
            9. 制定日・改定日
            
            ## 出力形式
            - Markdown形式で出力
            - 見出しはH2（##）とH3（###）を使用
            - 箇条書きや表を適宜使用
            - 法的に正確で、かつ読みやすい文章
            - 最後に「制定日: 2026年1月1日」を記載
            
            ## 注意点
            - 専門用語は分かりやすく説明
            - **技術予測・投資判断は自己責任**であるという免責を必ず含める
            - 連絡先を明記
            """),
            
            "about": textwrap.dedent("""
            あなたはコーポレートコミュニケーションの専門家です。
            以下の情報を基に、TechShiftの運営者情報ページを作成してください。
            
            【サイト情報】
            - サイト名: TechShift（テックシフト）
            - 運営者: TechShift編集部
            - 設立: 2026年1月
            - お問い合わせ: info@finshift.net
            
            【ビジョン: "Dynamic Navigation Chart"】
            既存の静的なロードマップ（PDF）を過去のものとし、
            日々のニュース解析を通じてリアルタイムで更新され続ける「動的航海図」を提供する。
            
            【ターゲット読者: "Visionary Practitioner"】
            企業のCTO、R&D責任者、新規事業担当者。
            技術の進化が速すぎて戦略が陳腐化する不安を持つリーダーたち。
            
            【主なコンテンツ】
            - Daily Briefing: 全セクターを横断した日刊技術予測
            - Deep Dive: 特定技術（全固体電池、AGI等）の実用化時期予測
            - Roadmap: 動的に変化する技術ロードマップの可視化
            
            ## 含めるべき項目
            1. TechShiftについて（サイトの目的・ビジョン「Dynamic Navigation Chart」）
            2. 基本情報（サイト名、運営者、設立年、お問い合わせ先）をテーブル形式で
            3. ミッション・提供価値（点ではなく線で見る、一次情報の徹底、波及の可視化）
            4. 主なコンテンツカテゴリの紹介
            5. 想定読者
            6. お問い合わせ先
            
            ## 出力形式
            - Markdown形式で出力
            - 見出しはH2（##）とH3（###）を使用
            - 基本情報はMarkdownテーブルで整理
            - 先進的で、信頼感があり、ビジョナリーな文章
            - 未来への情熱が伝わる内容
            """),
            
            "contact": textwrap.dedent("""
            あなたはカスタマーサポートの専門家です。
            以下の情報を基に、TechShiftのお問い合わせページを作成してください。
            
            【サイト情報】
            - サイト名: TechShift（テックシフト）
            - 運営者: TechShift編集部
            - お問い合わせ: info@finshift.net
            - 対応時間: 平日 10:00-18:00（土日祝日を除く）
            
            ## 含めるべき項目
            1. お問い合わせについて（導入文）
            2. お問い合わせ方法（メールアドレス）
            3. 対応時間
            4. お問い合わせ内容の例（記事の内容確認、プレスリリース送付、取材依頼など）
            5. 返信までの目安時間
            6. 注意事項（個人情報の取り扱いなど）
            
            ## 出力形式
            - Markdown形式で出力
            - 見出しはH2（##）とH3（###）を使用
            - 箇条書きを適宜使用
            - 丁寧で分かりやすい文章
            - お問い合わせしやすい雰囲気
            
            ## 注意点
            - メールアドレスは必ず記載
            - 対応時間を明記
            - プライバシーポリシーへのリンクを案内
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
        You are an expert content analyst. Analyze the following tech article and generate a structured summary in JSON format.
        This summary will be used by an AI system to identify relevant internal links.
        IMPORTANT: The content is Japanese, so the 'summary' and 'key_topics' MUST be written in Japanese.

        Article Content:
        {content[:4000]}... (truncated)

        Output JSON format (Strictly JSON only):
        {{
            "summary": "Detailed summary of the article content (300-500 chars) in Japanese. Focus on technical specifics and timeline impacts.",
            "key_topics": ["list", "of", "specific", "technologies", "covered", "(in Japanese)"],
            "entities": ["list", "of", "companies", "products", "or", "research_labs", "mentioned", "(preserve original names)"],
            "timeline_impact": "Brief description of how this affects the roadmap (Accelerated/Delay/Unchanged) in Japanese.",
            "technical_bottleneck": "Describe the technical bottleneck mentioned (if any) in Japanese."
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
        You are an expert social media manager for a futuristic tech media site "TechShift".
        Create an engaging X (Twitter) post content based on the following article.
        
        Target Audience: CTOs, R&D Leaders, Tech Investors (Visionary Practitioners).
        Goal: Maximize Engagement by appealing to "Deep Insight" and "Future Impact".
        
        Article Title: {title}
        Article Type: {article_type}
        Content (excerpt):
        {truncated_content}
        
        Requirements:
        1. **Hook**: A provocative opening. Focus on "What changed in the future timeline".
           - MUST include 1 relevant emoji (�, 🧬, 🤖, ⚛️, etc.).
           - Max 60 chars.
        2. **Summary**: Intellectual teaser. "Why this matters for the roadmap".
           - Focus on solving bottlenecks or new possibilities.
           - Max 120 chars.
        3. **Hashtags**: 5 hashtags optimized for Tech Communities.
           - **Required**:
             - Relevant Tech Keywords (e.g., #GenAI, #Quantum, #SolidStateBattery).
             - **Middle Words**: #技術戦略, #未来予測, #R_and_D (Avoid just #Technology).
             - Specific companies/labs if mentioned.
           - **Goal**: Reach professionals, not casual readers.
        
        4. Language: Japanese. 
        5. **Tone**: Visionary, Concise, Leading-edge. "Don't just read the news, read the future."
        
        Output JSON format (Strictly JSON only):
        {{
            "hook": "🚀 GPT-5の推論能力が、創薬タイムラインを「2年」短縮する。",
            "summary": "従来のスクリーニング手法は過去のものに。マルチエージェントシステムが解決した「3つのボトルネック」とは？",
            "hashtags": ["#GenerativeAI", "#DrugDiscovery", "#NVIDIA", "#BioTech", "#技術戦略"]
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
                "hook": f"{title}",
                "summary": "最新の技術動向とロードマップへの影響を分析しました。",
                "hashtags": ["#TechShift", "#DeepTech", "#FutureTrends", "#Innovation"]
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
        You are a duplicate content detector for a technology foresight media "TechShift".
        Determine if the "New Article" covers the **same specific news topic** as any of the "Existing Articles".
        
        Rule:
        - Return the EXACT title of the existing article ONLY if they are about the same specific news event or announcement.
        - If the new article is just a general topic match (e.g. both are about "Quantum Computing") but different specific news, return "None".
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
                "summary": art.get('summary', '')[:500] 
            })
            
        prompt = f"""
        You are a "Deep Tech" news filter for TechShift.
        Analyze the following list of articles and determine if EACH one is relevant to **Engineering, R&D, Science, or Future Technology Analysis**.
        
        Criteria for "Relevant":
        - **Scientific Breakthroughs**: New discoveries in AI, Quantum, Bio, Energy, Space.
        - **Engineering Milestones**: Successful tests (e.g., Starship launch), pilot plant openings, efficiency records.
        - **Strategic Business**: M&A in deep tech, huge VC funding rounds, major government regulation on tech.
        
        Criteria for "Not Relevant" (Noise):
        - **Consumer Gadgets**: Smartwatch reviews, minor iPhone updates (unless revolutionary).
        - **General Politics**: Elections (unless directly affecting tech policy).
        - **Celebrity/Gossip**: Tech CEO scandals (unless affecting company roadmap).
        - **Short-term Stock Noise**: Daily price fluctuation without fundamental news.
        
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
            # Fallback: Mark all as Relevant with error note
            fallback_map = {}
            for art in articles:
                fallback_map[art.get('url_hash')] = {
                    'is_relevant': True,
                    'reason': f"Batch AI Check Failed: {e}"
                }
            return fallback_map

    def analyze_tech_impact(self, context_news_list, market_data_str, economic_events_str, region, extra_context=""):
        """
        Analyze tech news AND market data to generate "Future Insight" (Evolution Phase & Timeline Impact).
        Returns: JSON with evolution_phase, timeline_impact, hero_topic, scenarios.
        """
        news_text = "\n".join([f"- [{art['published_at']}] {art['title']}: {art['summary'][:200]}" for art in context_news_list])
        
        prompt = textwrap.dedent(f"""
        You are the "Future Foresight Engine" for TechShift. Analyze the provided data for the **{region}** region.
        
        ## Input Data
        
        ### 1. Macro Context (Investment Climate)
        - Market/Econ Data: {market_data_str}
        - Note: Use this to judge "VC Funding Environment" or "Cost of Capital" for Deep Tech.
        
        ### 2. Tech News (Last 24h)
        {news_text}
        
        ### 3. Context & Continuity
        {extra_context}
        
        ## Analysis Tasks
        1. **Evolution Phase**: Define the current global tech phase in **Japanese**.
           - Examples: "生成AIの幻滅期入り", "量子技術の実用化前夜", "宇宙開発の商業化加速".
        2. **Timeline Impact**: 0 (Severe Delay) to 100 (Massive Acceleration). 50 is Neutral.
        3. **Hero Topic**: What single technology/topic is most critical today?
           - **Consistency Check**: Reference "Context". Is this a follow-up to yesterday's breakthrough?
        
        4. **Scenarios (The TechShift Logic)**:
           - **Main Scenario (Base Case)**: Most likely timeline evolution.
             - **Format**: "Event -> Impact on Roadmap".
             - **Example**: "OpenAIの新モデル発表 -> エージェント開発が加速し、2025年の実用化予測を維持".
           - **Accelerated Case (Bull)**: What could speed things up?
             - **Example**: "規制緩和が早期に実現 -> ドローン配送の全国展開が1年前倒し".
           - **Delayed Case (Bear)**: What are the risks/bottlenecks?
             - **Example**: "GPU供給不足が長期化 -> 大規模モデルの学習が停滞し、AGI到達が遅延".
           
           - **Probability**: Assign stats (Must sum to 100%).
        
        5. **AI Structured Summary**:
           - **summary**: Concise summary in **Japanese**.
           - **key_topics**: List of 3-5 tech keywords in **Japanese**.

        ## Output JSON
        {{
            "evolution_phase": "AI実装フェーズ (Implementation Phase)",
            "timeline_impact": 75, # 0-100 Impact Score (High = Acceleration)
            "impact_label": "Accelerated", # Label (Accelerated/Delayed/Neutral)
            "hero_topic": "...", # Hero Topic (formerly primary_driver)
            "scenarios": {{
                "review": "Verification of yesterday's view. e.g., 'The bottleneck identified yesterday is resolving...'",
                "main": {{ 
                    "condition": "Main timeline projection", 
                    "probability": "60%"
                }},
                "bull": {{ 
                    "condition": "Acceleration scenario", 
                    "probability": "20%"
                }},
                "bear": {{ 
                    "condition": "Delay/Bottleneck scenario", 
                    "probability": "20%"
                }},
                "mid_term": {{ 
                    "view": "Positive/Neutral/Negative", 
                    "events": "CES 2026, SpaceX Launch", 
                    "risk": "Regulatory Change" 
                }}
            }},
            "ai_structured_summary": {{
                "summary": "...",
                "key_topics": ["...", "..."]
            }},
            "reasoning": "Reasoning for the impact score"
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
            print(f"Tech Impact Analysis failed: {e}")
            return None

    def write_briefing(self, analysis_result, region, context_news=None, market_data_str=None, events_str=None, date_str=None, internal_links_context=None):
        """
        [Daily Briefing Pipeline]
        Write the final Daily Briefing article in Markdown based on the analysis and raw context.
        """
        # Prepare context strings
        news_text = ""
        if context_news:
             news_text = "\n".join([f"- {art['title']}" for art in context_news[:10]])

        prompt = textwrap.dedent(f"""
        You are the Editor-in-Chief of "TechShift". Write a "Daily Briefing" for the **{region}** region.
        
        ## Input Data
        
        ### 1. Future Insight (AI Strategy)
        {json.dumps(analysis_result, ensure_ascii=False, indent=2)}
        
        ### 2. Macro Context (Raw Data)
        {market_data_str if market_data_str else "N/A"}
        
        ### 3. Key Tech News
        {news_text if news_text else "N/A"}
        
        ### 4. Internal Links (Reference)
        {internal_links_context if internal_links_context else "N/A"}
        
        ## Goal
        Create a **Visionary, Insightful, and Logic-Driven** report.
        Focus on "Connecting Dots" (Line) rather than just reporting news (Point).
        
        ## Tone & Style
        - **Visionary & Sharp**: "Wired" meets "McKinsey Report".
        - **Japanese Language**: High-quality, professional Japanese.
        - **Data-Backed**: Cite specs, funding amounts, and dates.
        
        ## Output Structure (Japanese Headers)
        
        1. **Title**: Generated based on rules below.
        
        2. **【The Shift】 (今日の結論)**
           - Define how the "Humanity's Timeline" shifted today.
           - e.g., "AGI is 6 months closer," "Fusion power hits a cost wall."
           - **Bold** the key conclusion.
        
        3. **【Hero Topic: {analysis_result.get('hero_topic', analysis_result.get('primary_driver', 'Top Story'))}】**
           - Deep dive into the most important topic.
           - **Logic Chain**: Fact -> Analysis -> Future Impact.
           - Use `### 昨日のシナリオ検証` (Verification) here to check continuity if relevant.
        
        4. **【Cross-Sector Signals】 (他分野への波及)**
           - How does today's hero topic affect other sectors?
           - e.g., "AI improvement -> Robotics training acceleration."
           - Use bullet points.
        
        5. **【Reality Check】 (実態検証)**
           - **Bottleneck Analysis**: What stops this from happening tomorrow? (Cost, Law, Energy).
           - **Cost of Capital**: Mention Macro Environment (Interest rates) influence on VC/Deep Tech if relevant.
        
        6. **【Scenarios】 (未来予測)**
           - **Scenarios Table**: Create a Markdown table comparing Main, Accelerated, and Delayed scenarios.
           - **Mid-term Outlook**: Next big events (Conferences, Keep Launches).
        
        ## Internal Linking
        - Integrate relevant links from "Internal Links Context" naturally into the text.
        - Format: `[Title](URL)`
        
        ## Title Rules
        1. **Format**: 【Daily Shift】[Hero Topic]が変えた未来｜[Sub-Title]
        2. **Keywords**: Concrete names (OpenAI, Toyota, Starship).
        3. **Example**: 「【Daily Shift】GPT-5が創薬を2年加速｜「実験室」から「データセンター」へ」
        
        ## Format Rules
        - Markdown, approx 4000 chars.
        - **First line MUST be Title** (with #).
        - No HTML.
        - Use Japanese headers (e.g., ## 【The Shift】).
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
