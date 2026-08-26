# UADC_PoC Decisions

更新日: 2026-08-26 (JST)

## 採用済み設計指針

### D-001 Binding方式を混同しない

- Syntax BindingはXPath、JSONPath、CSV位置等の物理構文を扱う。
- Semantic Bindingは入力項目をHMD `semantic_path`へ対応付ける。
- Flat CSVは必要に応じてoccurrence selectorを含む`semantic_path`を列識別に使う。
- 別の`flat_semantic_path`という概念を導入しない。

### D-002 Binding Tableを外部化する

- 列、条件、変換、既定値、error処理はBinding Tableまたは明示された共通関数へ置く。
- source固有規則を汎用処理へ暗黙に混在させない。

### D-003 XBRL-GL-Nextとの境界は正式HMDとする

- UADCはXBRL-GL-NextのFSM／BSM／candidate LHMを直接修正しない。
- 正式HMDの`semantic_path`、`module`、`local_name`、`xpath`を版・SHA付きで参照する。

### D-004 LedgerExplorerとの境界はStructured CSVとする

- LedgerExplorer向け表示・分析データは公開可能なStructured CSV fixtureとして受け渡す。
- UADC内部のBinding TableをLedgerExplorer表示ロジックへ複製しない。

### D-005 実会計データを公開baselineに含めない

- 公開テストは合成または公開sampleだけで実行する。
- ログ、変換結果、抽出masterも個別承認なしにGitへ追加しない。

### D-006 CII BindingはCEN/TS Table 2を正本としgeneric runtimeで実行する

- CII D16B Syntax Bindingのsemantic path、XPath、cardinalityおよび順序はCEN/TS 16931-3-3:2020 Table 2を正本としてレビューする。
- Table 3は逆変換時の選択制約とambiguity判定に使用する。
- required empty container、predicate、alias-relative path、named transformation、XSD child orderはBinding／schemaから汎用的に処理し、CII項目別分岐をruntimeへ追加しない。
- 正式baselineは237行Binding SHA-256 `B529F2585CA2A5FBFDAF673A6F96B98135CE274B8B022C1B791FF9863C23BD23`、runtime SHA-256 `7CA92B9DB1724D1A5A3AE9C0FDD9A081ED73F34D1125A8626C880BE2AE5B11A9`とする。
- 購入済み規格PDFとtask-local抽出物はFormal repositoryへ格納しない。

## 保留事項

- 3プロジェクト共通integration manifestのschema。
- WORK側実装差分を次の正式baselineへ採用する条件。
