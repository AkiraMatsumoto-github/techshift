# FinShift サイトマップ

## 構造図

```mermaid
graph TD
    Home[トップページ /]
    
    subgraph Archives [記事一覧系]
        Cat[カテゴリ一覧 /category/slug/]
        Tag[タグ一覧 /tag/slug/]
        Search[検索結果 /?s=keyword]
        Date[月別アーカイブ /date/yyyy/mm/]
    end

    subgraph IndexLP [市況ランディングページ]
        LP1[日経225 /market/nikkei225/]
        LP2[NYダウ /market/ny-dow/]
        LP3[ドル円 /market/usd-jpy/]
        LP4[ビットコイン /market/btc-usd/]
        LP5[イーサリアム /market/eth-usd/]
        LP6[米10年債 /market/us10y/]
        LP7[インドSENSEX /market/sensex/]
        LP8[上海総合・香港 /market/china-indices/]
        LP9[インドネシアIDX /market/idx-composite/]
    end

    subgraph Categories [主要カテゴリ]
        Cat1[市況速報(Global) /category/global-news/]
        Cat2[仮想通貨(Crypto) /category/crypto/]
        Cat3[株式・指数(Index) /category/index-analysis/]
        Cat4[コモディティ・為替 /category/commodity-fx/]
        Cat5[初心者ガイド(How-to) /category/how-to/]
        Cat6[IPO・決算 /category/ipo-earnings/]
    end

    subgraph Regions [国別エリア]
        Reg1[アメリカ /tag/usa/]
        Reg2[日本 /tag/japan/]
        Reg3[中国 /tag/china/]
        Reg4[インド /tag/india/]
        Reg5[インドネシア /tag/indonesia/]
        Reg6[欧州・その他 /tag/others/]
    end
    
    subgraph Singles [詳細ページ系]
        Post[記事詳細 /post-slug/]
        Page[固定ページ /page-slug/]
    end
    
    Home --> Cat
    Home --> Tag
    Home --> Search
    Home --> Post
    Home --> Page
    Home --> LP1
    Home --> LP2

    Cat --> Cat1
    Cat --> Cat2
    Cat --> Cat3
    Cat --> Cat4
    Cat --> Cat5
    Cat --> Cat6

    Tag --> Reg1
    Tag --> Reg2
    Tag --> Reg3
    Tag --> Reg4
    Tag --> Reg5
    
    %% インデックスページから関連記事へのリンク
    LP1 --> Cat3
    LP4 --> Cat2
    
    %% 具体的な固定ページ
    Page --> About[運営者情報 /about/]
    Page --> Contact[お問い合わせ /contact/]
    Page --> Policy[プライバシーポリシー /privacy-policy/]
    Page --> Sitemap[サイトマップ /sitemap/]
    Page --> Disclaimer[免責事項 /disclaimer/]
```

## URL設計

| ページ種類 | URLパターン | 備考 |
| :--- | :--- | :--- |
| トップページ | `https://finshift.net/` | スイングトレーダー向けダッシュボードUI |
| 記事詳細 | `https://finshift.net/{post-slug}/` | |
| **市況ランディングページ** | | TradingViewウィジェット大 + 関連ニュース |
| 日経225 (日本) | `https://finshift.net/market/japan/` | |
| NYダウ/S&P500 (米国) | `https://finshift.net/market/usa/` | |
| 上海/香港 (中国) | `https://finshift.net/market/china/` | |
| SENSEX/Nifty (インド) | `https://finshift.net/market/india/` | |
| JCI (インドネシア) | `https://finshift.net/market/indonesia/` | |
| 仮想通貨 | `https://finshift.net/market/crypto/` | |
| **主要カテゴリ** | | |
| Daily Briefing | `https://finshift.net/category/daily-briefing/` | 国別デイリーまとめ |
| Featured News | `https://finshift.net/category/featured-news/` | 重要ニュース個別記事 |
| Weekly Summary | `https://finshift.net/category/weekly-summary/` | 週次振り返り & 展望 |
| 投資戦略・コラム | `https://finshift.net/category/strategy/` | |
| 初心者ガイド (How-to) | `https://finshift.net/category/how-to/` | |
| **国別タグ** | | |
| アメリカ | `https://finshift.net/tag/usa/` | |
| 日本 | `https://finshift.net/tag/japan/` | |
| 中国 | `https://finshift.net/tag/china/` | |
| インド | `https://finshift.net/tag/india/` | |
| インドネシア | `https://finshift.net/tag/indonesia/` | |
| **固定ページ** | | |
| 運営者情報 | `https://finshift.net/about/` | |
| お問い合わせ | `https://finshift.net/contact/` | |
| プライバシーポリシー | `https://finshift.net/privacy-policy/` | |
| 免責事項 | `https://finshift.net/disclaimer/` | **重要** (投資助言規制対策) |
