# Hierarchical CSV Binding Spec

This PoC uses a dimension-based hierarchical CSV for syntax-binding output.

## Column Groups

Columns are split into two groups.

1. BG/class dimensions
   - Defined from LHM **type=C** rows.
   - Column name is **d** + upper camel case of the LHM **element** value.
   - These columns are left aligned at the beginning of the CSV.
   - **Invoice** is represented by **dInvoice**.
   - BGs with **0..1** or **1..1** multiplicity do not define dimension columns.
   - Repeating BGs such as **Invoice line** define dimension columns.

2. BT/fact values
   - Defined from LHM **type=A** rows.
   - Column name is the LHM **element** value.
   - These columns follow all BG dimension columns.

## Row Rules

Each output row represents one BG occurrence or the invoice root.

- The invoice root row has **dInvoice=1** and root-level BT values.
- A repeating BG row has **dInvoice=1** plus its own dimension value.
- A **0..1** or **1..1** BG does not create a separate dimension row; its BT values are written to the nearest repeating ancestor row, or to the **dInvoice=1** row when there is no repeating ancestor.
  - Seller and buyer postal address values are written to the **dInvoice=1** row.
  - The first line extension amount row has **dInvoice=1**, **dInvoiceLine=1**, and **invoiceLineNetAmount=1230**.
  - The second line extension amount row has **dInvoice=1**, **dInvoiceLine=2**, and **invoiceLineNetAmount=560**.
- Repeated BGs increment their own dimension value in XML occurrence order.
- BT values are written to the row for their owning BG.

## Binding Rules

The syntax binding CSV provides **semantic_path** and **xpath**.

- For LHM semantic paths, the parent semantic path identifies the owning BG.
- The owning BG is resolved through the LHM **type=C** rows.
- The XML context for a BG is the LHM class **xpath**.
- **const:** binding rows are fixed XML generation values and are ignored for XML-to-CSV output.
- If a BT is not defined in the binding, its CSV column is kept empty.

## Binding Table Authority

The syntax binding table is authoritative for conversion. It embeds the required model columns, class rows, fact rows, semantic paths, structured CSV column names, and XPath expressions. The converter uses the binding table row order to keep Structured CSV output deterministic.

The converter writes values that can be resolved from binding rows and source XML. Columns that are part of the binding model remain available for review even when a particular sample document has no value for them.
