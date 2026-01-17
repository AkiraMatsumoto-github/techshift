# TechShift サイトマップ

## 構造図

```mermaid
graph TD
    Home[トップページ /]
    
    subgraph Roadmaps [トピック・ロードマップ (親)]
        RM1[マルチエージェント /roadmap/multi-agent/]
        RM2[全固体電池 /roadmap/solid-state-battery/]
        RM3[耐量子暗号 /roadmap/pqc/]
        RM_Other[...他27トピック]
    end

    subgraph Archives [記事一覧系]
        Cat[カテゴリ一覧 /category/slug/]
        Tag[タグ一覧 /tag/slug/]
        Search[検索結果 /?s=keyword]
    end

    subgraph Categories [主要カテゴリ]
        Cat1[ニュース(News) /category/news/]
        Cat2[分析・コラム(Insights) /category/insights/]
        Cat3[予測(Prediction) /category/prediction/]
    end
    
    subgraph Singles [詳細ページ系]
        Post[記事詳細 /post-slug/]
        Page[固定ページ /page-slug/]
    end
    
    Home --> RM1
    Home --> RM2
    Home --> RM3
    Home --> Cat
    Home --> Search
    Home --> Post
    Home --> Page
    
    %% ロードマップページから関連ニュースへのリンク
    RM1 --> Post
    RM2 --> Post
    
    %% カテゴリ構造
    Cat --> Cat1
    Cat --> Cat2
    Cat --> Cat3

    %% 固定ページ
    Page --> About[運営者情報 /about/]
    Page --> Contact[お問い合わせ /contact/]
    Page --> Policy[プライバシーポリシー /privacy-policy/]
    Page --> Sitemap[サイトマップ /sitemap/]
    Page --> Disclaimer[免責事項 /disclaimer/]
```

## URL設計

| ページ種類 | URLパターン | 備考 |
| :--- | :--- | :--- |
| トップページ | `https://techshift.net/` | **Global Dashboard** (全ロードマップのヒートマップ & Alert Stream) |
| **記事詳細** | `https://techshift.net/{post-slug}/` | 個別ニュース・分析記事 |
| **トピック・ロードマップ (Pillar)** | | **固定ページ + 専用テンプレート** |
| マルチエージェント (AI) | `https://techshift.net/roadmap/multi-agent/` | |
| 全固体電池 (Energy) | `https://techshift.net/roadmap/solid-state-battery/` | |
| 耐量子暗号 (Quantum) | `https://techshift.net/roadmap/pqc/` | |
| ...(その他全30トピック) | `https://techshift.net/roadmap/{slug}/` | |
| **カテゴリ** | | |
| ニュース | `https://techshift.net/category/news/` | フロー情報 |
| インサイト | `https://techshift.net/category/insights/` | ストック解説 |
| **固定ページ** | | |
| 運営者情報 | `https://techshift.net/about/` | |
| お問い合わせ | `https://techshift.net/contact/` | |
| 免責事項 | `https://techshift.net/disclaimer/` | |
