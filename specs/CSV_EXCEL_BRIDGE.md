# CSV / Excel Bridge Usage

Canonical CSV is the authoritative machine-readable source. XLSX is a review
and controlled-edit exchange artefact; Excel `Save As` must not be used to
create or overwrite Canonical CSV.

Canonical CSV uses strict UTF-8 without BOM. CRLF and LF record delimiters and
embedded line breaks in quoted fields are accepted. EOL style and final-line-
break presence are informational when CSV parsing, structure, cell values, and
business semantics are preserved.

Export a Canonical CSV for review:

```text
python src/csv_excel_bridge.py export input.csv --output review.xlsx
```

Import reviewed XLSX while preserving the baseline record delimiter where
possible:

```text
python src/csv_excel_bridge.py import review.xlsx --baseline input.csv \
  --output rebuilt.csv --eol preserve
```

`--eol` accepts `preserve`, `crlf`, or `lf`. The option controls record
delimiters only. Embedded line breaks in string cells are not rewritten.

Declare date columns explicitly with `--date-columns`. Only declared date
columns may be normalized to ISO 8601 `YYYY-MM-DD`; ambiguous dates are not
guessed. Formula, numeric, Boolean, error, and undeclared date cells are
rejected rather than silently changing lexical CSV values.

The bridge never uses stale template values, formulas, or cached values as
Canonical data. It does not overwrite an existing output path by default.
