# UADC PoC Collaboration Workspace

This workspace is for the xBRL-GL Next / UADC proof of concept.

The first PoC checkpoint is the EN 16931-1 invoice semantic model represented
as an LHM/HMD-style CSV, plus a binding-driven conversion from UBL Invoice XML
to structured CSV.

OpenPeppol BIS Billing is handled as the next layer: a CIUS/profile overlay on
top of EN 16931-1, with additional constraints, defaults, and syntax-specific
rules.

## Flow

```text
UBL Invoice XML
  -> EN 16931 syntax binding
  -> EN 16931 LHM/HMD structured CSV
  -> semantic binding
  -> flat CSV / xBRL-CSV taxonomy

OpenPeppol BIS CIUS
  -> profile constraints and extensions
  -> OpenPeppol-specific binding checks
```

## Directory Layout

- `docs/` - collaboration notes and decisions.
- `references/` - external source notes and links.
- `specs/lhm/` - LHM/HMD semantic model definitions.
- `specs/bindings/` - syntax and semantic binding definitions.
- `samples/input/` - sample input XML or CSV.
- `samples/expected/` - checked expected output.
- `src/` - PoC scripts copied or adapted from `../GIT`.
- `tests/` - regression checks.
- `out/` - generated local output, ignored by Git.

The taxonomy generator is included at `tools/taxonomy/xBRLGL_TaxonomyGenerator.py`; no external `XBRL-GL-2026` checkout is required for normal tests.

## Current Scope

1. Define and audit the Invoice LHM from EN 16931-1.
2. Confirm syntax-binding conversion from UBL Invoice XML to EN 16931
   structured CSV.
3. Layer OpenPeppol BIS Billing as CIUS/profile constraints and extensions.
3. Generate structured CSV and xBRL-CSV taxonomy candidates.

## Current Test

```powershell
& 'C:\Users\nobuy\AppData\Local\Programs\Python\Python310\python.exe' tests\test_openpeppol_invoice_conversion.py
```

This converts `samples/input/openpeppol_ubl_invoice_minimal.xml` using
`specs/bindings/syntax/EN16931_UBL_Invoice_Syntax_Binding.csv` and checks key
EN 16931 LHM values. The sample is UBL Invoice XML; OpenPeppol CIUS checks are
added after the EN 16931 conversion baseline is stable.

Semantic path elements are generated from Business Terms using
`lowerCamelCaseConcatenated`, for example:

```text
Invoice issue date -> invoiceIssueDate
Seller postal address -> sellerPostalAddress
```
