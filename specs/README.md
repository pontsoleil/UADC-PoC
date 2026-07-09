# Specifications Directory

This directory contains the CSV specifications that drive the PoC conversion
pipeline.

## Subdirectories

- `lhm/` - EN 16931 LHM/HMD semantic model CSV and its editable source CSV.
- `bindings/` - Binding definition CSVs that connect semantic paths to source
  syntax or downstream targets.
- `XBRL-GL/` - XBRL GL tuple taxonomy definition table derived from the
  `gl-plt-all-2016-12-01.xsd` profile and its imported XBRL GL modules.

The files here are inputs to scripts in `src/` and `tools/`. They should remain
small, reviewable, and deterministic.
