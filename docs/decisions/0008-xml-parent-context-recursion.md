# Decision: Use XML Parent Context Recursion for Phase 1 Forward Conversion

## Context

UADC Structured CSV represents repeated semantic classes with dimension columns such as **dInvoice** and **dInvoiceLine**. Nested repeated classes must be interpreted inside the correct parent XML context so that child dimensions belong to the right parent occurrence.

## Decision

1. Build a **BindingClass** tree from syntax binding **C** rows.
2. Process UBL XML by recursively walking that class tree.
3. For each class, evaluate direct **A** rows relative to the current XML
   context.
4. Reuse the current Structured CSV row for non-repeated child classes.
5. For repeated child classes, enumerate XML child contexts inside the current
   parent context.
6. Assign repeated dimension values as 1-based occurrence numbers inside the
   current parent context.
7. Preserve ancestor dimension values when creating nested repeated rows.

## Consequences

- **dInvoiceLine** values are assigned by invoice-line occurrence order within
  the invoice.
- Nested dimensions such as **dItemAttributes** are assigned within the current
  invoice line, not globally across the document.
- A row for a nested repeat carries its parent dimensions, such as
  **dInvoice=1**, **dInvoiceLine=2**, and **dItemAttributes=1**.
- The forward Phase 1 converter follows the same parent-child context model used by the binding table.
- Reverse conversion uses binding table paths and UBL child ordering rules to construct XML.
