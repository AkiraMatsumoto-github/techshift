
import os
import re
import json
import subprocess
import time
import sys
from datetime import datetime

MARKDOWN_FILE = "/Users/matsumotoakira/Documents/Private_development/media/docs/03_automation/seo_target_keywords_2025.md"
SCRIPT_PATH = "/Users/matsumotoakira/Documents/Private_development/media/automation/generate_article.py"
PYTHON_EXEC = "/Users/matsumotoakira/Documents/Private_development/media/automation/venv/bin/python"

def parse_markdown_table(file_path):
    tasks = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    in_table = False
    for line in lines:
        line = line.strip()
        if line.startswith('| Keyword'):
            in_table = True
            continue
        if line.startswith('| :---'):
            continue
        if not line.startswith('|') or not in_table:
            continue
            
        parts = [p.strip() for p in line.split('|')]
        # Expected parts: ['', 'Keyword (Vol)', 'Article Topic Idea', 'Type', '']
        if len(parts) >= 4:
            raw_keyword = parts[1]
            topic_idea = parts[2]
            raw_type = parts[3]
            
            # Clean keyword: "**物流 ニュース** (50,000)" -> "物流 ニュース"
            keyword_match = re.search(r'\*\*(.+?)\*\*', raw_keyword)
            if not keyword_match:
                # Try without bold
                keyword = raw_keyword.split('(')[0].strip()
            else:
                keyword = keyword_match.group(1)
            
            # Map type
            type_lower = raw_type.lower()
            article_type = 'know' # default
            if 'news' in type_lower or 'trend' in type_lower:
                article_type = 'news'
            elif 'global' in type_lower:
                article_type = 'global'
            elif 'how-to' in type_lower or 'do' in type_lower or 'case' in type_lower or 'issue' in type_lower:
                article_type = 'do'
            elif 'buy' in type_lower or 'comparison' in type_lower or 'selection' in type_lower or 'cost' in type_lower:
                article_type = 'buy'
            
            tasks.append({
                'keyword': keyword,
                'topic': topic_idea,
                'type': article_type,
                'raw_type': raw_type
            })
            
    return tasks

def main():
    if not os.path.exists(MARKDOWN_FILE):
        print(f"Error: File not found: {MARKDOWN_FILE}")
        return

    tasks = parse_markdown_table(MARKDOWN_FILE)
    print(f"Found {len(tasks)} articles to generate.")
    
    for i, task in enumerate(tasks):
        print(f"\n[{i+1}/{len(tasks)}] Processing: {task['keyword']} ({task['type']})")
        print(f"Topic: {task['topic']}")
        
        # Prepare context JSON
        context = {
            "summary": f"Article Plan: {task['topic']}. \nPlease strictly follow this topic idea when generating the article.",
            "key_facts": []
        }
        context_json = json.dumps(context, ensure_ascii=False)
        
        cmd = [
            PYTHON_EXEC, SCRIPT_PATH,
            '--keyword', task['keyword'],
            '--type', task['type'],
            '--context', context_json,
            # '--dry-run' # Uncomment for testing
        ]
        
        try:
            # Check for existing file to avoid duplicate work if re-run
            date_str = datetime.now().strftime("%Y-%m-%d")
            safe_keyword = re.sub(r'[\\/*?:"<>| ]', '_', task['keyword'])
            filename = f"{date_str}_{safe_keyword}.md"
            filepath = os.path.join(os.path.dirname(SCRIPT_PATH), "generated_articles", filename)
            
            if os.path.exists(filepath):
                 print(f"Skipping {task['keyword']} (File exists: {filename})")
                 continue
            
            result = subprocess.run(cmd, check=True, text=True, capture_output=True)
            print("Success:")
            # Print only relevant validation info from output
            for line in result.stdout.split('\n'):
                if "Generated Title:" in line or "Successfully created post" in line:
                    print(f"  {line}")
        except subprocess.CalledProcessError as e:
            print(f"Error generating article for {task['keyword']}:")
            print(e.stderr)
            print(e.stdout)
        
        # Wait a bit between calls to be nice to APIs
        time.sleep(10)

if __name__ == "__main__":
    main()
