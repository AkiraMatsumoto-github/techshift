
import os
import re
import json
import subprocess
import time
import sys
from datetime import datetime

# Path Configuration for TechShift
BASE_DIR = "/Users/matsumotoakira/Documents/Private_development/Techshift"
MARKDOWN_FILE = os.path.join(BASE_DIR, "docs/03_automation/seo_target_keywords_2025.md")
SCRIPT_PATH = os.path.join(BASE_DIR, "automation/generate_article.py")
# Assume running in the same venv or system python if explicit venv not found
PYTHON_EXEC = sys.executable 

def parse_markdown_table(file_path):
    tasks = []
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    in_table = False
    current_domain = "General"

    for line in lines:
        line = line.strip()
        
        # Track Domain Headers for context
        if line.startswith('#### Domain:'):
            current_domain = line.replace('#### Domain:', '').strip()
            continue

        # Detect Table Start (New Format)
        if line.startswith('| Keyword'):
            in_table = True
            continue
        if line.startswith('| :---'):
            continue
        
        # Skip empty lines or non-table lines
        if not line.startswith('|') or not in_table:
            # If we hit an empty line after being in a table, we might be out of it, 
            # but markdown tables can be adjacent. 
            # Simple heuristic: if line is empty, we are out.
            if in_table and not line:
                in_table = False
            continue
            
        parts = [p.strip() for p in line.split('|')]
        # Parts check: split('|') on "| A | B | C |" gives ['', 'A', 'B', 'C', ''] -> len 5
        # We need at least 3 content columns
        if len(parts) >= 5:
            raw_keyword_col = parts[1] # Keyword (JP/EN)
            intent = parts[2]          # Intent
            content_type = parts[3]    # Content Type
            
            # --- Keyword Extraction ---
            # Format: "**AGI ロードマップ**<br>AGI Roadmap"
            # We want "AGI ロードマップ"
            
            # 1. Remove <br> and everything after it
            keyword_primary = raw_keyword_col.split('<br>')[0].strip()
            
            # 2. Remove markdown bold/italic
            keyword_clean = re.sub(r'[*_]+', '', keyword_primary).strip()
            
            # Skip if empty
            if not keyword_clean:
                continue

            # --- Type Mapping ---
            # All automated SEO articles map to 'stock-analysis' structure by default
            # per updated strategy (Stock-First).
            gen_type = 'stock-analysis'
            
            # Optional: Override if needed based on Content Type, but default is Stock.
            if 'news' in content_type.lower():
                gen_type = 'topic-focus'
            
            # --- Context Construction ---
            summary_context = f"Domain: {current_domain}. User Intent: {intent}. Content Type: {content_type}."
            
            tasks.append({
                'keyword': keyword_clean,
                'type': gen_type,
                'context_summary': summary_context,
                'raw_type': content_type
            })
            
    return tasks

def main():
    if not os.path.exists(MARKDOWN_FILE):
        print(f"Error: File not found: {MARKDOWN_FILE}")
        return

    print(f"Reading target definitions from: {MARKDOWN_FILE}")
    tasks = parse_markdown_table(MARKDOWN_FILE)
    print(f"Found {len(tasks)} target articles.")
    
    for i, task in enumerate(tasks):
        print(f"\n[{i+1}/{len(tasks)}] Target: {task['keyword']}")
        print(f"  Context: {task['context_summary']}")
        
        # Prepare context JSON
        context = {
            "summary": f"{task['context_summary']} Please write a high-quality article satisfying this intent.",
            "key_facts": [] 
        }
        context_json = json.dumps(context, ensure_ascii=False)
        
        cmd = [
            PYTHON_EXEC, SCRIPT_PATH,
            '--keyword', task['keyword'],
            '--type', task['type'],
            '--context', context_json,
            # '--dry-run' # Uncomment to test without generating
        ]
        
        try:
            # Check for existing file (Simple check by keyword match in directory)
            # generate_article.py does its own saving, but we can skip early if we want.
            # For now, we let generate_article.py run, or we can check output dir.
            
            date_str = datetime.now().strftime("%Y-%m-%d")
            safe_keyword = re.sub(r'[\\/*?:"<>| ]', '_', task['keyword'])
            # Note: generate_article.py uses slightly different slugification logic depending on impl
            # But let's rely on the script execution.
            
            print(f"  Executing: {' '.join(cmd)}")
            
            # Run the generation script
            # We capture output to avoid spamming the console, but print errors
            result = subprocess.run(cmd, check=True, text=True, capture_output=True)
            
            print("  > Success!")
            # Extract generated file path or title from stdout if needed
            for line in result.stdout.split('\n'):
                if "Generated Title:" in line or "Saved local copy" in line:
                    print(f"    {line.strip()}")
            
        except subprocess.CalledProcessError as e:
            print(f"  > Error generating article for {task['keyword']}:")
            print(f"    STDOUT: {e.stdout[-500:]}") # Last 500 chars
            print(f"    STDERR: {e.stderr[-500:]}")
        
        # Usage throttling
        print("  Waiting 10s...")
        time.sleep(10)

if __name__ == "__main__":
    main()
