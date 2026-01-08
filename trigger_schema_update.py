import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from automation.db.client import DBClient

def trigger_update():
    print("Triggering Remote DB Schema Update...")
    db = DBClient()
    # This calls GET /finshift/v1/update-schema
    # which runs dbDelta() on the server
    db.update_schema()
    print("Trigger sent. Check server logs or try saving data to verify.")

if __name__ == "__main__":
    trigger_update()
