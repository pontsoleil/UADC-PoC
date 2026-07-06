# Decision: Use `lhm_level` as the Effective Hierarchy

## Context

The EN 16931 table level and the LHM logical level are useful for semantic
review, but they are not always the best hierarchy for structured CSV rows or
xBRL-CSV dimensions. In particular, BGs with `0..1` or `1..1` multiplicity such
as Seller, Buyer, and their postal addresses add semantic grouping but do not
need separate dimension columns.

## Decision

1. Keep `level` as the EN 16931/LHM logical hierarchy.
2. Add and use `lhm_level` as the effective hierarchy for structured CSV and
   taxonomy generation.
3. Leave `lhm_level` blank for non-repeating BGs that should not become
   dimensions.
4. Assign BT rows to the nearest ancestor BG with an effective `lhm_level`.
5. Emit dimensions only for the invoice root and BG rows with populated
   `lhm_level`.

## Consequences

- Non-repeating BGs remain in the LHM for semantic review and XPath ownership.
- Structured CSV avoids unnecessary `dSeller`, `dBuyer`, and postal-address
  dimension columns.
- Repeating BGs such as VAT breakdown and invoice line define stable dimension
  columns and taxonomy dimensions.
- Taxonomy generation and XML conversion use the same effective hierarchy.
