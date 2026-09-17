# UADC Specifications

This directory is the Canonical WORK location for the current UADC program and transformation-table specifications. The current body revision date is 2026-09-15.

## Current specifications

| Document | Role | Body revision date |
|---|---|---|
| `UADC_Common_Library_Program_Specification.docx` | Shared runtime contracts, diagnostics, and common services | 2026-09-15 |
| `UADC_Flat_CSV_Program_Specification.docx` | Flat CSV binding behaviour and accepted 16-column contract | 2026-09-15 |
| `UADC_Flat_CSV_Detailed_Program_Specification.docx` | Flat CSV implementation detail and traceability | 2026-09-15 |
| `UADC_Semantic_Binding_Program_Specification.docx` | HMD-to-HMD semantic binding and materialisation rules | 2026-09-15 |
| `UADC_Syntax_Binding_Program_Specification.docx` | XML/JSON physical syntax binding | 2026-09-15 |
| `UADC_Syntax_Binding_Detailed_Program_Specification.docx` | Syntax-binding implementation detail and traceability | 2026-09-15 |
| `UADC_Transformation_Table_Specification.docx` | Normative roles and columns of Binding, mapping, and tax tables | 2026-09-15 |

Program Specification and Detailed Program Specification are maintained as separate documents. `UADC_Transformation_Examples/` remains supporting material; executable code and tests remain in their established project locations.

## Current accepted boundaries

- The canonical Flat CSV Binding has 16 columns. A 17-column file is accepted only as legacy-compatible input and is normalised to the 16-column runtime contract.
- Binding identity excludes `id`; Structured CSV may retain an `id` data column and HMD identifiers remain distinct concepts.
- Selectors are encoded in `semantic_path` or `syntax_path` as applicable. The canonical HMD `semantic_path` remains occurrence-neutral.
- Structured CSV, formal xBRL-CSV JSON metadata, and LedgerExplorer input have distinct responsibilities.
- XBRL GL Next project namespaces use `https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/{module}`.
- Accounting Entries and Business Transactions are separate root-HMD DTSs. The accepted 14 differences are `ROOT_HMD_SPECIFIC_STRUCTURAL_DIFFERENCE`; the two DTSs are selected and validated separately.

## Evidence and unresolved items

The document update reuses accepted conversion, taxonomy-generation, Arelle, accounting-recalculation, and round-trip evidence; those tests were not repeated. Arelle taxonomy/OIM conformance does not establish accounting-value completeness or application import acceptance.

Open implementation or operational items remain: EPSON explicit tax facts totalling JPY 141,601,937 across 3,490 details are not preserved; reverse EPSON-to-PCA tax-code selection remains `TAX_POLICY_AMBIGUOUS`; EPSON account registration and real-application import are unverified; and the current LedgerExplorer screen/input connection is unverified. The documented account-attribute plus debit/credit return inference is also not implemented by the current PCA mapping, which uses explicit `return_flag` values.

## Archive

Predecessor documents and the former in-directory support archives were moved to `../archive/Specifications/20260915_1646/`. The immutable pre-change copy and provenance records are preserved under `../docs/Codex/2026/202609/20260915/20260915_1646/specifications-current-acceptance-update/outputs/`.
