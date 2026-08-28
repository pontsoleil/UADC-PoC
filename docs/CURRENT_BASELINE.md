# UADC_PoC Current Baseline

記録日: 2026-08-29 (JST)

## 2026-08-29 public repository cleanup baseline

- cleanup predecessor: `19982b517e83b40845476d7a9bba49af336e31c4`
- cleanup後のtracked file数: 655
- public Gitから、generated 179件、private one-time evidence 16件、duplicate 5件の合計200件を削除した。
- 削除前200件は、Canonical WORKを変更せず、task-local backupへ元の相対pathとSHA-256を保持して退避した。
- Markdown原文を保持する承認済みgenerated duplicate PDF 13件を削除し、同じexact pathを`.gitignore`へ追加した。
- current program source、Specifications 5件、public tests、public/synthetic fixtures、およびcurrent tests/docsが参照するpublished output familyは保持した。
- `XBRL-GL-PWD-2016-12-01/`はcurrent code/documentationから参照されるexternal historical sourceであるため保持した。exact path `XBRL GL 2017/`は存在しない。
- `specs/ads/source/ADS_Definition_Tables.xlsx`はcurrent mapping sourceとして保持するが、redistribution licence evidenceは`HOLD_LICENCE`である。
- cleanup commitは本文書を含むため自己参照SHAを固定せず、`git rev-parse HEAD`で確認する。

## 2026-08-26 CII D16B formal baseline

- CEN/TS 16931-3-3:2020 Table 2を正本として237/237行を正式レビューし、corrected candidateの13件を確認した。
- Table 3の逆変換制約を適用した結果、inverse ambiguityは0件である。
- CII Bindingは237行、24列、SHA-256 `B529F2585CA2A5FBFDAF673A6F96B98135CE274B8B022C1B791FF9863C23BD23`である。
- generic runtime `src/syntax_binding.py`のSHA-256は`7CA92B9DB1724D1A5A3AE9C0FDD9A081ED73F34D1125A8626C880BE2AE5B11A9`である。
- 配置後の代表値380はCII順逆各109値、XML Schema error 0、semantic diff 0、限定unit test 7/7 PASSである。
- 同一bytes・依存・fixtureで既にPASSした9コード、runtime 11件、reference 11件、identifier 9件、cross-route 79件はaccepted evidenceを再利用した。

## Git baseline

- branch: `main`
- upstream: `origin/main`
- code baseline commit: `c504f88dab62a6e6e1248f1fbfa4eaaf169f81ac`
- subject: `Publish reorganized Phase documentation`
- 記録時点のahead/behind: `0/0`
- 本文書を追加するdocumentation commitは自己参照を避けるため固定値として記録しない。最新値は`git rev-parse HEAD`で確認する。

## 正式入力

|相対パス|用途|GIT baseline SHA-256|
|---|---|---|
|`specs/bindings/syntax/EN16931_UBL_Invoice_Syntax_Binding.csv`|UBL Invoice syntax binding|`1C9F629FAE4A36250781EA39418F9817D33436C4FBF9D6E79F30B9ED6A925121`|
|`specs/bindings/syntax/EN16931_CII_D16B_Invoice_Syntax_Binding.csv`|CEN/TS-reviewed CII D16B syntax binding (237 rows)|`B529F2585CA2A5FBFDAF673A6F96B98135CE274B8B022C1B791FF9863C23BD23`|
|`README.md`|実行経路・文書案内|`6BC4EBBC95515D61E9EEB4CA3B7924B2B3070E34EDD32BAB78D4002F94EA8CA2`|

正式入力は公開sample、外部化されたBinding Table、対応仕様で構成する。実会計データと`README_PRIVATE.md`指定対象は含めない。

## 正式成果物と主要実装

正式仕様文書:

|相対パス|用途|GIT baseline SHA-256|
|---|---|---|
|`Specifications/UADC_Transformation_Table_Specification.docx`|Transformation-table contract including the full CII Binding|`08720791DA31D707478624F01852757B0FC2B01DA89422291E131A92F1FE6217`|
|`Specifications/UADC_Syntax_Binding_Program_Specification.docx`|Generic bidirectional Syntax Binding runtime contract|`DEDCFCC13C33873FA932C452058C3C7DF248EF1B2E589E7B029932CC2E6AD8CB`|

|相対パス|用途|GIT baseline SHA-256|
|---|---|---|
|`src/syntax_binding.py`|Generic bidirectional UBL/CII syntax binding runtime|`7CA92B9DB1724D1A5A3AE9C0FDD9A081ED73F34D1125A8626C880BE2AE5B11A9`|
|`src/semantic_binding.py`|Phase 2 semantic binding|`1C1CDF42D2EE0E93283BA9D6967876990D9186D35F1B28F0B32AE875D5779C7E`|
|`src/syntax_binding_ads_xbrl_gl.py`|ADS XBRL GL syntax binding|`F0BCE98024C4883B4A2A29334B6E86EA630A117673C6C509DDB4BF6129D778AC`|
|`out/phase1/openpeppol_ubl_invoice_minimal_binding_only.csv`|Phase 1 structured output sample|`89F355C8E91EFDEBC0E33711A73F8158141D534D508F6C61FB07C902F8471070`|
|`tests/test_roundtrip_artifacts.py`|round-trip artifact validation|`592FC0320D6917D7E55E3BDD1965738EEA706A7D47B988A430FD0AEE7D2AF173`|

成果物の主な配置:

- `out/phase1/`: Phase 1生成例
- `out/taxonomy/`: local生成taxonomy
- `tests/roundtrip/`: review可能なround-trip fixture
- `docs/`: Phase別仕様・tutorial

## 検証状態とWORK差分

- baseline commitの追跡ファイル数: 702
- 記録作業では変換・round-tripテストを再実行していない。
- WORKとGITでBinding CSV及び代表Phase 1 outputは一致する。
- WORKのREADME、主要3実装、round-trip testはGIT baselineと異なる。WORKを新しい正本としてGITへ反映する判断は本作業の対象外であり、別途差分レビューが必要である。
