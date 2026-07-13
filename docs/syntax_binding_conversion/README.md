# Syntax Binding Conversion Documentation

This directory documents the XML-to-structured-CSV and structured-CSV-to-XML conversion program.

For the detailed implementation-level explanation of XPath context processing, Semantic Path resolution, **dInvoice** and **dInvoiceLine** dimension handling, internal **dict/list/dataclass** objects, and function-level data flow, use **../README_SCRIPT_PROCESSING.md**. The files in this directory remain the program specification and operating guide for the syntax-binding command.

## Files

- **program_specification.md** - Defines converter inputs, outputs, dimension behavior, JSON metadata generation, reverse conversion, currency handling, XPath selector handling, and non-goals.
- **user_guide.md** - Gives command examples for forward conversion, reverse conversion, round-trip artifacts, and troubleshooting.

## Related Directories

- **../../src/** - Converter implementation, especially **syntax_binding.py**.
- **../../specs/bindings/syntax/** - Active UBL Invoice syntax binding CSV.
- **../../specs/lhm/** - LHM CSV used to define structured CSV columns and taxonomy concepts.
- **../../tests/roundtrip/** - Reviewable source XML, structured CSV, metadata JSON, and regenerated XML artifacts.

Phase 1 uses EN 16931 syntax binding as the stable baseline. OpenPeppol CIUS checks are planned as a later overlay.
