# UADC End-to-End Tutorial

## Table of Contents

1. [Purpose](#1-purpose)
2. [Tutorial Flow](#2-tutorial-flow)
3. [Check the Environment](#3-check-the-environment)
4. [Generate Phase 1 Structured CSV](#4-generate-phase-1-structured-csv)
5. [Round Trip to UBL XML](#5-round-trip-to-ubl-xml)
6. [Generate a Phase 2 ADS XBRL GL View](#6-generate-a-phase-2-ads-xbrl-gl-view)
7. [Inspect the Results](#7-inspect-the-results)
8. [What Happens Internally](#8-what-happens-internally)
9. [Simplified Tutorial Implementations](#9-simplified-tutorial-implementations)
10. [Next Steps](#10-next-steps)

## 1. Purpose

This tutorial demonstrates the common UADC flow without requiring the reader to
construct long commands. The scripts under **src/tutorial/** call the same
operational converters used by the full Phase 1 and Phase 2 workflows.

Run all commands from the repository root.

## 2. Tutorial Flow

```
UBL Invoice XML
  -> Phase 1 syntax binding
  -> Structured CSV and xBRL-CSV metadata
  -> reverse syntax binding
  -> regenerated UBL Invoice XML

Structured CSV
  -> Phase 2 ADS syntax binding
  -> ADS Invoices Received XBRL GL
```

Tutorial output is written under **out/tutorial/**.

## 3. Check the Environment

Windows PowerShell:

```
$python = 'python'
& $python .\src\tutorial\00_check_environment.py
```

The script reports:

- the Python executable;
- the detected repository root;
- missing operational scripts or definitions;
- whether the generated OIM taxonomy entry point already exists.

Internally, **REQUIRED_PATHS** lists the LHM, UBL and ADS bindings, sample XML,
runtime converters, round-trip builder, and taxonomy generator. The script
returns status **1** when any required source file is missing.

## 4. Generate Phase 1 Structured CSV

```
& $python .\src\tutorial\01_convert_sample_to_structured_csv.py
```

Input:

```
samples/input/openpeppol_ubl_invoice_minimal.xml
```

Outputs:

```
out/tutorial/openpeppol_ubl_invoice_minimal.csv
out/tutorial/openpeppol_ubl_invoice_minimal.json
```

The wrapper first calls **ensure_taxonomy**. If the local taxonomy is missing,
it runs the taxonomy generator regression script. It then invokes
**src/syntax_binding.py** with the EN 16931 UBL binding, metadata output path,
and taxonomy base.

Open the CSV and observe:

- **dInvoice** on the invoice row;
- separate rows for repeated invoice lines or VAT breakdowns;
- sparse cells outside the class that owns them;
- fact columns named from the LHM element definitions.

Open the JSON and observe the OIM document type, taxonomy entry point, table
template, dimensions, concepts, and currency units.

## 5. Round Trip to UBL XML

```
& $python .\src\tutorial\02_roundtrip_structured_csv_to_xml.py
```

Output:

```
out/tutorial/openpeppol_ubl_invoice_minimal.roundtrip.xml
```

**ensure_structured_csv** runs the previous tutorial step when necessary. The
wrapper invokes **src/syntax_binding.py** with **--reverse** and the same UBL
binding.

The regenerated XML is semantic output, not a byte-for-byte copy. Namespace
placement, indentation, XML declaration, and unbound content may differ. The
important checks are bound values, hierarchy, UBL child order, and schema
validity.

## 6. Generate a Phase 2 ADS XBRL GL View

```
& $python .\src\tutorial\03_generate_ads_xbrl_gl.py
```

Output directory:

```
out/tutorial/xbrl-gl/
```

The wrapper uses:

```
src/syntax_binding_ads_xbrl_gl.py
specs/bindings/syntax/ADS_Invoices_Received_XBRL_GL_Binding.csv
specs/lhm/EN16931_CIUS_Invoice_LHM.csv
specs/Currency.csv
```

The generated instance contains XBRL contexts and units plus the XBRL GL tuple
hierarchy required by the target view.

## 7. Inspect the Results

### 7.1 Structured CSV

Use a spreadsheet editor that preserves quoted CSV cells. Confirm that a parent
invoice row and repeated child rows do not combine unrelated class facts.

### 7.2 Metadata JSON

Confirm that the taxonomy entry is:

```
out/taxonomy/plt/en16931-oim-2026-07-05.xsd
```

### 7.3 Round-trip XML

Run:

```
& $python .\tests\test_syntax_binding_reverse.py
& $python .\tests\test_roundtrip_xml_ubl_schema.py
```

### 7.4 XBRL GL

Load the generated instance in Arelle. Confirm tuple hierarchy and facts rather
than expecting a presentation view identical to tuple-oriented legacy samples.

### 7.5 PSV or CSV

For delimiter-separated Phase 2 output, use **tools/psv_viewer.html**. It reads
files locally, supports pipe, comma, and tab delimiters, filters rows, keeps
headers visible, and hides wholly empty columns.

## 8. What Happens Internally

The tutorial wrappers use **subprocess.run** with **check=True**. A child
converter failure therefore stops the wrapper immediately.

Phase 1 performs these internal steps:

1. load binding class and fact rows;
2. derive dimensions and direct class fields;
3. walk XML class contexts recursively;
4. emit the parent row and repeated child rows;
5. write metadata using the same column and dimension layout.

Reverse conversion groups rows by dimensions, rebuilds XML nodes from absolute
binding XPaths, applies predicates and attributes, then orders UBL children from
schema-derived syntax sequences.

ADS XBRL GL generation validates fact ownership, selects the source rows for the
target view, creates contexts and currency units, follows target XPaths, and
writes facts in XBRL GL schema order.

## 9. Simplified Tutorial Implementations

The programs under **tools/tutorial/** are different from the wrappers above.
They implement smaller converters for learning and binding experiments:

```
tools/tutorial/syntax_binding_sample.py
tools/tutorial/semantic_binding_sample.py
```

They do not implement the complete hierarchical row ownership, repeated scope,
metadata, reverse UBL, or Phase 2 behavior. Use them to understand a small
algorithm, not to generate PoC deliverables.

## 10. Next Steps

After completing the tutorial:

1. Read **DATA_MODEL.md** for LHM, dimensions, and Structured CSV rules.
2. Read **SYNTAX_BINDING.md** before changing Phase 1 bindings.
3. Read **SEMANTIC_BINDING.md** before generating ADS PSV, ADS XBRL GL, or ADC.
4. Use **SETUP.md** to run the relevant regression and external validations.
