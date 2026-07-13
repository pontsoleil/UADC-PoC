# Semantic Binding Conversion Documentation

This directory documents the Structured-CSV-to-target-flat-file conversion program.

The semantic binding converter reads a Phase 1 UADC Structured CSV and a semantic binding CSV. It writes a Phase 2 target flat file such as ADS PSV or ISO 21378 ADC CSV. The binding table defines which target column receives which UADC **semantic_path** value, and which semantic class controls repeated target rows.

For implementation-level details shared with the broader processing model, including internal **dict/list/dataclass** objects and function-level data flow, use **../README_SCRIPT_PROCESSING.md**.

## Files

- **program_specification.md** - Defines converter inputs, outputs, semantic binding rows, repeated row scope, indexed repeated values, output naming, and non-goals.
- **user_guide.md** - Gives command examples for ADS PSV and CSV generation, directory input, and troubleshooting.

## Related Directories

- **../../src/** - Converter implementation, especially **semantic_binding.py**.
- **../../specs/bindings/semantic/** - Active semantic binding CSV files.
- **../../specs/bindings/syntax/** - Syntax binding CSV files that define the Phase 1 Structured CSV model used as semantic source.
- **../../out/phase1/** - Phase 1 Structured CSV inputs.
- **../../out/phase2/** - Generated Phase 2 target outputs.

Phase 2 semantic binding starts from the common Structured CSV. It does not parse XML directly and does not depend on source XML XPath expressions.
