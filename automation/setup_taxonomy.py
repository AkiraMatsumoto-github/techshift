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
        {"name": "宇宙・航空", "slug": "space-aero", "description": "Space & Aero: 再使用型ロケット、衛星コンステレーション、月面開発（アルテミス計画）を含む次世代宇宙ビジネスと、極超音速機・電動航空機(eVTOL)などの最先端航空技術の最新トレンドとインパクトを解説。"},
        {"name": "量子技術", "slug": "quantum", "description": "Quantum: 量子コンピューティング（ゲート型・アニーリング）、耐量子暗号(PQC)、量子センシング、量子インターネットなど、物理法則の限界に挑む量子技術の産業応用と未来予測。"},
        {"name": "次世代知能", "slug": "advanced-ai", "description": "Advanced AI: 大規模言語モデル(LLM)、マルチモーダルAI、自律エージェント、エッジAI、そしてAGI（汎用人工知能）への道筋。生成AIを超えた次世代人工知能技術の進化と社会への影響を分析。"},
        {"name": "ロボ・移動", "slug": "robotics", "description": "Robotics & Mobility: テスラOptimusrなどのヒューマノイドロボット、レベル4/5自動運転、空飛ぶクルマ、ブレイン・コンピュータ・インターフェース(BCI)など、物理世界を拡張するモビリティとロボティクスの最前線。"},
        {"name": "生命・バイオ", "slug": "life-science", "description": "Life Science: AlphaFoldによるAI創薬、CRISPRゲノム編集、合成生物学、老化制御（Longevity）、再生医療など、生命の設計図を書き換えるバイオテクノロジー革命の現在地。"},
        {"name": "環境・エネルギー", "slug": "green-tech", "description": "Green Tech: 核融合発電、全固体電池、直接空気回収(DAC)、グリーン水素、SMR（小型モジュール炉）など、脱炭素社会を実現しエネルギー問題を根本解決するクライメートテックの技術革新。"}
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
            {"name": "再使用型ロケット", "slug": "reusable-rockets", "description": "SpaceX StarshipやNew Glennに代表される、完全再使用型ロケット技術と打ち上げコスト破壊。"},
            {"name": "衛星コンステレーション", "slug": "mega-constellations", "description": "Starlinkなどの低軌道衛星群による地球規模の通信インフラ構築と宇宙空間の混雑問題。"},
            {"name": "月面開発・アルテミス計画", "slug": "lunar-exploration", "description": "NASAアルテミス計画、月面基地建設、月資源（水・ヘリウム3）の利用に向けた有人宇宙探査の最前線。"},
            {"name": "軌道上サービス・宇宙デブリ", "slug": "osam-debris", "description": "軌道上での衛星修理・燃料補給(OSAM)技術と、ADR（アクティブデブリ除去）による持続可能な宇宙環境。"},
            {"name": "超音速・極超音速技術", "slug": "supersonic-hypersonic", "description": "マッハ5を超える極超音速ミサイル技術や、静粛超音速旅客機(SST)の商用化に向けた開発動向。"},
        ],
        "quantum": [
            {"name": "量子ゲート型コンピュータ", "slug": "quantum-gate-computing", "description": "超伝導、イオントラップ、光方式など、誤り耐性型量子コンピュータ(FTQC)実現に向けたハードウェア開発競争。"},
            {"name": "量子アニーリング", "slug": "quantum-annealing", "description": "組合せ最適化問題に特化した量子アニーリング技術の物流、金融、創薬分野への産業応用事例。"},
            {"name": "耐量子暗号 (PQC)", "slug": "post-quantum-cryptography", "description": "量子コンピュータによる暗号解読脅威に対抗する、NIST標準化PQCアルゴリズムとシステム移行ガイドライン。"},
            {"name": "量子センシング", "slug": "quantum-sensing", "description": "ダイヤモンドNVセンタなどを用いた超高感度計測技術と、医療・GPS・資源探査への応用。"},
            {"name": "量子通信・インターネット", "slug": "quantum-internet", "description": "量子もつれを利用した盗聴不可能な量子暗号通信(QKD)と、地球規模の量子インターネット構築構想。"},
        ],
        "advanced-ai": [
            {"name": "基盤モデル (LLM/SLM)", "slug": "foundation-models", "description": "GPT-4, Claude, Geminiなどの大規模言語モデル(LLM)と、特定領域に特化した小規模言語モデル(SLM)の進化と推論能力。"},
            {"name": "マルチエージェント自律システム", "slug": "multi-agent-systems", "description": "複数のAIエージェントが協調して複雑なタスクを完遂する自律型AIシステムの設計と実装パターン。"},
            {"name": "オンデバイス・エッジAI", "slug": "edge-ai", "description": "クラウドを介さずスマートフォンやPCローカルで動作するAIモデルの軽量化技術とプライバシー保護。"},
            {"name": "AIネイティブ開発 (No-Code)", "slug": "ai-native-dev", "description": "自然言語等のプロンプトだけでアプリケーションを構築するAIネイティブ開発と、エンジニアリングの未来。"},
            {"name": "デジタル・プロヴェナンス", "slug": "digital-provenance", "description": "C2PAなどのコンテンツ来歴証明技術による、生成AIコンテンツの真正性保証とディープフェイク対策。"},
        ],
        "robotics": [
            {"name": "ヒューマノイドロボット", "slug": "humanoid-robots", "description": "工場労働から家事支援まで、人間の動作を模倣・代替する汎用人型ロボットのハードウェアと制御AIの進化。"},
            {"name": "自動運転", "slug": "autonomous-driving", "description": "特定条件下での完全無人運転（レベル4）の商用化、Robotaxiの社会実装、法規制と安全性の課題。"},
            {"name": "ラストワンマイル配送ロボ", "slug": "delivery-robots", "description": "物流の最終拠点を担う自動配送ロボット、ドローン配送の技術課題と都市インフラとの連携。"},
            {"name": "空間コンピューティング (XR)", "slug": "spatial-computing", "description": "Vision Proに代表されるMR/ARデバイス、空間OS、デジタルツインによる物理とデジタルの融合体験。"},
            {"name": "ブレイン・コンピュータ I/F (BCI)", "slug": "bci", "description": "Neuralinkなどの侵襲・非侵襲型BCIデバイスによる、脳とコンピュータの直接接続技術と医療応用。"},
        ],
        "life-science": [
            {"name": "AI創薬", "slug": "ai-drug-discovery", "description": "AlphaFoldなどの構造予測AIを活用した、新薬候補物質の探索・スクリーニング高速化と開発コスト削減。"},
            {"name": "ゲノム編集・遺伝子治療", "slug": "gene-editing", "description": "CRISPR-Cas9などのゲノム編集技術を用いた難病治療、農作物改良、および倫理的課題。"},
            {"name": "タンパク質構造予測", "slug": "protein-structure", "description": "アミノ酸配列からの3次元構造予測技術の進展と、酵素設計・ドラッグデザインへの応用。"},
            {"name": "再生医療・オルガノイド", "slug": "regenerative-medicine", "description": "iPS細胞やオルガノイド（ミニ臓器）を用いた組織再生、移植医療、動物実験代替法の開発動向。"},
            {"name": "老化制御・長寿研究", "slug": "longevity", "description": "老化を「治療可能な疾患」と捉えるLongevity研究、老化細胞除去、エピジェネティック時計の解析。"},
        ],
        "green-tech": [
            {"name": "核融合発電", "slug": "fusion-energy", "description": "「地上の太陽」を実現する核融合発電（トカマク型・レーザー型など）の点火実験進捗と商用炉ロードマップ。"},
            {"name": "全固体電池・次世代蓄電", "slug": "solid-state-batteries", "description": "EVの航続距離と安全性を飛躍させる全固体電池、ナトリウムイオン電池などの次世代エネルギー貯蔵技術。"},
            {"name": "直接空気回収 (DAC)", "slug": "direct-air-capture", "description": "大気中のCO2を直接回収・貯留するDAC技術のコスト削減、スケーリング、炭素除去クレジット市場。"},
            {"name": "小型モジュール炉 (SMR)", "slug": "smr", "description": "安全性と経済性を高めた小型原子炉(SMR)の開発、次世代炉（高温ガス炉等）、分散型エネルギー源としての活用。"},
            {"name": "水素・次世代燃料", "slug": "hydrogen-new-fuels", "description": "グリーン水素の製造・輸送チェーン、アンモニア燃料、e-fuelなどの脱炭素合成燃料の社会実装。"},
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


    # --- 1.5. Special Categories (Formats) ---
    formats = [
        {"name": "日次・週次まとめ", "slug": "summary", "description": "日次・週次のテクノロジーニュースまとめ。主要セクターの重要ニュースを横断的に分析し、1日のトレンドを短時間で把握するための要約レポート。"},
    ]

    print("\n--- Creating Special Categories (Formats) ---")
    for fmt in formats:
        _create_or_update_term(wp, "categories", fmt)

    # --- 3. Tags ---
    tags = [
        # Formats (Tags for Briefing)
        {"name": "Daily", "slug": "daily", "description": "日次レポート"},
        {"name": "Weekly", "slug": "weekly", "description": "週次レポート"},

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
