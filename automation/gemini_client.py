import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = os.getenv("GOOGLE_CLOUD_LOCATION")
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.use_vertex = False

        if self.api_key:
            print("Initializing Gemini with API Key")
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        elif self.project_id and self.location:
            print(f"Initializing Gemini with Vertex AI (Project: {self.project_id}, Location: {self.location})")
            try:
                import vertexai
                from vertexai.generative_models import GenerativeModel
                vertexai.init(project=self.project_id, location=self.location)
                self.model = GenerativeModel("gemini-1.5-flash-001")
                self.use_vertex = True
            except ImportError:
                print("Error: google-cloud-aiplatform not installed or vertexai import failed.")
                raise
        else:
            raise ValueError("Missing Gemini credentials. Set GEMINI_API_KEY or GOOGLE_CLOUD_PROJECT/LOCATION in .env")

    def generate_article(self, keyword):
        """
        Generate an article based on the keyword.
        """
        prompt = f"""
        あなたは物流業界の専門家です。以下のキーワードで、専門的かつ分かりやすい記事を執筆してください。
        
        キーワード: {keyword}
        
        ## 条件
        - ターゲット: 物流担当者、倉庫管理者、経営層
        - 構成: 導入、課題、解決策、まとめ の流れを含めること
        - フォーマット: Markdown形式（H2, H3を使用）
        - 文字数: 2000文字程度
        - 文体: です・ます調
        
        ## 出力形式
        タイトル: [記事タイトル]
        
        [記事本文]
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating content: {e}")
            return None

if __name__ == "__main__":
    # Test generation
    try:
        client = GeminiClient()
        print("GeminiClient initialized successfully.")
    except Exception as e:
        print(f"Initialization failed: {e}")
