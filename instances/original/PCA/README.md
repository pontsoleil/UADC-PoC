# PCA Synthetic Annual Demo

This dataset is independently generated synthetic demonstration data. It is not a copy or anonymized version of sample accounting data provided by PCA Corporation. PCA Corporation has not certified, warranted, or endorsed this dataset.

## Purpose

The dataset supports UADC and LedgerExplorer interoperability demonstrations using the PCA-style 81-column physical CSV layout implemented by this project.

## Dataset profile

| Item | Value |
| --- | ---: |
| Data rows | 1,271 |
| Vouchers | 708 |
| Account coverage | 58 / 58 |
| Departments | 6 |
| Counterparties | 29 |
| Synthetic banks | 3 |
| Public-data safety | PASS |
| Synthetic independence | PASS |

The fiscal period is April 2021 through March 2022. The file contains 1:1, N:1, 1:N, and N:M journal patterns. Every voucher balances, and all names, descriptions, dates, voucher numbers, amounts, opening balances, and transaction relationships were independently generated with fixed seed `20260903`.

## Generation window and balance validation

The synthetic accounting scenario is generated over a 16-month window: two months before the published fiscal year, the 12-month fiscal period, and two months after it. The pre-period is used to derive economically consistent opening balances, including outstanding receivables and payables. The post-period is used to validate settlement of receivables, payables, accrued payables, and temporary balances remaining at fiscal year end.

Only the 12-month fiscal-year dataset from April 2021 through March 2022 is published in this directory. The two-month pre-period and two-month post-period are retained as internal generation and validation context and are not included in this CSV.

## Limitations and status

Status: validated public demonstration data in Canonical WORK. This is an interoperability fixture, not production accounting data and not a certification of compatibility with every PCA product or version. Internal test evidence is intentionally kept outside this public instance directory.
