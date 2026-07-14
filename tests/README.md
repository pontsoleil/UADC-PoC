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

Run and interpret the suite using
[**Environment, Tests, and Tutorial**](../docs/01_ENVIRONMENT_TESTS_TUTORIAL.md).
Phase-specific expectations are documented in the Phase 1 UBL syntax-binding
and Phase 2 ADS binding documents listed in [**docs/README.md**](../docs/README.md).
