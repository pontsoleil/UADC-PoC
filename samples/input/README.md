# Sample Input Files

This directory contains committed XML input samples for conversion tests.

## Files and Subdirectories

- `openpeppol_ubl_invoice_minimal.xml` - Minimal UBL Invoice sample used for
  the baseline OpenPeppol/EN 16931 conversion check.
- `bis-billing3-examples/` - Selected BIS Billing 3 invoice examples used to
  test broader syntax binding coverage.

These samples are intentionally small enough to keep in Git. Generated
structured CSV, metadata JSON, and regenerated XML are kept in `tests/roundtrip/`
or `out/`.
