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

    def create_post(self, title, content, status="draft", categories=None, tags=None, date=None, excerpt=None, meta=None, featured_media=None):
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
            excerpt: Post excerpt (used for meta description)
            meta: Dictionary of meta fields (e.g., {"_yoast_wpseo_metadesc": "..."})
            featured_media: ID of the featured image
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
        if excerpt:
            data["excerpt"] = excerpt
        if meta:
            data["meta"] = meta
        if featured_media:
            data["featured_media"] = featured_media

        try:
            response = requests.post(url, json=data, auth=self.auth)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error creating post: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response content: {e.response.text}")
            return None
            return None

    def create_page(self, title, content, status="publish", slug=None, parent=None):
        """
        Create a new page in WordPress.
        
        Args:
            title: Page title
            content: Page content (HTML)
            status: Page status ("draft", "publish")
            slug: URL slug (e.g., "privacy-policy")
            parent: Parent page ID (for hierarchical pages)
        
        Returns:
            Response JSON or None
        """
        url = f"{self.api_url}/pages"
        
        data = {
            "title": title,
            "content": content,
            "status": status
        }
        
        if slug:
            data["slug"] = slug
        if parent:
            data["parent"] = parent

        try:
            response = requests.post(url, json=data, auth=self.auth)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error creating page: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response content: {e.response.text}")
            return None

    def get_category_id(self, slug):
        """Get category ID by slug."""
        try:
            # Use query param format for default permalink structure
            url = f"{self.wp_url}/?rest_route=/wp/v2/categories&slug={slug}"
            response = requests.get(url, auth=self.auth)
            response.raise_for_status()
            data = response.json()
            if data:
                return data[0]['id']
            return None
        except Exception as e:
            print(f"Error fetching category {slug}: {e}")
            return None

    def get_tag_id(self, slug):
        """Get tag ID by slug. Creates tag if not exists."""
        try:
            # Try to get existing tag
            url = f"{self.wp_url}/?rest_route=/wp/v2/tags&slug={slug}"
            response = requests.get(url, auth=self.auth)
            response.raise_for_status()
            data = response.json()
            if data:
                return data[0]['id']
            
            # Create if not exists
            create_url = f"{self.api_url}/tags"
            create_data = {"name": slug, "slug": slug}
            response = requests.post(create_url, json=create_data, auth=self.auth)
            response.raise_for_status()
            return response.json()['id']
            
        except Exception as e:
            print(f"Error fetching/creating tag {slug}: {e}")
            return None

    def get_posts(self, limit=10, category=None, tag=None, status="publish", after=None):
        """
        Retrieve recent posts from WordPress.
        
        Args:
            limit: Number of posts to retrieve (default: 10)
            category: Filter by category ID (int)
            tag: Filter by tag ID (int)
            status: Filter by post status (default: "publish")
            after: ISO 8601 date string to filter posts published after this date
            
        Returns:
            List of posts (dict) or None if error
        """
        try:
            url = f"{self.api_url}/posts"
            params = {
                "per_page": limit,
                "status": status,
                "orderby": "date",
                "order": "desc",
                "context": "edit"
            }
            
            if category:
                params["categories"] = category
            if tag:
                params["tags"] = tag
            if after:
                params["after"] = after
                
            response = requests.get(url, params=params, auth=self.auth)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"Error fetching posts: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response content: {e.response.text}")
            return None

    def upload_media(self, file_path, alt_text=""):
        """
        Upload a media file to WordPress.
        
        Args:
            file_path: Path to the file to upload
            alt_text: Alternative text for the image
            
        Returns:
            dict with 'id' and 'source_url' if successful, None otherwise
        """
        try:
            url = f"{self.api_url}/media"
            
            # Get filename
            filename = os.path.basename(file_path)
            
            # Use multipart upload which is often more robust
            with open(file_path, 'rb') as f:
                files = {
                    'file': (filename, f, 'image/png')
                }
                
                # Upload file
                response = requests.post(
                    url,
                    files=files,
                    auth=self.auth
                )
            
            response.raise_for_status()
            
            result = response.json()
            
            # Update alt text if provided
            if alt_text and 'id' in result:
                media_id = result['id']
                update_url = f"{self.api_url}/media/{media_id}"
                update_data = {"alt_text": alt_text}
                requests.post(update_url, json=update_data, auth=self.auth)
            
            return {
                'id': result.get('id'),
                'source_url': result.get('source_url')
            }
            
        except Exception as e:
            print(f"Error uploading media {file_path}: {e}")
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
