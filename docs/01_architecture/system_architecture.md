# TechShift System Architecture

## 1. System Overview

本システムは、世界中の技術ニュースを自動収集し、技術ロードマップへの影響（Impact）を分析してWebメディアに公開する完全自動化パイプラインです。
TechShiftでは、**「トピック別ロードマップ（ストック/親）」** と **「最新ニュース（フロー/子）」** のクラスター構造により、技術の現在地を動的に可視化します。

```mermaid
graph TD
    subgraph "Data Sources (Global)"
        S1[Tech Media<br/>(TechCrunch, VentureBeat, Nature)] -->|RSS/Scraping| Crawler
        S2[Gov/Institutions<br/>(NASA, White House, METI)] -->|RSS| Crawler
        S3[Corporate IR<br/>(NVIDIA, Toyota, IonQ)] -->|Monitoring| Crawler
    end

    subgraph "Intelligence Automation (Phase 2: Future)"
        Crawler --> RawDB[(Raw Data Store)]
        RawDB --> Pipeline{Pipeline Orchestrator<br/>(Event-Driven)}
        
        Pipeline -->|Fact Extraction| FactParser[Fact Parser]
        FactParser -->|Impact Analysis| ImpactAnalyzer[Impact Analyzer<br/>(Gemini 3 Pro)]
        ImpactAnalyzer -->|Logic Chain| LogicBuilder[Logic Build]
        
        LogicBuilder --> Drafter[Article Drafter]
    end

    subgraph "Presentation (WordPress)"
        Drafter -->|Post & Update| WP[WordPress Site]
        WP -->|Display| Page[Roadmap Page<br/>(Vertical Timeline)]
        WP -->|Update| Meta[Custom Fields<br/>(Prediction Date/Phase)]
    end
```

## 2. Component Design

### 2.1. Collectors (`automation/collectors/`)
外部データ収集を担当するモジュール群。
- **`collector.py`**: 
    - 重点3トピックおよび全30カテゴリに関連するRSSフィードを巡回。
    - **Filter**: 一般的なガジェットニュース（スマホのレビュー等）を除外し、「技術的進歩」に焦点を当ててフィルタリング。
- **`url_reader.py`**: 
    - 論文要旨やプレスリリースの本文抽出。
    - **Anti-Bot**: 取得困難なサイトはRSS Summaryで代替するフォールバック機能。

### 2.2. AI Analysis (`automation/analysis/`)
取得データに「技術的付加価値」を与えるコアロジック。
- **`impact_analyzer.py`** (Core): 
    - **Input**: ニュース記事 + 既存ロードマップ情報
    - **Process**:
        1.  **Fact**: 「何が起きたか」を特定。
        2.  **Analysis**: それが技術的ボトルネックの解消に繋がるか分析。
        3.  **Impact**: ロードマップの予測時期（Floating）または達成確度（Fixed）を更新判定。
    - **Output**: 構造化データ（JSON）と論理チェーン（Logic Chain）。
- **`sentiment_analyzer.py`**:
    - 技術トレンドに対する「過度な期待（Hype）」と「幻滅（Disillusionment）」を判定。
- **`scorer.py`**: 
    - ニュースの重要度を0-100で採点し、ロードマップ更新のトリガーとするかを決定。

### 2.3. Tools (`automation/tools/`)
- **`setup_taxonomy.py`**: WordPress上にTechShift用のカテゴリ構造（30トピック）を自動構築。

## 3. Workflow & Pipeline

### 3.1. Pipeline Execution
- **Trigger**: 6時間ごとの定期実行 + 緊急ニュース検出時。
- **Flow**:
    1.  ニュース収集・重要度判定。
    2.  重要ニュースの場合、記事（News Post）を生成。
    3.  同時に `Impact Analyzer` が親トピックへの影響を計算。
    4.  影響がある場合、親ページ（Roadmap Page）のメタデータ（予測時期、フェーズ）を更新。
    5.  X (Twitter) へ "Shift Alert" を通知。

## 4. WordPress Architecture (`themes/techshift`)

### 4.1. Theme Structure
- **Design**: "Intelligent Reality" (信頼感のあるラボ/シンクタンク風)。
- **`page-roadmap.php`** (核心): 
    - **Vertical Timeline**: 縦型のガントチャートでマイルストーンを表示。
    - **3-Layer View**: Regulation / Technology / Market の3層構造。
    - **Drift View**: 「前回の予測（Ghost）」と「最新の予測（Real）」のズレを可視化。
- **`single.php`**: 
    - 記事詳細。冒頭に「ロードマップへの影響スコア」を表示。

### 4.2. Data Integration
Automationとテーマの連携用データ。
- **Custom Fields (Roadmap Page)**:
    - `current_phase`: 現在のフェーズ（例: Phase 2 - PoC）。
    - `prediction_date`: 実用化予測時期（例: 2027-Q4）。
    - `last_shift_reason`: 直近で予測変更が起きた理由（記事IDへのリンク）。

## 5. Directory Structure

```text
/techshift
├── automation/
│   ├── collectors/
│   ├── analysis/           # Impact Analyzer, Scorer
│   ├── tools/              # Taxonomy Setup
│   └── pipeline.py         # Main Entry Point
├── themes/
│   └── techshift/          # Custom WP Theme
│       ├── page-roadmap.php
│       ├── single.php
│       └── ...
└── docs/
    ├── 00_project/         # Project Management
    ├── 01_architecture/    # System Design
    └── 00_meta/            # Operation Guidelines
```
