# Specifications Directory

This directory contains the CSV specifications that drive the PoC conversion
pipeline.

## Subdirectories

- `lhm/` - EN 16931 LHM/HMD semantic model CSV and its editable source CSV.
- `bindings/` - Binding definition CSVs that connect semantic paths to source
  syntax or downstream targets.

The files here are inputs to scripts in `src/` and `tools/`. They should remain
small, reviewable, and deterministic.
