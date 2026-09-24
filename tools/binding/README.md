**English** | [日本語](ja/README.md)

# tools/binding

## Purpose

This directory contains the current UADC binding and conversion runtime programs and their directly related supporting implementation files.

## Core transformation runtime

- [`syntax_binding.py`](syntax_binding.py) — XML ⇄ Structured CSV Syntax Binding.
- [`semantic_binding.py`](semantic_binding.py) — reversible Structured CSV ⇄ Structured CSV Semantic Binding.
- [`flat_csv.py`](flat_csv.py) — Flat CSV ⇄ Structured CSV conversion using the registered profile, Binding, account mapping, tax mapping, and related runtime definitions. It implements the canonical 16-column Binding contract and the registered compatibility handling described by the current specifications.

These programs implement the binding stages around the HMD and Structured CSV semantic layer. Presence in `tools/binding/` alone does not make a program a prerequisite of every UADC route.

## Additional and supporting implementation

- [`selector_multiplicity.py`](selector_multiplicity.py) — selector-aware effective multiplicity support imported by the Semantic Binding runtime.
- [`aggregate_pairing.py`](aggregate_pairing.py) — aggregate pairing support used by applicable Flat CSV conversion routes while retaining source-slot and occurrence ownership.
- [`tuple_binding.py`](tuple_binding.py) — XBRL 2.1 Tuple ⇄ Structured CSV conversion for the same HMD semantic model. Dedicated Tuple/OIM execution-manifest acceptance remains HOLD.
- [`syntax_binding_ads_xbrl_gl.py`](syntax_binding_ads_xbrl_gl.py) — ADS/XBRL GL-specific syntax conversion support used by applicable routes.

[`support/`](support/) contains directly related supporting implementation and documentation. [`tutorial/`](tutorial/) contains retained tutorial documentation and does not define current runtime programs.

No standalone `oim_metadata.py` exists in the current canonical tree. OIM metadata handling remains within the applicable runtime implementations.

## Optional review utility

[`tools/maintenance/csv_excel_bridge.py`](../maintenance/csv_excel_bridge.py) provides controlled CSV/XLSX interchange for review. It is not part of the core UADC transformation path and is not required for Syntax Binding, Flat CSV Binding, Structured CSV generation, or round-trip conversion. It is not referenced by the currently registered `tests/runtime/**/RUN_PARAMETERS.json` cases. See the [CSV/XLSX bridge documentation](csv_excel_bridge.md) for its separate usage.

## Repository responsibility boundaries

- [`tools/binding/**`](./) — UADC binding and conversion runtime programs and directly related supporting implementation.
- [`tools/taxonomy/**`](../taxonomy/) — taxonomy generation programs and supporting resources.
- [`tests/**`](../../tests/) — validation and regression material.
- [`tests/runtime/**`](../../tests/runtime/) — registered runtime and reproducibility manifests.
- [`bindings/**`](../../bindings/) — Binding, profile, account-mapping, tax-mapping, and related definitions consumed by applicable runtime routes.
- [`models/**`](../../models/) — semantic and HMD model inputs used by applicable processing routes.

## Execution and safety

Run commands from the repository root. Confirm input paths, output paths, and overwrite behavior before execution. Use task-local or explicitly approved output locations for experiments.

## Tests and reproducibility

Run only tests relevant to materially changed code or conditions. Reuse accepted PASS evidence when inputs, code, settings, dependency versions, outputs, and validation scope are materially identical.

Registered runtime and reproducibility cases are documented under [`tests/runtime/`](../../tests/runtime/). Each registered case uses its `RUN_PARAMETERS.json` as the execution-parameter authority.
