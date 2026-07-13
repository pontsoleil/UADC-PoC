# Taxonomy Generation Documentation

This directory documents how the xBRL-CSV taxonomy is generated from the LHM.

## Files

- **program_specification.md** - Defines the taxonomy generator inputs, output files, xBRL-CSV restrictions, dimensional relationships, and validation rules.
- **user_guide.md** - Gives command examples for generating and checking the taxonomy with local tests and Arelle.

## Related Directories

- **../../tools/taxonomy/** - Local UADC-compatible taxonomy generator and GL generic schema template.
- **../../specs/lhm/** - LHM CSV used as the taxonomy source.
- **../../out/taxonomy/** - Generated taxonomy output tracked by Git as PoC validation evidence.

Phase 1 generates **en16931-oim-<version>.xsd** as the xBRL-CSV taxonomy entry point and **en16931-def-<version>.xml** as its dimensional definition linkbase. The entry point references the EN 16931 presentation linkbase so the LHM hierarchy is visible to taxonomy processors. It does not generate **plt-all-<version>.xsd** or **<module>-content-<version>.xsd** tuple/content schemas.
