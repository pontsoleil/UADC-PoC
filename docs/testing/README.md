# Testing And Round-Trip Artifacts Guide

This guide explains test execution and round-trip review artifacts.

Run commands from the **UADC_PoC** directory. Test scripts are plain Python scripts and can be executed directly with **$python**. Some can also be run through **pytest** when pytest is installed.

## Supporting Files

- **tests/roundtrip/**: reviewable round-trip artifacts. Each case keeps source XML, Structured CSV, xBRL-CSV metadata JSON, and regenerated XML together.
- **tools/build_roundtrip_test_artifacts.py**: rebuilds round-trip artifact sets from sample XML inputs.

## Phase 1 Syntax Binding Tests

These tests verify UBL Invoice XML to Structured CSV, xBRL-CSV metadata, and UBL round-trip behavior.

```
& $python .\tests\test_openpeppol_invoice_conversion.py
& $python .\tests\test_lhm_hierarchical_csv_layout.py
& $python .\tests\test_syntax_binding.py
& $python .\tests\test_syntax_binding_reverse.py
& $python .\tests\test_ubl_schema_child_order.py
& $python .\tests\test_bis_billing3_examples_conversion.py
& $python .\tests\test_roundtrip_artifacts.py
```

The forward Phase 1 conversion uses XML parent context recursion, so nested repeated classes preserve parent dimension values such as **dInvoiceLine** with child dimensions such as **dItemAttributes**.

The reverse conversion can derive UBL child element order from XSD files by using **--ubl-schema-root** or **--ubl-schema-url**. **test_ubl_schema_child_order.py** checks this XSD-derived ordering logic without downloading the full UBL package.

**test_syntax_binding_reverse.py** also checks cross-scope absolute XPath handling: BT-90 must be written below the root **AccountingSupplierParty**, and **PaymentMeans/Invoice** must not exist. **test_bis_billing3_examples_conversion.py** checks the currency-filtered totals in **Allowance-example.xml**: BT-110 is **1225.00** and BT-111 is **9324.00**.

## Phase 2 ADS XBRL GL Tests

These tests regenerate Phase 1 Structured CSV first, then use ADS XBRL GL syntax binding CSV files under **specs/bindings/syntax/**.

```
& $python .\tests\test_ads_invoices_received_xbrl_gl.py
& $python .\tests\test_ads_invoices_generated_xbrl_gl.py
& $python .\tests\test_ads_invoices_received_lines_xbrl_gl.py
& $python .\tests\test_ads_invoices_generated_lines_xbrl_gl.py
& $python .\tests\test_ads_supplier_listing_xbrl_gl.py
& $python .\tests\test_ads_customer_master_xbrl_gl.py
```

Expected output:

```
out/phase2/ADS_XBRL_GL/<structured-csv-stem>/<target-view>.xbrl
```

Target view files:

```
Invoices_Received.xbrl
Invoices_Generated.xbrl
Invoices_Received_Lines.xbrl
Invoices_Generated_Lines.xbrl
Supplier_Listing.xbrl
Customer_Master.xbrl
```

## Phase 2 ADS PSV And CSV Tests

These tests use semantic binding files under **specs/bindings/semantic/**.

```
& $python .\tests\test_ads_invoices_received_psv.py
& $python .\tests\test_ads_invoices_generated_psv.py
& $python .\tests\test_semantic_binding_indexed_paths.py
& $python .\tests\test_semantic_binding_csv_format.py
& $python .\tests\test_phase2_outputs_by_structured_csv_stem.py
```

Expected output:

```
out/phase2/ADS_PSV/<structured-csv-stem>/<target-view>.psv
```

## Taxonomy And LHM Checks

```
& $python .\tests\test_lhm_semantic_paths.py
& $python .\tests\test_xbrlgl_generator_uadc_lhm.py
& $python .\tests\validate_taxonomy.py
```

## Round-Trip Artifacts

Round-trip flow:

```
source XML -> Structured CSV -> regenerated XML
```

Artifacts are under:

```
tests/roundtrip/<dataset>/
  source_xml/
  structured_csv/
  metadata_json/
  roundtrip_xml/
```

Current datasets:

```
tests/roundtrip/openpeppol-minimal/
tests/roundtrip/bis-billing3-examples/
```

Rebuild:

```
$python = 'python'
& $python .\tools\build_roundtrip_test_artifacts.py
```

Verify:

```
& $python .\tests\test_roundtrip_artifacts.py
```

The test checks source XML, Structured CSV, metadata JSON, and round-trip XML correspondence. It also checks representative values such as **InvoiceNumber**, **DocumentCurrencyCode**, **InvoiceLineIdentifier**, amount **currencyID**, taxonomy entry points, and xBRL-CSV column concept mappings.

## Optional Validation

Arelle metadata validation:

```
& $python .\tests\test_xbrl_csv_metadata_arelle.py
```

UBL 2.1 schema validation:

```
& $python .\tests\test_roundtrip_xml_ubl_schema.py
```

The regenerated XML is not expected to be byte-for-byte identical to the source XML. It is reconstructed from bound CSV values and may differ in XML declaration formatting, namespace placement, indentation, and unbound XML content.

## Current Test Execution Report

Last recorded report date:

```
2026-07-13
```

Recorded result:

```
PASS
```

Scope included EN 16931 LHM-driven syntax binding conversion, Structured CSV generation, xBRL-CSV metadata generation, Arelle validation, UBL reverse conversion, BIS Billing 3 example conversion, LHM checks, and local taxonomy generation checks.

The taxonomy/LHM checks, OpenPeppol conversion, all nine BIS Billing 3 conversions, Structured CSV metadata, ten round-trip artifact cases, and Arelle validation of all ten xBRL-CSV metadata files passed. Absolute currency-filtered XPath evaluation was corrected so **Allowance-example.xml** now writes BT-110 as **1225.00** and BT-111 as **9324.00**. Because this changed Structured CSV output, all Phase 2 ADS XBRL GL and ADS PSV/CSV outputs were regenerated and their tests passed.

The reverse converter keeps absolute binding XPaths rooted at the UBL document when a semantic child is stored outside its repeated syntax context. This prevents BT-90 from creating a nested **Invoice** below **PaymentMeans**. All ten regenerated round-trip XML files pass the UBL 2.1 Invoice schema validation when the test is run with an environment containing **xmlschema**.
