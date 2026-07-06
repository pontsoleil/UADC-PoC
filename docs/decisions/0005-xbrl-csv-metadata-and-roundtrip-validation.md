# Decision: Use xBRL-CSV Metadata and Schema-Validated Round Trip XML

## Context

The converter originally produced a UADC-specific JSON mapping file. That was
useful during early development, but it could not be loaded directly as an
xBRL-CSV report by Arelle. The PoC also needs proof that structured CSV can be
reconstructed into UBL Invoice XML with schema-valid syntax.

## Decision

1. Forward syntax binding conversion writes xBRL-CSV metadata JSON, not a
   UADC-specific metadata format.
2. The metadata uses `documentInfo`, `tables`, and `tableTemplates`.
3. Metadata references the generated `plt-oim` and EN 16931 taxonomy schemas.
4. Arelle `loadFromOIM` validation is a regression check for generated metadata.
5. Reverse conversion reconstructs UBL Invoice XML from structured CSV using
   LHM XPath and syntax binding rules.
6. Reverse conversion adds UBL-required support values that are not EN 16931 BT
   values when required for schema validity, such as `cac:TaxScheme/cbc:ID` and
   missing `cbc:ChargeIndicator=false` for price allowance contexts.
7. Reverse conversion normalizes supported UBL child element order before
   writing XML.
8. UBL 2.1 schema validation is a regression check for regenerated XML.

## Consequences

- Structured CSV output is tied directly to the xBRL-CSV taxonomy and can be
  loaded by Arelle.
- The PoC distinguishes semantic values from syntax-required support values.
- Round-trip XML is not expected to be byte-for-byte identical to source XML,
  but it must preserve bound values and satisfy UBL schema constraints.
- Local UBL 2.1 XSD cache remains generated or local verification data and is
  not committed.
