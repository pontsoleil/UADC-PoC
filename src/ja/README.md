[English](../README.md) | **日本語**

# src

## 目的

この directory は UADC の規定変換 program と通常実行に必須の library を保持します。

## Program

- `syntax_binding.py` — XML ⇄ Structured CSV Syntax Binding.
- `tuple_binding.py` — Tuple XBRL ⇄ Structured CSV syntax conversion.
- `semantic_binding.py` — Structured CSV ⇄ Structured CSV Semantic Binding.
- `selector_multiplicity.py` — 現行 binding 処理で使用する selector-effective multiplicity support.
- `csv_excel_bridge.py` — 管理された CSV/Excel review interchange.
- `syntax_binding_ads_xbrl_gl.py` — ADS/XBRL GL 固有の現行 syntax conversion support.
- `tutorial/` — 現行 tutorial program.

現行 Formal GIT には standalone `oim_metadata.py` は存在しません。OIM
metadata 処理は既存 runtime 実装内に残っています。

Flat CSV runtime は現在 Formal GIT `src/` に登録されていません。検証済み
WORK 実装は `Specifications/UADC_Flat_CSV_Program_Specification.docx` と現行の
transformation route status report に記録されています。

## 責任境界

`src/**` は規定 program と通常実行に必須の library を保持します。`tools/**` は任意の評価・tutorial・validation・同期用 tool、`tests/**` は検証 program です。`src/**` から `tools/**` を import してはいけません。

## 実行と安全

command は repository root から実行します。実行前に input path、output path、上書き動作を確認し、実験では task-local 又は明示承認された output location を使用します。

## Test

materially changed な code 又は条件に関係する test だけを実行します。入力、code、設定、依存 version、成果物、validation scope が materially 同一なら accepted PASS 証跡を再利用します。
