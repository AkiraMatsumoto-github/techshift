import os
import requests
from dotenv import load_dotenv

load_dotenv()

# The key provided by the user
POTENTIAL_KEY = "AQ.Ab8RN6KS_uU_DlwdMGgK1j1y4kgN4BJObskctlI4ja_yWovSwA"
WP_URL = os.getenv("WP_URL", "http://localhost:8000")
WP_USER = os.getenv("WP_USER", "matsumotoakira")

def test_wp_connection():
    print(f"Testing WordPress connection to {WP_URL} with user {WP_USER}...")
    
    # Try using it as an Application Password (Basic Auth)
    auth = (WP_USER, POTENTIAL_KEY)
    # Default permalink structure uses ?rest_route=
    url = f"{WP_URL}/?rest_route=/wp/v2/users/me"
    
    try:
        response = requests.get(url, auth=auth)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Success! The key is a valid WordPress Application Password.")
            print(f"User info: {response.json().get('name')}")
            return True
        else:
            print(f"Failed. Response: {response.text}")
            return False
    except Exception as e:
        print(f"Connection error: {e}")
        return False

if __name__ == "__main__":
    test_wp_connection()
