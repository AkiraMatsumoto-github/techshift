# TechShift Impact Analysis (インパクト分析) ロジック設計書

## 1. 概要と目的

### 1.1. プロジェクトのゴール
TechShiftのコア機能である **「Impact Analysis (インパクト分析)」** のロジックを定義します。
日々発生する膨大なテクノロジーニュースの中から「未来を変えるシグナル」を抽出し、それが **「ロードマップのどの分岐点（Node）に、どのような影響（加速/遅延）を与えるか」** を論理的かつ自動的に判定します。

### 1.2. ターゲットと提供価値
*   **ターゲット**: Visionary Practitioner (未来を実装する実務者), Macro Investor.
*   **課題**: 「今のニュースが、5年後の未来にどう繋がるのかが見えない」。
*   **提供価値**:
    *   **Context**: ニュースの単なる事実ではなく、「文脈（Roadmapへの影響）」を提供する。
    *   **Logic Chain**: 「風が吹けば桶屋が儲かる」のような、事象から結論に至る論理の連鎖を可視化する。
    *   **Dynamic Update**: 静的な予測ではなく、イベント駆動で動的に更新されるロードマップを提供する。

---

## 2. アーキテクチャ基本方針

### 2.1. イベント駆動型ロードマップ (Event-Driven Roadmap)
従来の「定期レポート」ではなく、**「重要なイベントが発生した時のみ更新される」** 仕組みを採用します。

> **原則:** "No Impact, No Update."
> 意味のないニュースでフィードを埋め尽くしません。ロードマップのタイムラインを変更するほどのインパクトがある場合のみ、ユーザーに通知（Shift Alert）を行います。

### 2.2. システム構成図

```mermaid
graph TD
    News[News Sources] -->|Collect| Collector[automation/collector.py]
    Collector -->|Save| DB_Articles[(MySQL: fs_articles)]
    
    subgraph Impact Analyzer [automation/impact_analyzer.py]
        DB_Articles -->|Fetch New| Analyzer
        DB_Roadmaps[(fs_roadmaps / fs_nodes)] -->|Load Context| Analyzer
        Analyzer -->|Analyze (Gemini 2.0)| AI[Gemini API]
        AI -->|Impact Score & Logic| Analyzer
    end
    
    Analyzer -->|Save Result| DB_Impact[(fs_impact_assessments)]
    Analyzer -->|Update Status| DB_Nodes[(fs_roadmap_nodes)]
    Analyzer -->|Publish| WP[WordPress (Roadmap Page)]
```

---

# TechShift Impact Analysis (Phase 1: Manual Curation)

> [!NOTE]
> **Phase 1 Strategy**:
> 初期フェーズでは、複雑な「自動スコアリング」や「予測日の自動計算」は実装しません。
> **「AIによるニュース収集」 + 「人間によるキュレーション（編集・判断）」** のハイブリッド運用でスタートし、コンテンツの品質と信頼性を最優先します。

## 1. 運用ワークフロー (Phase 1)

### Step 1: 収集 (Automated)
*   **Collector**: PythonスクリプトがRSS/APIからニュースを収集。
*   **Filtering**: 明らかなノイズ（無関係な記事）のみ除外。
*   **Drafting**: Gemini 2.0 Flash が記事の「要約」と「トピック分類」の下書きを作成し、WordPressに「下書き (Draft)」として保存。

### Step 2: 編集・分析 (Human Editorial)
人間のエディター（管理者）が下書きを確認し、以下の判断を行います。

1.  **Selection**: ロードマップに載せるべき「重要なシグナル」か？
2.  **Context**: 公式ロードマップ（Baseline）に対して、これはどういう意味を持つか？（順調？ 遅れ？ 加速？）
3.  **Writing**: `single.php` の記事本文として、その分析結果を執筆・リライトする。

### Step 3: Daily Briefing 作成 (Manual Curated)
編集者は、その日の重要な変更をまとめた「Daily Briefing（日刊記事）」を作成します。

*   **Hero Definition**: トップニュースを1つ選び、Front Pageのヒーローセクション用コピー（Impact Text）を定義します。
    *   例: "AGI Roadmap ACCELERATED BY 1 YR"
*   **Publication**: WordPressの投稿（Category: Daily Briefing）として公開。これがFront Pageの `[TODAY'S SHIFT]` に表示されます。

### Step 4: ロードマップ更新 (DB Sync)
記事公開と同時に、管理画面からDBの該当データを更新します。
*   `fs_roadmap_nodes`: 日付やステータスの変更。
*   `fs_impact_assessments`: 記事とノードの紐付け。

---

## 2. Future Logic (Phase 2 Idea)
*以下は、運用が安定しデータが蓄積された後の「自動化構想」として保持します。*

### Automated Concept
*   **Dual Node Logic**: Floating / Fixed ノードの自動計算。
*   **Impact Score**: -5 ~ +5 の数値化。
*   **Logic Chain**: 因果関係の自動図解生成。

(詳細は `docs/archive/impact_analysis_logic_v1.md` などを参照)

---

## 4. プロンプト設計 (Prompt Engineering)

### 4.1. Impact Analysis Prompt (概念)

```text
あなたは世界最高峰のテクノロジーアナリストです。
以下のニュース記事を読み、TechShiftが追跡している「Technology Roadmap」への影響を評価してください。

Task:
1. 関連するRoadmap Nodeを特定せよ。
2. Impact Scoreを -5(Delay) 〜 +5(Accelerate) で評価せよ。
3. その理由を「Event -> Mechanism -> Outcome」のLogic Chain形式で出力せよ。

News:
{news_content}

Target Nodes:
{list_of_nodes}
```

---

## 5. 今後の拡張性

*   **Confidence Interval**: 予測時期に幅を持たせる（例：2028年 ± 6ヶ月）。
*   **Source Credibility**: ソースの信頼度に応じた重み付け（論文 vs 噂記事）。