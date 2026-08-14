# UADC_PoC Decisions

更新日: 2026-08-14 (JST)

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

## 保留事項

- 3プロジェクト共通integration manifestのschema。
- WORK側実装差分を次の正式baselineへ採用する条件。
