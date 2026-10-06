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

- [`selector_multiplicity.py`](selector_multiplicity.py) — shared limited Semantic Path predicate parsing plus selector-aware effective multiplicity support. It supports scoped equality, presence, `and`, `or`, `not`, and parentheses; complex XPath-style expressions remain outside the current contract.
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
- [`bindings/hmd/**`](../../bindings/hmd/) — recovered HMD semantic authorities used by applicable processing routes.
- [`taxonomy/**`](../../taxonomy/) — corresponding taxonomy authorities and generated taxonomy resources where applicable.

## Execution and safety

Run commands from the repository root. Confirm input paths, output paths, and overwrite behavior before execution. Use task-local or explicitly approved output locations for experiments.

## Tests and reproducibility

Run only tests relevant to materially changed code or conditions. Reuse accepted PASS evidence when inputs, code, settings, dependency versions, outputs, and validation scope are materially identical.

Registered runtime and reproducibility cases are documented under [`tests/runtime/`](../../tests/runtime/). Each registered case uses its `RUN_PARAMETERS.json` as the execution-parameter authority.

## Formal OIM reverse conversion and negative-amount result reports

flat_csv.py to-flat consumes the JSON metadata of one dedicated Formal OIM CSV/JSON pair. It reconstructs selector-qualified semantic facts before reverse account or tax mapping and physical projection. Standalone legacy/Internal Structured CSV is not a substitute.

Negative monetaryAmount facts require MANUAL_REVIEW_REQUIRED; the report identifies the input pair, journal/detail coordinates, selector-qualified semantic path, available account information and amount. Values, accounts, sides and materialisation rules are not automatically corrected.

On a later ConversionError, the existing --summary-log saves the detected input facts, actual error and output_generated=false. The original exception and CLI exit code 2 are retained. Output record identifiers and negative-cell counts are null when no CSV has been generated; the report does not claim successful output preservation.

Successful reverse conversion writes the existing normalised CSV and an automatic <normalised CSV>.conversion-report.json sidecar containing its SHA-256 and negative-cell provenance. The normal csv_physical_adapter.py from-uadc route consumes this sidecar when present, verifies the normalised SHA and resolves final application CSV records, physical line ranges, sides, columns, accounts and amounts. It adds negative_amount_report to the existing --report result and writes <application CSV>.conversion-report.json.

Input negative-fact counts are distinct from split output-cell counts. Final cells link to input fact IDs. Embedded line breaks use physical line ranges. Existing adapter fields and exit status are retained. No conversion option, automatic sign reversal, absolute-value conversion, account replacement or test-only finalisation is introduced. Without a conversion sidecar, the adapter retains its existing behaviour.

These reports contain targeted accounting values and must remain within authorised private output locations. They are not publication artefacts. Reporting adoption does not resolve missing tax classification in Formal OIM. The EPSON45 route retains the adopted 6DB HMD, sequence-aligned Binding, existing tax mappings and physical format.

## Published synthetic EPSON45 reporting regression

The dedicated manifest is tests/runtime/epson/epson45-negative-report/RUN_PARAMETERS.json; the Formal CSV/JSON pair is instances/fixtures/epson45-negative-report/. It registers both normal CLI stages, relative paths, dependency SHA-256 and expected results: three negative input facts, four split output cells, final application physical rows and input provenance. Generated outputs/ files are private execution results, not publication artefacts; only the output destination may be redirected for a run.

Support is limited to the synthetic reporting regression. The historical pca-to-epson, epson-roundtrip and pca-roundtrip cases remain HOLD under the current runtime. Real EPSON45 conversion remains HOLD with TAX_POLICY_UNRESOLVED due to missing classification. Actual EPSON application import has not been accepted. Legacy migration and tax-contract changes are separate work.
