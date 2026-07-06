# Round-Trip Test Guide

## Purpose

This guide explains the round-trip test artifacts for UBL Invoice syntax binding conversion.

The round-trip flow is:

```text
source XML -> structured CSV -> regenerated XML
```

In this PoC, "structured CSV" means the dimension-based hierarchical CSV produced by:

```text
src/syntax_binding_hierarchical.py
```

## Directory Layout

The test artifacts are under:

```text
tests/roundtrip/
```

Each dataset has the same three subdirectories:

```text
tests/roundtrip/<dataset>/
  source_xml/
  structured_csv/
  metadata_json/
  roundtrip_xml/
```

Meaning:

- `source_xml/`: original UBL Invoice XML used as the conversion input.
- `structured_csv/`: hierarchical structured CSV generated from the source XML.
- `metadata_json/`: xBRL-CSV JSON metadata relating the structured CSV columns to the generated taxonomy.
- `roundtrip_xml/`: XML regenerated from the structured CSV.

Current datasets:

```text
tests/roundtrip/openpeppol-minimal/
tests/roundtrip/bis-billing3-examples/
```

`openpeppol-minimal` contains the PoC minimal invoice sample.

`bis-billing3-examples` contains the Invoice XML examples copied from:

```text
samples/input/bis-billing3-examples/
```

CreditNote samples are not included in this Invoice round-trip test.

## Rebuild Artifacts

Run from the `UADC_PoC` directory:

```powershell
$python = 'C:\Users\nobuy\AppData\Local\Programs\Python\Python310\python.exe'
& $python .\tests\build_roundtrip_test_artifacts.py
```

The script refreshes all four artifact directories for each dataset.
The syntax binding converter creates one metadata JSON file for each structured CSV during forward conversion.

Expected result:

```text
openpeppol-minimal: built 1 round-trip case(s)
bis-billing3-examples: built 9 round-trip case(s)
ok: built 10 round-trip artifact(s) under ...\tests\roundtrip
```

## Run Verification

Run:

```powershell
& $python .\tests\test_roundtrip_artifacts.py
```

This test rebuilds the artifacts and checks all generated cases.

Expected result:

```text
ok: checked 10 round-trip artifact case(s)
```

## Verification Points

The test checks:

- every source XML has a corresponding structured CSV;
- every structured CSV has a corresponding JSON metadata file;
- every structured CSV has a corresponding round-trip XML;
- `InvoiceNumber` is extracted into the structured CSV;
- `DocumentCurrencyCode` is extracted into the structured CSV;
- `InvoiceLineIdentifier` values are extracted into the structured CSV;
- the round-trip XML root-level `cbc:ID` matches the CSV `InvoiceNumber`;
- a representative amount in the round-trip XML has `currencyID` equal to `DocumentCurrencyCode`.
- the JSON metadata contains taxonomy entry point references;
- the JSON metadata maps CSV dimensions such as `dInvoice` to `plt:d_en16931_*` taxonomy concepts;
- the JSON metadata maps CSV fact columns such as `InvoiceNumber` to `en16931:*` taxonomy concepts.
- generated metadata can be loaded and validated by Arelle with `loadFromOIM`;
- regenerated round-trip XML is valid against the local UBL 2.1 Invoice schema.

## Metadata JSON

The metadata JSON is written beside the generated structured CSV unless `--metadata-output` is specified. In these round-trip tests it is written to:

```text
tests/roundtrip/<dataset>/metadata_json/<case>.metadata.json
```

Important sections:

- `documentInfo`: xBRL-CSV document type, namespaces, and taxonomy schema references.
- `tables`: the structured CSV URL.
- `tableTemplates`: table-level dimensions and fact concept mappings.

Example column mapping:

```json
{
  "InvoiceNumber": {
    "dimensions": {
      "concept": "en16931:InvoiceNumber"
    }
  }
}
```

Run Arelle metadata validation:

```powershell
& $python .\tests\test_xbrl_csv_metadata_arelle.py
```

Run UBL 2.1 schema validation for regenerated XML:

```powershell
& $python .\tests\test_roundtrip_xml_ubl_schema.py
```

For the BIS Billing 3 examples, the separate test:

```powershell
& $python .\tests\test_bis_billing3_examples_conversion.py
```

also checks:

- all 9 Invoice XML examples can be converted;
- VAT category values are extracted;
- `Allowance-example.xml` carries `TaxAccountingCurrencyCode=SEK`;
- `Allowance-example.xml` extracts `InvoiceTotalVatAmountInAccountingCurrency=9324.00`.

## Manual Review Points

When manually comparing `source_xml/` and `roundtrip_xml/`, note the following.

The regenerated XML is not intended to be byte-for-byte identical. It is reconstructed from bound CSV values.

Expected differences may include:

- XML declaration formatting;
- namespace prefix placement;
- indentation;
- XML elements that are not represented in the syntax binding.

The reverse converter adds UBL-required support elements that are not EN 16931 BT values when needed for schema validation, including `cac:TaxScheme/cbc:ID` and a default `cbc:ChargeIndicator=false` for price allowance contexts.

Important points to inspect:

- `cbc:ID`, `cbc:IssueDate`, `cbc:InvoiceTypeCode`, and `cbc:DocumentCurrencyCode`;
- `cac:AccountingSupplierParty` and `cac:AccountingCustomerParty`;
- document-level `cac:AllowanceCharge` with `cbc:ChargeIndicator=false` or `true`;
- line-level `cac:AllowanceCharge` with `cbc:ChargeIndicator=false` or `true`;
- `cac:TaxTotal` split by `cbc:TaxAmount/@currencyID`;
- amount elements with generated `currencyID` attributes;
- repeated invoice lines and VAT breakdown rows.

## Related Tests

Run these when changing syntax binding, LHM XPath, or currency handling:

```powershell
& $python .\tests\test_openpeppol_invoice_conversion.py
& $python .\tests\test_syntax_binding_reverse.py
& $python .\tests\test_bis_billing3_examples_conversion.py
& $python .\tests\test_roundtrip_artifacts.py
& $python .\tests\test_xbrl_csv_metadata_arelle.py
& $python .\tests\test_roundtrip_xml_ubl_schema.py
```
