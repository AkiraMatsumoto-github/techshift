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
        {
            "name": "物流DX・トレンド",
            "slug": "logistics-dx",
            "description": "物流DX（デジタルトランスフォーメーション）の最新トレンドから、2024年問題をはじめとする法規制への対応策、AI・IoT・ロボティクスを活用した次世代の物流戦略まで、業界変革に不可欠な情報を網羅。経営層や現場リーダーが知っておくべき、持続可能な物流構築のための実践的なノウハウをお届けします。"
        },
        {
            "name": "倉庫管理・WMS",
            "slug": "warehouse-management",
            "description": "WMS（倉庫管理システム）の選定・導入ガイドから、在庫管理の適正化、ピッキング作業の効率化、庫内オペレーションの改善手法までを徹底解説。人手不足を解消し、生産性を最大化するための倉庫DXノウハウを提供します。"
        },
        {
            "name": "輸配送・TMS",
            "slug": "transportation",
            "description": "TMS（輸配送管理システム）による配車計画の自動化、求荷求車システムの活用、ラストワンマイル配送の最適化など、輸送効率を劇的に改善するソリューションを紹介。2024年問題に伴うドライバー不足対策や、運送コスト削減の実践的なアプローチを提案します。"
        },
        {
            "name": "マテハン・ロボット",
            "slug": "material-handling",
            "description": "自動倉庫（AS/RS）、AGV（無人搬送車）、AMR（自律走行搬送ロボット）、RFIDなど、最新のマテリアルハンドリング機器とロボティクス技術を網羅。省人化・無人化を実現する自動化設備の導入事例や、投資対効果を高めるための選定ポイントを解説します。"
        },
        {
            "name": "サプライチェーン",
            "slug": "supply-chain",
            "description": "SCM（サプライチェーン・マネジメント）の全体最適化、調達物流の改善、グローバルロジスティクスの戦略立案まで、サプライチェーン強靱化のための知見を深掘り。不確実性の高い現代において、リスクヘッジと競争優位性を両立するための戦略的ロジスティクス論を展開します。"
        },
        {
            "name": "事例・インタビュー",
            "slug": "case-studies",
            "description": "物流改革に成功した先進企業の具体的な取り組み事例や、業界トップランナーへの独占インタビューを掲載。DX推進の苦労話から成功の秘訣、現場のリアルな声まで、他社の実践から学べる貴重な一次情報をお届けします。"
        },
        {
            "name": "ニュース・海外",
            "slug": "news-global",
            "description": "米国、中国、欧州など、世界の物流テック最前線をレポート。海外の最新スタートアップ動向、ユニコーン企業の戦略、クロスボーダーECのトレンドなど、日本の物流業界に影響を与えるグローバルニュースをいち早く解説します。"
        },
    ]
    
    print("Creating/Updating categories...")
    for cat in categories:
        try:
            # 1. Try to create
            url = f"{wp.api_url}/categories"
            response = requests.post(url, json=cat, auth=wp.auth)
            
            if response.status_code == 201:
                print(f"✓ Created category: {cat['name']}")
            elif response.status_code == 400 and "term_exists" in response.text:
                # 2. If exists, update
                print(f"- Category already exists: {cat['name']}. Updating...")
                
                # Get existing category ID
                # Since api_url already contains ?rest_route=..., we must use & for parameters
                get_url = f"{wp.api_url}/categories&slug={cat['slug']}"
                get_res = requests.get(get_url, auth=wp.auth)
                
                if get_res.status_code == 200 and len(get_res.json()) > 0:
                    cat_id = get_res.json()[0]['id']
                    update_url = f"{wp.api_url}/categories/{cat_id}"
                    # Update description
                    update_res = requests.post(update_url, json={'description': cat['description']}, auth=wp.auth)
                    
                    if update_res.status_code == 200:
                         print(f"  ✓ Updated description for: {cat['name']}")
                    else:
                         print(f"  ✗ Failed to update description: {update_res.text}")
                else:
                    print(f"  ✗ Could not find existing category ID for slug: {cat['slug']}")

            else:
                print(f"✗ Failed to create {cat['name']}: {response.text}")
        except Exception as e:
            print(f"✗ Error processing {cat['name']}: {e}")

def create_tags(wp):
    """Create all tags defined in content strategy with SEO descriptions."""
    tags = [
        # Industry
        {
            "name": "製造業", 
            "slug": "manufacturing",
            "description": "工場内物流から調達、出荷まで。製造業のサプライチェーン最適化、スマートファクトリー化、IoT活用に関する最新事例とソリューションを解説。"
        },
        {
            "name": "小売・流通", 
            "slug": "retail",
            "description": "オムニチャネル対応、店舗配送、在庫適正化など、変化の激しい小売・流通業界の物流戦略と店舗DX、効率化手法を紹介。"
        },
        {
            "name": "EC・通販", 
            "slug": "ecommerce",
            "description": "EC物流の自動化、フルフィルメント戦略、翌日配送の実現など、急成長するEC市場を勝ち抜くためのロジスティクス戦略とツール。"
        },
        {
            "name": "3PL・倉庫", 
            "slug": "3pl-warehouse",
            "description": "3PL事業者のための差別化戦略、WMS活用、荷主への提案力強化など、競争力ある倉庫運営と収益化のための実践ノウハウ。"
        },
        {
            "name": "食品・飲料", 
            "slug": "food-beverage",
            "description": "コールドチェーン（低温物流）、HACCP対応、鮮度管理など、食の安全と品質を守るための高度な物流技術と規制対応。"
        },
        {
            "name": "アパレル", 
            "slug": "apparel",
            "description": "SKU管理の効率化、返品物流（リバースロジスティクス）、RFID活用など、アパレル・ファッション業界特有の物流課題を解決。"
        },
        {
            "name": "医薬品・医療", 
            "slug": "medical",
            "description": "GDP（適正流通基準）対応、トレーサビリティ確保、厳格な温度管理など、生命を守る医薬品物流の専門知識と管理手法。"
        },
        # Theme
        {
            "name": "コスト削減", 
            "slug": "cost-reduction",
            "description": "運送費、保管費、人件費など、物流コストの構造を可視化し、ムリ・ムダ・ムラを省いて利益を最大化するための具体的施策。"
        },
        {
            "name": "人手不足対策", 
            "slug": "labor-shortage",
            "description": "採用難時代の省人化ソリューション。自動化機器の導入からワークシェアリング、外国人材活用まで、持続可能な現場作り。"
        },
        {
            "name": "品質向上・誤出荷防止", 
            "slug": "quality-improvement",
            "description": "誤出荷ゼロへの挑戦。バーコード管理、検品システムの導入、作業標準化など、物流品質を高めて顧客信頼を獲得する方法。"
        },
        {
            "name": "環境・SDGs", 
            "slug": "environment-sdgs",
            "description": "グリーンロジスティクス、脱炭素（カーボンニュートラル）、モーダルシフトなど、環境配慮型物流への取り組みと企業の社会的責任。"
        },
        {
            "name": "安全・BCP", 
            "slug": "safety-bcp",
            "description": "物流現場の事故防止、安全教育、そして災害時の事業継続計画（BCP）策定など、リスクマネジメントの重要ポイント。"
        },
        {
            "name": "補助金・助成金", 
            "slug": "subsidy",
            "description": "物流効率化法や省エネ補助金など、設備投資やDX推進に活用できる最新の補助金・助成金情報と申請のポイント。"
        },
        # Region/Country
        {
            "name": "日本", 
            "slug": "japan",
            "description": "国内物流の市況、2024年問題などの法改正、行政の動きなど、日本の物流ビジネスを取り巻く最新ニュースとトレンド。"
        },
        {
            "name": "アメリカ", 
            "slug": "usa",
            "description": "物流テックの震源地・アメリカの最新事例。AmazonやWalmartの戦略、シリコンバレー発のスタートアップ動向を現地視点で解説。"
        },
        {
            "name": "ヨーロッパ", 
            "slug": "europe",
            "description": "環境先進国・欧州のサステナブルな物流事例。フィジカルインターネット、都市内物流（シティロジスティクス）の先端モデル。"
        },
        {
            "name": "中国", 
            "slug": "china",
            "description": "世界の工場から巨大消費市場へ。アリババ、JD.comなどが牽引する圧倒的なスピードと規模の中国スマート物流と無人化技術。"
        },
        {
            "name": "東南アジア", 
            "slug": "southeast-asia",
            "description": "急成長するASEAN市場の物流事情。コールドチェーン需要や越境EC、ラストワンマイルの課題と日本企業の進出チャンス。"
        },
        {
            "name": "グローバル", 
            "slug": "global",
            "description": "国境を越えるサプライチェーン。国際輸送、地政学リスク、グローバル企業のロジスティクス戦略など、世界視点の物流情報。"
        },
    ]
    
    print("\nCreating/Updating tags...")
    for tag in tags:
        try:
            # 1. Try to create
            url = f"{wp.api_url}/tags"
            response = requests.post(url, json=tag, auth=wp.auth)
            
            if response.status_code == 201:
                print(f"✓ Created tag: {tag['name']}")
            elif response.status_code == 400 and "term_exists" in response.text:
                # 2. If exists, update
                print(f"- Tag already exists: {tag['name']}. Updating...")
                
                # Get existing tag ID
                get_url = f"{wp.api_url}/tags&slug={tag['slug']}" # tags endpoint usually accepts ?slug parameter
                get_res = requests.get(get_url, auth=wp.auth)
                
                if get_res.status_code == 200 and len(get_res.json()) > 0:
                    tag_id = get_res.json()[0]['id']
                    update_url = f"{wp.api_url}/tags/{tag_id}"
                    # Update description
                    update_res = requests.post(update_url, json={'description': tag['description']}, auth=wp.auth)
                    
                    if update_res.status_code == 200:
                         print(f"  ✓ Updated description for: {tag['name']}")
                    else:
                         print(f"  ✗ Failed to update description: {update_res.text}")
                else:
                    print(f"  ✗ Could not find existing tag ID for slug: {tag['slug']}")
            else:
                print(f"✗ Failed to create {tag['name']}: {response.text}")
        except Exception as e:
            print(f"✗ Error processing {tag['name']}: {e}")

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
