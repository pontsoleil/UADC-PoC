# Decision: EN 16931 First, OpenPeppol Overlay Second

## Context

The PoC needs to confirm that an LHM/HMD-style semantic model and binding-driven
conversion can represent the EN 16931-1 invoice model before adding profile
specific behavior.

OpenPeppol BIS Billing is not just a syntax sample. It is a CIUS/profile layer
over EN 16931 and can define additional constraints, default values, and
syntax-specific requirements.

## Decision

1. Keep the first checkpoint focused on EN 16931-1 LHM coverage and conversion.
2. Use UBL Invoice XML as a test input syntax for that checkpoint.
3. Treat OpenPeppol BIS Billing as a later overlay that adds CIUS/profile
   constraints and OpenPeppol-specific binding checks.

## Consequences

- `specs/lhm/EN16931_CIUS_Invoice_LHM.csv` is audited against EN 16931-1 BG/BT
  identifiers.
- `specs/bindings/syntax/EN16931_UBL_Invoice_Syntax_Binding.csv` is the current
  conversion baseline.
- OpenPeppol-specific constraints should be documented and tested separately
  after the EN 16931 baseline is stable.
