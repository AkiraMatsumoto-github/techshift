# SNS自動投稿 実装計画

## 目的
TechShiftで記事が公開された直後に、X (Twitter) および Threads へ自動投稿する仕組みを構築します。
単純にリンクを貼るだけでなく、クリック率（CTR）を高めるための魅力的な要約やハッシュタグを含めて投稿します。

## 投稿フォーマット (X / Threads)

エンゲージメントを最大化するため、以下のフォーマットを使用します。
投稿内容はGeminiが記事の内容に基づいて自動生成します。

```text
【新着記事】
{フックとなるタイトル}

{要約（80〜100文字程度で、続きを読みたくなる内容）}

{ハッシュタグ（3〜5個）}

{記事URL}
```

**実際の投稿例:**
```text
【新着記事】
倉庫の「2024年問題」は自動化で乗り越える！

人手不足が深刻化する中、注目の「AGV（無人搬送車）」導入でピッキング効率が3倍になった事例を解説。
導入コストや失敗しない選び方のポイントもまとめました。

#物流DX #AGV #自動化 #2024年問題

https://techshift.net/automation-agv-guide/
```

## アーキテクチャ

複数のプラットフォーム（X, Threads等）に対応できるよう、モジュール型の設計にします。

### 1. `SNSClient` (新規クラス)
各SNSプラットフォームへの統合インターフェースを提供します。
- ファイル: `automation/sns_client.py`
- 役割:
    - X API への認証 (ライブラリ `tweepy` を使用)
    - Threads API への認証 (将来的な実装)
    - `post_to_x(content: str)`
    - `post_to_threads(content: str)` (将来実装)

### 2. `GeminiClient` の機能拡張
SNS投稿用のテキストを生成するメソッドを追加します。
- ファイル: `automation/gemini_client.py`
- メソッド: `generate_sns_content(title, content, article_type)`
- プロンプト戦略:
    - 入力: 記事タイトル、本文（冒頭2000文字程度）
    - 出力: JSON形式 `{"hook": "...", "summary": "...", "hashtags": ["#tag1", "#tag2"]}`
    - 制約: 要約は簡潔に（100文字以内）。ハッシュタグは関連性の高いものを3〜5個厳選。

### 3. `generate_article.py` への統合
- `wp.create_post` が成功し、URLが確定した後に実行します：
    1. `gemini.generate_sns_content()` を呼び出して投稿用テキストを作成。
    2. フォーマットに従ってテキストを整形。
    3. `sns_client.post_to_x()` を呼び出して投稿。

## 実装ステップ

1.  **ライブラリ導入**: `tweepy` をインストールします（X APIの標準的なライブラリ）。
    - `pip install tweepy`
2.  **`GeminiClient`**: SNS用テキスト生成メソッド (`generate_sns_content`) を実装します。
3.  **`SNSClient`**: X認証および投稿ロジックを実装します。
4.  **`generate_article.py`**: 上記コンポーネントを統合し、記事公開フローに組み込みます。

## 依存ライブラリ

- **tweepy**: X API v2 との通信に使用します。
