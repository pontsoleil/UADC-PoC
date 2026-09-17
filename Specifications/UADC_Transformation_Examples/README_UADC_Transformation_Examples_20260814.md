# UADC transformation examples

The examples are organized by business document semantics:

1. **Invoice** — XBRL GL Next `btx` / **Business Transactions**. OpenPeppol UBL input, EN 16931 HMD, syntax binding, and expected UADC Structured CSV. Module-qualified example root: `$.btx_BusinessTransactions.btx_Invoice`.
2. **Journal Entry** — XBRL GL Next `cor` / **Accounting Entries**. PCA accounting flat CSV interpreted as entry-header and selected entry-detail semantics, Accounting Entries HMD extract, semantic-path binding, and LedgerExplorer-related configuration. Root: `$.cor_AccountingEntries.cor_EntryHeader`.

PCA accounting does not contain an Invoice document. It is therefore not placed under `btx` / Business Transactions and is not mapped to the Invoice profile. Private PCA instance data, master data, and generated accounting outputs are excluded.
