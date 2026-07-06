# EN 16931 LHM Source CSV

`EN16931_CIUS_Invoice_LHM_Source.csv` is the editable source file for generating
`../EN16931_CIUS_Invoice_LHM.csv`.

Use this file for individual adjustments to PDF-derived EN 16931-1 Table 2
items. The `.xlsx` workbook remains a review artifact and is not updated by
Codex.

Generation flow:

```powershell
python UADC_PoC/tools/build_lhm_from_source.py build `
  UADC_PoC/specs/lhm/source/EN16931_CIUS_Invoice_LHM_Source.csv `
  UADC_PoC/specs/lhm/EN16931_CIUS_Invoice_LHM.csv
```

The override columns are optional:

- `semantic_path_override`
- `class_term_override`
- `element_override`

When `element_override` is blank, the generator creates a unique UpperCamelCase
element name from the semantic path. If final path segments duplicate, it uses
the shortest unique semantic path suffix.
