# User Guide: Syntax Binding XML-to-Hierarchical-CSV Conversion

## 1. Working Directory

Run commands from the `UADC_PoC` directory:

```powershell
cd UADC_PoC
```

All paths below are relative to this directory unless they begin with `../`.

Set the Python command for the local Windows environment:

```powershell
$python = 'C:\Users\nobuy\AppData\Local\Programs\Python\Python310\python.exe'
```

## 2. Main Script

Use:

```text
src/syntax_binding_hierarchical.py
```

This script converts XML to dimension-based hierarchical CSV using a syntax binding CSV.
It also supports reverse conversion from hierarchical CSV back to XML with `--reverse`.

## 3. Convert the PoC OpenPeppol Sample

Run:

```powershell
& $python .\src\syntax_binding_hierarchical.py `
  .\samples\input\openpeppol_ubl_invoice_minimal.xml `
  -b .\specs\bindings\syntax\EN16931_UBL_Invoice_Syntax_Binding.csv `
  --lhm-csv .\specs\lhm\EN16931_CIUS_Invoice_LHM.csv `
  -o .\out\hierarchical\en16931_lhm_hierarchical.csv
```

Output:

```text
out/hierarchical/en16931_lhm_hierarchical.csv
out/hierarchical/en16931_lhm_hierarchical.csv.metadata.json
```

This command uses the LHM CSV to determine the output dimensions and fact columns. It also creates JSON metadata that relates the CSV columns to the generated taxonomy.

The converter treats `lhm_level` as the effective hierarchy for Structured CSV. BG rows with blank `lhm_level`, such as non-repeating Seller or Buyer groups, are semantic grouping nodes only; their BT values are written in the nearest ancestor dimension row.

## 4. Convert the Revised Package Sample

Run:

```powershell
& $python .\src\syntax_binding_hierarchical.py `
  ..\syntax_binding_revised_package\invoice.xml `
  -b ..\syntax_binding_revised_package\bindings.csv `
  --template-csv ..\syntax_binding_revised_package\invoice.csv `
  -o .\out\hierarchical\package_invoice_hierarchical.csv
```

Output:

```text
out/hierarchical/package_invoice_hierarchical.csv
out/hierarchical/package_invoice_hierarchical.csv.metadata.json
```

This command uses the package template CSV to preserve the expected output column order.

## 5. Command Options

Basic form:

```powershell
& $python .\src\syntax_binding_hierarchical.py XML_FILE `
  -b BINDING_CSV `
  -o OUTPUT_CSV
```

Options:

- `--lhm-csv`: use an LHM CSV to define dimension columns and BT value columns.
- `--template-csv`: use a template CSV header to define output column order.
- `--metadata-output`: set the JSON metadata output path. Default is `OUTPUT_CSV.metadata.json`.
- `--taxonomy-base`: set the generated taxonomy directory referenced by JSON metadata. Default is `out/taxonomy`.
- `--reverse`: convert hierarchical CSV back to XML.
- `--drop-empty-columns`: remove output columns that have no values.
- `--d-invoice`: set the `dInvoice` value. Default is `1`.
- `-e`, `--encoding`: CSV encoding. Default is `utf-8-sig`.

## 6. Reverse Hierarchical CSV to XML

First create or confirm the hierarchical CSV:

```powershell
& $python .\src\syntax_binding_hierarchical.py `
  .\samples\input\openpeppol_ubl_invoice_minimal.xml `
  -b .\specs\bindings\syntax\EN16931_UBL_Invoice_Syntax_Binding.csv `
  --lhm-csv .\specs\lhm\EN16931_CIUS_Invoice_LHM.csv `
  -o .\out\hierarchical\en16931_lhm_hierarchical.csv
```

Then reverse it to XML:

```powershell
& $python .\src\syntax_binding_hierarchical.py `
  .\out\hierarchical\en16931_lhm_hierarchical.csv `
  --reverse `
  -b .\specs\bindings\syntax\EN16931_UBL_Invoice_Syntax_Binding.csv `
  --lhm-csv .\specs\lhm\EN16931_CIUS_Invoice_LHM.csv `
  -o .\out\reverse\en16931_reverse_invoice.xml
```

Output:

```text
out/reverse/en16931_reverse_invoice.xml
```

The reverse XML is generated from bound CSV values. It is intended for round-trip verification and may not reproduce unbound XML content. When the LHM has `syntax_sequence` values, reverse output uses them to follow UBL schema order.

Amount `currencyID` attributes are derived during reverse conversion:

- `DocumentCurrencyCode` is used for ordinary invoice amount elements.
- `TaxAccountingCurrencyCode` is used for the tax accounting currency TaxTotal branch.

## 7. Generate Test Artifacts with Metadata

Round-trip test artifacts are built under:

```text
tests/roundtrip/
```

Run:

```powershell
& $python .\tests\build_roundtrip_test_artifacts.py
```

The generated layout is:

```text
tests/roundtrip/<dataset>/
  source_xml/
  structured_csv/
  metadata_json/
  roundtrip_xml/
```

Meaning:

- `source_xml`: source UBL Invoice XML.
- `structured_csv`: hierarchical structured CSV.
- `metadata_json`: JSON metadata relating the CSV columns to the taxonomy.
- `roundtrip_xml`: XML regenerated from the structured CSV.

The script uses `--metadata-output` to place metadata JSON in `metadata_json/`.

## 8. Input Binding CSV

The binding CSV should contain:

```text
semantic_path,xpath
```

Example:

```text
$.invoice.invoiceNumber,/Invoice/cbc:ID
$.invoice.invoiceIssueDate,/Invoice/cbc:IssueDate
```

Compatible column aliases are also accepted:

```text
path
source_xpath
xml_path
```

## 9. Output CSV Layout

The hierarchical CSV uses:

- `dInvoice` for the invoice root;
- `d*` columns for repeated BG dimensions;
- fact columns for BT values.

When the LHM is used, dimension columns are placed first and BT columns follow.

Example output pattern:

```text
dInvoice,dVatBreakdown,dInvoiceLine,InvoiceNumber,InvoiceIssueDate,...
1,,,INV-2026-0001,2026-07-06,...
1,1,,,,...
1,,1,,,...
```

## 10. JSON Metadata Layout

The metadata file is an xBRL-CSV metadata document. It has these main sections:

- `documentInfo`: xBRL-CSV document type and taxonomy references.
- `tables`: the generated structured CSV table URL.
- `tableTemplates`: table-level dimensions and fact concept mappings.

Check that important columns are mapped as expected:

```text
tableTemplates.structured.dimensions["plt:d_en16931_Invoice"] -> "$dInvoice"
tableTemplates.structured.columns.InvoiceNumber.dimensions.concept -> "en16931:InvoiceNumber"
tableTemplates.structured.columns.DocumentCurrencyCode.dimensions.concept -> "en16931:DocumentCurrencyCode"
```

## 11. Run Regression Checks

Run the LHM-driven OpenPeppol sample conversion check:

```powershell
& $python .\tests\test_lhm_hierarchical_csv_layout.py
```

Run the revised package conversion check:

```powershell
& $python .\tests\test_syntax_binding_hierarchical.py
```

Run the OpenPeppol structured conversion check:

```powershell
& $python .\tests\test_openpeppol_invoice_conversion.py
```

Run the reverse conversion round-trip check:

```powershell
& $python .\tests\test_syntax_binding_reverse.py
```

Run the round-trip artifact and metadata check:

```powershell
& $python .\tests\test_roundtrip_artifacts.py
```

Validate the generated xBRL-CSV metadata with Arelle:

```powershell
& $python .\tests\test_xbrl_csv_metadata_arelle.py
```

Validate the regenerated round-trip XML against the UBL 2.1 Invoice schema:

```powershell
& $python .\tests\test_roundtrip_xml_ubl_schema.py
```

## 12. Troubleshooting

### No usable bindings found

Check that the binding CSV contains `semantic_path` and `xpath` values.

### Missing output columns

If `--drop-empty-columns` is used, columns with no generated values are removed. Run without this option when a stable full header is required.

### Metadata JSON cannot locate the taxonomy

The converter must write a non-empty `documentInfo.taxonomy` array. Generate the taxonomy first:

```powershell
& $python .\tests\test_xbrlgl_generator_uadc_lhm.py
```

Or pass `--taxonomy-base` with the directory containing `plt/plt-oim-*.xsd`. If this schema is missing, metadata generation fails instead of writing an empty taxonomy list.

### Repeating rows are missing

Check that:

- the BG row in the LHM has repeating multiplicity such as `0..*` or `1..*`;
- the BG row has an XPath that points to the repeated XML context;
- the syntax binding CSV contains bindings under that BG semantic path.

### Values are written to the invoice root row instead of a dimension row

Use `--lhm-csv` so the converter can resolve each BT semantic path to its nearest LHM dimension.

### Package sample line rows are empty

Template columns alone do not create rows. Invoice line rows require invoice line bindings.

### Reverse XML does not match the original file order

Reverse XML is reconstructed from binding rows and hierarchical CSV values. Populate LHM `syntax_sequence` from the UBL schema when XML element order must be checked. Unbound XML content still cannot be reproduced until it is represented by a binding or fixed-value rule.
