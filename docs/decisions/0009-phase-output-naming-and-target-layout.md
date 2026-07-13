# Decision: Use Phase-Oriented Output Naming and Target View Layout

## Context

Earlier output names and directories mixed historical test names, converter
names, and project phase names. This made it difficult to explain which files
belong to Phase 1 and which files are Phase 2 target outputs.

The PoC processing flow distinguishes Phase 1 common Structured CSV generation
from Phase 2 target-view generation.

## Decision

1. Phase 1 outputs are written under **out/phase1/**.
2. Phase 1 output filenames use the input XML stem with only the extension
   changed.
3. Phase 1 metadata JSON uses the same stem and the short **.json** extension,
   not **.csv.metadata.json**.
4. Phase 2 ADS XBRL GL outputs are written under **out/phase2/ADS_XBRL_GL/**.
5. Phase 2 ADS PSV outputs are written under **out/phase2/ADS_PSV/**.
6. Phase 2 ISO 21378 ADC CSV outputs are written under **out/phase2/ISO21378_ADC/**.
7. For directory input, Phase 2 outputs are grouped by Structured CSV stem.
8. Target filenames follow the Figure 1 target view names, such as
   **Invoices_Received.xbrl**, **Invoices_Generated_Lines.xbrl**,
   **Supplier_Listing.psv**, **Customer_Master.psv**, and
   **PUR_Invoice_Received.csv**.

## Consequences

- **samples/input/openpeppol_ubl_invoice_minimal.xml** becomes
  **out/phase1/openpeppol_ubl_invoice_minimal.csv** and
  **out/phase1/openpeppol_ubl_invoice_minimal.json**.
- A Phase 2 XBRL GL output for **Allowance-example.csv** becomes
  **out/phase2/ADS_XBRL_GL/Allowance-example/Invoices_Received_Lines.xbrl**.
- ADS PSV follows the same grouping convention under **out/phase2/ADS_PSV/**.
- ISO 21378 ADC CSV follows the same grouping convention under
  **out/phase2/ISO21378_ADC/**.
- Phase 2 outputs can be compared by source Structured CSV and by target view.
- Test scripts are expected to use these names and directories.
