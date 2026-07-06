# Decision: Generate xBRL-CSV Taxonomy Only

## Context

Earlier experiments distinguished XBRL 2.1 tuple-oriented taxonomy output from
xBRL-CSV taxonomy output. The UADC PoC structured CSV is intended to be validated
as xBRL-CSV, so tuple concepts and tuple entry-point schemas add complexity
without supporting the current checkpoint.

## Decision

1. Generate the `plt-oim-<version>.xsd` xBRL-CSV taxonomy schema.
2. Generate hypercube, dimension, and primary item concepts in `plt-oim`.
3. Do not generate `en16931-content-<version>.xsd`; item declarations remain in the module schema and xBRL-CSV primary items remain in `plt-oim`.
4. Do not generate `plt-all-<version>.xsd`.
5. Do not define XBRL 2.1 tuple `complexType` structures for this PoC.
6. Reference `gl-gen` from generated module schemas as `../gen/gl-gen-<version>.xsd`.

## Consequences

- The taxonomy output matches the structured CSV validation target.
- Arelle validation focuses on the xBRL-CSV DTS entry point.
- Tuple-specific implementation and tests are removed from the current scope.
- Future tuple taxonomy work, if needed, should be handled as a separate design
  track.
