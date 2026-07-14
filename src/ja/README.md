# 運用変換スクリプト

このディレクトリには、プロダクションPoCコンバーターが含まれています。

- **syntax_binding.py**Phase 1 UBL XML を Structured CSV 変換、
xBRL-CSV メタデータ生成と Structured CSV から UBL XML 逆変換。
- **semantic_binding.py**Phase 2 Structured CSV を ADS PSV または ISO に実行します
21378 ADC区切り変換。
- **syntax_binding_ads_xbrl_gl.py**Phase 2 Structured CSV を ADS XBRL に実行
GLインスタンス変換。
- **tutorial/**には、これらの運用プログラムを呼び出す短いラッパーが含まれています。

文書:

- [**Phase 1 UBL構文結合**](../../docs/ja/03_PHASE1_UBL_SYNTAX_BINDING.md)
- [**Phase 2 ADS PSVセマンティック結合**](../../docs/ja/04_PHASE2_ADS_PSV_SEMANTIC_BINDING.md)
- [**Phase 2 ADS XBRL GL構文結合**](../../docs/ja/05_PHASE2_ADS_XBRL_GL_SYNTAX_BINDING.md)
- [**環境、テスト及びチュートリアル**](../../docs/ja/01_ENVIRONMENT_TESTS_TUTORIAL.md)

**tools/tutorial/**のプログラムは、単純化された教育の実装であり、このディレクトリの運用コンバーターと混同してはならない。
