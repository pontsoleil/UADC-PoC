# UADC PoC Canonical Baseline

This document identifies the authoring and validation baseline reconstructed on
2026-09-19. The repository root is the canonical publication tree; no nested
`canonical/`, `transformations/`, or `legacy/` tree is part of this baseline.

## Authority

- Runtime, bindings, accepted fixtures, specifications, and publication controls
  originate from GitHub-synchronized Official GIT commit
  `702f168ad2b9e3b82a1967a27f2596330554d2d3`, except where noted below.
- Business Transactions HMD authority is
  `bindings/hmd/gl-bus/business-transactions/XBRL_GL_Next_HMD_BusinessTransactions_for_taxonomy.csv`
  with SHA-256
  `14EC10D441FC98F17F17866394504281006A6D441D554389B16D3ADCA74A6974`.
- Accounting Entries HMD authority is
  `bindings/hmd/gl-cor/accounting-entries/XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv`
  with SHA-256
  `6DB8C6AAD8C2FBAEC710DDF104405D22CC13BAD0BA52038DF471F7FE5850AD81`.
- `taxonomy/accounting-entries/` contains the accepted 58-file XBRL GL Next family.
- `taxonomy/business-transactions/` contains the accepted 58-file XBRL GL Next family; its relative-path set and all file SHA-256 values exactly match upstream commit `3a3ba3506833c56ffea3a9318b71d8160da43146`.
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

## COR/BTX authority recovery status (2026-09-30)

- The accepted upstream source is XBRL GL Next Official GIT commit `3a3ba3506833c56ffea3a9318b71d8160da43146`.
- The governed COR HMD copy is `bindings/hmd/gl-cor/accounting-entries/XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv`, 401 rows × 18 columns, SHA-256 `6DB8C6AAD8C2FBAEC710DDF104405D22CC13BAD0BA52038DF471F7FE5850AD81`.
- The governed BTX HMD copy is `bindings/hmd/gl-bus/business-transactions/XBRL_GL_Next_HMD_BusinessTransactions_for_taxonomy.csv`, 439 rows × 18 columns, SHA-256 `14EC10D441FC98F17F17866394504281006A6D441D554389B16D3ADCA74A6974`.
- The 58 accepted COR taxonomy files and the 58 accepted BTX taxonomy files are byte-exact copies of that upstream commit.
- The 18 upstream-absent legacy MUC/IVC files were removed under explicit approval. `taxonomy/business-transactions/` is now an exact 58-file mirror with MUC and IVC paths/references at 0/0.
- The current accepted PCA V17/V14 Binding authority is `bindings/flat-csv/PCA_Accounting_81col_AnonymousEvaluation_V17_V14/PCA_Accounting_81col_AnonymousEvaluation_V17_V14_BINDING.csv`, SHA-256 `E8DA1565AEC40D3212BF89FEFF31C34EC09C620635B07559F01292DE36ABBD1E`. Its sequence and multiplicity metadata are synchronised with the current COR HMD; it is not a task-local candidate.
- This PCA authority reconciliation does not change the EPSON Binding or any separately recorded Account Mapping or runtime hold.
- EN CIUS → BTX remains under semantic review because 79 target paths do not resolve in the latest BTX HMD. No successor mapping was inferred.
