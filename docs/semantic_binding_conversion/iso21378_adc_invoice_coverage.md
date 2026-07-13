# ISO 21378 ADC Invoice Semantic Binding Coverage

## Scope

The Phase 2 semantic binding covers these ISO 21378:2019 Audit Data Collection invoice views:

| ADC table | Target view | Binding file |
| --- | --- | --- |
| Table 38 | SAL Invoice Generated | **ISO21378_SAL_Invoice_Generated_CSV_Binding.csv** |
| Table 39 | SAL Invoice Generated Details | **ISO21378_SAL_Invoice_Generated_Details_CSV_Binding.csv** |
| Table 53 | PUR Invoice Received | **ISO21378_PUR_Invoice_Received_CSV_Binding.csv** |
| Table 54 | PUR Invoice Received Details | **ISO21378_PUR_Invoice_Received_Details_CSV_Binding.csv** |

The bindings use the ISO 21378 flat invoice model. Repeated TAX groups are expanded to four numbered column sets. BUSINESS SEGMENT is expanded to five numbered columns.

This scope is complete for Phase 2 of the PoC. The completion criterion is a reviewed target definition, executable binding, generated CSV output for all current Phase 1 inputs, and an explicit classification for fields that cannot be copied directly. Full population of every ISO 21378 field is not a completion criterion because the EN 16931 source model does not contain ERP audit-trail and posting data.

## Mapping Coverage

| Target view | Fields | Direct | Approximate | Requires transformation | Not available | Bound path |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| PUR Invoice Received | 42 | 17 | 5 | 5 | 15 | 22 |
| PUR Invoice Received Details | 39 | 12 | 1 | 2 | 24 | 13 |
| SAL Invoice Generated | 41 | 17 | 4 | 5 | 15 | 21 |
| SAL Invoice Generated Details | 39 | 11 | 1 | 2 | 25 | 12 |

**Bound path** is the sum of direct and approximate mappings. A required transformation is not counted as bound because the current semantic binding converter only copies values and does not calculate or parse them.

## Data Sufficiency Assessment

The Phase 1 EN 16931 Structured CSV is sufficient for a useful invoice-core projection. It provides invoice identifiers, dates, parties, currency, totals, payment information, VAT breakdowns, invoice lines, quantities, prices, item identifiers, and purchase or sales order references.

It is not sufficient for a complete ISO 21378 ADC delivery. The main gaps are:

- fiscal year and accounting period, which require an accounting calendar;
- normalized payment-term components, which require parsing or dedicated source fields;
- ERP activity records for created, approved, and last modified events;
- invoice lifecycle status;
- general-ledger debit, credit, and tax posting accounts;
- gross line amounts and line tax amounts, which require calculation or allocation;
- separate basic-unit quantities and codes;
- multiple business segment values beyond the single EN 16931 accounting reference;
- multiple tax structures on one invoice line, because EN 16931 defines one VAT classification per line.

Therefore the current bindings are suitable for Phase 2 proof-of-concept generation and mapping-gap analysis, but not for claiming full ISO 21378 ADC completeness.

## Test Result

The four bindings were applied to all 10 current Phase 1 Structured CSV invoice files. The run generated 40 target files:

| Target view | Files | Total data rows | Minimum rows per file | Maximum rows per file |
| --- | ---: | ---: | ---: | ---: |
| PUR Invoice Received | 10 | 10 | 1 | 1 |
| PUR Invoice Received Details | 10 | 18 | 1 | 3 |
| SAL Invoice Generated | 10 | 10 | 1 | 1 |
| SAL Invoice Generated Details | 10 | 18 | 1 | 3 |

All non-empty semantic paths in the four bindings were also checked against **EN16931_CIUS_Invoice_LHM.csv**. Every bound path exists in the current UADC LHM.
