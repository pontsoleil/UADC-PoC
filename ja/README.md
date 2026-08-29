[English](../README.md) | **日本語**

# UADC-PoC

## 目的

UADC (Universal Adapter for Data Conversion) は、HMD に対応した Structured CSV を syntax・semantic・flat-file 変換の共通データ層として使用します。

## 現行 repository の責任範囲

```text
src/            既存の flat layout にある現行の規定／runtime program
src/tutorial/   現行 tutorial program
tools/          任意の評価・build・validation・migration・tutorial utility
tests/          現行の検証 program と fixture
bindings/       Syntax Binding Table と Semantic Binding Table
models/         semantic/model input
definitions/    canonical definition と taxonomy generation input
instances/      original/derived/roundtrip instance artefact
Specifications/ 規定文書および program specification DOCX
taxonomy/       taxonomy artefact
docs/           公開 project 文書および validation 文書
```

現行 Formal GIT 実装は flat な `src/*.py` program layout を使用します。
以前提案された `src/syntax/`、`src/semantic/`、`src/common/`、
`src/flat_csv/` の Python package layout は実装されていません。

repository root の README は root に保持します。`src/README.md` は runtime tree の追加説明であり、root README を置き換えません。

## 実行と安全

command は repository root から実行します。実行前に input path、output path、上書き動作を確認し、実験では task-local 又は明示承認された output location を使用します。

## Test

materially changed な code 又は条件に関係する test だけを実行します。入力、code、設定、依存 version、成果物、validation scope が materially 同一なら accepted PASS 証跡を再利用します。
