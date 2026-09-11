# pca-synthetic-fy2021-v1

Public synthetic evaluation data for fiscal year 2021-04 through 2022-03.

- April physical PCA source: `original/pca/PCA_synthetic_2021-04.csv` (112 data rows)
- Opening balances: `original/pca/PCA_SYNTHETIC_OPENING_BALANCES_2021-04-01.csv` (58 accounts, as of 2021-04-01 before April activity)
- Monthly xBRL-CSV pairs: `structured/YYYY-MM.csv` and `structured/YYYY-MM.json`
- Annual accepted sources remain in `instances/original/PCA` and `instances/derived/PCA`; they are not duplicated here.
- EPSON output is intentionally absent until an exact product, edition, version, and import-field contract are resolved.

All names and transactions are fictional.

## Required repository layout

The monthly metadata uses a relative taxonomy reference. Obtain the two repositories as sibling directories with these exact checkout names:

```text
<parent>/
  UADC-PoC/
  XBRL_GL_Next/
```

From `UADC-PoC/instances/evaluation/pca-synthetic-fy2021-v1/structured/YYYY-MM.json`, the taxonomy reference resolves to:

```text
<parent>/XBRL_GL_Next/taxonomy/accounting-entries/oim/cor_accountingEntries/cor-all-oim-2026-12-31.xsd
```

Renaming either checkout requires the consumer to update the metadata reference. No local absolute path is embedded.

The V17/V14 anonymous evaluation profile and its entity settings are internal resources and are not part of this public dataset.
