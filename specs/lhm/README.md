# LHM Specifications

This directory contains the EN 16931 invoice LHM used by the Phase 1 PoC.

## Files and Subdirectories

- `EN16931_CIUS_Invoice_LHM.csv` - Current generated LHM CSV consumed by
  structured CSV conversion and taxonomy generation.
- `source/` - Editable source CSV used to regenerate or adjust the LHM.
- `EN16931_CIUS_Invoice.xlsx` - Local reviewer workbook. It is ignored by Git
  and should not be updated by automation.

The LHM defines semantic paths, class/element names, multiplicity, effective
`lhm_level`, UBL XPath bindings, and other fields needed for structured CSV and
xBRL-CSV taxonomy generation.
