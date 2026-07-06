# Decision: Keep the Taxonomy Generator in This Repository

## Context

Taxonomy generation tests previously depended on a sibling checkout of
`XBRL-GL-2026`. That made the PoC harder to reproduce after moving the active
GitHub synchronization target to `UADC_GIT` / `UADC-PoC`.

## Decision

1. Keep the UADC-compatible taxonomy generator at
   `tools/taxonomy/xBRLGL_TaxonomyGenerator.py`.
2. Keep the required `gl-gen` template at
   `tools/taxonomy/gen/gl-gen-2026-MM-DD.xsd`.
3. Update tests and documentation to use the local generator.
4. Treat `../XBRL-GL-2026` as a historical/reference workspace only, not a
   runtime dependency for normal PoC tests.
5. Mirror the same layout into the old `UADA/UADC_PoC` work area only for
   local synchronization checks. GitHub push target remains `UADC_GIT`.

## Consequences

- `tests/test_xbrlgl_generator_uadc_lhm.py` can run from a fresh clone without a
  sibling `XBRL-GL-2026` checkout.
- The repository carries the generator code needed for the PoC checkpoint.
- Generated taxonomy output under `out/` remains ignored and is not committed.
- Future changes to taxonomy generation should be made in the local generator
  first and then mirrored to any old working copies only when needed.
