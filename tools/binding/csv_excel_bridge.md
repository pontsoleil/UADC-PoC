**English** | [日本語](ja/csv_excel_bridge.md)

# csv_excel_bridge

## Purpose

`src/csv_excel_bridge.py` provides controlled CSV ⇄ Excel interchange and comparison without changing the canonical CSV meaning.

## CLI examples

```text
py src/csv_excel_bridge.py csv-to-xlsx <input.csv> -o <output.xlsx>
py src/csv_excel_bridge.py xlsx-to-csv <input.xlsx> -o <output.csv> --baseline <baseline.csv>
```

## Execution and safety

Run commands from the repository root. Confirm input paths, output paths, and overwrite behavior before execution. Use task-local or explicitly approved output locations for experiments.

## Tests

Run only tests relevant to materially changed code or conditions. Reuse accepted PASS evidence when inputs, code, settings, dependency versions, outputs, and validation scope are materially identical.
