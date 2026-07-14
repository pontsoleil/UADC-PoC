# Operational Conversion Scripts

This directory contains the production PoC converters.

- **syntax_binding.py** performs Phase 1 UBL XML to Structured CSV conversion,
  xBRL-CSV metadata generation, and Structured CSV to UBL XML reverse conversion.
- **semantic_binding.py** performs Phase 2 Structured CSV to ADS PSV or ISO
  21378 ADC delimiter-separated conversion.
- **syntax_binding_ads_xbrl_gl.py** performs Phase 2 Structured CSV to ADS XBRL
  GL instance conversion.
- **tutorial/** contains short wrappers that call these operational programs.

Documentation:

- [**Phase 1 UBL syntax binding**](../docs/03_PHASE1_UBL_SYNTAX_BINDING.md)
- [**Phase 2 ADS PSV semantic binding**](../docs/04_PHASE2_ADS_PSV_SEMANTIC_BINDING.md)
- [**Phase 2 ADS XBRL GL syntax binding**](../docs/05_PHASE2_ADS_XBRL_GL_SYNTAX_BINDING.md)
- [**Environment, tests, and tutorial**](../docs/01_ENVIRONMENT_TESTS_TUTORIAL.md)

Programs under **tools/tutorial/** are simplified teaching implementations and
must not be confused with the operational converters in this directory.
