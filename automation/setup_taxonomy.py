#!/usr/bin/env python3
"""
Setup WordPress Categories and Tags based on content_strategy.md
"""

try:
    from automation.wp_client import WordPressClient
except ImportError:
    from wp_client import WordPressClient

import requests

def create_categories(wp):
    """Create all categories defined in content strategy."""
    categories = [
        {"name": "物流DX・トレンド", "slug": "logistics-dx", "description": "物流業界の最新動向、法規制(2024年問題など)、DX全般の話題"},
        {"name": "倉庫管理・WMS", "slug": "warehouse-management", "description": "WMS、在庫管理、ピッキング、庫内作業の効率化"},
        {"name": "輸配送・TMS", "slug": "transportation", "description": "トラック輸送、配車計画(TMS)、ラストワンマイル、動態管理"},
        {"name": "マテハン・ロボット", "slug": "material-handling", "description": "自動倉庫、AGV/AMR、RFID、マテハン機器"},
        {"name": "サプライチェーン", "slug": "supply-chain", "description": "SCM、調達、ロジスティクス戦略、国際物流"},
        {"name": "事例・インタビュー", "slug": "case-studies", "description": "企業の成功事例、現場インタビュー"},
        {"name": "ニュース・海外", "slug": "news-global", "description": "国内外のニュース解説、海外トレンド"},
    ]
    
    print("Creating categories...")
    for cat in categories:
        try:
            url = f"{wp.api_url}/categories"
            response = requests.post(url, json=cat, auth=wp.auth)
            if response.status_code == 201:
                print(f"✓ Created category: {cat['name']}")
            elif response.status_code == 400 and "term_exists" in response.text:
                print(f"- Category already exists: {cat['name']}")
            else:
                print(f"✗ Failed to create {cat['name']}: {response.text}")
        except Exception as e:
            print(f"✗ Error creating {cat['name']}: {e}")

def create_tags(wp):
    """Create all tags defined in content strategy."""
    tags = [
        # Industry
        {"name": "製造業", "slug": "manufacturing"},
        {"name": "小売・流通", "slug": "retail"},
        {"name": "EC・通販", "slug": "ecommerce"},
        {"name": "3PL・倉庫", "slug": "3pl-warehouse"},
        {"name": "食品・飲料", "slug": "food-beverage"},
        {"name": "アパレル", "slug": "apparel"},
        {"name": "医薬品・医療", "slug": "medical"},
        # Theme
        {"name": "コスト削減", "slug": "cost-reduction"},
        {"name": "人手不足対策", "slug": "labor-shortage"},
        {"name": "品質向上・誤出荷防止", "slug": "quality-improvement"},
        {"name": "環境・SDGs", "slug": "environment-sdgs"},
        {"name": "安全・BCP", "slug": "safety-bcp"},
        {"name": "補助金・助成金", "slug": "subsidy"},
        # Region/Country
        {"name": "日本", "slug": "japan"},
        {"name": "アメリカ", "slug": "usa"},
        {"name": "ヨーロッパ", "slug": "europe"},
        {"name": "中国", "slug": "china"},
        {"name": "東南アジア", "slug": "southeast-asia"},
        {"name": "グローバル", "slug": "global"},
    ]
    
    print("\nCreating tags...")
    for tag in tags:
        try:
            url = f"{wp.api_url}/tags"
            response = requests.post(url, json=tag, auth=wp.auth)
            if response.status_code == 201:
                print(f"✓ Created tag: {tag['name']}")
            elif response.status_code == 400 and "term_exists" in response.text:
                print(f"- Tag already exists: {tag['name']}")
            else:
                print(f"✗ Failed to create {tag['name']}: {response.text}")
        except Exception as e:
            print(f"✗ Error creating {tag['name']}: {e}")

def main():
    print("=== WordPress Taxonomy Setup ===\n")
    try:
        wp = WordPressClient()
        create_categories(wp)
        create_tags(wp)
        print("\n✓ Setup complete!")
    except Exception as e:
        print(f"\n✗ Setup failed: {e}")

if __name__ == "__main__":
    main()
