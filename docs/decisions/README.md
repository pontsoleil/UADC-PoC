# Decision Records

This directory records project decisions that should survive beyond individual chat sessions or implementation turns.

## Contents

- **0000-hierarchical_csv_binding_spec.md** - Working notes for the hierarchical CSV binding model.
- **0001-workspace-scope.md** - Defines the repository boundary and treats external XBRL-GL workspaces as references rather than runtime dependencies.
- **0002-en16931-first-openpeppol-overlay.md** - Establishes EN 16931 as the first conversion baseline and OpenPeppol as a later overlay.
- **0003-lhm-level-effective-hierarchy.md** - Explains **lhm_level** as the effective hierarchy used by structured CSV and taxonomy generation.
- **0004-xbrl-csv-only-taxonomy.md** - Limits Phase 1 taxonomy output to xBRL-CSV, with **en16931-oim** as the taxonomy entry point and no tuple/content schemas.
- **0005-xbrl-csv-metadata-and-roundtrip-validation.md** - Documents the use of xBRL-CSV metadata JSON and schema-validated round-trip XML.
- **0006-local-taxonomy-generator.md** - Records that the UADC-compatible taxonomy generator is kept in this repository.
- **0007-binding-tables-are-runtime-authority.md** - Records that operational converters use binding tables, not runtime LHM fallback, to determine source columns and repeated row scope.
- **0008-xml-parent-context-recursion.md** - Records the Phase 1 forward conversion model that walks XML parent contexts recursively from binding **C** rows.
- **0009-phase-output-naming-and-target-layout.md** - Records Phase 1 and Phase 2 output directory and filename conventions.
- **0010-documentation-consolidation.md** - Records that current documentation
  is consolidated into five chapter-numbered guides, with short README files in
  script directories.

Add a new numbered decision record when a design choice changes the data model, taxonomy shape, validation approach, repository boundary, or future phase plan.
