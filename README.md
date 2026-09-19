# UADC PoC Collaboration Workspace

This workspace is for the xBRL-GL Next / UADC proof of concept. It implements the UADC processing model for "A Hierarchical Tidy Data Universal Audit Data Converter for Invoice Reuse".

UADC-PoC and the bundled XBRL GL Next taxonomy are prototype project
artefacts, not official specifications. The accepted taxonomy families use
XBRL Japan namespace URIs, but that use does not imply approval, endorsement,
or official publication by XBRL Japan or XBRL International. See the
[XBRL GL source notice](taxonomy/NOTICE_XBRL_GL.md),
[licence scope](LICENSE-SCOPE.md), [third-party notices](THIRD_PARTY_NOTICES.md),
and the [publication and namespace decision](docs/decisions/ADR-XBRL-GL-NEXT-PROTOTYPE-TAXONOMY-PUBLICATION.md).

## Project Entry Points

- [Current baseline](docs/CURRENT_BASELINE.md)
- [Handoff and next work](docs/HANDOFF.md)
- [License scope](LICENSE-SCOPE.md)
- [Third-party notices](THIRD_PARTY_NOTICES.md)
- [XBRL GL source notice](taxonomy/NOTICE_XBRL_GL.md)
- [Runtime programs](tools/binding/README.md)
- [Taxonomy generator](tools/taxonomy/README.md)
- [Registered runtime cases](tests/runtime/README.md)

## Validated pre-reorganization baseline (2026-08-22)

Three binding methods have independent public-safe WORK validation evidence. Syntax Binding converts a repository-owned synthetic UBL Invoice to and from EN CIUS Structured CSV. Flat CSV Binding converts a synthetic 81-column PCA record set to and from XBRL GL Next Accounting Entries Structured CSV. Semantic Table converts an explicitly reviewed three-concept reversible subset from EN CIUS to XBRL GL Next Business Transactions and back. The Semantic Table result is not a claim of complete EN CIUS mapping.

Each route uses its applicable HMD. The OIM taxonomy is generated or identity-verified and validated before conversion. An XBRL-CSV Structured CSV is a same-directory, same-basename `.csv`/`.json` pair, and metadata uses a package-relative taxonomy URI. Arelle validation and reverse semantic/normalized comparison passed for all three accepted scopes. Private accounting data and PINT JP official fixtures were not used or promoted.

The current runtime programs are under `tools/binding/`, including
`syntax_binding.py`, `semantic_binding.py`, and `flat_csv.py`.  Registered
PCA/EPSON execution contracts are under `tests/runtime/`.  Accepted XBRL GL
Next taxonomy families are under `taxonomy/business-transactions/` and
`taxonomy/accounting-entries/`.

## Project Charter

This PoC is an implementation and validation project for the **XBRL GL Next
Requirements Specification** and the companion **XBRL GL Next Taxonomy
Framework**. Its purpose is to turn the framework's requirements into
executable bindings, semantic models, serialisations, transformations, and
repeatable tests.

The project follows these framework principles:

- semantics are primary and are separated from any single serialisation;
- the semantic model is layered as FSM (Foundational Semantic Model), BSM
  (Business Semantic Model), and LHM (Logical Hierarchical Model);
- a deterministic graph walk derives serialisation-ready LHM structures from
  a constrained BSM;
- XBRL GL Next acts as the core semantic dataset for a Universal Adapter
  connecting EDI, ERP, accounting, audit, tax, statistical, and reporting
  systems;
- the same semantics can be realised through XBRL 2.1 palette taxonomies and
  OIM-based serialisations, including xBRL-CSV;
- extensions are governed as Shared, Aligned, or Distinct so that local needs
  do not silently redefine common meanings.

The governing draft document set reviewed for this charter consists of:

1. **XBRL GL Next — Requirements Specification**
2. **XBRL GL Next Taxonomy Framework — Part 1: General rules**
3. **XBRL GL Next Taxonomy Framework — Part 2: XBRL 2.1 palette taxonomy**
4. **XBRL GL Next Taxonomy Framework — Part 3: xBRL-CSV palette taxonomy**
5. **XBRL GL Next Taxonomy Framework — Part 4: Aligned pool for extension**
6. **XBRL GL Next Taxonomy Framework — How to extend the taxonomy**

The source document set is maintained outside this WORK workspace. It is a
framework reference, not a distributable project artifact, and is not copied
into this PoC without an explicit publication and licensing decision.

The proposal defines UADC as a Universal Audit Data Converter that uses hierarchical tidy data as a common semantic representation. The target architecture separates source syntax conversion from downstream audit-view generation:

- syntax binding maps source invoice XML into a common EN 16931 / XBRL GL Next semantic layer;
- the common semantic layer preserves document-level invoice information, parties, tax subtotals, invoice lines, identifiers, dates, currencies, and monetary amounts;
- semantic binding then projects the common dataset into downstream audit views, including ISO 21378:2019 Audit data collection Sales/Purchase invoice views and AICPA ADS O2C/P2P invoice views.

This repository is the working implementation space for that proposal. The current implementation completes the planned Phase 1 and Phase 2 PoC baseline. Phase 1 provides the EN 16931 Structured CSV, xBRL-CSV taxonomy and metadata, validation, and UBL round trip. Phase 2 provides ADS XBRL GL and ADS PSV target views plus ISO 21378 ADC invoice CSV views with explicit mapping-gap classification.

ADS and ISO 21378 ADC assume a wider ERP environment in which user activity
history is captured and detailed accounting records continue into period-end
processing and annual-report preparation. An invoice alone therefore cannot
populate every audit-data field. This PoC makes that boundary explicit: it
shows which audit views can be derived from invoice data, which fields require
transformation or semantic approximation, and which fields must be supplied by
ERP ledgers, master data, workflow logs, or other operational systems.

Source and target interface files may remain organization-specific. By binding
those interfaces to the common UADC semantic structure, an organization can
separate changing application formats from the meaning, hierarchy, provenance,
and validation rules of the retained data. The PoC therefore demonstrates a
practical foundation for stable, long-term data retention that remains
traceable and usable in audits, while allowing ERP products and interface
formats to change over time.

The first PoC checkpoint is the EN 16931-1 invoice semantic model represented as an LHM/HMD-style CSV, plus binding-driven conversion from UBL Invoice XML to structured CSV, xBRL-CSV JSON metadata, and round-trip UBL Invoice XML.

OpenPeppol BIS Billing is handled as the next layer: a CIUS/profile overlay on top of EN 16931-1, with additional constraints, defaults, and syntax-specific rules.

The CII development route remains declared HOLD until its accepted input,
reverse output, and complete execution manifest can be reconstructed from
preserved evidence. No CII fixture is inferred or regenerated for this
canonical baseline.

## Clone And Setup Overview

After cloning the GitHub repository, use this sequence to prepare a local execution and development environment.

Windows PowerShell:

```
git clone https://github.com/pontsoleil/UADC-PoC.git
cd .\UADC-PoC
$python = 'python'
& $python --version
```

macOS / Linux shell:

```
git clone https://github.com/pontsoleil/UADC-PoC.git
cd ./UADC-PoC
PYTHON=python3
$PYTHON --version
```

In PowerShell, **$python = 'python'** is a variable assignment and **& $python ...** uses PowerShell's call operator to run that command. In macOS/Linux shells, use **PYTHON=python3** and run commands as **$PYTHON ...** without **&**. If Python is not on **PATH**, set the variable to the full local Python executable path instead.

If this repository is checked out inside a larger workspace, enter the PoC directory instead:

```
cd <local-clone-directory>\UADC-PoC
```

Then prepare generated local files and test artifacts:

Windows PowerShell:

```
& $python -m py_compile .\tools\binding\syntax_binding.py .\tools\binding\semantic_binding.py .\tools\binding\flat_csv.py .\tools\taxonomy\xBRLGL_TaxonomyGenerator.py
& $python .\tests\test_xbrlgl_generator_uadc_lhm.py
& $python .\tools\build_roundtrip_test_artifacts.py
& $python .\tests\test_roundtrip_artifacts.py
```

macOS / Linux shell:

```
$PYTHON -m py_compile ./tools/binding/syntax_binding.py ./tools/binding/semantic_binding.py ./tools/binding/flat_csv.py ./tools/taxonomy/xBRLGL_TaxonomyGenerator.py
$PYTHON ./tests/test_xbrlgl_generator_uadc_lhm.py
$PYTHON ./tools/build_roundtrip_test_artifacts.py
$PYTHON ./tests/test_roundtrip_artifacts.py
```

Accepted taxonomy bytes are registered under **taxonomy/**. Runtime cases and
their accepted fixtures are described by **tests/runtime/** manifests; generated
scratch output is not part of the canonical publication tree.

For environment setup, tests, and the end-to-end learning flow, see
**docs/01_ENVIRONMENT_TESTS_TUTORIAL.md**. The Structured CSV and LHM contract
is in **docs/02_STRUCTURED_CSV_LHM_BINDINGS.md**. Phase 1 UBL, Phase 2 ADS PSV,
and Phase 2 ADS XBRL GL conversion details are in documents 03 through 05.

## Figure 1

![Figure 1 - UADC PoC processing flow](references/figures/uadc_poc_processing_flow_figure1.png)

Figure 1 from the proposal shows the intended UADC processing flow. Phase 1 covers the source-to-semantic path from OpenPeppol/UBL Invoice XML to EN 16931 hierarchical tidy data, structured CSV, JSON metadata, taxonomy validation, and round-trip XML. Phase 2 extends the same semantic layer toward ISO 21378 and AICPA ADS target views through semantic binding.

## UADC Processing Steps

The phases below describe the UADC processing model, not project management milestones.

| Phase | Processing Step | Main Inputs And Outputs | Current Status |
| --- | --- | --- | --- |
| Phase 1 | Create a generic Structured CSV from source invoice syntaxes. | Input starts with Peppol UBL Invoice XML. The source syntax binding maps invoice facts into the common EN 16931 / UADC hierarchical Structured CSV. The same phase writes xBRL-CSV metadata JSON and validates the generic representation against the generated xBRL-CSV taxonomy. | **Complete for the PoC baseline.** Peppol UBL input, Structured CSV generation, metadata JSON generation, taxonomy and metadata validation, and UBL round-trip schema checks are functioning. |
| Phase 2 | Convert the generic Structured CSV into purpose-specific common formats. | The current targets are six ADS XBRL GL views, six ADS PSV views, and ISO 21378:2019 ADC Tables 38, 39, 53, and 54 CSV views. | **Complete for the planned PoC scope.** Target bindings, generation, regression tests, and documented ISO mapping gaps are in place. |
| Phase 3 | Expand supported input syntaxes and interoperability tests. | Add UN/CEFACT Invoice and XBRL GL invoice examples as additional source inputs, alongside Peppol UBL. Add corresponding output conversions to Peppol Invoice, UN/CEFACT Invoice, and XBRL GL invoice. | **HOLD for the canonical publication baseline.** CII development evidence exists, but forward/reverse publication acceptance requires a complete preserved execution set; CII reverse conversion and EN 16931 Schematron validation remain future work. |

Phase 1 intentionally focuses on the neutral intermediate representation: a generic, hierarchical Structured CSV that can be validated and round-tripped. Phase 2 uses that common representation as the source for multiple downstream formats. This separation is the core UADC idea: source syntax conversion is kept separate from target-format projection.

## Processing Flow

```
Phase 1 source syntax conversion
  Peppol UBL Invoice XML
  future: UN/CEFACT Invoice, XBRL GL invoice
    -> syntax binding
    -> generic EN 16931 / UADC Structured CSV
    -> xBRL-CSV metadata JSON
    -> taxonomy and metadata validation
    -> round-trip validation back to source syntax where supported

Phase 2 target-format projection
  generic EN 16931 / UADC Structured CSV
    -> ADS XBRL GL syntax binding
       -> Invoices Received/Generated and Lines
       -> Supplier Listing and Customer Master
    -> ADS semantic binding
       -> ADS O2C/P2P PSV views
    -> ISO 21378 semantic binding
       -> ADC Tables 38, 39, 53, and 54 CSV views

Future additional target projections
    -> Peppol Invoice
    -> UN/CEFACT Invoice
    -> other XBRL GL invoice profiles

Later interoperability tests
  -> XBRL GL invoice examples and profiles
  -> Finland and Estonia XBRL GL discussion targets
```

## Directory Layout

- **bindings/** - Syntax, semantic, structured-CSV, PCA, and EPSON binding and mapping definitions.
- **models/** - EN CIUS invoice, GL business-transactions, GL accounting-entries, and related HMD/model inputs.
- **instances/** - Accepted `original/`, `derived/`, and `roundtrip/` fixtures and outputs.
- **tests/** - Registered runtime cases, successor `RUN_PARAMETERS.json` files, and focused regression programs.
- **tools/binding/** - Syntax, semantic, flat-CSV, Tuple, and supporting conversion programs.
- **tools/taxonomy/** - Taxonomy generation programs, templates, datatype bindings, and generator documentation.
- **taxonomy/** - Accepted XBRL Japan namespace taxonomy families for Business Transactions and Accounting Entries.
- **definitions/** - Shared definitions used by model and taxonomy tooling.
- **Specifications/** - Maintained public specifications plus `technical/` implementation definitions.
- **docs/** - Maintained implementation and governance documentation. Start with **docs/README.md**.
- **references/** - Reproducible reference notes, provenance, and project figures; large licensed source material is not copied here.
- [**XBRL_GL_Next_UADC_PoC.pdf**](XBRL_GL_Next_UADC_PoC.pdf) - Project overview document for the UADC PoC
  and its relationship to XBRL GL Next.

The taxonomy generator is included at **tools/taxonomy/xBRLGL_TaxonomyGenerator.py**.
Published XBRL GL Next entry points are registered as accepted exact bytes below
**taxonomy/business-transactions/** and **taxonomy/accounting-entries/**; this
canonical reconstruction does not regenerate those families.

## Current Scope

1. Define and audit the EN 16931 invoice LHM used by the generic Structured CSV.
2. Convert Peppol UBL Invoice XML into the generic UADC Structured CSV.
3. Generate xBRL-CSV metadata that references the **en16931-oim** taxonomy entry point.
4. Validate generated xBRL-CSV metadata with Arelle.
5. Reconstruct UBL Invoice XML from Structured CSV and validate it with UBL 2.1 schemas.
6. Generate Phase 2 ADS XBRL GL target views from the Phase 1 Structured CSV. The current ADS XBRL GL outputs are written under **out/phase2/ADS_XBRL_GL/<structured-csv-stem>/** as **Invoices_Received.xbrl**, **Invoices_Generated.xbrl**, **Invoices_Received_Lines.xbrl**, **Invoices_Generated_Lines.xbrl**, **Supplier_Listing.xbrl**, and **Customer_Master.xbrl**.
7. Generate Phase 2 ADS PSV views under **out/phase2/ADS_PSV/** and ISO 21378 ADC invoice CSV views under **out/phase2/ISO21378_ADC/**.
8. Keep OpenPeppol BIS Billing as the first CIUS/profile layer on top of the EN 16931 baseline.
9. Prepare the next-phase design for additional source inputs and target profiles, including UN/CEFACT Invoice and other XBRL GL invoice examples.

## Tasks

1. Define the LHM for the generic Structured CSV. The LHM describes the EN 16931 invoice business terms as a hierarchy. It includes semantic paths, effective **lhm_level** values, and syntax binding references. The first syntax binding maps Peppol UBL Invoice XML into this neutral Structured CSV representation.

2. Define the xBRL-CSV taxonomy for the LHM. The taxonomy generator reads the LHM CSV and emits the EN 16931 module schema, **en16931-oim** entry point, **en16931-def** dimensional definition linkbase, labels, and presentation linkbase. Hypercubes, dimensions, primary items, and presentation parent-child relationships are derived from the effective LHM hierarchy. Class/BG presentation nodes use OIM primary items; BT/fact nodes use module concepts. The generated taxonomy is checked with Arelle using **out/taxonomy/plt/en16931-oim-2026-07-05.xsd** as the entry point.

3. Convert XML instances to structured CSV with JSON metadata. The syntax binding converter reads a Peppol UBL Invoice XML instance, applies the LHM XPath bindings, and writes a hierarchical Structured CSV. At the same time it writes xBRL-CSV JSON metadata that links CSV dimensions and fact columns to the generated taxonomy. The JSON metadata is validated with Arelle **loadFromOIM**.

4. Perform round trip conversion from structured CSV to XML instances. The reverse conversion reads the structured CSV and the same LHM/syntax binding definitions, reconstructs a UBL Invoice XML instance, and adds required syntax support values where needed for UBL schema validity. Absolute binding XPaths that point outside a repeated semantic context remain rooted at the UBL document; for example, BT-90 is semantically under payment instructions but is written to **AccountingSupplierParty**, not below **PaymentMeans**. The resulting XML is checked with an XML parser and UBL 2.1 schema validation.

5. Add additional source syntaxes after the Peppol UBL baseline is stable. Planned source inputs include UN/CEFACT Invoice and XBRL GL invoice examples. These should map into the same generic Structured CSV wherever the semantic model overlaps.

6. Complete the planned Phase 2 target projections from the generic Structured CSV. ADS O2C/P2P XBRL GL and PSV bindings and ISO 21378:2019 ADC Tables 38, 39, 53, and 54 CSV bindings are defined and tested. Supplier Listing places Seller postal address under the **identifierType=V** identifier reference. The ISO bindings identify direct mappings, semantic approximations, required transformations, and data absent from EN 16931. This completes Phase 2 for the PoC scope; it does not claim that EN 16931 alone supplies every ISO 21378 audit field.

The resulting artifacts are therefore checked at two levels: xBRL-CSV reports and taxonomy are verified with Arelle, while regenerated XML instances are verified with XML parsing and UBL schema validation.

## Current Tests

```
& $python .\tests\test_xbrlgl_generator_uadc_lhm.py
& $python .\tests\validate_taxonomy.py
& $python .\tests\test_bis_billing3_examples_conversion.py
& $python .\tests\test_pint_jp_examples_conversion.py
& $python .\tests\test_roundtrip_artifacts.py
& $python .\tests\test_xbrl_csv_metadata_arelle.py
& $python .\tests\test_ads_invoices_received_xbrl_gl.py
& $python .\tests\test_ads_invoices_generated_xbrl_gl.py
& $python .\tests\test_ads_invoices_received_lines_xbrl_gl.py
& $python .\tests\test_ads_invoices_generated_lines_xbrl_gl.py
& $python .\tests\test_ads_supplier_listing_xbrl_gl.py
& $python .\tests\test_ads_customer_master_xbrl_gl.py
```

The sample UBL Invoice XML and BIS Billing examples are converted using **bindings/syntax/EN16931_UBL_Invoice_Syntax_Binding.csv**. OpenPeppol CIUS checks are added after the EN 16931 conversion baseline is stable.

Semantic path elements are generated from Business Terms using **lowerCamelCaseConcatenated**, for example:

```
Invoice issue date -> invoiceIssueDate
Seller postal address -> sellerPostalAddress
```

## License

UADC-PoC separates executable logic from original meaning-bearing content:

- First-party executable program logic—including Python conversion,
  validation, generation, input/output, CLI, and test-support logic—is licensed
  under the [MIT License](LICENSE-CODE).
- Original first-party semantic content—including LHM definitions, syntax and
  semantic bindings, join and relationship tables, field mappings,
  transformation rules, semantic definitions, Structured CSV schemas, labels,
  translation dictionaries, original public samples, documentation, diagrams,
  and explanations—is licensed under
  [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), as described
  in [LICENSE-CONTENT](LICENSE-CONTENT).
- In a mixed Python or other source file, original semantic constants,
  dictionaries, lists, tables, comments, and docstrings are CC BY-SA 4.0; the
  surrounding executable logic remains MIT-licensed.

Third-party material is not relicensed. ISO standards text, reproduced EN 16931
material, AICPA ADS material, XBRL/XBRL GL, UBL and Peppol specifications or
samples, and third-party code lists remain subject to their rightsholders'
conditions. Publishing an original UADC-PoC reference ID or mapping under
CC BY-SA 4.0 does not make the referenced standard text CC BY-SA 4.0.

Generated files under `out/`, PDFs, CSV files, XML/XBRL, and other rendered
artifacts inherit the rights and restrictions of their inputs. Original public
samples must be distinguished from third-party samples and mechanically
regenerated outputs. Real data, secrets, personal data, machine-specific
configuration, and purchased standards text are outside the public license
scope and must not be published.

See [LICENSE-SCOPE.md](LICENSE-SCOPE.md) for the boundary rules and
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for third-party sources and
rights.
