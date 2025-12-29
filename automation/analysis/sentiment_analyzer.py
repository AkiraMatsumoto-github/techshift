import sys
import os
import json
import textwrap
from google.genai import types

# Add parent directory to path to import GeminiClient
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from gemini_client import GeminiClient

class SentimentAnalyzer:
    def __init__(self):
        self.client = GeminiClient()

    def analyze_sentiment(self, market_data_path, headlines):
        """
        Calculate a "FinShift Sentiment Index" (0-100) based on:
        1. Technical Data (VIX, S&P500 Momentum)
        2. News Sentiment (AI Analysis of Headlines)
        
        Args:
            market_data_path (str): Path to risk_monitor.json
            headlines (list): List of news headlines strings.
        
        Returns:
            dict: {"score": int, "label": str, "rationale": str}
        """
        
        # 1. Load Market Data (Technical)
        technical_score = 50 # Default Neutral
        technical_context = ""
        
        try:
            with open(market_data_path, 'r') as f:
                market_data = json.load(f)
                
            data_map = {item['symbol']: item for item in market_data.get('data', {}).get('indices', [])}
            
            # VIX Logic (Fear Gauge)
            # VIX > 30 = Extreme Fear (Score < 25)
            # VIX < 15 = Greed (Score > 75)
            vix_data = data_map.get('^VIX')
            sp500_data = data_map.get('^GSPC')
            
            if vix_data:
                vix = vix_data['price']
                # Inverse relationship: Low VIX -> High Score (Greed)
                # Normalize VIX roughly: 10(Greed) to 40(Fear) mapping to 100-0
                # Formula: 100 - ((VIX - 10) * 3.33)  roughly
                v_score = max(0, min(100, 100 - ((vix - 12) * 3)))
                technical_context += f"VIX: {vix} (Score contribution: {v_score:.0f}). "
            else:
                v_score = 50
                
            # Momentum Logic (S&P 500 1W Change)
            if sp500_data:
                change_1w = sp500_data['changes']['1w']
                # +2% = Strong Greed, -2% = Strong Fear
                m_score = 50 + (change_1w * 10)
                m_score = max(0, min(100, m_score))
                technical_context += f"S&P500 1W: {change_1w}% (Score contribution: {m_score:.0f})."
            else:
                m_score = 50
                
            technical_score = (v_score * 0.6) + (m_score * 0.4)
            
        except Exception as e:
            print(f"Error reading market data: {e}")
            technical_context = "Market data unavailable."

        # 2. News Analysis (AI)
        headlines_text = "\n".join([f"- {h}" for h in headlines[:20]]) # Limit to top 20
        
        prompt = textwrap.dedent(f"""
        You are a Market Sentiment Analyst. 
        Calculate a "Market Sentiment Score" (0-100) based on the supplied news headlines and technical context.
        
        0 = Extreme Fear (Panic, Crash)
        50 = Neutral
        100 = Extreme Greed (Euphoria)
        
        ## Technical Context
        {technical_context}
        (Note: VIX suggests volatility level, S&P500 change suggests momentum)
        
        ## Recent Headlines
        {headlines_text}
        
        ## Task
        1. Analyze the headlines for overall tone (Bullish/Bearish).
        2. Combine with technical context.
        3. Output the final score, label, and a brief rationale explain why.
        
        Output JSON:
        {{
            "score": 65,
            "label": "Greed" | "Fear" | "Neutral" | "Extreme Greed" | "Extreme Fear",
            "rationale": "VIX is stable at 14 indicating complacency, and headlines are dominated by positive earnings..."
        }}
        """)
        
        try:
             response = self.client._retry_request(
                self.client.client.models.generate_content,
                model='gemini-3-pro-preview',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
             
             text = response.text.strip()
             if text.startswith("```json"):
                 text = text[7:]
             if text.endswith("```"):
                 text = text[:-3]
             return json.loads(text)
             
        except Exception as e:
            print(f"Sentiment analysis failed: {e}")
            # Fallback to technical score only
            label = "Neutral"
            if technical_score > 75: label = "Extreme Greed"
            elif technical_score > 60: label = "Greed"
            elif technical_score < 25: label = "Extreme Fear"
            elif technical_score < 40: label = "Fear"
            
            return {
                "score": int(technical_score),
                "label": label,
                "rationale": f"AI Analysis failed. Based on Technicals only: {technical_context}"
            }

if __name__ == "__main__":
    # Test
    analyzer = SentimentAnalyzer()
    dummy_headlines = [
        "S&P 500 hits fresh record high on AI optimism",
        "Inflation cools more than expected in November",
        "Fed signals three rate cuts in 2024",
        "Oil prices drop as supply concerns ease"
    ]
    # Assuming risk_monitor.json exists from previous step
    data_path = os.path.join(os.getcwd(), "themes/finshift/assets/data/risk_monitor.json")
    
    print("Analyzing sentiment...")
    result = analyzer.analyze_sentiment(data_path, dummy_headlines)
    print(json.dumps(result, indent=2))
