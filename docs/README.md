# Documentation Directory

This directory contains human-readable project documentation for the UADC PoC. It explains what the scripts do, how to run them, and why the current design choices were made.

## Subdirectories

- **README_SCRIPT_PROCESSING.md** - Integrated script-processing guide. This is the main technical explanation of how binding rows, XPath, Semantic Path, repeated dimensions such as **dInvoice** and **dInvoiceLine**, and the implementation functions build Structured CSV, UBL XML, ADS XBRL GL, and ADS PSV/CSV outputs.
- **syntax_binding_conversion/** and **semantic_binding_conversion/** - Binding CSV contracts, class and fact rows, XPath and Semantic Path rules, target mapping, command usage, and limitations.
- **decisions/** - Architecture and design decision records. These capture the important choices made during the PoC, such as EN 16931-first scope, **lhm_level**, xBRL-CSV-only taxonomy output, metadata policy, and local taxonomy generator ownership.
- **development/** - Clone, setup, tooling, model-maintenance, taxonomy generation, and continuing development guide.
- **lhm_generation/** - Program specification and operating guide for building the EN 16931 LHM CSV from the editable source CSV.
- **repository_files/** - Guide for sample files, expected files, references, and figure assets.
- **semantic_binding_conversion/** - Program specification and operating guide for converting Structured CSV into semantic target flat files such as ADS PSV or CSV.
- **specifications/** - Guide for machine-readable specification CSV files under **specs/**.
- **syntax_binding_conversion/** - Program specification and operating guide for converting UBL Invoice XML to structured CSV and reconstructing XML from structured CSV.
- **taxonomy_generation/** - Program specification and operating guide for generating the xBRL-CSV taxonomy from the LHM CSV.
- **testing/** - Test execution and round-trip artifact guide.
- **tools/** - Program specification for all supporting scripts and the PSV viewer under **tools/**.

The files in this directory are the source documentation. Generated PDFs should be recreated from these Markdown files when needed.

The planned PoC baseline for Phase 1 and Phase 2 is complete. Phase 1 covers the EN 16931 Structured CSV, xBRL-CSV taxonomy and metadata, and UBL round trip. Phase 2 covers ADS XBRL GL, ADS PSV, and the four documented ISO 21378 ADC invoice CSV views. Later source syntaxes and additional target profiles belong to the next expansion phase.
