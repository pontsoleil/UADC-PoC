# XBRL GL Next Accounting Entries model unit

This WORK model unit groups the Accounting Entries HMD, PCA Flat CSV Binding, converter, synthetic 81-column fixture, expected Structured CSV pair, and OIM taxonomy closure.

## Contents

- `hmd/`: XBRL GL Next Accounting Entries Canonical HMD.
- `bindings/flat-csv/`: confirmed PCA Flat CSV Binding.
- `scripts/`: Flat CSV forward/reverse converter.
- `scripts/csv2tidy.py`: 16列Binding/HMDによるPCA 81列順変換の追加経路。従来の13列経路及び`flat_csv.py`は置換しない。匿名評価用定義、入力、独立テストと異なるSHAのtaxonomy閉包は `../../../data/private/anonymized/pca-csv2tidy-review-r1/` に内部限定で配置する。
- `taxonomy/`: OIM taxonomy closure; entry point `taxonomy/cor_accountingEntries/cor-all-oim-2026-12-31.xsd`.
- `fixtures/input/`: synthetic PCA data only; no private accounting data.
- `fixtures/expected/`: accepted Structured CSV and JSON metadata with the same basename and a relative taxonomy URI.
- `tests/`: path-sensitive relocation checks.

The XBRL GL Next HMD and taxonomy are collaborative-review WORK assets. Their inclusion in a formal/public distribution remains review-required pending an explicit provenance and licence release decision.

Run the focused check from the repository root:

```text
python -m unittest discover -s models/xbrl-gl-next/accounting-entries/tests -v
```
