# Operational Workflow Tutorial Wrappers

These numbered scripts provide a short end-to-end learning sequence while
calling the operational converters under **src/**.

| Script | Result |
|---|---|
| **00_check_environment.py** | Checks required scripts, definitions, samples, and taxonomy status. |
| **01_convert_sample_to_structured_csv.py** | Creates tutorial Structured CSV and metadata JSON. |
| **02_roundtrip_structured_csv_to_xml.py** | Regenerates a UBL Invoice from tutorial CSV. |
| **03_generate_ads_xbrl_gl.py** | Creates an ADS Invoices Received XBRL GL view. |

Run them from the repository root. See [**docs/TUTORIAL.md**](../../docs/TUTORIAL.md) for commands,
expected files, internal flow, and verification points.
