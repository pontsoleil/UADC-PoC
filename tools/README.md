# Supporting Tools

This directory contains model maintenance and development support programs, not
the operational Phase 1 and Phase 2 converters.

The tools cover:

- EN 16931 LHM generation, normalization, ordering, coverage, and validation;
- syntax binding generation;
- round-trip artifact regeneration;
- local xBRL-CSV taxonomy generation under **taxonomy/**;
- simplified converter implementations under **tutorial/**;
- Japanese Markdown regeneration with **translate_markdown_ja.py** and
  **docs/ja/TERMINOLOGY.csv**;
- local ADS PSV and CSV inspection with **psv_viewer.html**.

The full list of 15 programs, their arguments, functions, side effects,
dependencies, and validation rules is in
[**docs/DATA_MODEL.md**](../docs/DATA_MODEL.md). Environment and test commands
are in [**docs/SETUP.md**](../docs/SETUP.md).

After editing Japanese terminology in Excel, run
**tools/translate_markdown_ja.py** from the repository root. Detailed setup,
regeneration, and validation commands are in Chapter 10.1 of
[**docs/SETUP.md**](../docs/SETUP.md).
