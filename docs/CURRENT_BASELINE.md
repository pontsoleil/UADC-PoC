# UADC PoC Canonical Baseline

This document identifies the authoring and validation baseline reconstructed on
2026-09-19. The repository root is the canonical publication tree; no nested
`canonical/`, `transformations/`, or `legacy/` tree is part of this baseline.

## Authority

- Runtime, bindings, accepted fixtures, specifications, and publication controls
  originate from GitHub-synchronized Official GIT commit
  `702f168ad2b9e3b82a1967a27f2596330554d2d3`, except where noted below.
- Business Transactions HMD authority is
  `models/gl-bus/business-transactions/XBRL_GL_Next_HMD_BusinessTransactions_for_taxonomy.csv`
  with SHA-256
  `6B8A5C971C569326614C96CF82FA4DE1B37CE89A500E05F8ECDE7A12F2B7F744`.
- Accounting Entries HMD authority is
  `models/gl-cor/accounting-entries/hmd/XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv`
  with SHA-256
  `9E3A47B4335C15B0EDCD7299962BC15878BE8288116927C2A7691A5B0C2CE362`.
- `taxonomy/business-transactions/` is the accepted 67-file XBRL GL Next family.
- `taxonomy/accounting-entries/` is the accepted 58-file XBRL GL Next family.
- Registered runtime cases use canonical-tree successor `RUN_PARAMETERS.json`
  files under `tests/runtime/`.

The complete relative-path and SHA-256 inventory is preserved by the canonical
build evidence `CANONICAL_FILE_MANIFEST.csv`.

## Declared holds

- CII forward/reverse conversion lacks a complete accepted exact execution set.
- Dedicated OIM-to-Tuple and Tuple-to-OIM execution manifests are not registered.
- EPSON-to-PCA remains HOLD.
- PCA explicit tax-amount preservation in EPSON remains HOLD.
- EPSON actual-application import remains HOLD.

These holds are not represented as PASS and do not change the accepted
PCA/EPSON or taxonomy baselines.
## Current anonymous_v17 fixture (2026-09-28)

The current PCA/EPSON interoperability fixture is `anonymous_v17`:

- PCA: `instances/original/PCA/anonymous_v17/PCA_anonymous_v17.csv`, SHA-256
  `03240CD380F5B23E7234B300D9523386466BD750AD48E8445CF68A8B3EEEC844`.
- Structured CSV: `instances/structured-csv/PCA/anonymous_v17/PCA_anonymous_v17.csv`, SHA-256
  `7114A070D9862003801932DDC440FE9285ECC896E7950334A0C6B9A5FEC80295`.
- xBRL-CSV metadata: `instances/structured-csv/PCA/anonymous_v17/PCA_anonymous_v17.json`, SHA-256
  `25A94236D9191E38A79D9EBB6464B3F6074BF774AA1AB6D864B3815421A12A61`.
- EPSON 45-column normalised CSV: `instances/derived/EPSON/anonymous_v17/45col/PCA_anonymous_v17_EPSON_45col.normalized.csv`, SHA-256
  `38F3EF6C3553C7DE6CAC24D6C0110C03A5871E60F8246764069706BEAB883794`.
- EPSON 45-column application CSV: `instances/derived/EPSON/anonymous_v17/45col/PCA_anonymous_v17_EPSON_45col.application.csv`, SHA-256
  `AD2A593CBDC4AFEF857C1093916B65FB2E6BD37ABBB67D05487773C03774D1C4`.

The accepted provenance is:

```text
PCA anonymous_v17
  -> Structured CSV anonymous_v17
     +-> LedgerExplorer
     +-> EPSON anonymous_v17
```

`original_basis` and `evaluation_v17_basis` remain separate historical fixture
identities. They are not renamed, replaced, or deleted by this registration.
