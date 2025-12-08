import json
from typing import List, Dict, Optional

class InternalLinkSuggester:
    """
    Suggests relevant internal links for a new article based on existing content.
    Phase 1: One-way linking (New Article -> Existing Articles).
    """

    def __init__(self, wp_client, gemini_client):
        self.wp = wp_client
        self.gemini = gemini_client

    def fetch_candidates(self, limit: int = 100) -> List[Dict]:
        """
        Fetch existing posts from WordPress to serve as link candidates.
        """
        print(f"Fetching last {limit} posts for internal linking candidates...")
        posts = self.wp.get_posts(limit=limit, status="publish")
        
        if not posts:
            print("No existing posts found.")
            return []

        candidates = []
        for post in posts:
            # Try to get structured summary from meta
            # Note: The WP client's get_posts might return 'meta' if the API supports it in list view, 
            # or we might rely on the fact that we put it there.
            # If not available, fall back to excerpt.
            
            ai_summary_json = None
            if 'meta' in post and 'ai_structured_summary' in post['meta']:
                 try:
                     ai_summary_json = json.loads(post['meta']['ai_structured_summary'])
                 except:
                     pass
            
            summary_text = ""
            if ai_summary_json:
                summary_text = f"Title: {post['title']['rendered']}\nSummary: {ai_summary_json.get('summary', '')}\nTopics: {', '.join(ai_summary_json.get('key_topics', []))}\nEntities: {', '.join(ai_summary_json.get('entities', []))}"
            else:
                summary_text = f"Title: {post['title']['rendered']}\nExcerpt: {self._clean_excerpt(post['excerpt']['rendered'])}"

            candidates.append({
                "id": post['id'],
                "title": post['title']['rendered'],
                "url": post['link'],
                "summary_context": summary_text, # Store combined context for prompting
                "excerpt": self._clean_excerpt(post['excerpt']['rendered']) # Keep original for fallback
            })
        
        print(f"Loaded {len(candidates)} candidates.")
        return candidates

    def score_relevance(self, new_article_keyword: str, new_article_context: str, candidates: List[Dict]) -> List[Dict]:
        """
        Score the relevance of candidate articles against the new article's topic.
        Returns a list of highly relevant articles (score >= 80).
        """
        if not candidates:
            return []

        print("Scoring candidate relevance with Gemini (Enhanced Context)...")
        
        # Prepare candidates for the prompt
        candidates_text = ""
        for c in candidates:
            # Use the rich summary context if available
            candidates_text += f"- ID: {c['id']} | {c['summary_context']}\n"

        prompt = f"""
        You are an SEO expert. We are writing a new article about "{new_article_keyword}".
        Context/Outline of new article: {new_article_context[:500]}...

        Evaluate the following existing articles and determine which ones are HIGHLY RELEVANT to the new article.
        Relevance means the existing article provides valuable supplementary information, detailed explanation of a sub-topic, or a related case study.
        
        Existing Articles:
        {candidates_text}

        Task:
        1. Rate each article's relevance from 0 to 100.
        2. Select only articles with valid relevance >= 80.
        3. Return the result in JSON format:
        [
            {{"id": 123, "title": "Title", "score": 95, "reason": "Explains the specific tech mentioned in new article"}},
            ...
        ]
        
        Output JSON only. If no articles are relevant, output [].
        """

        try:
            response = self.gemini.generate_content(prompt)
            if not response or not response.text:
                print("No response from Gemini for relevance scoring.")
                return []
                
            response_text = response.text
            # basic cleanup for code blocks if gemini adds them
            clean_text = response_text.replace('```json', '').replace('```', '').strip()
            results = json.loads(clean_text)
            
            # Map back to full candidate objects
            relevant_posts = []
            for res in results:
                if res['score'] >= 80:
                    # Find original candidate data
                    original = next((c for c in candidates if c['id'] == res['id']), None)
                    if original:
                        original['relevance_score'] = res['score']
                        original['relevance_reason'] = res.get('reason', '')
                        relevant_posts.append(original)
            
            # Sort by score desc
            relevant_posts.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            print(f"Found {len(relevant_posts)} highly relevant articles.")
            return relevant_posts[:5] # Return top 5 max

        except Exception as e:
            print(f"Error during relevance scoring: {e}")
            return []

    def _clean_excerpt(self, html_excerpt: str) -> str:
        """Remove HTML tags from excerpt for cleaner prompt usage."""
        # Simple tag removal
        import re
        clean = re.sub('<[^<]+?>', '', html_excerpt)
        return clean.strip()
