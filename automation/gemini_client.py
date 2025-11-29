import os
import base64
from google import genai
from google.genai import types
from dotenv import load_dotenv

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

    def generate_article(self, keyword, article_type="know"):
        """
        Generate an article based on the keyword and content type.
        
        Args:
            keyword: Target keyword
            article_type: 'know' (default), 'buy', 'do', 'news', 'global'
        """
        
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
            - **Markdownテーブル内ではHTMLタグ（<br>など）を使用せず、シンプルなテキストのみを使用する**
            - タイトル: [魅力的な記事タイトル]
            ## 注意点
            - 信頼感を与えるため自分から物流エバンジェリストですと名乗らないこと 
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
            - **Markdownテーブル内ではHTMLタグ（<br>など）を使用せず、シンプルなテキストのみを使用する**
            - 2500文字程度
            - タイトル: [比較・選定ガイドのタイトル]
            
            ## 注意点
            - 信頼感を与えるため自分から物流エバンジェリストですと名乗らないこと 
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
            - **Markdownテーブル内ではHTMLタグ（<br>など）を使用せず、シンプルなテキストのみを使用する**
            - 2000文字程度
            - タイトル: [事例・ノウハウ記事タイトル]
            
            ## 注意点
            - 信頼感を与えるため自分から物流エバンジェリストですと名乗らないこと
            """,
            
            "news": f"""
            あなたは物流業界のニュースコメンテーターです。以下のキーワードに関する最新トレンドやニュース解説記事を執筆してください。
            
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
            - **Markdownテーブル内ではHTMLタグ（<br>など）を使用せず、シンプルなテキストのみを使用する**
            - 1500文字程度
            - タイトル: [ニュース解説タイトル]
            ## 注意点
            - 信頼感を与えるため自分から物流エバンジェリストですと名乗らないこと
            """,
            
            "global": f"""
            あなたは物流業界の海外トレンドウォッチャーです。以下のキーワードに関連する海外の最新事例やトレンドを紹介する記事を執筆してください。
            
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
            - **Markdownテーブル内ではHTMLタグ（<br>など）を使用せず、シンプルなテキストのみを使用する**
            - 2000文字程度
            - タイトル: [海外トレンド記事タイトル]
            ## 注意点
            - 信頼感を与えるため自分から物流エバンジェリストですと名乗らないこと
            """
        }
        
        prompt = prompts.get(article_type, prompts["know"])
        
        # Add common formatting instruction
        prompt += """
        
        [記事本文]
        """
        
        try:
            response = self.client.models.generate_content(
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
            response = self.client.models.generate_images(
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
            response = self.client.models.generate_content(
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
