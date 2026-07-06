# Documentation Directory

This directory contains human-readable project documentation for the UADC PoC.
It explains what the scripts do, how to run them, and why the current design
choices were made.

## Subdirectories

- `decisions/` - Architecture and design decision records. These capture the
  important choices made during the PoC, such as EN 16931-first scope,
  `lhm_level`, xBRL-CSV-only taxonomy output, metadata policy, and local
  taxonomy generator ownership.
- `lhm_generation/` - Program specification and operating guide for building
  the EN 16931 LHM CSV from the editable source CSV.
- `syntax_binding_conversion/` - Program specification and operating guide for
  converting UBL Invoice XML to structured CSV and reconstructing XML from
  structured CSV.
- `taxonomy_generation/` - Program specification and operating guide for
  generating the xBRL-CSV taxonomy from the LHM CSV.

The files in this directory are source documentation. Generated Word documents
at the repository root are review artifacts derived from these Markdown files.
