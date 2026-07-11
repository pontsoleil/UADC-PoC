# Tests

Run commands from the `UADC_PoC` directory.

## Subdirectories and Supporting Files

- `roundtrip/` - Reviewable round-trip artifacts. Each case keeps source XML,
  structured CSV, xBRL-CSV metadata JSON, and regenerated XML together.
- `roundtrip_test_guide.md` - Explains the round-trip artifact layout, test
  commands, and review points.
- `test_execution_report.md` - Current test execution report for the PoC.
- `../tools/build_roundtrip_test_artifacts.py` - Rebuilds the round-trip
  artifact sets from sample XML inputs.

The main syntax binding and round-trip checks are:

```powershell
& $python .\tests\test_openpeppol_invoice_conversion.py
& $python .\tests\test_lhm_hierarchical_csv_layout.py
& $python .\tests\test_syntax_binding_hierarchical.py
& $python .\tests\test_syntax_binding_reverse.py
& $python .\tests\test_bis_billing3_examples_conversion.py
& $python .\tests\test_roundtrip_artifacts.py
```

The Phase 2 downstream XBRL GL target checks are:

```powershell
& $python .\tests\test_ads_invoices_received_xbrl_gl.py
& $python .\tests\test_ads_invoices_generated_xbrl_gl.py
& $python .\tests\test_ads_invoices_received_lines_xbrl_gl.py
& $python .\tests\test_ads_invoices_generated_lines_xbrl_gl.py
& $python .\tests\test_ads_supplier_listing_xbrl_gl.py
& $python .\tests\test_ads_customer_master_xbrl_gl.py
```

These tests first regenerate the Phase 1 structured CSV as
`out/phase1/EN16931_Core_Invoice.csv`, then use the ADS XBRL GL syntax binding
CSV files under `specs/bindings/syntax/` to write Figure 1 target instances
directly under `out/phase2/ADS_XBRL_GL/`:

```text
Invoices_Received.xbrl
Invoices_Generated.xbrl
Invoices_Received_Lines.xbrl
Invoices_Generated_Lines.xbrl
Supplier_Listing.xbrl
Customer_Master.xbrl
```

The current party direction is tested explicitly: `Invoices_Received` includes
invoice Seller data as Supplier data, `Invoices_Generated` includes invoice
Buyer data as Customer data, `Supplier_Listing` is derived from invoice Seller
terms, and `Customer_Master` is derived from invoice Buyer terms.

The LHM and taxonomy checks are:

```powershell
& $python .\tests\test_lhm_semantic_paths.py
& $python .\tests\test_xbrlgl_generator_uadc_lhm.py
```

Round-trip test artifacts are documented in:

```text
tests/roundtrip_test_guide.md
```

Current test execution report:

```text
tests/test_execution_report.md
```

Some tests write generated files under `out/`, which is ignored by Git. The round-trip artifact test also refreshes files under `tests/roundtrip/` so source XML, structured CSV, metadata JSON, and regenerated XML can be reviewed together.
