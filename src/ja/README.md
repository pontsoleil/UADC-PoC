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

- [**docs/SYNTAX_BINDING.md**](../../docs/ja/SYNTAX_BINDING.md)
- [**docs/SEMANTIC_BINDING.md**](../../docs/ja/SEMANTIC_BINDING.md)
- [**docs/TUTORIAL.md**](../../docs/ja/TUTORIAL.md)

**tools/tutorial/**のプログラムは、単純化された教育の実装であり、このディレクトリの運用コンバーターと混同してはならない。
