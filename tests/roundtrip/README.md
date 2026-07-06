# Round-Trip Test Artifacts

This directory contains reviewable test evidence for XML -> structured CSV ->
XML round-trip conversion.

## Subdirectories

- `openpeppol-minimal/` - Round-trip case for the minimal UBL Invoice sample.
- `bis-billing3-examples/` - Round-trip cases for selected BIS Billing 3
  invoice examples.

Each case directory follows the same internal structure:

- `source_xml/` - Original XML inputs.
- `structured_csv/` - Hierarchical structured CSV generated from XML.
- `metadata_json/` - xBRL-CSV metadata JSON generated alongside the CSV.
- `roundtrip_xml/` - XML regenerated from structured CSV.

These artifacts are committed because they are useful for review and regression
discussion. Temporary generated output belongs under ignored `out/`.
