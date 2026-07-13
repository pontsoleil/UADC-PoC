# Decision: Make Binding Tables the Runtime Authority

## Context

Earlier converter drafts could read the LHM CSV or use compatibility fallback
columns to resolve Structured CSV columns and repeated row scope. That made the
runtime behavior depend on more than the active binding table and made it harder
to review what a conversion would do by inspecting one CSV.

The PoC now needs binding tables that are explicit enough for operation and
review. The same principle applies to syntax binding and semantic binding:
the binding table should carry the model information needed by the converter.

## Decision

1. Do not require **--lhm-csv** for operational syntax binding or semantic
   binding conversion.
2. Treat the active binding CSV as the runtime authority for row scope,
   semantic paths, source columns, and target paths.
3. Keep **type=C** rows for semantic classes and **type=A** rows for facts or
   target fields.
4. Use **multiplicity** on **C** rows to determine whether a class is repeated.
5. In semantic binding, derive **source_column** from **semantic_path** and derive
   repeated row scope from **C** rows in the same binding table.
6. Do not keep runtime-only derived columns such as **source_column**,
   **repeat_group_path**, or **repeat_group_column** in semantic binding CSV
   files.
7. Remove unused syntax binding columns **path** and **abbreviation_path**.

## Consequences

- A reviewer can understand runtime row-scope behavior by inspecting the binding
  table alone.
- Semantic binding files now include target definition columns plus
  **semantic_path**, **type**, and **multiplicity**.
- Syntax binding files include the LHM-derived columns needed at runtime,
  including **structured_csv_level**, **structured_csv_column**, **element**,
  **xpath**, **type**, and **multiplicity**.
- The LHM remains the governance source, but operational scripts do not need to
  load it to perform normal conversion.
- Updating a binding table requires care: repeated target behavior depends on
  correct **C** rows and **multiplicity** values.
