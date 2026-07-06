# UADC PoC Collaboration Workspace

This workspace is for the xBRL-GL Next / UADC proof of concept. It supports
the proposal documented in `XBRL_GL_Next_UADC_PoC.pdf`, "PoC Proposal for XBRL
GL Next: A Hierarchical Tidy Data Universal Audit Data Converter for Invoice
Reuse".

The proposal defines UADC as a Universal Audit Data Converter that uses
hierarchical tidy data as a common semantic representation. The target
architecture separates source syntax conversion from downstream audit-view
generation:

- syntax binding maps source invoice XML into a common EN 16931 / XBRL GL Next
  semantic layer;
- the common semantic layer preserves document-level invoice information,
  parties, tax subtotals, invoice lines, identifiers, dates, currencies, and
  monetary amounts;
- semantic binding then projects the common dataset into downstream audit
  views, including ISO 21378:2019 Audit data collection Sales/Purchase invoice
  views and AICPA ADS O2C/P2P invoice views.

This repository is the working implementation space for that proposal. The
current implementation is Phase 1 of the PoC.

The first PoC checkpoint is the EN 16931-1 invoice semantic model represented
as an LHM/HMD-style CSV, plus binding-driven conversion from UBL Invoice XML to
structured CSV, xBRL-CSV JSON metadata, and round-trip UBL Invoice XML.

OpenPeppol BIS Billing is handled as the next layer: a CIUS/profile overlay on
top of EN 16931-1, with additional constraints, defaults, and syntax-specific
rules.

## Figure 1

![Figure 1 - UADC PoC processing flow](references/figures/uadc_poc_processing_flow_figure1.png)

Figure 1 from the proposal shows the intended UADC processing flow. Phase 1
covers the source-to-semantic path from OpenPeppol/UBL Invoice XML to EN 16931
hierarchical tidy data, structured CSV, JSON metadata, taxonomy validation, and
round-trip XML. Phase 2 extends the same semantic layer toward ISO 21378 and
AICPA ADS target views through semantic binding.

## Project Milestones

| Phase | Objective | Main Deliverables | Current Status |
| --- | --- | --- | --- |
| Phase 1 | Establish the EN 16931 core invoice baseline as a structured, testable semantic model. | LHM CSV, UBL syntax binding CSV, xBRL-CSV taxonomy, XML-to-structured-CSV conversion, xBRL-CSV JSON metadata, structured-CSV-to-XML round trip, Arelle and UBL schema validation. | In progress and functioning as the current repository baseline. The active syntax binding is EN 16931 based, the taxonomy entry point is `plt-oim`, and round-trip test artifacts are available under `tests/roundtrip/`. |
| Phase 2 | Extend the UADC toward the full proposal: multi-invoice hierarchical tidy data and downstream audit reuse. | Multi-invoice datasets, related invoice CSV and line CSV outputs, reusable supplier/customer instances, semantic binding CSV definitions, ISO 21378 Sales/Purchase invoice outputs, AICPA ADS O2C/P2P outputs, and traceability from source facts to target views. | Planned. Phase 2 should start after the Phase 1 EN 16931 baseline remains stable. |
| Phase 3 | Generalize the approach for broader XBRL GL Next interoperability. | Profile governance, extension rules, additional source syntaxes or CIUS overlays, broader audit/tax/statistical/reporting mappings, and lessons learned for standardization. | Future direction. |

Phase 1 intentionally focuses on deterministic transformation and validation
for a constrained EN 16931 invoice scope. Phase 2 adds the wider UADC value
proposition described in the PDF: semantic reuse across multiple invoices,
seller-side and buyer-side audit views, and projection from one common semantic
source into multiple target formats.

## Flow

```text
UBL Invoice XML
  -> EN 16931 syntax binding
  -> EN 16931 LHM/HMD structured CSV
  -> xBRL-CSV JSON metadata
  -> Arelle xBRL-CSV validation
  -> round-trip UBL Invoice XML
  -> UBL 2.1 schema validation

OpenPeppol BIS CIUS
  -> profile constraints and extensions
  -> checks layered on the EN 16931 conversion baseline

Phase 2 downstream reuse
  -> multi-invoice hierarchical tidy data
  -> semantic binding CSV
  -> ISO 21378 Sales/Purchase invoice views
  -> AICPA ADS O2C/P2P views
```

## Directory Layout

- `docs/` - Human-readable collaboration material. This includes design decisions in `docs/decisions/`, LHM generation specifications and user guides in `docs/lhm_generation/`, syntax binding conversion specifications and user guides in `docs/syntax_binding_conversion/`, and taxonomy generation specifications and user guides in `docs/taxonomy_generation/`.
- `references/` - External source notes and links used to interpret standards, source specifications, and implementation references. Keep large licensed source documents outside the repository and record only reproducible notes or pointers here.
- `XBRL_GL_Next_UADC_PoC.pdf` - Proposal document that motivates this repository and defines the broader UADC direction beyond the current Phase 1 implementation.
- `specs/lhm/` - LHM/HMD semantic model definitions for the EN 16931 invoice PoC. The generated/current CSV is stored here, while `specs/lhm/source/` keeps the editable source CSV used to regenerate or adjust the LHM. Local reviewer workbooks are ignored by Git.
- `specs/bindings/` - Binding definitions. The active UBL Invoice syntax binding is `specs/bindings/syntax/EN16931_UBL_Invoice_Syntax_Binding.csv`; it maps LHM semantic paths to UBL XPath expressions and selector predicates used by forward and reverse conversion.
- `samples/input/` - Small sample input files committed for baseline checks, including the minimal UBL Invoice sample and selected BIS Billing example invoices.
- `samples/expected/` - Checked expected output for lightweight regression checks where a stable expected artifact is useful.
- `src/` - PoC conversion and binding scripts. The main structured CSV converter is `src/syntax_binding_hierarchical.py`; supporting scripts cover syntax binding, semantic binding, and LHM semantic path normalization.
- `tests/` - Regression checks, test documentation, generated round-trip review artifacts, and the current test execution report. `tests/roundtrip/` keeps source XML, structured CSV, xBRL-CSV metadata JSON, and regenerated XML side by side for review.
- `tools/` - Supporting generation tools that are part of this repository. The local taxonomy generator is in `tools/taxonomy/`, including the copied UADC-compatible `xBRLGL_TaxonomyGenerator.py` and its GL generic schema template.
- `out/` - Generated local output, ignored by Git. This includes taxonomy output, structured CSV output, reverse-conversion output, temporary caches, and rendered document QA artifacts.

The taxonomy generator is included at `tools/taxonomy/xBRLGL_TaxonomyGenerator.py`; no external `XBRL-GL-2026` checkout is required for normal tests.
The generated xBRL-CSV taxonomy entry point is `out/taxonomy/plt/plt-oim-2026-07-05.xsd`.
Tuple/content taxonomy schemas such as `plt-all-<version>.xsd` and `en16931-content-<version>.xsd` are not generated for this PoC.

## Current Scope

1. Define and audit the Invoice LHM from EN 16931-1.
2. Confirm syntax-binding conversion from UBL Invoice XML to EN 16931
   structured CSV.
3. Generate xBRL-CSV metadata that references the `plt-oim` taxonomy entry point.
4. Validate generated xBRL-CSV metadata with Arelle.
5. Reconstruct UBL Invoice XML from structured CSV and validate it with UBL 2.1 schemas.
6. Layer OpenPeppol BIS Billing as CIUS/profile constraints and extensions after the EN 16931 baseline remains stable.

## Tasks

1. Define the LHM for the hierarchical semantic model.
   The LHM describes the EN 16931 invoice business terms as a hierarchy. It includes semantic paths, effective `lhm_level` values, and UBL XPath bindings for the source XML document. The syntax binding connects each semantic path to the XML element or selector predicate used during conversion.

2. Define the xBRL-CSV taxonomy for the LHM.
   The taxonomy generator reads the LHM CSV and emits the EN 16931 module schema plus the `plt-oim` xBRL-CSV taxonomy schema and definition linkbase. Hypercubes, dimensions, and primary items are derived from the effective LHM hierarchy. The generated taxonomy is checked with Arelle using `out/taxonomy/plt/plt-oim-2026-07-05.xsd` as the entry point.

3. Convert XML instances to structured CSV with JSON metadata.
   The syntax binding converter reads a UBL Invoice XML instance, applies the LHM XPath bindings, and writes a hierarchical structured CSV. At the same time it writes xBRL-CSV JSON metadata that links CSV dimensions and fact columns to the generated taxonomy. The JSON metadata is validated with Arelle `loadFromOIM`.

4. Perform round trip conversion from structured CSV to XML instances.
   The reverse conversion reads the structured CSV and the same LHM/syntax binding definitions, reconstructs a UBL Invoice XML instance, and adds required syntax support values where needed for UBL schema validity. The resulting XML is checked with an XML parser and UBL 2.1 schema validation.

The resulting artifacts are therefore checked at two levels: xBRL-CSV reports and taxonomy are verified with Arelle, while regenerated XML instances are verified with XML parsing and UBL schema validation.

## Current Tests

```powershell
& 'C:\Users\nobuy\AppData\Local\Programs\Python\Python310\python.exe' tests\test_xbrlgl_generator_uadc_lhm.py
& 'C:\Users\nobuy\AppData\Local\Programs\Python\Python310\python.exe' tests\validate_taxonomy.py
& 'C:\Users\nobuy\AppData\Local\Programs\Python\Python310\python.exe' tests\test_openpeppol_invoice_conversion.py
& 'C:\Users\nobuy\AppData\Local\Programs\Python\Python310\python.exe' tests\test_bis_billing3_examples_conversion.py
& 'C:\Users\nobuy\AppData\Local\Programs\Python\Python310\python.exe' tests\test_roundtrip_artifacts.py
& 'C:\Users\nobuy\AppData\Local\Programs\Python\Python310\python.exe' tests\test_xbrl_csv_metadata_arelle.py
```

The sample UBL Invoice XML and BIS Billing examples are converted using
`specs/bindings/syntax/EN16931_UBL_Invoice_Syntax_Binding.csv`. OpenPeppol CIUS
checks are added after the EN 16931 conversion baseline is stable.

Semantic path elements are generated from Business Terms using
`lowerCamelCaseConcatenated`, for example:

```text
Invoice issue date -> invoiceIssueDate
Seller postal address -> sellerPostalAddress
```
