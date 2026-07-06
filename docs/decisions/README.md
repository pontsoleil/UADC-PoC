# Decision Records

This directory records project decisions that should survive beyond individual
chat sessions or implementation turns.

## Contents

- `0001-workspace-scope.md` - Defines the repository boundary and treats
  external XBRL-GL workspaces as references rather than runtime dependencies.
- `0002-en16931-first-openpeppol-overlay.md` - Establishes EN 16931 as the
  first conversion baseline and OpenPeppol as a later overlay.
- `0003-lhm-level-effective-hierarchy.md` - Explains `lhm_level` as the
  effective hierarchy used by structured CSV and taxonomy generation.
- `0004-xbrl-csv-only-taxonomy.md` - Limits Phase 1 taxonomy output to
  xBRL-CSV, with `plt-oim` as the taxonomy entry point and no tuple/content
  schemas.
- `0005-xbrl-csv-metadata-and-roundtrip-validation.md` - Documents the use of
  xBRL-CSV metadata JSON and schema-validated round-trip XML.
- `0006-local-taxonomy-generator.md` - Records that the UADC-compatible
  taxonomy generator is kept in this repository.
- `hierarchical_csv_binding_spec.md` - Working notes for the hierarchical CSV
  binding model.

Add a new numbered decision record when a design choice changes the data model,
taxonomy shape, validation approach, repository boundary, or future phase plan.
