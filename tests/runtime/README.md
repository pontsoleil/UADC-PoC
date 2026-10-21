# Independent conversion execution definitions

## Stage A — PCA anonymous V17 to Formal OIM

The [Forward definition](pca/pca-xbrl-csv-arelle/RUN_PARAMETERS.json) records
`flat_csv.py to-structured`, the PCA input/profile, HMD, Binding, account and tax
mappings, taxonomy and runtime arguments. Its Structured CSV and JSON metadata
are one inseparable Formal OIM pair.

## Stage B — Formal OIM to EPSON45

The [Reverse definition](cross-format/pca-to-epson/RUN_PARAMETERS.json) consumes
the registered Formal OIM pair. It records `flat_csv.py to-flat` followed by
`csv_physical_adapter.py from-uadc`, with the EPSON45 profile and dependencies.
Stage B does not invoke Forward or require Stage A to be rerun. An existing
registered pair is sufficient as its data input; Stage A execution logs are not
runtime prerequisites.

## Execution and records

Paths are repository-root-relative and use `/`. A definition records existing
runtime invocations; it does not add runtime options or a `--config` interface.
Run conversion in authorised WORK locations, rather than developing or testing
inside Official GIT. Confirm input and output destinations before execution.

Generated diagnostics under `outputs/` remain private WORK execution outputs;
only their output destination may be redirected for a run. Do not publish
summary/debug reports, individual acceptance evidence or execution histories.
Formal input/output data, profiles, runtime arguments, HMD, Bindings, mappings,
taxonomy and shared dependencies remain distinct from those execution records.

The earlier conversion and round-trip cases are retired. Their original
execution definitions and histories are preserved in WORK. This does not imply
PCA-to-EPSON-to-PCA or actual EPSON application-import acceptance.
