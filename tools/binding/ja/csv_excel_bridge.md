[English](../csv_excel_bridge.md) | **日本語**

# csv_excel_bridge

## 目的

`src/csv_excel_bridge.py` は canonical CSV の意味を変更せず、管理された CSV ⇄ Excel 変換と比較を提供します。

## CLI 例

```text
py src/csv_excel_bridge.py csv-to-xlsx <input.csv> -o <output.xlsx>
py src/csv_excel_bridge.py xlsx-to-csv <input.xlsx> -o <output.csv> --baseline <baseline.csv>
```

## 実行と安全

command は repository root から実行します。実行前に input path、output path、上書き動作を確認し、実験では task-local 又は明示承認された output location を使用します。

## Test

materially changed な code 又は条件に関係する test だけを実行します。入力、code、設定、依存 version、成果物、validation scope が materially 同一なら accepted PASS 証跡を再利用します。
