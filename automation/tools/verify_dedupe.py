
import sys
import os
import hashlib
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from automation.db.client import DBClient
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path, override=True)

def verify_dedupe():
    db = DBClient()
    
    # 1. Create a fake article hash
    test_url = "https://example.com/test-dedupe-" + str(datetime.now().timestamp())
    u_hash = hashlib.sha256(test_url.encode('utf-8')).hexdigest()
    
    print(f"Testing URL Hash: {u_hash}")
    
    # 2. Verify it DOES NOT exist
    exists_before = db.check_article_exists(u_hash)
    print(f"Exists Before Save? {exists_before}")
    
    if exists_before:
        print("Error: Hash already exists unexpectedly.")
        return

    # 3. Save it as Irrelevant (0)
    article = {
        "url_hash": u_hash,
        "title": "Dedupe Test Article",
        "source": "test_source",
        "region": "Global",
        "published_at": datetime.now().isoformat(),
        "summary": "Skip me next time",
        "is_relevant": 0,
        "relevance_reason": "Manual Test"
    }
    db.save_article(article)
    print("Saved as Irrelevant (0).")
    
    # 4. Verify it NOW EXISTS
    exists_after = db.check_article_exists(u_hash)
    print(f"Exists After Save? {exists_after}")
    
    if exists_after:
        print("SUCCESS: Irrelevant article was found by check_article_exists.")
    else:
        print("FAILURE: Irrelevant article was NOT found.")

if __name__ == "__main__":
    verify_dedupe()
