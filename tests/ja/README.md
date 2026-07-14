# 回帰テスト

このディレクトリには、完全なPhase 1とPhase 2 PoCの実行可能な回帰スクリプトが直接含まれています。

テスト カバー:

- LHM 意味パス と Structured CSV 階層;
- UBL 転送と逆 構文バインディング;
- BISビルイング3例とUBLスキーマ検証;
- xBRL-CSV メタデータと タクソノミ Arelle による検証
- すべて 6 ADS XBRL GL 表示モード;
- ADS PSV および ISO 21378 ADC CSV 生成;
- 出力ディレクトリとファイル名の慣例。

**phase1_helpers.py**共有 Phase 1 変換パスとヘルパーを提供します。**roundtrip/**には、生成されたソース、CSV、メタデータ、およびテストで使用されるXMLアーティファクトの再生が含まれています。

[**環境、テスト及びチュートリアル**](../../docs/ja/01_ENVIRONMENT_TESTS_TUTORIAL.md)を参照してテスト一式を実行し、結果を確認します。Phase別の想定結果は、[**docs/README.md**](../../docs/ja/README.md)に掲載したPhase 1 UBL構文結合及びPhase 2 ADS結合の各文書に記載しています。
