import os
import base64
from google import genai
from google.genai import types
from dotenv import load_dotenv
import time
import random

load_dotenv()

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

    def generate_content(self, prompt, model='gemini-2.5-flash', config=None):
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

    def generate_article(self, keyword, article_type="know", context=None):
        """
        Generate an article based on the keyword and content type.
        
        Args:
            keyword: Target keyword
            article_type: 'know' (default), 'buy', 'do', 'news', 'global'
            context: Optional context dict with keys: summary, key_facts, logishift_angle
        """
        
        # Create context section if provided (for News/Global articles)
        if context:
            context_section = f"""
【参考情報】
以下の元記事の情報を基に、LogiShift読者向けの記事を作成してください。
事実関係(数値、固有名詞、主張)は正確に反映してください。

要約: {context['summary']}
重要な事実: {', '.join(context['key_facts'])}
LogiShift視点: {context['logishift_angle']}

"""
            print("Using context for article generation")
        else:
            context_section = ""
            print("Generating from keyword only")
        
        prompts = {
            "know": f"""
            あなたは物流業界のDXエバンジェリストです。以下のキーワードについて、基礎から分かりやすく解説する記事を執筆してください。
            
            キーワード: {keyword}
            
            ## ターゲット
            - 物流担当者、倉庫管理者（基礎知識を求めている）
            
            ## 構成案
            1. **導入**: 読者の課題に共感し、なぜこのキーワードが重要なのかを提示
            2. **基礎知識**: {keyword}とは何か？定義や仕組みを解説
            3. **メリット・重要性**: 導入することで何が変わるのか
            4. **注意点・課題**: 導入や運用の際のハードル
            5. **まとめ**: 次のアクション
            
            ## フォーマット
            - Markdown形式（H2, H3を使用）
            - 2000文字程度
            - 専門用語は噛み砕いて解説
            - **複雑な情報や一覧はMarkdownテーブルを使用して整理する**
            - **【重要】Markdownテーブル内では<br>タグや他のHTMLタグを一切使用禁止。改行が必要な場合は、セル内で自然な文章として記述する**
            
            ## タイトル生成ルール
            - **文字数**: 32文字前後（最大40文字以内）
            - **キーワード配置**: ターゲットキーワード「{keyword}」を可能な限り冒頭に配置
            - **独自性**: 数字、ターゲット層の明示、ベネフィットを含める
            - **パワーワード**: 【徹底解説】【完全版】【図解あり】などを適宜使用
            
            ## タイトルテンプレート（以下のいずれかの形式で生成）
            1. {keyword}とは？[メリット/仕組み]と[導入手順]を[ターゲット]向けに解説
            2. 【徹底解説】{keyword}の基礎知識と導入メリット
            3. {keyword}を[ターゲット]向けに分かりやすく解説
            
            例: WMS（倉庫管理システム）とは？導入メリットと選び方を物流担当者向けに徹底解説
            ## 注意点
            - 信頼感を与えるため自分から物流エバンジェリストですと名乗らないこと
            - **HTMLタグ（<br>, <p>, <div>など）は絶対に使用しないこと** 
            """,
            
            "buy": f"""
            あなたは物流業界のDXエバンジェリストです。以下のキーワードに関連するツールの選び方や比較記事を執筆してください。
            
            キーワード: {keyword}
            
            ## ターゲット
            - ツール導入を検討している経営層、IT担当者
            
            ## 構成案
            1. **導入**: ツール選定の難しさと重要性
            2. **比較のポイント**: 選ぶ際に重視すべき基準（機能、コスト、サポートなど）
            3. **主要なタイプ/製品**: 市場にある主なソリューションの種類と特徴
            4. **メリット・デメリット**: それぞれのタイプの長所と短所
            5. **おすすめの選び方**: 自社に合ったツールの見つけ方
            
            ## フォーマット
            - Markdown形式
            - 比較表を作成すること（Markdownテーブル）
            - **各製品の比較やメリット・デメリットは必ずテーブルで整理する**
            - **【重要】Markdownテーブル内では<br>タグや他のHTMLタグを一切使用禁止。改行が必要な場合は、セル内で自然な文章として記述する**
            - 2500文字程度
            
            ## タイトル生成ルール
            - **文字数**: 32文字前後（最大40文字以内）
            - **キーワード配置**: ターゲットキーワード「{keyword}」を可能な限り冒頭に配置
            - **独自性**: 数字、比較軸、ターゲット層を含める
            - **パワーワード**: 【最新】【完全版】【徹底比較】などを適宜使用
            
            ## タイトルテンプレート（以下のいずれかの形式で生成）
            1. 【2024年最新】{keyword}おすすめ[数字]選！[比較軸]で徹底比較
            2. {keyword}の選び方完全ガイド｜[ターゲット]必見
            3. 失敗しない{keyword}選び｜[比較軸]を徹底解説
            
            例: 【2024年最新】クラウド型WMSおすすめ10選！価格・機能を徹底比較
            
            ## 注意点
            - 信頼感を与えるため自分から物流エバンジェリストですと名乗らないこと
            - **HTMLタグ（<br>, <p>, <div>など）は絶対に使用しないこと** 
            """,
            
            "do": f"""
            あなたは物流業界のDXエバンジェリストです。以下のキーワードに関連する具体的な事例やノウハウ記事を執筆してください。
            
            キーワード: {keyword}
            
            ## ターゲット
            - 現場改善を目指す倉庫管理者、実務担当者
            
            ## 構成案
            1. **導入**: よくある現場の悩み（Before）
            2. **解決策の提示**: {keyword}を活用した具体的な手法（What）
            3. **実践プロセス**: どのように導入・実践するか（How）
            4. **期待される効果**: 導入後の変化（After、定量・定性）
            5. **まとめ**: 成功の秘訣
            
            ## フォーマット
            - Markdown形式
            - 具体的な数字やステップを含める
            - **手順やBefore/Afterの比較はMarkdownテーブルを使用する**
            - **Markdownテーブル内ではHTMLタグ（<br>など）を絶対に使用せず、シンプルなテキストのみを使用する**
            - 2000文字程度
            
            ## タイトル生成ルール
            - **文字数**: 32文字前後（最大40文字以内）
            - **キーワード配置**: ターゲットキーワード「{keyword}」を可能な限り冒頭に配置
            - **独自性**: 課題、ベネフィット、数字を含める
            - **パワーワード**: 【事例あり】【実践ガイド】などを適宜使用
            
            ## タイトルテンプレート（以下のいずれかの形式で生成）
            1. [悩み]を解決！{keyword}を活用した[解決策]とは？【事例あり】
            2. {keyword}で[ベネフィット]を実現する方法
            3. [課題]を[数字]削減！{keyword}活用事例
            
            例: 倉庫のピッキングミスをゼロに！バーコード管理を活用した誤出荷防止策【事例あり】
            
            ## 注意点   
            - 信頼感を与えるため自分から物流エバンジェリストですと名乗らないこと
            """,
            
            "news": f"""
            {context_section}あなたは物流業界のニュースコメンテーターです。以下のキーワードに関する最新トレンドやニュース解説記事を執筆してください。
            
            キーワード: {keyword}
            
            ## ターゲット
            - 業界動向をキャッチアップしたい全層
            
            ## 構成案
            1. **ニュース概要**: 今、何が起きているのか（背景）
            2. **業界への影響**: 物流業界にどのようなインパクトがあるか
            3. **LogiShiftの視点**: 独自の考察、今後の予測
            4. **まとめ**: 企業はどう備えるべきか
            
            ## フォーマット
            - Markdown形式
            - 速報性を意識した簡潔な文体
            - **要点や時系列はMarkdownテーブルを使用して整理する**
            - **Markdownテーブル内ではHTMLタグ（<br>など）を絶対に使用せず、シンプルなテキストのみを使用する**
            - 1500文字程度
            
            ## タイトル生成ルール
            - **文字数**: 32文字前後（最大40文字以内）
            - **キーワード配置**: ターゲットキーワード「{keyword}」を可能な限り冒頭に配置
            - **独自性**: 速報性、影響範囲を含める
            - **パワーワード**: 【速報】【注目】【最新】などを適宜使用
            
            ## タイトルテンプレート（以下のいずれかの形式で生成）
            1. 【速報】{keyword}｜物流業界への影響を解説
            2. {keyword}が物流を変える？最新トレンドを分析
            3. 注目の{keyword}｜[業界/企業]の動向まとめ
            
            例: 【速報】物流2024年問題｜運送業界への影響と対策を徹底解説
            ## 注意点
            - 信頼感を与えるため自分から物流エバンジェリストですと名乗らないこと
            """,
            
            "global": f"""
            {context_section}あなたは物流業界の海外トレンドウォッチャーです。以下のキーワードに関連する海外の最新事例やトレンドを紹介する記事を執筆してください。
            
            キーワード: {keyword}
            
            ## ターゲット
            - イノベーションを求める経営層、新規事業担当者
            
            ## 構成案
            1. **海外の動向**: 米国・中国・欧州などで何が起きているか
            2. **先進事例**: 具体的な企業やスタートアップの取り組み
            3. **日本への示唆**: 日本の物流企業はこれをどう捉え、どう活かすべきか
            4. **まとめ**: 将来の展望
            
            ## フォーマット
            - Markdown形式
            - 日本未上陸の概念や技術を分かりやすく
            - **国別の比較や事例の一覧はMarkdownテーブルを使用する**
            - **Markdownテーブル内ではHTMLタグ（<br>など）を絶対に使用せず、シンプルなテキストのみを使用する**
            - 2000文字程度
            
            ## タイトル生成ルール
            - **文字数**: 32文字前後（最大40文字以内）
            - **キーワード配置**: ターゲットキーワード「{keyword}」を可能な限り冒頭に配置
            - **独自性**: 国名、先進性、日本への示唆を含める
            - **パワーワード**: 【海外事例】【最前線】【日本未上陸】などを適宜使用
            
            ## タイトルテンプレート（以下のいずれかの形式で生成）
            1. 【海外事例】{keyword}｜[国名]の最新動向と日本への示唆
            2. {keyword}の最前線｜米国・中国の先進事例
            3. 日本未上陸の{keyword}｜海外トレンドを徹底解説
            
            例: 【海外事例】倉庫自動化ロボット｜米国の最新動向と日本への示唆
            ## 注意点
            - 信頼感を与えるため自分から物流エバンジェリストですと名乗らないこと
            """
        }
        
        prompt = prompts.get(article_type, prompts["know"])
        
        # Add common formatting instruction
        prompt += """
        
        ## 出力形式
        必ず以下の形式で出力してください：
        
        1行目: # [生成したタイトル]
        2行目: 空行
        3行目以降: 記事本文（導入から始める）
        
        例:
        # WMS（倉庫管理システム）とは？導入メリットと選び方を物流担当者向けに徹底解説
        
        物流倉庫の現場で働く担当者や倉庫管理者の皆様なら...
        """
        
        try:
            response = self._retry_request(
                self.client.models.generate_content,
                model='gemini-2.5-pro',
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Error generating content: {e}")
            return None

    def generate_image(self, prompt, output_path, aspect_ratio="16:9"):
        """
        Generate an image using Imagen 3.0.
        """
        try:
            print(f"Generating image with Imagen 3.0 for prompt: {prompt}")
            
            # google-genai implementation
            response = self._retry_request(
                self.client.models.generate_images,
                model='imagen-3.0-generate-001',
                prompt=prompt,
                config={
                    'aspect_ratio': aspect_ratio
                }
            )
            
            # Extract image from response
            if response.generated_images:
                image_bytes = response.generated_images[0].image.image_bytes
                
                with open(output_path, 'wb') as f:
                    f.write(image_bytes)
                print(f"Image saved to: {output_path}")
                return output_path
            
            print("No image generated in response.")
            return None
                
        except Exception as e:
            print(f"Failed to generate image: {e}")
            import traceback
            traceback.print_exc()
            return None

    def generate_image_prompt(self, title, content_summary, article_type="know"):
        """
        Generate an optimized English image prompt based on article title and content.
        
        Args:
            title: Article title
            content_summary: Brief summary or first paragraph of the article
            article_type: Type of article (know, buy, do, news, global)
        
        Returns:
            English image prompt optimized for Imagen 3.0
        """
        prompt = f"""
        You are an expert at creating image generation prompts for Imagen 3.0.
        
        Based on the following article information, create a detailed English image prompt that:
        1. Captures the main theme and context of the article
        2. Is specific and descriptive (not abstract)
        3. Focuses on logistics/warehouse/supply chain context
        4. Is photorealistic and professional
        5. Avoids text, people's faces, or complex diagrams
        
        Article Title: {title}
        Article Type: {article_type}
        Content Summary: {content_summary[:500]}
        
        Generate a single, detailed English image prompt (max 100 words) that would create a compelling hero image for this article.
        Output ONLY the prompt text, no explanations.
        """
        
        try:
            response = self._retry_request(
                self.client.models.generate_content,
                model='gemini-2.5-pro',
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error generating image prompt: {e}")
            # Fallback to simple prompt
            return f"Professional logistics warehouse scene related to {title}, photorealistic, high quality, 4k"

    def classify_content(self, content):
        """
        Classify the article content into categories and tags.
        """
        prompt = f"""
        You are an expert content classifier for a logistics media site.
        Analyze the following article content and classify it.

        Content:
        {content[:3000]}... (truncated)

        Output JSON format:
        {{
            "category": "one of [warehouse-management, logistics-dx, material-handling, 2024-problem, cost-reduction, global-logistics]",
            "industry_tags": ["list", "of", "relevant", "industries", "e.g.", "manufacturing", "retail", "ecommerce", "3pl-warehouse", "transportation"],
            "theme_tags": ["list", "of", "relevant", "themes", "e.g.", "labor-shortage", "automation", "cost-reduction", "quality-improvement", "safety", "environment"]
        }}
        """
        
        try:
            response = self._retry_request(
                self.client.models.generate_content,
                model='gemini-2.5-pro',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            import json
            return json.loads(response.text)
        except Exception as e:
            print(f"Classification failed: {e}")
            import traceback
            traceback.print_exc()
            return None

if __name__ == "__main__":
    # Test generation
    try:
        client = GeminiClient()
        print("GeminiClient initialized successfully.")
    except Exception as e:
        print(f"Initialization failed: {e}")
