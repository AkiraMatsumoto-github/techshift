#!/usr/bin/env python3
"""
Setup WordPress Categories and Tags for FinShift
Based on docs/00_project/finshift_media_plan.md
"""

try:
    from automation.wp_client import WordPressClient
except ImportError:
    from wp_client import WordPressClient

import requests

def create_categories(wp):
    """Create FinShift categories."""
    categories = [
        {
            "name": "Market Analysis",
            "slug": "market-analysis",
            "description": "米国・日本・インド・中国・インドネシアなど、世界主要市場のデイリー市況解説。AIシナリオ分析による「今日の強気・弱気」判断と、スイングトレーダー向けのアクションプランを提供します。"
        },
        {
            "name": "Featured News",
            "slug": "featured-news",
            "description": "市場を動かす重要ニュース（雇用統計、決算、政策転換）の深掘り解説。単なる事実の報道ではなく、それが「どの銘柄に」「どう影響するか」を投資家視点で分析します。"
        },
        {
            "name": "Strategic Assets",
            "slug": "strategic-assets",
            "description": "株式市場の先行指標となる「仮想通貨（Crypto）」「金・原油（Commodities）」の分析。市場間の相関性（Inter-market Correlation）を読み解き、リスクセンチメントの変化を捉えます。"
        },
        {
            "name": "Investment Guide",
            "slug": "investment-guide",
            "description": "新興国株（インド・中国）の買い方、証券口座の選び方、TradingViewなどのツール活用法。初心者から中級者へのステップアップを支援する普遍的な知識（ストック情報）。"
        }
    ]
    
    print("Creating/Updating Categories (FinShift)...")
    _process_terms(wp, "categories", categories)

def create_tags(wp):
    """Create FinShift tags."""
    tags = [
        # Region
        {"name": "US Market", "slug": "us-market", "description": "米国株市場（S&P500, Nasdaq, NYダウ）。世界の金融センターであるウォール街の動向を追う。"},
        {"name": "Japan Market", "slug": "japan-market", "description": "日本株市場（日経平均, TOPIX）。円安・金融政策・外国人投資家の動向。"},
        {"name": "China Market", "slug": "china-market", "description": "中国・香港市場（上海総合, ハンセン）。政府の景気刺激策やEV・テック規制の動き。"},
        {"name": "India Market", "slug": "india-market", "description": "インド市場（SENSEX, Nifty50）。世界一の人口ボーナスと高成長企業のトレンド。"},
        {"name": "Indonesia Market", "slug": "indonesia-market", "description": "インドネシア市場（IDX）。東南アジアの成長エンジンとコモディティ関連株。"},
        {"name": "Global", "slug": "global", "description": "クロスボーダーな市場動向、地政学リスク、世界経済全体のトレンド。"},

        # Asset Class
        {"name": "Stock", "slug": "stock", "description": "個別銘柄（Stock）の分析。決算、M&A、新製品発表など。"},
        {"name": "Crypto", "slug": "crypto", "description": "ビットコイン、イーサリアムなど暗号資産（仮想通貨）。リスクオン・オフの温度計。"},
        {"name": "Forex", "slug": "forex", "description": "為替市場（ドル円、ユーロドル）。金利差や通貨強弱による市場への影響。"},
        {"name": "Commodity", "slug": "commodity", "description": "金（ゴールド）、原油、銅など商品市場。インフレ動向や地政学リスクの反映。"},

        # Sector / Theme
        {"name": "Tech & AI", "slug": "tech-ai", "description": "半導体、人工知能、SaaS。市場を牽引するハイテク・グロース株。"},
        {"name": "EV & Auto", "slug": "ev-auto", "description": "電気自動車、バッテリー、自動運転技術。産業構造の転換点。"},
        {"name": "Energy", "slug": "energy", "description": "再生可能エネルギー、石油・ガス、電力インフラ。"},
        {"name": "Earnings", "slug": "earnings", "description": "決算速報。サプライズ決算やガイダンス修正におる株価変動。"},
        {"name": "Central Bank", "slug": "central-bank", "description": "FRB, 日銀, ECBなどの金融政策決定会合。利上げ・利下げシナリオ。"},
    ]
    
    print("\nCreating/Updating Tags (FinShift)...")
    _process_terms(wp, "tags", tags)

def _process_terms(wp, taxonomy, terms):
    """Helper to create or update terms."""
    for term in terms:
        try:
            # 1. Try create
            url = f"{wp.api_url}/{taxonomy}"
            response = requests.post(url, json=term, auth=wp.auth)
            
            if response.status_code == 201:
                print(f"✓ Created {taxonomy[:-1]}: {term['name']}")
            elif response.status_code == 400 and "term_exists" in response.text:
                # 2. Update existing
                print(f"- {taxonomy[:-1].capitalize()} exists: {term['name']}. Updating...")
                
                # Fetch ID
                get_url = f"{wp.api_url}/{taxonomy}&slug={term['slug']}"
                get_res = requests.get(get_url, auth=wp.auth)
                
                if get_res.status_code == 200 and len(get_res.json()) > 0:
                    term_id = get_res.json()[0]['id']
                    update_url = f"{wp.api_url}/{taxonomy}/{term_id}"
                    update_res = requests.post(update_url, json={'description': term['description']}, auth=wp.auth)
                    
                    if update_res.status_code == 200:
                         print(f"  ✓ Updated description.")
                    else:
                         print(f"  ✗ Update failed: {update_res.text}")
                else:
                    print(f"  ✗ ID lookup failed for {term['slug']}")
            else:
                print(f"✗ Creation failed: {response.text}")
                
        except Exception as e:
            print(f"✗ Error: {e}")

def main():
    print("=== FinShift Taxonomy Setup ===\n")
    try:
        wp = WordPressClient()
        create_categories(wp)
        create_tags(wp)
        print("\n✓ Setup complete!")
    except Exception as e:
        print(f"\n✗ Setup failed: {e}")

if __name__ == "__main__":
    main()
