# TechShift マスター・メディアコンセプトシート

**Version:** 2.0 (Comprehensive)
**Last Updated:** 2026-01-15
**Status:** 開発指針確定 (Master Document)

本ドキュメントは、B2B技術メディア「TechShift」の構築・運営における唯一の正本（Source of Truth）です。
`concept.md`（初期構想）と `proposal_draft.md`（品質向上提案）の内容を全統合し、実装レベルの粒度まで記述しています。

---

## 1. プロジェクト概要 (Executive Summary)

### 1-1. ビジョン: "Dynamic Navigation Chart"
既存のシンクタンク（NRI, Gartner等）が発行するロードマップは「静的なPDF」であり、発行された瞬間から陳腐化が始まります。
**TechShift** は、日々のニュース解析を通じて、技術ロードマップ上の現在地と未来予測をリアルタイムで微修正（Shift）し続ける、世界初の「動的航海図」です。

### 1-2. ターゲット・ユーザー
*   **Primary: "The Visionary Practitioner" (ビジョナリー実務家)**
    *   企業のCTO、VPoE、新規事業責任者など、技術ロードマップを策定する立場の人。
    *   また、「新しい技術が好きでたまらない」知的好奇心旺盛なテック愛好家層も含む。
    *   **Pain**: 技術の進化が速すぎて、自社の戦略が陳腐化する不安。「絵に描いた餅」ではない、生きた情報を求めている。
*   **Secondary: "Agro-Investor" (マクロ投資家)**
    *   技術トレンドを先行指標として捉え、中長期の投資判断を行う層。

### 1-3. 提供価値 (Core Value)
1.  **Context (点ではなく線)**:
    単発のニュース速報（点）ではなく、「それがロードマップをどう変えたか（線）」としての文脈を提供します。
2.  **Accuracy & Trust (一次情報の徹底)**:
    フェイクや煽りを排除し、公的機関や信頼できる一次情報をベースにした堅牢な予測を提供します。
3.  **Ripple Effect (波及の可視化)**:
    ある分野のブレイクスルーが、他分野のボトルネック解消につながる連鎖を可視化します。

---

## 2. カテゴリ・コンテンツ詳細定義 (Taxonomy)

### 2-1. 初期重点3トピック (Phase 1 Priorities)
立ち上げフェーズ（Phase 1）では、全30カテゴリの中から以下の「最も変化が激しく、社会的インパクトが大きい3つ」にリソースを集中投下します。

1.  **マルチエージェント自律システム** (Category: 次世代知能)
    *   *Why*: 「LLM単体」から「自律エージェント」へのシフトが2026年の最大のトレンドであるため。
2.  **耐量子暗号 (PQC)** (Category: 量子技術)
    *   *Why*: 政府・金融機関のシステム移行期限が迫っており、実需としての関心が高いため。
3.  **全固体電池・次世代蓄電** (Category: 環境・エネルギー)
    *   *Why*: EV、スマホ、ドローンすべてのボトルネックであり、産業への波及効果が最大であるため。

---

### 2-2. 全30カテゴリ一覧 (Full Taxonomy)
WordPressの投稿カテゴリとして実装するリストです。上記3トピック以外はPhase 2以降で順次コンテンツを拡充します。

| メインカテゴリ | サブカテゴリ (WordPress Category Slug) |
| :--- | :--- |
| **1. 宇宙・航空**<br>(Space & Aero) | 1. **再使用型ロケット** (Reusable Rockets)<br>2. **衛星コンステレーション** (Mega Constellations)<br>3. **月面開発・アルテミス計画** (Lunar Exploration)<br>4. **軌道上サービス・宇宙デブリ** (OSAM / Debris)<br>5. **超音速・極超音速技術** (Supersonic / Hypersonic) |
| **2. 量子技術**<br>(Quantum) | 6. **量子ゲート型コンピュータ** (Quantum Gate Computing)<br>7. **量子アニーリング** (Quantum Annealing)<br>8. **耐量子暗号 (PQC)** (Post-Quantum Cryptography)<br>9. **量子センシング** (Quantum Sensing)<br>10. **量子通信・インターネット** (Quantum Internet) |
| **3. 次世代知能**<br>(Advanced AI) | 11. **基盤モデル (LLM/SLM)** (Foundation Models)<br>12. **マルチエージェント自律システム** (Multi-Agent Systems)<br>13. **オンデバイス・エッジAI** (Edge AI)<br>14. **AIネイティブ開発 (No-Code)** (AI-Native Dev)<br>15. **デジタル・プロヴェナンス** (Digital Provenance) |
| **4. ロボ・移動**<br>(Robotics) | 16. **ヒューマノイドロボット** (Humanoid Robots)<br>17. **レベル4 自動運転** (L4 Autonomous Driving)<br>18. **ラストワンマイル配送ロボ** (Delivery Robots)<br>19. **空間コンピューティング (XR)** (Spatial Computing)<br>20. **ブレイン・コンピュータ I/F (BCI)** (BCI) |
| **5. 生命・バイオ**<br>(Life Science) | 21. **AI創薬** (AI Drug Discovery)<br>22. **ゲノム編集・遺伝子治療** (Gene Editing)<br>23. **タンパク質構造予測** (Protein Structure)<br>24. **再生医療・オルガノイド** (Regenerative Medicine)<br>25. **老化制御・長寿研究** (Longevity) |
| **6. 環境・エネ**<br>(Green Tech) | 26. **核融合発電** (Fusion Energy)<br>27. **全固体電池・次世代蓄電** (Solid-State Batteries)<br>28. **直接空気回収 (DAC)** (Direct Air Capture)<br>29. **小型モジュール炉 (SMR)** (SMR)<br>30. **水素・次世代燃料** (Hydrogen & New Fuels) |

---

## 3. クオリティ・コントロール方針 (Quality Assurance)

### 3-1. 信頼性の担保 (Trust & Authority)
AIによる自動生成記事のリスク（ハルシネーション）を防ぎ、プロ向け品質を維持するための厳格なルールです。

1.  **一次情報至上主義 (Primary Source First)**
    *   **優先ソース**: 政府機関（ホワイトハウス、経産省、NASA等）の発表、査読付き論文（Nature/Science等）、上場企業のIR資料（決算説明資料）。
    *   **二次ソースの扱い**: 信頼できる大手技術メディア（TechCrunch, Bloomberg, Nikkei等）は採用するが、ゴシップブログやSNSの噂レベルは除外する。
    *   **アクセス不能時の対応**: 一次情報にアクセスできない場合（有料記事や非公開PDF等）は、記事内に「※本予測は○○の報道に基づいています」と明記する。

2.  **ロジック・チェーンの可視化 (Detailed Logic Chain)**
    予測を変更する場合、単に「2026年になりました」と表示するのではなく、以下の論理構造を表示します。
    > **【予測変更の論理構造】**
    > *   **Step 1 (Fact)**: トヨタが全固体電池の量産パイロットラインを公開 (Source: トヨタ公式リリース 2026.01)
    > *   **Step 2 (Analysis)**: 従来の「実験室レベル」から「工業的製造プロセス」への移行を確認。
    > *   **Step 3 (Impact)**: 量産開始のマイルストーンにおけるボトルネック「製造コスト」の解消目処が立ったと判断。
    > *   **Conclusion**: 普及フェーズの開始予測を「2028年」から「2027年Q4」へ修正。

3.  **確信度の提示**
    *   現状では複雑な数値スコア（S/A/B等）は避け、予測記事の文脈内で「不確実性の高さ」や「前提条件（もし法改正が通れば）」をテキストで丁寧に説明する方針をとる。

### 3-2. UX/UI デザイン方針 (Visualization)

スマートフォンでの閲覧を主とした「見るだけでわかる」UIを構築します。

1.  **Vertical Timeline (縦型タイムライン)**
    *   スマホ画面に最適化するため、**縦軸を時間（上＝現在、下＝未来）**にとったガントチャート・タイムラインを採用します。
    *   ユーザーはスクロールすることで未来へと進んでいく直感的な操作感を実現します。

2.  **Ghost Projection & Drift (変化の残像)**
    *   **Current Line (実線)**: 最新の予測ロードマップ。
    *   **Ghost Line (点線・半透明)**: 3ヶ月前（または半年前）の予測ロードマップ。
    *   この2本の線の「ズレ」を表示することで、**「技術開発が加速しているのか（前倒し）、停滞しているのか（遅延）」**を一目で把握可能にします。

3.  **Layer Structure (3層構造)**
    一つのトピック（例：自動運転）詳細画面では、以下の3つのレイヤーを並行して表示します。
    *   **Layer 1 (Regulation/Gov)**: 規制・法律・インフラ整備（**Fixed Node**: 期限は動かず、達成確度が変動する）。
    *   **Layer 2 (Tech/Biz)**: 技術開発・製品リリース（**Floating Node**: 進捗により予測時期が前倒し/遅延する）。
    *   **Layer 3 (Market)**: コスト・普及率（**Floating Node**: 同上）。

4.  **Ripple Effect (波及効果)**
    *   バッジによる単純なスコアリング（+1.5年など）は廃止。
    *   記事下部に「関連トピックへの波及」セクションを設け、リンク構造で表現する。
    *   例：「GPU性能向上」記事 → 「AI創薬」トピックへリンク（計算能力向上によりシミュレーション加速が見込まれるため）。

---

## 4. コンテンツ生成ロジック (Analysis Logic)

AI（LLM）がニュースを解析し、記事を生成する際の思考プロセス定義です。

### 4-1. 3段階の示唆抽出法 (The "TechShift" Prompting)
1.  **Connecting Dots (接続)**:
    「一見関係ないニュース」と「ロードマップ」を接続する。
    *   例：「テスラのFSDベータ版更新」というニュースを、「日本のレベル4自動運転認可」の議論に接続し、技術的成熟度が法整備に与える圧力を論じる。
2.  **Checking Reality (検証)**:
    「政府目標」と「現場の実態」の乖離を指摘する。
    *   例：政府の「2026年普及目標」に対し、現在のバッテリー素材価格高騰から「コスト的に2026年は困難、2028年が現実線」と指摘する。
3.  **Scenario Planning (ベースシナリオ構築)**:
    *   初期リリースでは複雑な分岐（Best/Worst）はUI上非表示とし、「最も蓋然性の高いベースシナリオ」一本を表示する。
    *   ただし、進行上の**決定的なボトルネック**（ここが通らないと進まない点）や、**マイルストーン**（ここを通過すれば確定する点）は記事内で明確に指摘する。

---

### 4-2. ロードマップの解像度 (Granularity Policy)
「2030年 実用化」といった粗いマイルストーンだけでは実用的ではありません。TechShiftでは、一つの大きな目標を**「技術的絶対条件 (Technical Prerequisites)」**に分解して管理します。

1.  **Level 1 (Major Node)**: 公式ロードマップ上の大きなマイルストーン（例: 全固体電池 実用化）。
2.  **Level 2 (Sub Node)**: それを実現するための技術的詳細要件。
    *   例: "Sulfide Electrolyte Conductivity > 10mS/cm"（電解質伝導率の達成）
    *   例: "Anode Expansion < 5%"（負極膨張率の抑制）
3.  **Update Logic**: ニュース記事は Level 2 (Sub Node) の達成/未達を判定し、その積み上げ結果として Level 1 (Major Node) の予測を変動させる。

### 4-3. Daily Briefing Policy (New)
TechShiftのメインコンテンツは、全セクターを横断する**「日刊ブリーフィング」**です。

*   **Format**: 1日1記事、全セクターを横断 (Cross-Sectional)。
*   **Hero Topic**: その日、全分野の中で**「最も人類の未来に影響を与えたトピック」**を1つだけ選定し、メインVisualとして扱います（例: AI > Space > Bio）。
*   **Structure**:
    1.  **The Shift (Headline)**: 今日の結論（例: "AGI Accelerated by 1 Year"）。
    2.  **Top Story**: Hero Topicの詳細解説。
    3.  **Other Signals**: 他のセクターで起きた重要な動きを箇条書き。
*   **Goal**: 読者はこの記事さえ読めば「今日の技術的進捗」を全て把握できる。

---

## 5. システム・アーキテクチャ詳細

運用コストと開発速度のバランスを考慮し、既存のWordPressエコシステムを最大限活用する構成とします。

### 5-1. 全体構成図 (Phase 1: Hybrid Curation)
Phase 1では「情報の正確性」と「文脈の深さ」を優先し、最終決定権を人間（エディター）が持つハイブリッド構成とします。

```mermaid
graph TD
    subgraph "Sources"
        RSS[Tech/Gov RSS]
    end

    subgraph "Automation (Support)"
        Collector[Python Collector]
        Draft[Draft Generator<br/>(Gemini 2.0)]
    end

    subgraph "Human Decision"
        Editor((Chief Editor))
        Briefing[Daily Briefing]
    end

    subgraph "Platform (WordPress)"
        WP[WordPress]
        Page[Roadmap Page]
        Front[Front Page<br/>(Today's Shift)]
    end

    RSS --> Collector
    Collector --> Draft
    Draft -->|Review| Editor
    Editor -->|1. Write| Briefing
    Editor -->|2. Update| Page
    Briefing -->|Display| Front
    Page -->|Reference| Briefing
```

### 5-2. 技術スタック・仕様
*   **Infrastructure**: Docker based (WP + MySQL).
*   **Frontend**: WordPress Custom Theme (PHP + Vanilla JS).
    *   **Roadmap Page**: `page-roadmap.php` でDBから取得したデータを描画。
    *   **Front Page**: `front-page.php` で最新の "Daily Briefing" をヒーロー表示。
*   **Backend Support**: Python
    *   **Phase 1**: `collector.py` (News Fetching Only).
    *   **Phase 2**: `impact_analyzer.py` (Analysis Automation).

---

## 6. デザイン・トーン (Creative Direction)
(変更なし)

---

## 7. 開発・実行ロードマップ

### Phase 1: Foundation & Daily Briefing (Now)
*   **Infrastructure**: Docker構築 (WP + MySQL)。
*   **Theme**: Front Page (Daily Shift Hero) & Roadmap Page (V4) の実装。
*   **Content**: "Daily Briefing" の運用開始（1日1記事、全セクター横断）。
*   **Logic**: エディターによる手動更新フローの確立。

### Phase 2: Intelligence Automation (Future)
*   Pythonパイプライン (`impact_analyzer.py`) の実装。
*   Ripple Effect Graph の可視化。
*   X (Twitter) Bot の稼働。

### Phase 3: 全カテゴリ展開 (4 ~ 6 Weeks)
*   残りの27カテゴリへの展開。

---

## 8. マーケティング・SEO戦略 (Marketing & SEO)

### 8-1. SEO構造: トピッククラスターモデル
Googleに「このサイトはこのトピックの権威である」と認識させるため、親子構造を徹底します。

1.  **Pillar Content (親: 固定ページ / ロードマップ)**
    *   URL: `/roadmap/[topic-slug]`
    *   役割: そのトピックの「現在地」と「未来」を網羅するダッシュボード。常に最新状態に保つ。
    *   Target KW: "[トピック名] ロードマップ", "[トピック名] 実用化 いつ"
2.  **Cluster Content (子: ニュース記事)**
    *   URL: `/news/[article-slug]`
    *   役割: 日々の変化（Delta）を伝え、親ページへ内部リンクを送る。
    *   Target KW: "[トピック名] 最新ニュース", "[企業名] [技術名]"

### 8-2. 更新戦略: Event-Driven Update (即時整合性)
SEOの「Freshness（鮮度）」と情報の「Consistency（整合性）」を両立させるため、**「ニュース発生時の即時更新」**を採用します。

*   **Logic**:
    *   毎日実行されるニュース生成ボットが、記事を作成すると同時に「ロードマップへの影響（Impact）」を判定する。
    *   もし影響がある場合（例：予測時期がズレた、重要マイルストーンを通過した）、**即座に親ページ（Pillar）のデータも更新する**。
    *   これにより、ユーザーはいつ見ても「記事」と「ロードマップ」の矛盾がない状態を体験できる。

### 8-3. ディストリビューション (Distribution)
Phase 1 (ローンチ時) から以下の自動連携を実装します。

*   **SNS Automation (X / Threads)**:
    *   ニュース記事が公開されたら、要約とリンクを自動投稿。
    *   「Shift Alert」: ロードマップの時期が変更された場合は、"🚨 Market Shift: [トピック名]の普及予測が 2026 Q1 → 2025 Q4 に早まりました" といったシグナル投稿を行う。

