# Tools Directory

This directory contains helper tools used to maintain generated specifications
and taxonomy output.

## Top-Level Tools

- `build_lhm_from_source.py` - Builds the generated LHM CSV from the editable
  source CSV.
- `audit_en16931_coverage.py` - Checks EN 16931 coverage in the LHM.
- `check_lhm_class_element.py` - Audits class and element naming.
- `extend_en16931_lhm_coverage.py` - Helps extend LHM coverage.
- `normalize_lhm_class_element.py` - Normalizes class and element names.
- `order_lhm_by_en16931_table2.py` - Orders LHM rows by EN 16931 Table 2
  sequence.
- `update_lhm_definitions_from_pdf.py` - Updates LHM definitions from extracted
  source text.
- `update_lhm_syntax_sequence_from_ubl_xsd.py` - Helps align syntax sequence
  with UBL schema order.

## Subdirectories

- `taxonomy/` - Local UADC-compatible xBRL-CSV taxonomy generator and related
  schema templates.

Tools should be deterministic and should write generated artifacts under
ignored `out/` unless they update a committed source CSV by design.
