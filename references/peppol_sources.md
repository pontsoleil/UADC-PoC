# OpenPeppol Sources

Checked source pages:

- Peppol BIS Billing 3.0 upcoming:
  https://docs.peppol.eu/poacc/billing/3.0/upcoming/
- UBL Invoice syntax tree:
  https://docs.peppol.eu/poacc/billing/3.0/upcoming/syntax/ubl-invoice/tree/
- EN 16931 model bound to UBL rules:
  https://docs.peppol.eu/poacc/billing/3.0/upcoming/rules/ubl-tc434/

The upcoming page identifies the May 2026 Release and separates syntax
documentation for UBL Invoice from rules for the EN 16931 model bound to UBL.

The PoC LHM in `../specs/lhm/EN16931_CIUS_Invoice_LHM.csv` follows the
LHM/HMD-style columns used in `../../XBRL-GL-2026`, adding OpenPeppol UBL XPath
bindings where the syntax location is straightforward.

## EN 16931 Sources

Local EN 16931 references used for the base semantic model:

- `NEN-EN_16931-1_2017+A1_2019_en.pdf`
  - Clause 6.2 defines how each information element and group is described:
    ID, level, cardinality, business term, description, usage note,
    requirement ID, and semantic data type.
  - Clause 6.3 Table 2 is the semantic data model of the core elements of an
    electronic invoice.
  - The current LHM extension includes the EN 16931 groups for document level
    allowances, document level charges, document totals, VAT breakdown, invoice
    line, invoice line period, invoice line allowances, and invoice line
    charges.

OpenPeppol BIS Billing is treated as a CIUS and syntax-binding source layered
on top of the EN 16931 semantic model, not as the primary source of the LHM.
