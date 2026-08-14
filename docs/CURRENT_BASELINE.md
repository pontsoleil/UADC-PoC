# UADC_PoC Current Baseline

記録日: 2026-08-14 (JST)

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
|`README.md`|実行経路・文書案内|`6BC4EBBC95515D61E9EEB4CA3B7924B2B3070E34EDD32BAB78D4002F94EA8CA2`|

正式入力は公開sample、外部化されたBinding Table、対応仕様で構成する。実会計データと`README_PRIVATE.md`指定対象は含めない。

## 正式成果物と主要実装

|相対パス|用途|GIT baseline SHA-256|
|---|---|---|
|`src/syntax_binding.py`|Phase 1 syntax binding|`0AF9521C2A0B6A5B418C544DED17A3E4B5CE976FE2846D92A6D75B31029C5CA3`|
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
