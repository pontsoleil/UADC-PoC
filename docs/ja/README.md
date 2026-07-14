# UADC PoC 日本語文書案内

文書を読者の目的に応じた5文書へ完全に再編しました。従来の **SETUP.md**、**TUTORIAL.md**、**DATA_MODEL.md**、**SYNTAX_BINDING.md** 及び **SEMANTIC_BINDING.md** は、次の文書へ置き換えています。

| No. | 文書 | 内容 | 主なプログラム |
| ---: | --- | --- | --- |
| 1 | [環境設定、テスト、保守及びチュートリアル](01_ENVIRONMENT_TESTS_TUTORIAL.md) | 環境設定、定義ファイル、回帰テスト、保守及び一連の実行例 | すべてのプログラム |
| 2 | [構造化CSV、LHM、構文結合及びセマンティック結合](02_STRUCTURED_CSV_LHM_BINDINGS.md) | 21世紀の正規化表としての構造化CSV、LHM、XPath／selectorによる構文結合、**semantic_path**、selector、**[n]**及びCSV列によるセマンティック結合 | **tools/**及び結合表 |
| 3 | [Phase 1 UBL構文結合](03_PHASE1_UBL_SYNTAX_BINDING.md) | **syntax_binding.py** の環境定義、変換操作及び関数単位の処理 | **src/syntax_binding.py** |
| 4 | [Phase 2 ADS PSVセマンティック結合](04_PHASE2_ADS_PSV_SEMANTIC_BINDING.md) | **semantic_binding.py** の環境定義、変換操作及び関数単位の処理。ISO 21378 ADC CSVも併せて説明 | **src/semantic_binding.py** |
| 5 | [Phase 2 ADS XBRL GL構文結合](05_PHASE2_ADS_XBRL_GL_SYNTAX_BINDING.md) | 環境定義、変換操作、結合表の解釈、XPath／selector処理及び関数単位の処理 | **src/syntax_binding_ads_xbrl_gl.py** |

## 推奨する読み順

1. 文書1で環境を設定し、PoCを実行します。
2. 文書2で共通データモデル及び結合方式を理解します。
3. 文書3～5で、各変換経路の実装を確認します。

英語文書である上位の [**docs/**](../) も、同じファイル構成及び文書区分に統一しています。
