# Decision: Keep the Taxonomy Generator in This Repository

## Context

Taxonomy generation is part of the UADC PoC repository. A clean checkout of **UADC_PoC** must contain the scripts and templates needed for normal taxonomy generation and regression testing.

## Decision

1. Keep the UADC-compatible taxonomy generator at
   **tools/taxonomy/xBRLGL_TaxonomyGenerator.py**.
2. Keep the required **gl-gen** template at
   **tools/taxonomy/gen/gl-gen-2026-MM-DD.xsd**.
3. Use the local generator in tests and documentation.
4. Treat **out/taxonomy/** as generated local output.
5. Keep generated taxonomy output out of the committed source tree.

## Consequences

- **tests/test_xbrlgl_generator_uadc_lhm.py** can run from a fresh clone.
- The repository carries the generator code needed for the PoC checkpoint.
- Generated taxonomy output under **out/** remains ignored and is not committed.
- Future changes to taxonomy generation are made in **tools/taxonomy/xBRLGL_TaxonomyGenerator.py**.
