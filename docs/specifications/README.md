# Specification Files Guide

This guide explains the specification files under **specs/** and how those files are defined and maintained.

The **specs/** directory contains machine-readable CSV specifications used by the UADC PoC conversion pipeline. These files are inputs to scripts under **src/** and **tools/**. They should remain small, reviewable, and deterministic.

## Directory Map

```
specs/
  Currency.csv
  CountryCurrency.csv
  lhm/
  bindings/
  XBRL-GL/
```

## Currency Tables

**Currency.csv** maps ISO 4217 currency codes to minor units. It is used when XBRL GL monetary facts need a **decimals** value.

Typical columns:

```
currency_code,minor_unit,currency_name
```

Examples:

```
JPY,0,Japanese Yen
EUR,2,Euro
```

**CountryCurrency.csv** maps country examples to currency codes. It is used as reference data for country-oriented examples such as Finland and Estonia.

Examples:

```
FI,Finland,EUR,2,Euro
EE,Estonia,EUR,2,Euro
```

Runtime XBRL units still use the ISO 4217 currency code from **Currency.csv**.

## LHM Specification Files

The LHM files are under:

```
specs/lhm/
```

Important files:

- **EN16931_CIUS_Invoice_LHM.csv**: generated EN 16931 invoice LHM consumed by Structured CSV conversion and taxonomy generation.
- **source/EN16931_CIUS_Invoice_LHM_Source.csv**: editable source CSV used to regenerate or adjust the generated LHM.
- **EN16931_CIUS_Invoice.xlsx**: local reviewer workbook. It is ignored by Git and should not be updated by automation.

The LHM defines:

- semantic paths;
- class and element names;
- multiplicity;
- effective **lhm_level**;
- UBL XPath binding references;
- fields needed for Structured CSV and xBRL-CSV taxonomy generation.

### LHM Source CSV

Use **specs/lhm/source/EN16931_CIUS_Invoice_LHM_Source.csv** for individual adjustments to PDF-derived EN 16931-1 Table 2 items.

Generation flow:

```
python UADC_PoC/tools/build_lhm_from_source.py build `
  UADC_PoC/specs/lhm/source/EN16931_CIUS_Invoice_LHM_Source.csv `
  UADC_PoC/specs/lhm/EN16931_CIUS_Invoice_LHM.csv
```

Optional override columns:

- **semantic_path_override**;
- **class_term_override**;
- **element_override**.

When **element_override** is blank, the generator creates a unique UpperCamelCase element name from the semantic path. If final path segments duplicate, it uses the shortest unique semantic path suffix.

## Binding Specification Files

Binding files are under:

```
specs/bindings/
```

Binding authoring and conversion rules are documented in:

- **../syntax_binding_conversion/README.md** for syntax bindings;
- **../semantic_binding_conversion/README.md** for semantic bindings;
- **../README_SCRIPT_PROCESSING.md** for the shared row-scope and function-level processing model.

Binding files connect:

- source syntax to the UADC semantic model;
- UADC Structured CSV to downstream target syntax;
- UADC Structured CSV to flat semantic target tables.

## XBRL GL Specification Files

The XBRL GL definition table is under:

```
specs/XBRL-GL/
```

Important file:

- **xbrl-gl.csv**: XBRL GL definition table aligned with **XBRL-GL-PWD-2016-12-01/gl/plt/case-c-b-m-u-e-t-s/gl-plt-all-2016-12-01.xsd** and the imported **gl-cor**, **gl-bus**, **gl-muc**, **gl-ehm**, **gl-taf**, **gl-srcd**, and **gl-usk** modules.

The table preserves existing English and Japanese labels where available. The sequence, module names, cardinalities, type names, and parent-child order are normalized from the selected XBRL GL taxonomy profile.

The **XPath** column records the absolute tuple or fact path from **xbrli:xbrl**. It is generated from the taxonomy parent-child tree so binding tables can point directly to the target XBRL GL location without carrying internal row IDs.

## Maintenance Rules

- Keep CSV files UTF-8 or UTF-8 BOM where spreadsheet editing requires it.
- Use structured CSV writers or spreadsheet tools that preserve quoted fields, because descriptions can contain commas.
- Do not commit local reviewer workbook changes unless the workbook is explicitly part of the review deliverable.
- Regenerate derived CSV files from their source CSVs or scripts rather than editing generated files by hand when a generator exists.
- Keep runtime-derived data out of binding tables unless it is deliberately part of the binding contract.
