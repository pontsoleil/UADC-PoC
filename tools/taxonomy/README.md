# Taxonomy Tools

This directory contains the local taxonomy generator used by the UADC PoC.

## Files and Subdirectories

- `xBRLGL_TaxonomyGenerator.py` - UADC-compatible taxonomy generator adapted
  for the repository's LHM CSV layout and xBRL-CSV-only Phase 1 output.
- `gen/` - GL generic schema template used by generated module schemas.

## Output

The generator writes taxonomy output under `out/taxonomy/`, including:

- `en16931/en16931-<version>.xsd`
- `en16931/*-presentation.xml`
- `en16931/lang/*-label*.xml`
- `gen/gl-gen-<version>.xsd`
- `plt/plt-oim-<version>.xsd`
- `plt/plt-def-<version>.xml`

The generator does not create XBRL 2.1 tuple/content entry points for Phase 1.
