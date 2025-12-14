import argparse
import sys
import re
import json
import markdown
from datetime import datetime
try:
    from automation.gemini_client import GeminiClient
    from automation.wp_client import WordPressClient
    from automation.classifier import ArticleClassifier
    from automation.internal_linker import InternalLinkSuggester
except ImportError:
    import gemini_client
    from gemini_client import GeminiClient
    from wp_client import WordPressClient
    from classifier import ArticleClassifier
    from internal_linker import InternalLinkSuggester

def parse_article_content(text):
    """
    Parse the generated text to extract title and content.
    Extracts the first Markdown heading (# Title) as the title.
    """
    lines = text.split('\n')
    title = "無題"
    content_start_index = 0
    
    for i, line in enumerate(lines):
        clean_line = line.strip()
        
        # Check if line starts with # (Markdown heading)
        if clean_line.startswith('#'):
            # Extract title by removing # and whitespace
            title = clean_line.lstrip('#').strip()
            content_start_index = i + 1
            break
            
    content = "\n".join(lines[content_start_index:]).strip()
    return title, content

def parse_schedule_date(schedule_str):
    """
    Parse schedule string to ISO 8601 format for WordPress.
    Accepts formats:
    - "2025-11-27 10:00"
    - "2025-11-27 10:00:00"
    Returns ISO 8601 format: "2025-11-27T10:00:00"
    """
    try:
        # Try parsing with seconds
        dt = datetime.strptime(schedule_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            # Try parsing without seconds
            dt = datetime.strptime(schedule_str, "%Y-%m-%d %H:%M")
        except ValueError:
            raise ValueError(f"Invalid date format: {schedule_str}. Use 'YYYY-MM-DD HH:MM' or 'YYYY-MM-DD HH:MM:SS'")
    
    # Convert to ISO 8601 format
    return dt.strftime("%Y-%m-%dT%H:%M:%S")

def save_to_file(title, content, keyword):
    import os
    
    output_dir = os.path.join(os.path.dirname(__file__), "generated_articles")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    date_str = datetime.now().strftime("%Y-%m-%d")
    safe_keyword = re.sub(r'[\\/*?:\"<>| ]', '_', keyword)
    filename = f"{date_str}_{safe_keyword}.md"
    filepath = os.path.join(output_dir, filename)
    
    file_content = f"""---
title: {title}
date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
keyword: {keyword}
---

{content}
"""
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(file_content)
        print(f"Saved local copy to: {filepath}")
    except Exception as e:
        print(f"Warning: Failed to save local file: {e}")

def main():
    parser = argparse.ArgumentParser(description="Generate and post an article to WordPress.")
    parser.add_argument('--keyword', type=str, required=True, help='Keyword for the article')
    parser.add_argument('--type', type=str, default='know', choices=['know', 'buy', 'do', 'news', 'global'], help='Article type')
    parser.add_argument('--dry-run', action='store_true', help='Generate content but do not post to WordPress')
    parser.add_argument('--schedule', type=str, help='Schedule date (YYYY-MM-DD HH:MM or YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('--context', type=str, help='Article context for News/Global articles (JSON string, optional)')
    
    args = parser.parse_args()
    
    # Define output directory
    import os
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "generated_articles")
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    print(f"Starting article generation for keyword: {args.keyword} (Type: {args.type})")
    
    # 1. Initialize Clients
    wp_client = None
    try:
        gemini = GeminiClient()
        # Initialize WP client for reading (linking) even in dry-run
        try:
            from wp_client import WordPressClient # Ensure class is available if not imported top-level
        except ImportError:
            pass # Already imported
            
        try:
            wp_client = WordPressClient()
            print("WordPress Client initialized (for reading/linking).")
        except Exception as e:
            print(f"Warning: WordPress Client initialization failed: {e}. Internal linking will be skipped.")
            
        if not args.dry_run and wp_client is None:
             print("Error: WordPress credentials required for non-dry-run mode.")
             sys.exit(1)
            
        # Assign to 'wp' for compatibility (though we use wp_client now)
        wp = wp_client
             
    except Exception as e:
        print(f"Failed to initialize Gemini Client: {e}")
        sys.exit(1)
        
    # Parse context if provided
    context = None
    if args.context:
        try:
            context = json.loads(args.context)
            print("Context-based generation mode")
            print(f"  Summary: {context['summary'][:100]}...")
            print(f"  Key facts: {len(context['key_facts'])} items")
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid context JSON ({e}), falling back to keyword-based generation")
    else:
        print("Keyword-based generation mode")
    
    # 1.5 Internal Linking Suggestions
    extra_instructions = None
    if wp_client:
        try:
            print("--- Internal Link Suggester ---")
            linker = InternalLinkSuggester(wp_client, gemini)
            # Limit to 50 for performance during generation
            candidates = linker.fetch_candidates(limit=50) 
            
            if candidates:
                # Simple context for scoring
                scoring_context = f"Keyword: {args.keyword}\nType: {args.type}"
                if context:
                    scoring_context += f"\nSummary: {context.get('summary', '')}"
                    
                relevant_links = linker.score_relevance(args.keyword, scoring_context, candidates)
                
                if relevant_links:
                    print(f"Found {len(relevant_links)} relevant articles for linking.")
                    
                    # Sort by score descending and take top 5 for context inclusion
                    top_relevant = sorted(relevant_links, key=lambda x: x.get('score', 0), reverse=True)[:5]
                    
                    # Build instructions
                    links_text = ""
                    for l in relevant_links: # Link suggestions still include all relevant ones (up to 5 or more)
                         links_text += f"- ID: {l['id']} | Title: {l['title']} | URL: {l['url']}\n"

                    # Build Context from summaries
                    context_summaries = ""
                    for i, l in enumerate(top_relevant):
                        summary_data = l.get('summary_data')
                        if summary_data and isinstance(summary_data, dict):
                            summary_text = summary_data.get('summary', 'No summary available.')
                            context_summaries += f"Article {i+1}: {l['title']}\nSummary: {summary_text}\n\n"
                        elif l.get('excerpt'):
                            context_summaries += f"Article {i+1}: {l['title']}\nSummary: {l['excerpt']}\n\n"

                    extra_instructions = f"""
## Context from Existing Articles
The following are summaries of existing related articles on the blog. 
Use this information to:
1. maintain consistency in tone and facts.
2. avoid unnecessary repetition of basic concepts if they are already covered (briefly recap instead).
3. explicitly reference them where appropriate (e.g., "As discussed in our previous article on [Topic]...").

[Related Article Summaries]
{context_summaries}

## Internal Linking Instructions
You have access to the following existing articles on the blog. 
Select the most relevant ones (if any) and include them in the article using standard Markdown link syntax: [Title](URL).

[Existing Articles List]
{links_text}

[Rules]
1. PRIORITIZE specific, high-relevance articles.
2. Format options:
   - Inline: ... as discussed in [Topic Name](URL)...
   - Block: See also: [Title](URL) at the end of sections.
3. If no article is strictly relevant, do not force a link.
"""
                else:
                    print("No relevant internal links found.")
            else:
                 print("No existing articles found for linking candidates.")
                 
        except Exception as e:
            print(f"Warning: Internal linking failed: {e}")

    # 2. Generate Content
    print("Generating content with Gemini...")
    generated_text = gemini.generate_article(args.keyword, article_type=args.type, context=context, extra_instructions=extra_instructions)
    
    if not generated_text:
        print("Failed to generate content.")
        sys.exit(1)
        
    title, content = parse_article_content(generated_text)
    
    print(f"Generated Title: {title}")
    print(f"Content Length: {len(content)} chars")
    
    # 3. Generate SEO Metadata
    print("Generating SEO metadata...")
    meta_desc = ""
    optimized_title = title
    
    try:
        try:
            from seo_optimizer import SEOOptimizer
        except ImportError:
            from automation.seo_optimizer import SEOOptimizer
            
        optimizer = SEOOptimizer()
        
        # Generate Meta Description
        meta_desc = optimizer.generate_meta_description(title, content, args.keyword)
        print(f"Meta Description: {meta_desc}")
        
        # Optimize Title
        optimized_title = optimizer.optimize_title(title)
        print(f"Original Title: {title}")
        print(f"Optimized Title: {optimized_title}")
        
    except Exception as e:
        print(f"Warning: SEO Optimization failed: {e}")

    # 2.5 Generate Hero Image
    # if gemini.use_vertex: # Allow for both Vertex and API Key
    print("Generating hero image...")
    
    # Generate contextual image prompt based on article content
    content_summary = content[:1000]  # Use first 1000 chars as summary
    image_prompt = gemini.generate_image_prompt(title, content_summary, args.type)
    print(f"Image prompt: {image_prompt}")
    
    import os
    output_dir = os.path.join(os.path.dirname(__file__), "generated_articles")
    date_str = datetime.now().strftime("%Y-%m-%d")
    safe_keyword = re.sub(r'[\\/*?:"\<\>| ]', '_', args.keyword)
    image_filename = f"{date_str}_{safe_keyword}_hero.png"
    image_path = os.path.join(output_dir, image_filename)
    
    generated_image_path = gemini.generate_image(image_prompt, image_path, aspect_ratio="16:9")
    
    if generated_image_path:
        # Re-save the file (without inserting image into content)
        save_to_file(title, content, args.keyword)
        print(f"Hero image generated: {image_filename}")
    
    # 3. Classify Content
    print("Classifying content...")
    category_id = None
    tag_ids = []
    
    try:
        classifier = ArticleClassifier()
        classification = classifier.classify_article(title, content[:1000])
        print(f"Classification Result: {classification}")
        
        # Resolve IDs if not dry-run (or even in dry-run if we want to test lookup, but let's skip for speed)
        # Actually, let's resolve them to verify logic if we have a client.
        # But we initialize wp_client later. Let's initialize it earlier if needed.
        # Or just do it in the posting block.
        # Let's do it here if we want to print them in dry run?
        # No, let's keep it simple. Just pass the classification dict to the posting block?
        # No, create_post expects IDs.
        # Let's initialize WP client here if we are going to post.
        
    except Exception as e:
        print(f"Classification failed: {e}")
        classification = {}

    # 4. Generate AI Structured Summary (New)
    print("Generating AI Structured Summary...")
    # Strip HTML for efficient token usage
    text_content_for_summary = re.sub('<[^<]+?>', '', content)
    structured_summary = gemini.generate_structured_summary(text_content_for_summary)
    
    if structured_summary:
        print("  - Structured summary generated.")
        if args.dry_run:
            print(f"  [Dry Run Preview] Summary: {structured_summary.get('summary')}")
            print(f"  [Dry Run Preview] Topics: {structured_summary.get('key_topics')}")
    else:
        print("  - Warning: Failed to generate structured summary.")
        structured_summary = None

    if args.dry_run:
        print("Dry run mode. Skipping WordPress posting.")
        print("--- Preview ---")
        print(f"Title: {optimized_title}")
        print(f"Meta Description: {meta_desc}")
        print(content[:500] + "...")
        return

    # 5. Post to WordPress
    print("Posting to WordPress...")
    try:
        wp = WordPressClient()
        
        # Resolve Categories and Tags
        if classification:
            cat_slug = classification.get("category")
            if cat_slug:
                cat_id = wp.get_category_id(cat_slug)
                if cat_id:
                    category_id = [cat_id]
                    print(f"Resolved Category: {cat_slug} -> {cat_id}")
            
            t_slugs = classification.get("industry_tags", []) + classification.get("theme_tags", []) + classification.get("region_tags", [])
            for t_slug in t_slugs:
                t_id = wp.get_tag_id(t_slug)
                if t_id:
                    tag_ids.append(t_id)
            print(f"Resolved Tags: {t_slugs} -> {tag_ids}")

        featured_media_id = None

        # Upload generated hero image explicitly
        if 'generated_image_path' in locals() and generated_image_path and os.path.exists(generated_image_path):
            print(f"Uploading hero image to WordPress: {image_filename}")
            media_result = wp.upload_media(generated_image_path, alt_text=args.keyword)
            if media_result and 'id' in media_result:
                featured_media_id = media_result['id']
                print(f"Set as featured media ID: {featured_media_id}")
            else:
                print(f"Failed to upload hero image.")

        # Upload other images found in content
        image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        image_matches = re.findall(image_pattern, content)
        
        for i, (alt_text, match_filename) in enumerate(image_matches):
            # Check if it's a local file (not a URL)
            if not match_filename.startswith('http'):
                image_path = os.path.join(OUTPUT_DIR, match_filename)
                if os.path.exists(image_path):
                    print(f"Uploading image to WordPress: {match_filename}")
                    media_result = wp.upload_media(image_path, alt_text=alt_text or args.keyword)
                    if media_result and 'source_url' in media_result:
                        # Replace local path with WordPress URL
                        content = content.replace(f']({match_filename})', f']({media_result["source_url"]})')
                        print(f"Image uploaded successfully: {media_result['source_url']}")
                        
                        # Set as featured image if not already set
                        if featured_media_id is None and (i == 0 or '_hero' in match_filename):
                            featured_media_id = media_result.get('id')
                            print(f"Set as featured media ID: {featured_media_id}")
                    else:
                        print(f"Failed to upload image: {match_filename}")


        # Clean up HTML tags that Gemini might insert (especially <br> in tables)
        # Replace <br> with space to avoid breaking table syntax
        content = re.sub(r'<br\s*/?>\s*', ' ', content)
        # Remove any other HTML tags (but keep the content)
        content = re.sub(r'<([^>]+)>', '', content)
        
        # Convert Markdown to HTML (tables will be properly converted)
        html_content = markdown.markdown(content, extensions=['extra', 'nl2br', 'tables'])
        
        # Determine status and date
        if args.schedule:
            try:
                schedule_date = parse_schedule_date(args.schedule)
                status = "future"
                print(f"Scheduling post for: {schedule_date}")
            except ValueError as e:
                print(f"Error: {e}")
                sys.exit(1)
        else:
            schedule_date = None
            status = "publish"
        
        # Prepare metadata for SEO plugins (Yoast/All in One SEO)
        meta_fields = {}
        if meta_desc:
            meta_fields["_yoast_wpseo_metadesc"] = meta_desc
            # meta_fields["_aioseop_description"] = meta_desc # Uncomment if using AIOSEO

        if 'structured_summary' in locals() and structured_summary:
            meta_fields["ai_structured_summary"] = json.dumps(structured_summary, ensure_ascii=False)

        result = wp.create_post(
            title=optimized_title, 
            content=html_content, 
            status=status,
            date=schedule_date,
            categories=category_id,
            tags=tag_ids,
            featured_media=featured_media_id,
            excerpt=meta_desc,
            meta=meta_fields
        )
        
        if result:
            print(f"Successfully created post. ID: {result.get('id')}")
            print(f"Link: {result.get('link')}")
            
            # --- SNS Posting (X/Twitter) ---
            # Only post if status is 'publish' (not 'future' or 'draft')
            if status == "publish" and not args.dry_run:
                try:
                    try:
                        from automation.sns_client import SNSClient
                    except ImportError:
                        from sns_client import SNSClient
                    print("Initializing SNS Client...")
                    sns = SNSClient()
                    
                    if sns.x_client:
                        print("Generating SNS content...")
                        sns_content_data = gemini.generate_sns_content(optimized_title, content, args.type)
                        
                        if sns_content_data:
                            # Construct post text
                            post_text = f"【新着記事】\n{sns_content_data.get('hook', optimized_title)}\n\n"
                            post_text += f"{sns_content_data.get('summary', '')}\n\n"
                            
                            tags = sns_content_data.get('hashtags', [])
                            if tags:
                                post_text += " ".join(tags) + "\n\n"
                                
                            post_text += result.get('link')
                            
                            print("--------------------------------------------------")
                            print(f"Posting to X:\n{post_text}")
                            print("--------------------------------------------------")
                            
                            sns.post_to_x(post_text)
                        else:
                             print("Failed to generate SNS content data.")
                    else:
                        print("Skipping X post: Client not authenticated (Check .env)")
                        
                except Exception as e:
                    print(f"SNS Posting failed: {e}")
            # -------------------------------
        else:
            print("Failed to create post.")

    except Exception as e:
        print(f"Failed to post to WordPress: {e}")



def save_to_file(title, content, keyword):
    """Save the article to a local markdown file."""
    import os
    
    # Create directory if not exists
    output_dir = os.path.join(os.path.dirname(__file__), "generated_articles")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Format filename: YYYY-MM-DD_keyword.md
    date_str = datetime.now().strftime("%Y-%m-%d")
    safe_keyword = re.sub(r'[\\/*?:"<>| ]', '_', keyword)
    filename = f"{date_str}_{safe_keyword}.md"
    filepath = os.path.join(output_dir, filename)
    
    # Add frontmatter
    file_content = f"""---
title: {title}
date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
keyword: {keyword}
---

{content}
"""
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(file_content)
        print(f"Saved local copy to: {filepath}")
    except Exception as e:
        print(f"Warning: Failed to save local file: {e}")

if __name__ == "__main__":
    main()
