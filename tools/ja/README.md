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

15プログラムの完全なリスト、その引数、関数、副作用、依存性、検証ルールは[[**docs/DATA_MODEL.md**]](../../docs/ja/DATA_MODEL.md)にあります。 環境・テストコマンドは[[**docs/SETUP.md**]](../../docs/ja/SETUP.md)内にあります。

Excelで日本語の用語を編集した後、rootリポジトリから**tools/translate_markdown_ja.py**を実行します。 [**docs/SETUP.md**]の第1章(../docs/SETUP.md)に、詳細な設定、再生、検証コマンドが組み込まれています。
