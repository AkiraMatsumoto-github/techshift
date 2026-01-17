#!/usr/bin/env python3
"""
Setup WordPress Categories and Tags for TechShift
Based on docs/00_project/media_concept_sheet.md
"""

import sys
import os

# Ensure automation directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from wp_client import WordPressClient
except ImportError:
    # Fallback for running from root
    from automation.wp_client import WordPressClient

import requests

def create_techshift_taxonomy(wp):
    """Create TechShift categories and tags."""
    
    # --- 1. Main Categories (Sectors) ---
    # Slug format: English slug derived from "Space & Aero" -> "space-aero"
    sectors = [
        {"name": "宇宙・航空", "slug": "space-aero", "description": "Space & Aero: ロケット、衛星、月面開発などの宇宙技術および航空技術。"},
        {"name": "量子技術", "slug": "quantum", "description": "Quantum: 量子コンピューティング、量子暗号、量子センシング。"},
        {"name": "次世代知能", "slug": "advanced-ai", "description": "Advanced AI: LLM, 自律エージェント, エッジAIなどの次世代人工知能技術。"},
        {"name": "ロボ・移動", "slug": "robotics", "description": "Robotics & Mobility: ヒューマノイド, 自動運転, BCI, 空間コンピューティング。"},
        {"name": "生命・バイオ", "slug": "life-science", "description": "Life Science: AI創薬, ゲノム編集, 次世代医療技術。"},
        {"name": "環境・エネルギー", "slug": "green-tech", "description": "Green Tech: 核融合, 全固体電池, DAC, 水素などの気候テック。"}
    ]

    print("--- Creating Main Categories (Sectors) ---")
    sector_map = {} # name -> id
    for sector in sectors:
        cat_id = _create_or_update_term(wp, "categories", sector)
        if cat_id:
            sector_map[sector["slug"]] = cat_id

    # --- 2. Sub Categories (Topics) ---
    # Structure: parent_slug -> list of children
    topics = {
        "space-aero": [
            {"name": "再使用型ロケット", "slug": "reusable-rockets", "description": "Reusable Rockets"},
            {"name": "衛星コンステレーション", "slug": "mega-constellations", "description": "Mega Constellations"},
            {"name": "月面開発・アルテミス計画", "slug": "lunar-exploration", "description": "Lunar Exploration"},
            {"name": "軌道上サービス・宇宙デブリ", "slug": "osam-debris", "description": "OSAM / Debris"},
            {"name": "超音速・極超音速技術", "slug": "supersonic-hypersonic", "description": "Supersonic / Hypersonic"},
        ],
        "quantum": [
            {"name": "量子ゲート型コンピュータ", "slug": "quantum-gate-computing", "description": "Quantum Gate Computing"},
            {"name": "量子アニーリング", "slug": "quantum-annealing", "description": "Quantum Annealing"},
            {"name": "耐量子暗号 (PQC)", "slug": "post-quantum-cryptography", "description": "Post-Quantum Cryptography"},
            {"name": "量子センシング", "slug": "quantum-sensing", "description": "Quantum Sensing"},
            {"name": "量子通信・インターネット", "slug": "quantum-internet", "description": "Quantum Internet"},
        ],
        "advanced-ai": [
            {"name": "基盤モデル (LLM/SLM)", "slug": "foundation-models", "description": "Foundation Models"},
            {"name": "マルチエージェント自律システム", "slug": "multi-agent-systems", "description": "Multi-Agent Systems"},
            {"name": "オンデバイス・エッジAI", "slug": "edge-ai", "description": "Edge AI"},
            {"name": "AIネイティブ開発 (No-Code)", "slug": "ai-native-dev", "description": "AI-Native Dev"},
            {"name": "デジタル・プロヴェナンス", "slug": "digital-provenance", "description": "Digital Provenance"},
        ],
        "robotics": [
            {"name": "ヒューマノイドロボット", "slug": "humanoid-robots", "description": "Humanoid Robots"},
            {"name": "レベル4 自動運転", "slug": "l4-autonomous-driving", "description": "L4 Autonomous Driving"},
            {"name": "ラストワンマイル配送ロボ", "slug": "delivery-robots", "description": "Delivery Robots"},
            {"name": "空間コンピューティング (XR)", "slug": "spatial-computing", "description": "Spatial Computing"},
            {"name": "ブレイン・コンピュータ I/F (BCI)", "slug": "bci", "description": "BCI"},
        ],
        "life-science": [
            {"name": "AI創薬", "slug": "ai-drug-discovery", "description": "AI Drug Discovery"},
            {"name": "ゲノム編集・遺伝子治療", "slug": "gene-editing", "description": "Gene Editing"},
            {"name": "タンパク質構造予測", "slug": "protein-structure", "description": "Protein Structure"},
            {"name": "再生医療・オルガノイド", "slug": "regenerative-medicine", "description": "Regenerative Medicine"},
            {"name": "老化制御・長寿研究", "slug": "longevity", "description": "Longevity"},
        ],
        "green-tech": [
            {"name": "核融合発電", "slug": "fusion-energy", "description": "Fusion Energy"},
            {"name": "全固体電池・次世代蓄電", "slug": "solid-state-batteries", "description": "Solid-State Batteries"},
            {"name": "直接空気回収 (DAC)", "slug": "direct-air-capture", "description": "Direct Air Capture"},
            {"name": "小型モジュール炉 (SMR)", "slug": "smr", "description": "SMR"},
            {"name": "水素・次世代燃料", "slug": "hydrogen-new-fuels", "description": "Hydrogen & New Fuels"},
        ]
    }

    print("\n--- Creating Sub Categories (Topics) ---")
    for parent_slug, children in topics.items():
        if parent_slug not in sector_map:
            print(f"Skipping children for {parent_slug} (Parent not found)")
            continue
            
        parent_id = sector_map[parent_slug]
        for child in children:
            child["parent"] = parent_id # Assign parent ID
            _create_or_update_term(wp, "categories", child)


    # --- 3. Tags ---
    tags = [
        # Layers (Roadmap Layers)
        {"name": "Regulation", "slug": "regulation", "description": "規制・法整備・政策"},
        {"name": "Technology", "slug": "technology", "description": "技術開発・R&D"},
        {"name": "Market", "slug": "market", "description": "市場・ビジネス・普及"},
        
        # Region (Roadmap Comparison)
        {"name": "Global (General)", "slug": "global-general", "description": "世界全体の横断的トレンド"},
        {"name": "US", "slug": "us", "description": "米国・北米市場"},
        {"name": "Europe", "slug": "europe", "description": "欧州・EU市場 (AI法規制など)"},
        {"name": "China", "slug": "china", "description": "中国市場・技術動向"},
        {"name": "Asia (Ex-China)", "slug": "asia", "description": "インド・東南アジアなどの新興市場"},
        {"name": "Japan", "slug": "japan", "description": "日本国内動向"},
        
        # Priority/Impact
        {"name": "Hero Topic", "slug": "hero-topic", "description": "トップストーリー"},
        {"name": "Strategic Asset", "slug": "strategic-asset", "description": "戦略的技術資産"},
    ]

    print("\n--- Creating Tags ---")
    for tag in tags:
        _create_or_update_term(wp, "tags", tag)


def _create_or_update_term(wp, taxonomy, term_data):
    """Helper to create or update terms."""
    # term_data should have 'name', 'slug', 'description', and optional 'parent'
    
    try:
        # 1. Try create
        url = f"{wp.api_url}/{taxonomy}"
        response = requests.post(url, json=term_data, auth=wp.auth)
        
        if response.status_code == 201:
            print(f"✓ Created {taxonomy[:-1]}: {term_data['name']}")
            return response.json()['id']
            
        elif response.status_code == 400 and "term_exists" in response.text:
            # 2. Update existing
            # First, we need to find the ID of the existing term.
            # Unfortunately, the 400 error usually contains the ID, but it's cleaner to fetch by slug.
            
            get_url = f"{wp.api_url}/{taxonomy}"
            params = {"slug": term_data['slug']}
            get_res = requests.get(get_url, params=params, auth=wp.auth)
            
            if get_res.status_code == 200 and len(get_res.json()) > 0:
                existing = get_res.json()[0]
                term_id = existing['id']
                
                print(f"- {taxonomy[:-1].capitalize()} exists: {term_data['name']} (ID: {term_id}). Updating...")
                
                # Prepare update data (excluding slug/name to avoid conflicts if case differs)
                update_data = {"description": term_data.get('description', '')}
                if 'parent' in term_data:
                    update_data['parent'] = term_data['parent']
                
                update_url = f"{wp.api_url}/{taxonomy}/{term_id}"
                update_res = requests.post(update_url, json=update_data, auth=wp.auth)
                
                if update_res.status_code == 200:
                     print(f"  ✓ Updated.")
                     return term_id
                else:
                     print(f"  ✗ Update failed: {update_res.text}")
                     return term_id # Return ID anyway
            else:
                print(f"  ✗ ID lookup failed for {term_data['slug']}")
                return None
        else:
            print(f"✗ Creation failed for {term_data['name']}: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Error processing {term_data['name']}: {e}")
        return None

def main():
    print("=== TechShift Taxonomy Setup ===\n")
    try:
        wp = WordPressClient()
        create_techshift_taxonomy(wp)
        print("\n✓ Setup complete!")
    except Exception as e:
        print(f"\n✗ Setup failed: {e}")

if __name__ == "__main__":
    main()
