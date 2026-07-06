# Source Scripts

This directory contains PoC conversion and binding scripts.

## Main Scripts

- `syntax_binding_hierarchical.py` - Main structured CSV converter. It supports
  XML-to-structured-CSV conversion, xBRL-CSV JSON metadata generation, and
  structured-CSV-to-XML reverse conversion.
- `syntax_binding.py` - Earlier syntax binding conversion script kept for
  reference and comparison with the revised hierarchical converter.
- `semantic_binding.py` - Early semantic binding script for downstream
  CSV-to-CSV projection work.
- `build_syntax_binding.py` - Helper for building syntax binding definitions.
- `normalize_lhm_semantic_paths.py` - Helper for normalizing LHM semantic path
  values.

Scripts should read specification CSVs from `specs/` and write generated output
under ignored `out/` unless a test explicitly writes review artifacts under
`tests/roundtrip/`.
