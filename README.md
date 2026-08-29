**English** | [日本語](ja/README.md)

# UADC-PoC

## Purpose

UADC (Universal Adapter for Data Conversion) uses HMD-aligned Structured CSV as a common data layer for syntax, semantic, and flat-file conversion.

## Current repository responsibilities

```text
src/            current normative/runtime programs in the existing flat layout
src/tutorial/   current tutorial programs
tools/          optional evaluation, build, validation, migration and tutorial utilities
tests/          current verification programs and fixtures
bindings/       Syntax Binding and Semantic Binding Tables
models/         semantic/model inputs
definitions/    canonical definitions and taxonomy-generation inputs
instances/      original/derived/roundtrip instance artefacts
Specifications/ normative and program specification DOCX documents
taxonomy/       taxonomy artefacts
docs/           public project and validation documentation
```

The current Formal GIT implementation uses a flat `src/*.py` program layout.
The previously proposed `src/syntax/`, `src/semantic/`, `src/common/`, and
`src/flat_csv/` Python package layout has not been implemented.

The repository-root README remains at the repository root. The `src/README.md` file is additional documentation for the runtime tree; it does not replace the root README.

## Execution and safety

Run commands from the repository root. Confirm input paths, output paths, and overwrite behavior before execution. Use task-local or explicitly approved output locations for experiments.

## Tests

Run only tests relevant to materially changed code or conditions. Reuse accepted PASS evidence when inputs, code, settings, dependency versions, outputs, and validation scope are materially identical.
