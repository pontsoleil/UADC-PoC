# cor / Accounting Entries — PCA GL Journal Entry package

This folder contains the PCA GL example interpreted as an XBRL GL Next `cor` / `Accounting Entries` Journal Entry, with its semantic-path binding and the extracted JP Journal Entry HMD subtree.

## Part 1 naming rule

The canonical key is `semantic_path`. It begins with `$.` and joins lowerCamelCase hierarchy elements with dots, for example:

`$.cor_AccountingEntries.cor_EntryHeader.cor_EntryDetail[cor_DebitCreditIndicator="D"].cor_MonetaryAmount`

The previous label-style path and abbreviated path are compatibility references only. New bindings and selectors use the canonical `semantic_path`. The HMD in this package contains only the JP07a Journal Entry subtree; unrelated JP HMD roots are not presented as Accounting Entries.

## Included files

See `cor_Accounting_Entries_Journal_Entry_manifest.csv`. The two principal review tables are `cor_Accounting_Entries_Journal_Entry_HMD_semantic_path_Part1_revised.xlsx` and `cor_Accounting_Entries_PCA_GL_flat_csv_semantic_path_binding_Part1_revised.xlsx`; CSV companions support machine processing.

## Data boundary

The package does not include PCA accounting input/output, LedgerExplorer outputs, master data, credentials, purchased standards text, or the legacy example-value column. Parameter files retain references to private workspace paths but do not copy those files.

## Mapping status

Unmapped physical PCA fields remain explicitly marked `unmapped`. They must not receive guessed semantic paths. `__source_row__` is a declared profile coordinate used to distinguish journal-line occurrences where the legacy flat CSV has no physical line identifier.
