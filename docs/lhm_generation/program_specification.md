# Program Specification: LHM Generation

## 1. Purpose

This document specifies the programs used to generate and validate the EN 16931 invoice Logical Hierarchical Model (LHM) CSV for the UADC Proof of Concept.

All paths in this document are relative to the **UADC_PoC** working directory after the repository is pushed or cloned.

## 2. Scope

The current baseline is the EN 16931-1 invoice semantic model. OpenPeppol BIS Billing is handled later as a CIUS/profile overlay.

Controlled source:

```
specs/lhm/source/EN16931_CIUS_Invoice_LHM_Source.csv
```

Generated LHM:

```
specs/lhm/EN16931_CIUS_Invoice_LHM.csv
```

## 3. Components

### 3.1 Source-to-LHM builder

Program:

```
tools/build_lhm_from_source.py
```

Responsibilities:

- create an editable source CSV from an existing LHM CSV with **init-source**;
- generate the normalized LHM CSV from the editable source CSV with **build**;
- derive lowerCamelCaseConcatenated semantic path segments from Business Term values;
- derive **class_term** from the nearest parent BG Business Term, singularized;
- derive **lhm_level** for Structured CSV and xBRL-CSV taxonomy modeling;
- generate unique UpperCamelCase **element** values when no override is provided;
- preserve manual override columns.

### 3.2 Class and element normalizer

Program:

```
tools/normalize_lhm_class_element.py
```

Responsibilities:

- normalize **class_term**;
- normalize **element**;
- ensure generated element values are unique.

Rules:

- BG rows use their own Business Term as **class_term**, singularized.
- BT rows use the nearest parent BG Business Term as **class_term**, singularized.
- **element** is generated from **semantic_path**.
- **element** starts with an uppercase letter.
- If final semantic path segments duplicate, the shortest unique semantic path suffix is used.

### 3.3 Class and element checker

Program:

```
tools/check_lhm_class_element.py
```

Responsibilities:

- report **class_term** mismatches;
- report **element** mismatches;
- return a non-zero exit code when mismatches are found.

### 3.4 PDF definition updater

Program:

```
tools/update_lhm_definitions_from_pdf.py
```

Responsibilities:

- extract EN 16931-1 Table 2 Description cells with **pdfplumber**;
- update the LHM **definition** column for extracted BT/BG identifiers;
- apply built-in overrides for rows where PDF extraction is known to split cells;
- report unresolved empty definitions.

This utility updates the specified LHM CSV.

### 3.5 UBL syntax sequence updater

Program:

```
tools/update_lhm_syntax_sequence_from_ubl_xsd.py
```

Responsibilities:

- read extracted OASIS UBL 2.1 XSD files;
- resolve each LHM XPath against the UBL Invoice schema sequence;
- write **syntax_sequence** values that can be used for XML-order checks;
- keep the downloaded UBL schema package outside version control, normally under **out/cache**.

## 4. Editable Source CSV

Fields:

```
sequence
syntax_sequence
id
level
type
cardinality
business_term
description
usage_note
req_id
semantic_data_type
path
xpath
semantic_path_override
class_term_override
element_override
label_local
definition_local
source_ref
adjustment_note
```

Important fields:

- **sequence**: EN 16931-1 Table 2 order.
- **syntax_sequence**: UBL Invoice XML schema order, when populated from OASIS UBL 2.1 XSD.
- **id**: EN 16931 identifier such as **BG-4** or **BT-27**.
- **level**: hierarchy level. Invoice is level **0**; **BT-1** is level **1**.
- **cardinality**: source cardinality. Values ending in **..n** are normalized to **..***.
- **business_term**: EN 16931 Business Term.
- **description**: EN 16931 Description. This becomes the LHM **definition**.
- **path**: slash-separated identifier path used to locate the parent BG.
- **xpath**: syntax binding reference path for UBL Invoice where available.
- **semantic_path_override**: optional full semantic path override.
- **class_term_override**: optional class term override.
- **element_override**: optional element name override.

## 5. Generated LHM CSV

Fields:

```
sequence
syntax_sequence
level
lhm_level
type
identifier
name
datatype
multiplicity
domain_name
definition
module
class_term
id
path
semantic_path
label_local
definition_local
element
xpath
```

Mapping rules:

- **level** preserves the EN 16931/LHM logical hierarchy.
- **lhm_level** is the effective hierarchy used by Structured CSV and xBRL-CSV taxonomy generation.
- **BG-ROOT** has **lhm_level=0**.
- A BG with multiplicity **0..*** or **1..*** has **lhm_level** equal to the nearest ancestor BG with an **lhm_level** plus **1**.
- A BG with multiplicity **0..1** or **1..1** has blank **lhm_level**, except **BG-ROOT**.
- A BT has **lhm_level** equal to the nearest ancestor BG with an **lhm_level** plus **1**.
- Blank **lhm_level** BG rows are retained in the semantic model but are not emitted as Structured CSV dimensions or xBRL-CSV dimension concepts.

- **name** is copied from **business_term**.
- **syntax_sequence** is copied from the source CSV or populated by the UBL syntax sequence updater.
- **datatype** is copied from **semantic_data_type**.
- **multiplicity** is copied from **cardinality**.
- **definition** is copied from **description**.
- **module** is currently **en16931**.
- **semantic_path** is either **semantic_path_override** or a generated path.
- **element** is either **element_override** or a generated unique UpperCamelCase name.

Semantic path rules:

- Business Terms are converted to lowerCamelCaseConcatenated path segments.
- The semantic path starts at **$.invoice**.
- **BG-0** is not generated because EN 16931-1 does not define it.

Multiplicity rules:

- LHM **multiplicity** must be one of **0..1**, **0..***, **1..1**, or **1..***.
- Source cardinalities **0..n** and **1..n** are normalized to **0..*** and **1..***.
- Other multiplicity values are rejected during LHM generation.

Element name uniqueness rules:

1. Split **semantic_path** into path segments after removing the leading **$.**.
2. Use the final segment as the first candidate.
3. Convert the candidate segment or suffix to UpperCamelCase.
4. If that name is unique, use it as **element**.
5. If it duplicates another row, expand the candidate one segment to the left and try again.
6. Continue until the shortest unique semantic path suffix is found.
7. If no suffix is unique, append the row identifier without hyphens as a final fallback.

Example:

```
$.invoice.precedingInvoiceReference.precedingInvoiceReference
```

The final segment alone would produce **PrecedingInvoiceReference**, which also belongs to the BG row. The generator therefore expands the suffix and produces:

```
PrecedingInvoiceReferencePrecedingInvoiceReference
```

Example:

```
BT-1 Invoice number
semantic_path = $.invoice.invoiceNumber
class_term = Invoice
element = InvoiceNumber
level = 1
```

## 6. Validation Rules

The LHM checks verify that:

- semantic paths use lowerCamelCaseConcatenated path segments;
- **BG-0** is not present;
- **BG-ROOT** represents Invoice at level **0**;
- **BT-1** is **$.invoice.invoiceNumber** at level **1**;
- LHM element names are unique;
- multiplicity values are limited to **0..1**, **0..***, **1..1**, and **1..***;
- BG dimension columns are left aligned in hierarchical CSV output;
- non-repeating BGs such as Seller and Buyer are not emitted as dimension columns;
- repeating BGs such as Invoice Line are emitted as dimension columns.

## 7. Dependencies

Required:

- Python 3.10 or later.

Optional:

- **pdfplumber**, only for **tools/update_lhm_definitions_from_pdf.py**.

## 8. Non-Goals

The LHM generation programs do not:

- publish generated **out/** files to GitHub;
- fully model OpenPeppol BIS Billing profile constraints;
- validate XBRL taxonomy output.
