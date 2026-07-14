# UADC ポック 文書

このディレクトリには、UADC PoC の現在の運用ガイド、データ型仕様、アーキテクチャの決定レコードが含まれています。

## 文書 セット

1. [**SETUP.md**](SETUP.md) - GitHubのセットアップ、Python環境を説明します。
ソース定義、生成されたデータ、環境チェック、回帰テスト、リポジトリメンテナンス、およびMarkdown PDFワークフロー。
2. [**TUTORIAL.md**](TUTORIAL.md) - のための短いエンドツーエンドの練習を提供して下さい
Phase 1 と Phase 2 の処理と出力の検査
3. [**SYNTAX_BINDING.md**](SYNTAX_BINDING.md) - Phase 1 構文を指定します
結合、UBL入力配置、Structured CSVおよびメタデータ生成、逆UBL変換、コマンド使用量、内部処理、検証。
4. [**SEMANTIC_BINDING.md**](SEMANTIC_BINDING.md) - 区 Phase 2
ADS PSV、 ADS XBRL GL、 ISO 21378 ADC へのバインディングとコンバージョン。対象カバレッジ、コマンド使用量、内部処理、検証を含みます。
5. [**DATA_MODEL.md**](DATA_MODEL.md) - LHM、階層型Tidy Dataを定義します、
Structured CSV 代替正規化フォーム、階層および multiplicity ルール、 意味パスs、 OIM タクソノミ 構造、通貨および selector ルール、監査データ境界、およびすべての支持ツール。

## 建築の決定

[**決定・決定**](../decisions/ja/README.md)はアーキテクチャの決定レコードが含まれています。 それらは重要な適用範囲、階層、タクソノミ、結合、検証、出力レイアウト、および文書の選択肢の理由を説明しています。

## 文書 ソース

Markdownファイルは文書ソースです。 PDFは、出版物や同期リリースの準備時に、現在のMarkdownから生成されます。

プログラムディレクトリのショート GitHub-browser の要約は別々に提供されます**src/README.md**, **src/tutorial/README.md**, **tools/README.md**, **tools/taxonomy/README.md**, **tools/tutorial/README.md**と**tests/README.md**.
