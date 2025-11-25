# LogiShift サイトマップ

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
    
    subgraph Singles [詳細ページ系]
        Post[記事詳細 /post-slug/]
        Page[固定ページ /page-slug/]
    end
    
    Home --> Cat
    Home --> Tag
    Home --> Search
    Home --> Post
    Home --> Page
    
    Cat --> Post
    Tag --> Post
    Search --> Post
    
    %% 具体的な固定ページ
    Page --> About[運営者情報 /about/]
    Page --> Contact[お問い合わせ /contact/]
    Page --> Policy[プライバシーポリシー /privacy-policy/]
    Page --> Sitemap[サイトマップ /sitemap/]
```

## URL設計

| ページ種類 | URLパターン | 備考 |
| :--- | :--- | :--- |
| トップページ | `https://logishift.jp/` | |
| 記事詳細 | `https://logishift.jp/{post-slug}/` | 英単語のスラッグを推奨 |
| カテゴリ一覧 | `https://logishift.jp/category/{slug}/` | |
| タグ一覧 | `https://logishift.jp/tag/{slug}/` | |
| 固定ページ (汎用) | `https://logishift.jp/{slug}/` | |
| 運営者情報 | `https://logishift.jp/about/` | |
| お問い合わせ | `https://logishift.jp/contact/` | |
| プライバシーポリシー | `https://logishift.jp/privacy-policy/` | |
| サイトマップ | `https://logishift.jp/sitemap/` | |
| 検索結果 | `https://logishift.jp/?s={keyword}` | |
