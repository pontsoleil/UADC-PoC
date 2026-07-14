# UADC PoC Documentation

This directory contains the current operating guides, data-model specification,
and architecture decision records for the UADC PoC.

## Documentation Set

1. [**SETUP.md**](SETUP.md) - Explains GitHub setup, the Python environment,
   source definitions, generated data, environment checks, regression tests,
   repository maintenance, and the Markdown PDF workflow.
2. [**TUTORIAL.md**](TUTORIAL.md) - Provides a short end-to-end exercise for
   understanding Phase 1 and Phase 2 processing and inspecting their outputs.
3. [**SYNTAX_BINDING.md**](SYNTAX_BINDING.md) - Specifies Phase 1 syntax
   binding, UBL input placement, Structured CSV and metadata generation,
   reverse UBL conversion, command usage, internal processing, and validation.
4. [**SEMANTIC_BINDING.md**](SEMANTIC_BINDING.md) - Specifies Phase 2 semantic
   binding and conversion to ADS PSV, ADS XBRL GL, and ISO 21378 ADC, including
   target coverage, command usage, internal processing, and validation.
5. [**DATA_MODEL.md**](DATA_MODEL.md) - Defines the LHM, Hierarchical Tidy Data,
   Structured CSV as an alternative normalization form, hierarchy and
   multiplicity rules, semantic paths, OIM taxonomy structure, currency and
   selector rules, audit-data boundaries, and all supporting tools.

## Architecture Decisions

[**decisions/**](decisions/README.md) contains the architecture decision records.
They explain the reasons for important scope, hierarchy, taxonomy, binding,
validation, output-layout, and documentation choices.

## Documentation Sources

The Markdown files are the documentation sources. PDFs are generated from the
current Markdown when preparing a publication or synchronized release.

Short GitHub-browser summaries for program directories are provided separately
in **src/README.md**, **src/tutorial/README.md**, **tools/README.md**,
**tools/taxonomy/README.md**, **tools/tutorial/README.md**, and
**tests/README.md**.
