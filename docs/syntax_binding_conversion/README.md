# Syntax Binding Conversion Documentation

This directory documents the XML-to-structured-CSV and structured-CSV-to-XML
conversion program.

## Files

- `program_specification.md` - Defines converter inputs, outputs, dimension
  behavior, JSON metadata generation, reverse conversion, currency handling,
  XPath selector handling, and non-goals.
- `user_guide.md` - Gives command examples for forward conversion, reverse
  conversion, round-trip artifacts, and troubleshooting.

## Related Directories

- `../../src/` - Converter implementation, especially
  `syntax_binding_hierarchical.py`.
- `../../specs/bindings/syntax/` - Active UBL Invoice syntax binding CSV.
- `../../specs/lhm/` - LHM CSV used to define structured CSV columns and
  taxonomy concepts.
- `../../tests/roundtrip/` - Reviewable source XML, structured CSV, metadata
  JSON, and regenerated XML artifacts.

Phase 1 uses EN 16931 syntax binding as the stable baseline. OpenPeppol CIUS
checks are planned as a later overlay.
