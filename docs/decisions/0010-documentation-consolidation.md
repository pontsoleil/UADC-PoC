# Decision: Consolidate Script Processing Documentation Under docs

## Context

The project documentation is maintained under **docs/**. The documentation describes the current specification directly: how binding rows, XPath, Semantic Path, Structured CSV dimensions, and converter functions work together.

## Decision

1. Keep operational command summaries in **docs/development/README.md** and **docs/testing/README.md**.
2. Keep binding-table authoring instructions in **docs/bindings/README.md**.
3. Keep implementation-level script processing details in **docs/README_SCRIPT_PROCESSING.md**.
4. Use **docs/README_SCRIPT_PROCESSING.md** as the primary explanation for:
   XPath context processing, Semantic Path interpretation, **dInvoice** and
   **dInvoiceLine** dimension assignment, internal dictionaries and lists, and
   function-level conversion flow.
5. Keep **docs/syntax_binding_conversion/** as the syntax-binding program
   specification and operating guide, but point readers to the consolidated
   processing guide for implementation-level details.
6. Use **docs/**, not **doc/**, as the documentation directory.

## Consequences

- Script internals are documented in **docs/README_SCRIPT_PROCESSING.md**.
- Subdirectory documents focus on their subject areas.
- Behavior changes update **docs/** together with the corresponding scripts and CSV definitions.
