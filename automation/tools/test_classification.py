
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from automation.gemini_client import GeminiClient
from dotenv import load_dotenv

# Force load .env
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path, override=True)

def test():
    client = GeminiClient()
    print("Testing check_relevance...")
    
    title = "Bitcoin hits $100k all time high"
    summary = "Cryptocurrency markets rally as institutional adoption grows."
    
    is_rel, reason = client.check_relevance(title, summary)
    
    print(f"Title: {title}")
    print(f"Relevant: {is_rel}")
    print(f"Reason: '{reason}'")

if __name__ == "__main__":
    test()
