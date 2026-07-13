# Documentation Directory

This directory contains human-readable project documentation for the UADC PoC. It explains what the scripts do, how to run them, and why the current design choices were made.

## Subdirectories

- **README_SCRIPT_PROCESSING.md** - Integrated script-processing guide. This is the main technical explanation of how binding rows, XPath, Semantic Path, repeated dimensions such as **dInvoice** and **dInvoiceLine**, and the implementation functions build Structured CSV, UBL XML, ADS XBRL GL, and ADS PSV/CSV outputs.
- **bindings/** - Syntax binding and semantic binding CSV guide. It explains the binding columns, class rows, fact rows, XPath rules, Semantic Path rules, and target-output mapping rules.
- **decisions/** - Architecture and design decision records. These capture the important choices made during the PoC, such as EN 16931-first scope, **lhm_level**, xBRL-CSV-only taxonomy output, metadata policy, and local taxonomy generator ownership.
- **development/** - Clone, setup, tooling, model-maintenance, taxonomy generation, and continuing development guide.
- **lhm_generation/** - Program specification and operating guide for building the EN 16931 LHM CSV from the editable source CSV.
- **repository_files/** - Guide for sample files, expected files, references, and figure assets.
- **semantic_binding_conversion/** - Program specification and operating guide for converting Structured CSV into semantic target flat files such as ADS PSV or CSV.
- **specifications/** - Guide for machine-readable specification CSV files under **specs/**.
- **syntax_binding_conversion/** - Program specification and operating guide for converting UBL Invoice XML to structured CSV and reconstructing XML from structured CSV.
- **taxonomy_generation/** - Program specification and operating guide for generating the xBRL-CSV taxonomy from the LHM CSV.
- **testing/** - Test execution and round-trip artifact guide.

The files in this directory are the source documentation. Generated PDFs should be recreated from these Markdown files when needed.
