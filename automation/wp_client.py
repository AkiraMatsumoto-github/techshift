import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

class WordPressClient:
    def __init__(self):
        self.wp_url = os.getenv("WP_URL")
        self.wp_user = os.getenv("WP_USER")
        self.wp_password = os.getenv("WP_APP_PASSWORD")
        
        if not all([self.wp_url, self.wp_user, self.wp_password]):
            raise ValueError("Missing WordPress credentials in .env")

        self.auth = (self.wp_user, self.wp_password)
        # Use query param format for default permalink structure
        self.api_url = f"{self.wp_url}/?rest_route=/wp/v2"

    def create_post(self, title, content, status="draft", categories=None, tags=None, date=None):
        """
        Create a new post in WordPress.
        
        Args:
            title: Post title
            content: Post content (HTML)
            status: Post status ("draft", "publish", "future")
            categories: List of category IDs
            tags: List of tag IDs
            date: Publication date in ISO 8601 format (e.g., "2025-11-27T10:00:00")
                  Required when status="future"
        """
        url = f"{self.api_url}/posts"
        
        data = {
            "title": title,
            "content": content,
            "status": status
        }
        
        if categories:
            data["categories"] = categories
        if tags:
            data["tags"] = tags
        if date:
            data["date"] = date

        try:
            response = requests.post(url, json=data, auth=self.auth)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error creating post: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response content: {e.response.text}")
            return None

if __name__ == "__main__":
    # Test connection
    try:
        client = WordPressClient()
        print("WordPressClient initialized successfully.")
    except Exception as e:
        print(f"Initialization failed: {e}")
