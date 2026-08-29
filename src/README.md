**English** | [日本語](ja/README.md)

# src

## Purpose

This directory contains the normative UADC conversion programs and required runtime libraries.

## Programs

- `syntax_binding.py` — XML ⇄ Structured CSV Syntax Binding.
- `tuple_binding.py` — Tuple XBRL ⇄ Structured CSV syntax conversion.
- `semantic_binding.py` — Structured CSV ⇄ Structured CSV Semantic Binding.
- `selector_multiplicity.py` — selector-effective multiplicity support used by current binding processing.
- `csv_excel_bridge.py` — controlled CSV/Excel review interchange.
- `syntax_binding_ads_xbrl_gl.py` — ADS/XBRL GL-specific current syntax conversion support.
- `tutorial/` — current tutorial programs.

No standalone `oim_metadata.py` exists in the current Formal GIT. OIM metadata
processing remains within the existing runtime implementation.

The Flat CSV runtime is not currently registered under Formal GIT `src/`. The
validated WORK implementation is documented by
`Specifications/UADC_Flat_CSV_Program_Specification.docx` and the current
transformation route status report.

## Responsibility boundary

`src/**` contains normative programs and required runtime libraries. `tools/**` contains optional evaluation, tutorial, validation, or synchronization tools. `tests/**` contains verification programs. Code under `src/**` must not import `tools/**`.

## Execution and safety

Run commands from the repository root. Confirm input paths, output paths, and overwrite behavior before execution. Use task-local or explicitly approved output locations for experiments.

## Tests

Run only tests relevant to materially changed code or conditions. Reuse accepted PASS evidence when inputs, code, settings, dependency versions, outputs, and validation scope are materially identical.
