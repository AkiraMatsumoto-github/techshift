
import os
import requests
import sys

# Add automation directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'automation'))

try:
    from automation.wp_client import WordPressClient
except ImportError:
    # Try alternate path if running from root
    sys.path.append(os.path.join(os.getcwd(), 'automation'))
    from wp_client import WordPressClient


def main():
    print("Initializing WordPressClient with Session...")
    try:
        client = WordPressClient()
    except Exception as e:
        print(f"Failed to initialize client: {e}")
        return

    if not hasattr(client, 'session'):
         print("❌ Error: Client does not have 'session' attribute. Update failed?")
         return
    else:
         print("✅ Client has 'session' attribute.")

    print(f"Target URL: {client.api_url}")
    print("Attempting to fetch posts (Reuse connection test)...")

    # Call 1
    print("Request 1...")
    posts = client.get_posts(limit=1)
    if posts:
        print(f"✅ Success 1: {posts[0].get('title', {}).get('rendered', 'No Title')}")
    else:
        print("❌ Failed 1")

    # Call 2 (Should reuse connection)
    print("Request 2 (Should be faster/reuse SSL)...")
    posts2 = client.get_posts(limit=1)
    if posts2:
         print(f"✅ Success 2: {len(posts2)} posts")
    else:
         print("❌ Failed 2")

if __name__ == "__main__":
    main()
