# Regression Tests

This directory contains directly executable regression scripts for the complete
Phase 1 and Phase 2 PoC.

The tests cover:

- LHM semantic paths and Structured CSV hierarchy;
- UBL forward and reverse syntax binding;
- BIS Billing 3 examples and UBL schema validation;
- xBRL-CSV metadata and taxonomy validation with Arelle;
- all six ADS XBRL GL views;
- ADS PSV and ISO 21378 ADC CSV generation;
- output directory and filename conventions.

**phase1_helpers.py** provides shared Phase 1 conversion paths and helpers.
**roundtrip/** contains generated source, CSV, metadata, and regenerated XML
artifacts used by the tests.

Run and interpret the suite using [**docs/SETUP.md**](../docs/SETUP.md).
Phase-specific expectations are documented in
[**docs/SYNTAX_BINDING.md**](../docs/SYNTAX_BINDING.md) and
[**docs/SEMANTIC_BINDING.md**](../docs/SEMANTIC_BINDING.md).
