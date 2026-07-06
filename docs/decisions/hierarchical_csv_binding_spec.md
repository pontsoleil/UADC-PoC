# Hierarchical CSV Binding Spec

This PoC uses a dimension-based hierarchical CSV for syntax-binding output.

## Column Groups

Columns are split into two groups.

1. BG/class dimensions
   - Defined from LHM `type=C` rows.
   - Column name is `d` + upper camel case of the LHM `element` value.
   - These columns are left aligned at the beginning of the CSV.
   - `Invoice` is represented by `dInvoice`.
   - BGs with `0..1` or `1..1` multiplicity do not define dimension columns.
   - Repeating BGs such as `Invoice line` define dimension columns.

2. BT/fact values
   - Defined from LHM `type=A` rows.
   - Column name is the LHM `element` value.
   - These columns follow all BG dimension columns.

## Row Rules

Each output row represents one BG occurrence or the invoice root.

- The invoice root row has `dInvoice=1` and root-level BT values.
- A repeating BG row has `dInvoice=1` plus its own dimension value.
- A `0..1` or `1..1` BG does not create a separate dimension row; its BT values are written to the nearest repeating ancestor row, or to the `dInvoice=1` row when there is no repeating ancestor.
  - Seller and buyer postal address values are written to the `dInvoice=1` row.
  - The first line extension amount row has `dInvoice=1`, `dInvoiceLine=1`, and `invoiceLineNetAmount=1230`.
  - The second line extension amount row has `dInvoice=1`, `dInvoiceLine=2`, and `invoiceLineNetAmount=560`.
- Repeated BGs increment their own dimension value in XML occurrence order.
- BT values are written to the row for their owning BG.

## Binding Rules

The syntax binding CSV provides `semantic_path` and `xpath`.

- For LHM semantic paths, the parent semantic path identifies the owning BG.
- The owning BG is resolved through the LHM `type=C` rows.
- The XML context for a BG is the LHM class `xpath`.
- `const:` binding rows are fixed XML generation values and are ignored for XML-to-CSV output.
- If a BT is not defined in the binding, its CSV column is kept empty.

## Japan_core Compatibility Notes

The rule follows the Japan_core Java/Python conversion line:

- `Invoice2csv.java` builds `multipleMap` only for repeating model groups that are used in the XML.
- `boughMap` carries occurrence indexes for those repeating groups.
- `Python/csv2tidy.py` keeps dimension line counters only for dimension columns and resets lower-level counters when a parent repeat changes.
- `Python/xml2tidy.py` writes only used fields. The PoC converter keeps LHM columns by default, and offers `--drop-empty-columns` for this compatibility mode.

## Package Template Compatibility

The older package sample can still be checked with `--template-csv`.

In template mode, the template CSV fixes column order and gives placement hints for fields such as payment fields. In LHM mode, `--lhm-csv` is authoritative and should be used for EN 16931 CIUS PoC work.
