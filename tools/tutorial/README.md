# Tutorial Tool Implementations

This directory contains small, self-contained converter implementations for
learning, prototyping, and binding-table experiments.

- **syntax_binding_sample.py** demonstrates XML-to-flat-CSV extraction with a
  compact syntax binding and a limited XPath evaluator.
- **semantic_binding_sample.py** demonstrates row-for-row projection from a
  Structured CSV to a flat CSV with legacy binding-column compatibility.

These programs are not the operational UADC converters. Production Phase 1 and
Phase 2 processing uses:

```
src/syntax_binding.py
src/syntax_binding_ads_xbrl_gl.py
src/semantic_binding.py
```

The separate **src/tutorial/** directory contains beginner workflow wrappers
that call the operational converters. This **tools/tutorial/** directory instead
contains the simplified converter implementations themselves.

Detailed behavior, arguments, functions, limitations, and validation guidance
are documented in
[**Structured CSV, LHM, and Bindings**](../../docs/02_STRUCTURED_CSV_LHM_BINDINGS.md).
The operational walkthrough is in
[**Environment, Tests, and Tutorial**](../../docs/01_ENVIRONMENT_TESTS_TUTORIAL.md).
