# Utility Scripts — UADC-PoC

## Purpose and scope

This document describes the four Python scripts present under `tools/binding/` in the accepted R10 WORK Candidate evidence package dated 2026-10-21. It is a descriptive README, **not** a new specification, authority, acceptance criterion, or publication approval.

The authoritative sources for execution and change control remain the applicable `AGENTS.md`, `DECISIONS`, `CURRENT_BASELINE`, `HANDOFF`, the approved profiles and mappings, and the registered runtime `RUN_PARAMETERS.json` files. Consult those sources before using or modifying the scripts. The script inventory below is limited to the files verified in the supplied package; it is not an inventory of every utility in the repository.

## Script inventory

| Script | Responsibility | Interface |
| --- | --- | --- |
| `flat_csv.py` | Converts application-oriented flat CSV to Structured CSV / Formal OIM, and performs reverse conversion from a matched Formal OIM CSV + JSON metadata pair to normalized flat CSV. Uses HMD, Binding, account mappings and tax mappings for semantic conversion. | CLI: `to-structured`, `to-flat` |
| `csv_physical_adapter.py` | Converts and validates the physical CSV representation at the application boundary, according to a physical-format profile; handles serialization details rather than accounting semantics. | CLI: `inspect` and application/UADC conversion subcommands |
| `selector_multiplicity.py` | Shared selector-aware interpretation and effective-multiplicity functionality for semantic paths and HMD-related processing. | Imported Python module |
| `aggregate_pairing.py` | Shared aggregate pairing/materialization functionality, preserving source occurrence ownership and checking debit/credit totals. | Imported Python module |

## Conversion workflow

```text
Application CSV
    |
    | csv_physical_adapter.py (physical format normalization)
    v
Normalized flat CSV
    |
    | flat_csv.py to-structured (Binding + HMD + mappings)
    v
Formal OIM CSV + its matching JSON metadata
    |
    | flat_csv.py to-flat (target Binding + mappings)
    v
Normalized target flat CSV
    |
    | csv_physical_adapter.py (target physical profile)
    v
Target application CSV
```

The Formal OIM CSV and JSON metadata form a **single inseparable input/output pair**. Do not treat a standalone legacy Structured CSV as a substitute for the current reverse-input authority.

## Key operating principles

- **Definition-driven conversion.** The HMD and Binding define the semantic structure and destination projection. Account and tax mapping tables govern code conversions. Application-specific exceptions must come from approved definitions rather than guesses based on debit/credit sides or account labels.
- **Fact identity.** Preserve the selector-qualified `semantic_path` as the fact identity. Interpreting selectors for HMD lookup must not change that identity.
- **Destination projection.** A source fact without a corresponding destination Binding projection is not, by itself, a conversion error. Such facts remain in the source Formal OIM pair. When existing `--debug` and `--summary-log` are enabled, non-projected fact paths and counts are reported as `unprojected_facts`.
- **Document-level tax inclusion.** The document's `taxInclusion` value supplies the inclusive/exclusive selection context. Tax mappings determine the application tax code using the applicable tax category, rate and transaction classification; document-level information is not duplicated into journal headers or details.
- **Mapping direction.** The NTA account code in Formal OIM is mapped to the destination application's account code. Approved many-to-one NTA-to-application mappings may exist; ambiguous mappings in the reverse direction must not be silently resolved.
- **No silent value repair.** Do not recompute, replace or silently discard monetary amounts or change signs as a substitute for an approved conversion rule. Existing negative-amount diagnostics and provenance remain applicable.
- **Physical versus semantic concerns.** `csv_physical_adapter.py` handles encoding, line endings, BOM policy, quoting, date representation and physical columns; it does not determine tax semantics or account equivalence.

## Running and diagnostics

Use the **registered case's** `RUN_PARAMETERS.json` and applicable authority for complete command lines, paths, dependencies and accepted execution conditions. This README intentionally does not invent a new invocation or test fixture.

`flat_csv.py` exposes the existing `--debug` and `--summary-log` options. The accepted R10 Candidate records non-projected source fact counts in the success summary when debug reporting is requested. A successful CLI exit code is not, by itself, a complete acceptance decision; the required checks and evidence reuse conditions are defined by the existing authority.

`csv_physical_adapter.py` supports inspection against a profile and conversion between application and UADC physical CSV representations. Consult its built-in command help and the registered runtime case before selecting a subcommand.

The R10 acceptance evidence covers a Windows WORK Candidate. It does **not** establish that this README has been adopted into Canonical or Official GIT, or that an EPSON GUI import test has passed.

## Maintenance and publication

Changes follow the approved workflow:

`WORK Candidate → acceptance → Canonical registration → Official GIT full accepted-collection comparison → commit → push`

Preserve original files and evidence. Do not MOVE, unconditionally mirror, delete, or change approval status without authorization. For the Official GIT comparison, compare relative paths and file existence as well as text content, normalizing only permitted line-ending differences; preserve quoted CSV field values and retain raw SHA-256 for provenance.

## Verification basis

- Submitted `UADC_EPSON_success_summary_debug_results_PASS_20261021_0616.zip`: verified presence and source headers of the four scripts under `candidate/tools/binding/`.
- Supplied R10 `FINAL_REPORT.md` and `ACCEPTANCE_RESULTS.json`: WORK Candidate accepted; Reverse exit code 0, non-projected fact reporting completed, Formal OIM Forward and physical adapter evidence reused.
- Live repository-wide inventories and current on-disk authority files were **not** independently read for this document. Any broader coverage or formal adoption remains subject to comparison with those sources.
