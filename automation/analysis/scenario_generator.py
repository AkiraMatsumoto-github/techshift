import sys
import os
import json
import textwrap
from google.genai import types

# Add parent directory to path to import GeminiClient
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from gemini_client import GeminiClient

class ScenarioGenerator:
    def __init__(self):
        self.client = GeminiClient()

    def generate_scenario(self, article_text, article_meta=None):
        """
        Generate a trading scenario (Main vs Risk) based on the article text.
        
        Args:
            article_text (str): Full text or summary of the news article.
            article_meta (dict): Optional metadata (title, source, etc.)
        
        Returns:
            dict: Structured scenario data (JSON).
        """
        
        # Prepare context info
        meta_info = ""
        if article_meta:
            meta_info = f"Title: {article_meta.get('title', 'N/A')}\nSource: {article_meta.get('source', 'N/A')}\n"

        prompt = textwrap.dedent(f"""
        You are a professional market strategist for swing traders (holding period: days to weeks).
        Analyze the provided news/market data and generate a trading scenario.
        
        ## Input Data
        {meta_info}
        Content:
        {article_text[:5000]}... (truncated if too long)
        
        ## Logic: Dynamic Dual-Track (Main vs Risk)
        1. **Market Sentiment Check**: First, determine if the news is clearly Bullish, Bearish, or Mixed/Neutral.
        2. **Scenario Construction**:
           - **Main Scenario**: The most likely outcome based on the news (Probability > 50%).
             - Should include the rationale and key price levels (Support/Resistance) if applicable.
           - **Risk Scenario**: The alternative outcome or what could go wrong (Probability < 50%).
             - Crucial for risk management. Define invalidation levels (Stop Loss).
        
        ## Strategy Guidelines for Swing Traders
        - **Actionable**: Output must help decide whether to Buy, Sell, or Wait.
        - **Specific**: Avoid vague terms. Use "Break above resistance" or "Earnings beat expectation".
        - **Balanced**: Always provide a "Risk" scenario to prevent blind optimism/pessimism.
        
        ## Output Format (JSON Only)
        Strictly output valid JSON. No markdown fencing (```json ... ```) is needed if possible, but handle if present.
        
        {{
          "market_sentiment": "Bullish" | "Bearish" | "Mixed",
          "confidence_score": 0.85, 
          "main_scenario": {{
            "direction": "Bullish" | "Bearish" | "Neutral",
            "probability": "70%",
            "headline": "Brief, punchy headline for the main view (Japanese)",
            "rationale": "Why this will happen (Japanese)",
            "key_levels": "e.g., Target: $150, Support: $135"
          }},
          "risk_scenario": {{
            "direction": "Bearish" | "Bullish" | "Neutral",
            "probability": "30%",
            "headline": "Brief headline for the risk view (Japanese)",
            "rationale": "What invalidates the main view (Japanese)",
            "invalidation_level": "e.g., Close below $130"
          }},
          "action_plan": {{
            "recommendation": "Buy" | "Sell" | "Wait & See" | "Buy on Dip",
            "timeframe": "1-2 weeks"
          }}
        }}
        """)

        try:
            # Use the retry logic from GeminiClient, accessing the raw client model
            response = self.client._retry_request(
                self.client.client.models.generate_content,
                model='gemini-3-pro-preview',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            # Parse JSON
            try:
                # Remove markdown code blocks if present
                text = response.text.strip()
                if text.startswith("```json"):
                    text = text[7:]
                if text.endswith("```"):
                    text = text[:-3]
                return json.loads(text)
            except json.JSONDecodeError as e:
                print(f"JSON Parse Error: {e}")
                print(f"Raw Output: {response.text}")
                return None

        except Exception as e:
            print(f"Scenario generation failed: {e}")
            return None

if __name__ == "__main__":
    # Test Run
    generator = ScenarioGenerator()
    test_text = """
    Apple reported quarterly revenue of $119.6 billion, up 2% year over year, and quarterly earnings per diluted share of $2.18, up 16% year over year. 
    The results beat analyst expectations. CEO Tim Cook highlighted strong services growth and the upcoming Vision Pro launch. 
    However, China sales dropped 13%, raising concerns about competition from Huawei.
    """
    print("Generating scenario for test article...")
    result = generator.generate_scenario(test_text, {"title": "Apple Earnings Beat, China Sales Lag"})
    print(json.dumps(result, indent=2, ensure_ascii=False))
