# Repository Files Guide

This guide explains the repository sample files, expected files, references, and figure assets.

## Samples

Committed sample files are under:

```
samples/
```

Subdirectories:

- **input/**: source XML samples used by conversion tests.
- **expected/**: stable expected outputs used by focused regression checks.

Important input files:

- **samples/input/openpeppol_ubl_invoice_minimal.xml**: minimal UBL Invoice sample used for the baseline OpenPeppol and EN 16931 conversion check.
- **samples/input/bis-billing3-examples/**: selected BIS Billing 3 invoice examples used to test broader syntax binding coverage.

BIS Billing 3 examples exercise allowances, VAT categories, negative correction invoices, sales order references, and tax accounting currency handling.

Generated Structured CSV, metadata JSON, and regenerated XML are kept in **tests/roundtrip/** or **out/**, not under **samples/**.

## References

Lightweight reference material is under:

```
references/
```

Files and subdirectories:

- **peppol_sources.md**: notes and links for OpenPeppol and BIS Billing source material.
- **figures/**: images extracted or prepared from proposal material for Markdown documentation.

Checked source pages:

- Peppol BIS Billing 3.0 upcoming: https://docs.peppol.eu/poacc/billing/3.0/upcoming/
- UBL Invoice syntax tree: https://docs.peppol.eu/poacc/billing/3.0/upcoming/syntax/ubl-invoice/tree/
- EN 16931 model bound to UBL rules: https://docs.peppol.eu/poacc/billing/3.0/upcoming/rules/ubl-tc434/

The upcoming page identifies the May 2026 Release and separates syntax documentation for UBL Invoice from rules for the EN 16931 model bound to UBL.

Local EN 16931 references used for the base semantic model include **NEN-EN_16931-1_2017+A1_2019_en.pdf**. Clause 6.2 defines how each information element and group is described. Clause 6.3 Table 2 is the semantic data model of the core elements of an electronic invoice.

The current LHM extension includes EN 16931 groups for document-level allowances, document-level charges, document totals, VAT breakdown, invoice line, invoice line period, invoice line allowances, and invoice line charges.

OpenPeppol BIS Billing is treated as a CIUS and syntax-binding source layered on top of the EN 16931 semantic model, not as the primary source of the LHM.

## Figures

Figure assets are under:

```
references/figures/
```

Important file:

- **uadc_poc_processing_flow_figure1.png**: Figure 1 from the PoC proposal, showing the two-stage UADC processing flow from OpenPeppol invoice XML to hierarchical tidy data and downstream audit views.

When adding figures, prefer stable PNG files with descriptive names. Keep intermediate render files only when they are useful for traceability.
