# 支援ツール

このディレクトリには、モデルのメンテナンスと開発支援プログラム、運用中のPhase 1とPhase 2コンバータではなくが含まれています。

ツールカバー:

- EN 16931 LHM 生成、正規化、注文、カバレッジ、検証;
- 構文バインディング 生成;
- 往復アーティファクト再生;
- ローカル xBRL-CSV タクソノミ 生成下**タクソノミ/**;
- **tutorial/**の下の単純化されたコンバーターの実装;
- **translate_markdown_ja.py**および
**docs/ja/TERMINOLOGY.csv**;
- **psv_viewer.html**でローカル ADS PSV と CSV の検査。

15プログラムの一覧、引数、関数、副作用、依存関係及び検証規則は、[**構造化CSV、LHM及び結合**](../../docs/ja/02_STRUCTURED_CSV_LHM_BINDINGS.md)に記載しています。環境及びテストのコマンドは、[**環境、テスト及びチュートリアル**](../../docs/ja/01_ENVIRONMENT_TESTS_TUTORIAL.md)に記載しています。

Excelで日本語用語を編集した後、リポジトリのルートから **tools/translate_markdown_ja.py** を実行します。詳細な設定、再生成及び検証コマンドは、[**環境、テスト及びチュートリアル**](../../docs/ja/01_ENVIRONMENT_TESTS_TUTORIAL.md)の第10.1節に記載しています。
