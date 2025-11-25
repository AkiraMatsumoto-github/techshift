# LogiShift (ロジシフト)

物流業界の課題解決に貢献するSEOメディアプロジェクト。

## プロジェクト概要
- **目的**: 物流担当者・経営層向けに、コスト削減やDX、2024年問題などの高品質な情報を提供。
- **目標**: 業界No.1の物流メディアを目指す。

## 技術スタック
- **CMS**: WordPress
- **テーマ**: オリジナルカスタムテーマ開発 (Gemini共同開発)

## ディレクトリ構成
- `docs/`: ドキュメント類
    - `00_project/`: プロジェクト概要、運用ガイドライン
    - `01_architecture/`: システム構成、サイトマップ
    - `02_design/`: デザイン仕様、ワイヤーフレーム
- `themes/`: WordPressカスタムテーマ格納用

## 開発状況
- [x] 企画・設計フェーズ完了
- [x] 環境構築フェーズ完了
- [ ] 実装フェーズ (現在ここ)

## ローカル開発環境の起動
Dockerを使用してローカル環境を起動します。

1. **起動**:
   ```bash
   docker-compose up -d
   ```
2. **アクセス**:
   - ブラウザで [http://localhost:8000](http://localhost:8000) にアクセス。
   - WordPressのインストール画面が表示されるので、手順に従ってインストール。
3. **テーマ有効化**:
   - 管理画面 (`/wp-admin/`) > 外観 > テーマ から「LogiShift」を有効化。

## 参照ドキュメント
- [Gemini運用ガイドライン](docs/00_project/GEMINI.md)
- [サイトアーキテクチャ](docs/01_architecture/site_architecture.md)
- [セットアッププロセス](docs/01_architecture/SETUP_PROCESS.md)
- [デザインガイドライン](docs/02_design/design_guidelines.md)
