# Source Scripts

`src/` contains only the operational conversion scripts and beginner tutorial
wrappers.

Top-level `src/` is intentionally small:

```text
ads_invoices_received_xbrl_gl.py
syntax_binding_hierarchical.py
tutorial/
```

Development helpers, legacy experiments, LHM maintenance scripts, taxonomy
generation scripts, and test artifact builders are kept under `tools/`.

Run commands from the UADC PoC root:

Windows PowerShell:

```powershell
cd <local-clone-directory>\UADC-PoC
$python = 'python'
```

`$python` is a PowerShell variable used to shorten the examples. Change it to
the full path of your Python executable if `python` is not available on `PATH`.

macOS / Linux shell:

```sh
cd <local-clone-directory>/UADC-PoC
PYTHON=python3
```

For macOS/Linux, replace PowerShell examples such as `& $python script.py` with
`$PYTHON script.py`, and use `/` path separators.

## Operational Scripts

### `syntax_binding_hierarchical.py`

Primary Phase 1 converter.

Position:
Main operational script for UBL Invoice XML to hierarchical Structured CSV,
xBRL-CSV metadata JSON, and Structured-CSV-to-UBL-XML round trip conversion.

Inputs:
UBL Invoice XML or hierarchical Structured CSV when `--reverse` is used; syntax
binding CSV; LHM CSV; optional metadata path, template CSV, and taxonomy base.

Outputs:
Hierarchical Structured CSV plus xBRL-CSV metadata JSON in forward mode; UBL
Invoice XML in reverse mode.

Forward conversion example:

```powershell
& $python .\src\syntax_binding_hierarchical.py `
  .\samples\input\openpeppol_ubl_invoice_minimal.xml `
  -b .\specs\bindings\syntax\EN16931_UBL_Invoice_Syntax_Binding.csv `
  --lhm-csv .\specs\lhm\EN16931_CIUS_Invoice_LHM.csv `
  --metadata-output .\out\phase1\EN16931_Core_Invoice.json `
  --taxonomy-base .\out\taxonomy `
  -o .\out\phase1\EN16931_Core_Invoice.csv
```

Reverse conversion example:

```powershell
& $python .\src\syntax_binding_hierarchical.py `
  .\out\phase1\EN16931_Core_Invoice.csv `
  --reverse `
  -b .\specs\bindings\syntax\EN16931_UBL_Invoice_Syntax_Binding.csv `
  --lhm-csv .\specs\lhm\EN16931_CIUS_Invoice_LHM.csv `
  -o .\out\roundtrip\openpeppol_ubl_invoice_minimal.xml
```

### `ads_invoices_received_xbrl_gl.py`

Generates XBRL GL tuple instances for ADS target views.

Position:
Operational downstream generator that consumes Structured CSV produced by
`syntax_binding_hierarchical.py`. The script name remains historical; the same
implementation now generates all current ADS XBRL GL Figure 1 targets.

Inputs:
Structured CSV file or directory, ADS syntax binding CSV, LHM CSV, schema href,
currency minor-unit CSV, and optional fallback monetary decimal setting.

Outputs:
One `*.xbrl` XBRL GL tuple instance per target view.

Example:

```powershell
& $python .\src\ads_invoices_received_xbrl_gl.py `
  .\out\phase1\EN16931_Core_Invoice.csv `
  -b .\specs\bindings\syntax\ADS_Invoices_Received_XBRL_GL_Binding.csv `
  --lhm-csv .\specs\lhm\EN16931_CIUS_Invoice_LHM.csv `
  --currency-csv .\specs\Currency.csv `
  -o .\out\phase2\ADS_XBRL_GL `
  --output-filename Invoices_Received.xbrl
```

Phase 2 Invoices Generated example:

```powershell
& $python .\src\ads_invoices_received_xbrl_gl.py `
  .\out\phase1\EN16931_Core_Invoice.csv `
  -b .\specs\bindings\syntax\ADS_Invoices_Generated_XBRL_GL_Binding.csv `
  --lhm-csv .\specs\lhm\EN16931_CIUS_Invoice_LHM.csv `
  --currency-csv .\specs\Currency.csv `
  -o .\out\phase2\ADS_XBRL_GL `
  --output-filename Invoices_Generated.xbrl
```

Phase 2 Invoices Received Lines example:

```powershell
& $python .\src\ads_invoices_received_xbrl_gl.py `
  .\out\phase1\EN16931_Core_Invoice.csv `
  -b .\specs\bindings\syntax\ADS_Invoices_Received_Lines_XBRL_GL_Binding.csv `
  --lhm-csv .\specs\lhm\EN16931_CIUS_Invoice_LHM.csv `
  --currency-csv .\specs\Currency.csv `
  -o .\out\phase2\ADS_XBRL_GL `
  --output-filename Invoices_Received_Lines.xbrl
```

Phase 2 Invoices Generated Lines example:

```powershell
& $python .\src\ads_invoices_received_xbrl_gl.py `
  .\out\phase1\EN16931_Core_Invoice.csv `
  -b .\specs\bindings\syntax\ADS_Invoices_Generated_Lines_XBRL_GL_Binding.csv `
  --lhm-csv .\specs\lhm\EN16931_CIUS_Invoice_LHM.csv `
  --currency-csv .\specs\Currency.csv `
  -o .\out\phase2\ADS_XBRL_GL `
  --output-filename Invoices_Generated_Lines.xbrl
```

Phase 2 Supplier Listing example. This maps invoice Seller data to the ADS
Supplier Listing target:

```powershell
& $python .\src\ads_invoices_received_xbrl_gl.py `
  .\out\phase1\EN16931_Core_Invoice.csv `
  -b .\specs\bindings\syntax\ADS_Supplier_Listing_XBRL_GL_Binding.csv `
  --lhm-csv .\specs\lhm\EN16931_CIUS_Invoice_LHM.csv `
  --currency-csv .\specs\Currency.csv `
  -o .\out\phase2\ADS_XBRL_GL `
  --output-filename Supplier_Listing.xbrl
```

Phase 2 Customer Master example. This maps invoice Buyer data to the ADS
Customer Master target:

```powershell
& $python .\src\ads_invoices_received_xbrl_gl.py `
  .\out\phase1\EN16931_Core_Invoice.csv `
  -b .\specs\bindings\syntax\ADS_Customer_Master_XBRL_GL_Binding.csv `
  --lhm-csv .\specs\lhm\EN16931_CIUS_Invoice_LHM.csv `
  --currency-csv .\specs\Currency.csv `
  -o .\out\phase2\ADS_XBRL_GL `
  --output-filename Customer_Master.xbrl
```

## Tutorial Scripts

Beginner-friendly wrappers are under:

```text
src/tutorial/
```

Recommended first run:

```powershell
& $python .\src\tutorial\00_check_environment.py
& $python .\src\tutorial\01_convert_sample_to_structured_csv.py
& $python .\src\tutorial\02_roundtrip_structured_csv_to_xml.py
& $python .\src\tutorial\03_generate_ads_xbrl_gl.py
```

Tutorial output is written under `out/tutorial/`.

## Validation

Compile the operational and tutorial scripts:

```powershell
& $python -m py_compile `
  .\src\ads_invoices_received_xbrl_gl.py `
  .\src\syntax_binding_hierarchical.py `
  .\src\tutorial\00_check_environment.py `
  .\src\tutorial\01_convert_sample_to_structured_csv.py `
  .\src\tutorial\02_roundtrip_structured_csv_to_xml.py `
  .\src\tutorial\03_generate_ads_xbrl_gl.py
```

Run focused operational checks:

```powershell
& $python .\tests\test_syntax_binding_hierarchical.py
& $python .\tests\test_syntax_binding_reverse.py
& $python .\tests\test_roundtrip_artifacts.py
```

## Directory Boundary

- Use top-level `src/` for operational conversion scripts.
- Use `src/tutorial/` for beginner wrappers that call operational scripts.
- Use `tools/` for setup, maintenance, legacy/simple converters, taxonomy
  generation, and test artifact building.
- Use `out/` for generated local output.
