# Accounts Period Balances model

This directory publishes a project-authored model for account period balances and the Flat CSV Binding used by the public `pca-synthetic-fy2021-v1` opening-balance fixture.

The model was independently designed by the user with ISO 21378 used as a reference. It is not an ISO publication, is not an ISO-certified model, and does not include the ISO 21378 FDIS source. The names, hierarchy, consolidation choices, extensions, and profile exclusions in this model are project design decisions.

## Files

- `hmd/ISO21378_GL_ACCOUNTS_PERIOD_BALANCE_HMD.csv`: canonical 18-column HMD, model version `2021-v1`.
- `bindings/flat-csv/PCA_SYNTHETIC_OPENING_BALANCES_FLAT_CSV_BINDING.csv`: canonical 16-column Binding for the accepted public synthetic opening-balance source.
- `MODEL_MANIFEST.csv`: file-level hashes, roles, dependencies, validation, and publication status.

The accepted technical evidence records 58 input rows, 3,945 Structured CSV rows, 58 reverse rows, complete cell-level logical equality, zero ambiguous reverse mappings, and zero shared-column overwrites. That accepted test was not repeated for this publication-only relocation.
