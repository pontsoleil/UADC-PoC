# Minimal OpenPeppol Round-Trip Case

This directory contains the round-trip artifacts for the minimal UBL Invoice
sample.

## Subdirectories

- `source_xml/` - Original minimal invoice XML.
- `structured_csv/` - Structured CSV generated from the XML.
- `metadata_json/` - xBRL-CSV metadata JSON for the structured CSV.
- `roundtrip_xml/` - XML regenerated from the structured CSV.

This case is the smallest baseline for checking that core EN 16931 values,
dimension columns, metadata, and reverse XML generation remain stable.
