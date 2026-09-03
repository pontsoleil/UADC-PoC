# PCA Synthetic Annual Demo — Structured CSV

## Transformation

| Item | Value |
| --- | --- |
| Input | `../../original/PCA/PCA_synthetic_annual_demo.csv` |
| Transformation | `tools/uadc/flat_csv.py` |
| Binding | canonical PCA 16-column Semantic Binding |
| CSV output | `PCA_synthetic_annual_demo_structured.csv` |
| Metadata output | `PCA_synthetic_annual_demo_structured.json` |

## Validation

| Item | Result |
| --- | ---: |
| Structured CSV rows | 26,339 |
| Semantic roundtrip | 0 differences |
| Binding local_name | 38 / 38 |
| Binding fallback | 0 |
| HMD unresolved | 0 |
| Arelle | 0 errors / 0 warnings |

The metadata uses the XBRL Japan XBRL GL Next experimental `cor` and `plt` namespaces dated 2026-12-31.

## Limitations and status

Status: validated derived output in Canonical WORK. This output is tied to the accompanying CSV/JSON pair and the stated taxonomy version. It is demonstration data, not production accounting data and not a PCA Corporation certification or endorsement. Internal validation logs and private references are not included in this public instance directory.
