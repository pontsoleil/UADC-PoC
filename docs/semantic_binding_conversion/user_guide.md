# User Guide: Semantic Binding Structured-CSV-to-Flat-File Conversion

## 1. Working Directory

Run commands from the **UADC_PoC** directory:

```
cd UADC_PoC
```

Set the Python command for Windows PowerShell:

```
$python = 'python'
```

For macOS or Linux shell:

```
PYTHON=python3
```

## 2. Main Script

Use:

```
src/semantic_binding.py
```

The script converts Phase 1 Structured CSV into Phase 2 target PSV or CSV files using a semantic binding CSV.

## 3. Generate ADS Invoices Received PSV

Run:

```
& $python .\src\semantic_binding.py `
  .\out\phase1\openpeppol_ubl_invoice_minimal.csv `
  -b .\specs\bindings\semantic\ADS_Invoices_Received_PSV_Binding.csv `
  -o .\out\phase2\ADS_PSV `
  --format psv
```

Output:

```
out/phase2/ADS_PSV/openpeppol_ubl_invoice_minimal/Invoices_Received.psv
```

## 4. Generate ADS Invoices Received Lines PSV

Run:

```
& $python .\src\semantic_binding.py `
  .\out\phase1\openpeppol_ubl_invoice_minimal.csv `
  -b .\specs\bindings\semantic\ADS_Invoices_Received_Lines_PSV_Binding.csv `
  -o .\out\phase2\ADS_PSV `
  --format psv
```

Output:

```
out/phase2/ADS_PSV/openpeppol_ubl_invoice_minimal/Invoices_Received_Lines.psv
```

This target has a repeated row scope. The binding table includes **type=C** for **$.invoice.invoiceLine** with repeated multiplicity, so the converter emits one row per **dInvoiceLine** occurrence.

## 5. Convert All Phase 1 Structured CSV Files

Run:

```
& $python .\src\semantic_binding.py `
  .\out\phase1 `
  -b .\specs\bindings\semantic\ADS_Invoices_Received_PSV_Binding.csv `
  -o .\out\phase2\ADS_PSV `
  --format psv
```

Each input CSV creates one output directory named by the input Structured CSV stem.

Example:

```
out/phase2/ADS_PSV/Allowance-example/Invoices_Received.psv
```

## 6. Generate CSV Instead Of PSV

Use **--format csv**:

```
& $python .\src\semantic_binding.py `
  .\out\phase1\openpeppol_ubl_invoice_minimal.csv `
  -b .\specs\bindings\semantic\ADS_Invoices_Received_PSV_Binding.csv `
  -o .\out\phase2\ADS_CSV `
  --format csv
```

Output:

```
out/phase2/ADS_CSV/openpeppol_ubl_invoice_minimal/Invoices_Received.csv
```

## 7. Command Options

Basic form:

```
& $python .\src\semantic_binding.py INPUT `
  -b BINDING_CSV `
  -o OUTPUT_DIR `
  --format psv
```

Options:

- **INPUT**: one Structured CSV file or a directory containing Structured CSV files.
- **-b**, **--binding-csv**: semantic binding CSV.
- **-o**, **--output-dir**: output directory.
- **--format**: output preset, either **psv** or **csv**.
- **--delimiter**: explicit delimiter. This overrides **--format**.
- **--extension**: explicit output extension. This overrides **--format**.
- **--output-filename**: explicit output filename for single-file input.

## 8. Binding Table Review Points

For target fields:

- Use **type=A**.
- Put the emitted target column name in **field_name**.
- Put the UADC source in **semantic_path**.
- Keep **field_no** in the target output order.

For row-scope classes:

- Use **type=C**.
- Put the semantic class path in **semantic_path**.
- Put the Structured CSV model description in **description**.
- Put the class multiplicity in **multiplicity**.

For horizontally repeated values:

- Use zero-based indexed paths such as **$.invoice.vatBreakdown[0].vatCategoryCode**.
- Include the repeated class as a **type=C** row in the same binding table.

## 9. Troubleshooting

If an output column is blank, check that the **semantic_path** final segment matches the Structured CSV source column after UpperCamelCase conversion.

If a line-level file has only one row, check that the binding table includes a repeated **type=C** row for **$.invoice.invoiceLine** with multiplicity **1..*** or **0..***.

If a target filename is unexpected, check the binding CSV filename. The converter derives the target view from names such as **ADS_Invoices_Received_PSV_Binding.csv**.
