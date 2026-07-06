# User Guide: LHM Generation

## 1. Working Directory

Run commands from the `UADC_PoC` directory:

```powershell
cd UADC_PoC
```

All paths below are relative to this directory.

Set the Python command for the local Windows environment:

```powershell
$python = 'C:\Users\nobuy\AppData\Local\Programs\Python\Python310\python.exe'
```

## 2. Edit the LHM Source

Edit:

```text
specs/lhm/source/EN16931_CIUS_Invoice_LHM_Source.csv
```

Commonly edited columns:

- `description`
- `path`
- `xpath`
- `semantic_path_override`
- `class_term_override`
- `element_override`
- `label_local`
- `definition_local`
- `adjustment_note`

Leave override columns blank when generated values are acceptable.

Use only these multiplicity values in the generated LHM:

```text
0..1
0..*
1..1
1..*
```

If source material uses `0..n` or `1..n`, the LHM generator normalizes those values to `0..*` or `1..*`.

The generated LHM has both `level` and `lhm_level`:

- `level` preserves the EN 16931/LHM logical hierarchy.
- `lhm_level` is the effective hierarchy for Structured CSV and xBRL-CSV taxonomy generation.
- `0..1` and `1..1` BG rows normally have blank `lhm_level` and are not emitted as dimensions.
- BT rows under those BGs use the nearest ancestor BG with an `lhm_level` plus `1`.
- Repeating BG rows, `0..*` and `1..*`, receive their own `lhm_level` and become dimensions.

## 3. Generate the LHM CSV

Run:

```powershell
& $python .\tools\build_lhm_from_source.py build `
  .\specs\lhm\source\EN16931_CIUS_Invoice_LHM_Source.csv `
  .\specs\lhm\EN16931_CIUS_Invoice_LHM.csv
```

Expected output:

```text
Wrote generated LHM CSV: specs\lhm\EN16931_CIUS_Invoice_LHM.csv
```

## 4. Optional: Initialize the Source CSV

Use this only when a new editable source CSV must be created from an existing LHM CSV:

```powershell
& $python .\tools\build_lhm_from_source.py init-source `
  .\specs\lhm\EN16931_CIUS_Invoice_LHM.csv `
  .\specs\lhm\source\EN16931_CIUS_Invoice_LHM_Source.csv
```

This command rewrites the source CSV. Use it carefully.

## 5. Optional: Normalize Class and Element Values

Prefer rebuilding from the source CSV. If the generated LHM CSV has been edited directly, normalize it with:

```powershell
& $python .\tools\normalize_lhm_class_element.py `
  .\specs\lhm\EN16931_CIUS_Invoice_LHM.csv
```

## 6. Optional: Populate UBL Syntax Sequence

Download and extract the official OASIS UBL 2.1 package into a local, non-versioned directory such as:

```text
out/cache/UBL-2.1
```

Then populate `syntax_sequence` values from the UBL Invoice schema:

```powershell
& $python .\tools\update_lhm_syntax_sequence_from_ubl_xsd.py `
  .\specs\lhm\EN16931_CIUS_Invoice_LHM.csv `
  --schema-root .\out\cache\UBL-2.1\xsd `
  -o .\out\cache\EN16931_CIUS_Invoice_LHM.syntax_sequence_check.csv
```

Use the generated file to review XML schema order. The EN 16931 `sequence` column remains the semantic Table 2 order; `syntax_sequence` is the UBL XML order used for XML-oriented checks and reverse output ordering.

## 7. Optional: Update Definitions from PDF

If the EN 16931-1 PDF is available and `pdfplumber` is installed:

```powershell
& $python .\tools\update_lhm_definitions_from_pdf.py `
  "<path-to-EN16931-1-pdf>" `
  .\specs\lhm\EN16931_CIUS_Invoice_LHM.csv `
  --first-page 43 `
  --last-page 75
```

This updates only the CSV file passed on the command line.

## 8. Check the LHM

Run semantic path checks:

```powershell
& $python .\tests\test_lhm_semantic_paths.py
```

Run class and element checks:

```powershell
& $python .\tools\check_lhm_class_element.py `
  .\specs\lhm\EN16931_CIUS_Invoice_LHM.csv
```

Run hierarchical CSV layout checks:

```powershell
& $python .\tests\test_lhm_hierarchical_csv_layout.py
```

## 9. Troubleshooting

### Duplicate element names

Regenerate the LHM from the source CSV. Element names are generated from `semantic_path` by using the shortest unique suffix. If a duplicate remains intentional, set `element_override` in the source CSV.

### Wrong class term

Check the source CSV `path` column. BT rows use the nearest parent BG found in the path.

### Wrong semantic path

Set `semantic_path_override` in the source CSV and rebuild the LHM.

### Missing PDF descriptions

Check the PDF page range. Some rows may need manual `description` values in the source CSV because PDF table extraction can split cells.
