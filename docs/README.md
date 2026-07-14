# UADC PoC Documentation

The documentation has been completely reorganized into five purpose-oriented documents. The former files **SETUP.md**, **TUTORIAL.md**, **DATA_MODEL.md**, **SYNTAX_BINDING.md**, and **SEMANTIC_BINDING.md** have been replaced by the documents below.

| No. | Document | Scope | Main program |
| ---: | --- | --- | --- |
| 1 | [Environment Setup, Tests, Maintenance, and Tutorial](01_ENVIRONMENT_TESTS_TUTORIAL.md) | Environment setup, definition files, regression tests, maintenance, and an end-to-end exercise | All programs |
| 2 | [Structured CSV, LHM, Syntax Binding, and Semantic Binding](02_STRUCTURED_CSV_LHM_BINDINGS.md) | Structured CSV as a 21st-century normalized table; LHM; XPath/selector syntax binding; **semantic_path**, selectors, **[n]**, and CSV-column semantic binding | **tools/** and binding tables |
| 3 | [Phase 1 UBL Syntax Binding](03_PHASE1_UBL_SYNTAX_BINDING.md) | Environment contract, conversion operations, and function-level processing of **syntax_binding.py** | **src/syntax_binding.py** |
| 4 | [Phase 2 ADS PSV Semantic Binding](04_PHASE2_ADS_PSV_SEMANTIC_BINDING.md) | Environment contract, conversion operations, and function-level processing of **semantic_binding.py**; ISO 21378 ADC CSV is also covered | **src/semantic_binding.py** |
| 5 | [Phase 2 ADS XBRL GL Syntax Binding](05_PHASE2_ADS_XBRL_GL_SYNTAX_BINDING.md) | Environment contract, conversion operations, binding-table interpretation, XPath/selector processing, and function-level processing | **src/syntax_binding_ads_xbrl_gl.py** |

## Recommended Reading Order

1. Start with Document 1 to configure and run the PoC.
2. Read Document 2 to understand the common data and binding model.
3. Use Documents 3–5 for implementation details of each conversion path.

The Japanese documentation under [**ja/**](ja/) uses exactly the same file structure and document boundaries.
