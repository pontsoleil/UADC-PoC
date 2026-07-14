# Taxonomy Generator

This directory contains the local UADC-compatible taxonomy generator and the GL
generic schema template used by it.

- **xBRLGL_TaxonomyGenerator.py** reads the LHM CSV and generates module schemas,
  the EN 16931 OIM entry point, presentation and definition linkbases, metadata,
  and a CSV skeleton.
- **gen/** contains the generic datatype schema template.

The current OIM entry point is **en16931-oim-2026-07-05.xsd** and the dimensional
definition linkbase is **en16931-def-2026-07-05.xml**. See
[**Structured CSV, LHM, and Bindings**](../../docs/02_STRUCTURED_CSV_LHM_BINDINGS.md)
for the taxonomy model and generator internals.
