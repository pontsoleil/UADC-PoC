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

- [**docs/SYNTAX_BINDING.md**](../docs/SYNTAX_BINDING.md)
- [**docs/SEMANTIC_BINDING.md**](../docs/SEMANTIC_BINDING.md)
- [**docs/TUTORIAL.md**](../docs/TUTORIAL.md)

Programs under **tools/tutorial/** are simplified teaching implementations and
must not be confused with the operational converters in this directory.
