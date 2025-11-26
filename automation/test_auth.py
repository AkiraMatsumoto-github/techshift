import os
import requests
from dotenv import load_dotenv

load_dotenv()

wp_url = os.getenv("WP_URL")
wp_user = os.getenv("WP_USER")
wp_password = os.getenv("WP_APP_PASSWORD")

print(f"Testing WordPress authentication...")
print(f"URL: {wp_url}")
print(f"User: {wp_user}")
print(f"Password length: {len(wp_password) if wp_password else 0}")

# Test authentication with /users/me endpoint
auth = (wp_user, wp_password)
url = f"{wp_url}/?rest_route=/wp/v2/users/me"

try:
    response = requests.get(url, auth=auth)
    print(f"\nStatus Code: {response.status_code}")
    if response.status_code == 200:
        user_data = response.json()
        print(f"✅ Authentication successful!")
        print(f"User ID: {user_data.get('id')}")
        print(f"Username: {user_data.get('username')}")
        print(f"Roles: {user_data.get('roles')}")
        print(f"Capabilities: {list(user_data.get('capabilities', {}).keys())[:10]}...")
    else:
        print(f"❌ Authentication failed")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
