# Antigravity + Vertex AI (Gemini 3 Pro) セットアップガイド

このドキュメントは、Antigravity (Gemini CLI) を Google Cloud Vertex AI 経由で利用し、最新の **Gemini 3 Pro** モデルを使用するためのセットアップ手順をまとめたものです。

## 1. 前提条件

*   **Google Cloud Project (GCP)**:
    *   有効なGoogle Cloudプロジェクトがあること。
*   **Google Cloud SDK (`gcloud`)**:
    *   PCに `gcloud` コマンドがインストールされていること。

## 2. 認証設定 (Google Cloud SDK)

ターミナルで以下のコマンドを実行し、Googleアカウントで認証を行います。

### 手順 1: Googleアカウントでのログイン

まず、`gcloud` コマンド自体があなたのGoogleアカウントを使えるようにします。

```bash
gcloud auth login
```

**実行後の流れ:**
1.  コマンドを実行すると、ブラウザが自動的に起動します（またはURLが表示されるのでクリックします）。
2.  Googleのログイン画面が表示されるので、**GCPプロジェクトへのアクセス権を持つGoogleアカウント**を選択してログインします。
3.  「Google Cloud SDK が Google アカウントへのアクセスを求めています」という画面が表示されたら、**「許可 (Allow)」** をクリックします。
4.  ブラウザに「You are now authenticated with the Google Cloud SDK!」と表示されれば成功です。ターミナルに戻ってください。

### 手順 2: アプリケーションのデフォルト認証情報 (ADC) の設定

次に、Antigravity (プログラム) が認証情報を使えるように設定します。

```bash
gcloud auth application-default login
```

**実行後の流れ:**
1.  再度ブラウザが起動します。
2.  先ほどと同じGoogleアカウントを選択します。
3.  「Google Auth Library が Google アカウントへのアクセスを求めています」という画面で、再度 **「許可 (Allow)」** をクリックします。
4.  認証が完了すると、ターミナルに `Credentials saved to file: [...]` と表示されます。これで準備完了です。

## 3. 環境変数の設定 (`~/.gemini/.env`)

AntigravityがVertex AIを使用するように、ホームディレクトリ配下の設定ファイルを作成・編集します。

**ファイルパス:** `~/.gemini/.env`

以下の内容を記述してください。`GOOGLE_CLOUD_PROJECT` には各自のプロジェクトIDを設定してください。

```env
# Vertex AI を有効化
GOOGLE_GENAI_USE_VERTEXAI=true

# 使用するGoogle CloudプロジェクトID (各自のIDに書き換えてください)
GOOGLE_CLOUD_PROJECT=231503280916

# リージョン (Gemini 3 Proが利用可能なリージョン、例: us-central1)
GOOGLE_CLOUD_LOCATION=us-central1
```

> **Note:** ディレクトリ `~/.gemini` が存在しない場合は、`mkdir ~/.gemini` で作成してください。

## 4. モデルの選択 (Antigravity UI)

設定が完了したら、Antigravity (Agent) の画面でモデルを選択します。

1.  Antigravityのチャット画面を開きます。
2.  モデル選択プルダウンメニューをクリックします。
3.  **"Gemini 3 Pro (High)"** を選択します。

## 5. 動作確認

Antigravityで適当な質問（例: "Hello"）を投げ、正常に応答が返ってくることを確認してください。

> **補足:**
> *   **Gemini 3 Pro** は現在プレビュー版です。
> *   AgentがPC操作（コマンド実行やファイル編集）を行う際の「Computer Use」機能については、システム上 **"Gemini 2.5 Pro"** のSKUとして課金・ログ記録される場合がありますが、これは正常な動作です。

## 6. 開発ワークフロー

### Pull Request (PR) の利用
大きな修正や機能追加を行う際は、直接 `main` ブランチにプッシュせず、以下の手順で Pull Request (PR) を作成します。

1.  作業用の新しいブランチを作成する (`git checkout -b feature/xxx` など)
2.  変更をコミットし、リモートリポジトリにプッシュする
3.  GitHub上で `main` ブランチに対する Pull Request を作成する
4.  (必要に応じて) レビューを行い、マージする
