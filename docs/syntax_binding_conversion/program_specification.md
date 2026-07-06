# Program Specification: Syntax Binding XML-to-Hierarchical-CSV Conversion

## 1. Purpose

This document specifies the syntax binding conversion program used by the UADC Proof of Concept.

The program converts an XML invoice document into a dimension-based hierarchical CSV by applying a syntax binding CSV. During forward conversion it also writes JSON metadata that relates the CSV columns to the generated taxonomy. It can also reverse a hierarchical CSV back to XML with the same binding information.

All paths in this document are relative to the `UADC_PoC` working directory after the repository is pushed or cloned, except paths beginning with `../`, which refer to sibling directories of `UADC_PoC`.

## 2. Main Program

Program:

```text
src/syntax_binding_hierarchical.py
```

Supporting XML extraction module:

```text
src/syntax_binding.py
```

The hierarchical converter imports namespace and XPath helper functions from `syntax_binding.py`.

## 3. Input Files

### 3.1 XML input

The XML input is a UBL Invoice XML document.

PoC sample:

```text
samples/input/openpeppol_ubl_invoice_minimal.xml
```

Package sample:

```text
../syntax_binding_revised_package/invoice.xml
```

### 3.2 Syntax binding CSV

The binding CSV maps semantic model paths to XML XPath expressions.

PoC binding:

```text
specs/bindings/syntax/EN16931_UBL_Invoice_Syntax_Binding.csv
```

Package binding:

```text
../syntax_binding_revised_package/bindings.csv
```

Required binding columns:

```text
semantic_path
xpath
```

The parser also accepts compatible column names:

```text
path
source_xpath
xml_path
```

Rows without both semantic path and XPath are ignored.

### 3.3 LHM CSV

When `--lhm-csv` is supplied, the converter uses the LHM to define:

- output column order;
- BG dimension columns;
- BT value columns;
- mapping from semantic paths to final LHM `element` names;
- repeating BGs based on `multiplicity`;
- repeat context XPath for BG rows where available.

PoC LHM:

```text
specs/lhm/EN16931_CIUS_Invoice_LHM.csv
```

### 3.4 Template CSV

When `--template-csv` is supplied, the converter uses its header as the output column order and infers some field-to-dimension placement from non-empty template rows.

Package template:

```text
../syntax_binding_revised_package/invoice.csv
```

If both `--lhm-csv` and `--template-csv` are supplied, the LHM layout controls the main field order and the template may still provide field placement hints.

## 4. Forward Output

The output is a UTF-8-SIG CSV file.

PoC output:

```text
out/hierarchical/en16931_lhm_hierarchical.csv
```

Package output:

```text
out/hierarchical/package_invoice_hierarchical.csv
```

The output contains:

- `dInvoice` as the root dimension column;
- additional `d*` columns for repeating BGs;
- BT value columns after dimension columns;
- one root row for invoice-level facts;
- one row per repeated BG context where bindings produce values.

Forward conversion also writes JSON metadata. By default the metadata file name is:

```text
<output-csv>.metadata.json
```

For example:

```text
out/hierarchical/en16931_lhm_hierarchical.csv.metadata.json
```

The metadata is an xBRL-CSV metadata document that Arelle can load with the
`loadFromOIM` plugin. It links the structured CSV table to the generated
xBRL-CSV taxonomy entry points and maps CSV columns to taxonomy concepts.

## 5. Reverse Output

When `--reverse` is used, the input is a hierarchical CSV and the output is an XML file.

Reverse output example:

```text
out/reverse/en16931_reverse_invoice.xml
```

The reverse converter:

- reads the hierarchical CSV rows;
- resolves fields through the syntax binding CSV;
- uses the LHM layout to associate fields with dimension rows;
- creates UBL Invoice XML elements from bound XPath expressions;
- creates one XML context for each repeated dimension row that has bound values.
- derives required `currencyID` attributes for amount elements from invoice currency fields.

## 6. Command-Line Interface

```text
syntax_binding_hierarchical.py XML_FILE -b BINDING_CSV -o OUTPUT_CSV [options]
```

Reverse form:

```text
syntax_binding_hierarchical.py INPUT_CSV --reverse -b BINDING_CSV -o OUTPUT_XML [options]
```

Arguments:

- `XML_FILE`: input XML file in forward mode.
- `INPUT_CSV`: input hierarchical CSV file in reverse mode.
- `-b`, `--binding`: syntax binding CSV.
- `-o`, `--output`: output hierarchical CSV in forward mode, or output XML in reverse mode.
- `--template-csv`: optional CSV template defining column order and dimension placement.
- `--lhm-csv`: optional LHM CSV defining BG dimension columns and BT value columns.
- `--metadata-output`: optional JSON metadata output path. Default is output CSV path plus `.metadata.json`.
- `--taxonomy-base`: generated taxonomy base directory referenced by JSON metadata. Default is `out/taxonomy`.
- `--reverse`: convert hierarchical CSV back to XML.
- `--drop-empty-columns`: remove columns that have no values in the generated rows.
- `--d-invoice`: value written into the `dInvoice` column. Default is `1`.
- `-e`, `--encoding`: CSV encoding. Default is `utf-8-sig`.

## 7. Forward Processing Model

### 7.1 Namespace handling

The converter collects XML namespace declarations from the input XML using `xml.etree.ElementTree.iterparse`.

XPath helper functions support namespace-prefixed elements such as:

```text
/Invoice/cbc:ID
/Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name
```

### 7.2 LHM layout loading

When an LHM CSV is provided:

1. C rows are treated as BG/class rows.
2. A C row becomes a dimension only if it is the invoice root or if `lhm_level` is populated.
3. Non-repeating BG rows normally have blank `lhm_level`; they remain semantic grouping nodes and are not emitted as dimensions.
4. Dimension names are generated as `d` + UpperCamelCase(`element`).
5. A rows are treated as BT/fact rows.
6. Fact column names are taken from the LHM `element` column.
7. Each fact is assigned to the nearest ancestor dimension, equivalent to the nearest ancestor BG with an `lhm_level`.

Repeating multiplicity is detected when the upper bound is:

```text
*
n
unbounded
```

or a numeric value greater than `1`.

### 7.3 Binding parsing

Each binding row is converted into an internal binding record:

```text
semantic_path
xpath
root
dimension
filter_field
filter_value
field
```

The converter supports:

- root-level paths such as `$.invoice.invoiceNumber`;
- dimension paths with optional filter predicates;
- generic nested semantic paths resolved through the nearest LHM dimension.

### 7.4 Row generation

The converter creates:

- a root invoice row for invoice-level facts;
- dimension rows for filtered dimension facts;
- repeated BG rows for repeated contexts such as VAT breakdown or invoice line.

For repeated BG rows:

1. Bindings are grouped by dimension.
2. The repeat XPath is taken from the LHM BG row XPath when available.
3. Otherwise the repeat XPath is inferred from common binding XPath prefixes.
4. One output row is written for each matched XML context.
5. Ancestor repeating dimension values are copied into nested repeated rows.

### 7.5 Column handling

If the LHM is used, field order is:

```text
dimension columns first, then fact columns
```

If a template is used without LHM, the template header controls the output order.

If neither LHM nor template provides a header, field names are derived from bindings.

## 8. Metadata JSON Processing Model

In forward mode the converter writes JSON metadata after the structured CSV is generated.

The metadata structure follows the xBRL-CSV report package shape:

- `documentInfo`: xBRL-CSV document type, namespaces, and taxonomy entry point references.
- `tables`: the generated structured CSV table and its relative URL.
- `tableTemplates`: table-level dimensions and per-column concept mappings.

Dimension columns are declared as table dimensions:

```json
"plt:d_en16931_Invoice": "$dInvoice"
```

Fact columns are declared with xBRL concepts:

Example:

```json
{
  "InvoiceNumber": {
    "dimensions": {
      "concept": "en16931:InvoiceNumber"
    }
  }
}
```

Amount facts receive a default test unit of `iso4217:JPY` in metadata when the LHM datatype indicates an amount. Production use should derive the unit from the applicable currency term.

## 9. Reverse Processing Model

In reverse mode:

1. The converter reads the input hierarchical CSV with `csv.DictReader`.
2. The converter reads the LHM layout and binding CSV in the same way as forward mode.
3. Root-level fields are written to XML paths directly below the invoice root.
4. Dimension fields are grouped by their `d*` dimension column.
5. For each dimension row with bound values, the converter creates a repeated XML context from the BG XPath.
6. Bound field values are written to relative XPaths under that context.
7. XPath predicates such as `cbc:ChargeIndicator=false()` and `cbc:DocumentTypeCode='130'` are materialized as child values when a matching XML context is created.
8. Amount elements receive `currencyID` from the invoice document currency field. Tax accounting currency TaxTotal paths receive `currencyID` from the tax accounting currency field.
9. UBL-required supporting elements that are not EN 16931 BT values are added where needed for schema validation, including `cac:TaxScheme/cbc:ID` and missing `cbc:ChargeIndicator=false`.
10. Generated UBL child elements are normalized to the UBL 2.1 sequence for the supported Invoice structures.

The reverse converter currently targets the PoC UBL Invoice binding pattern. It is intended for round-trip verification of the structured CSV representation rather than canonical XML reproduction.

## 10. Currency Attribute Rules

The syntax binding treats `currencyID` as syntax metadata derived from semantic currency terms:

- BT-5 `DocumentCurrencyCode` is the default `currencyID` for invoice amount elements.
- BT-6 `TaxAccountingCurrencyCode` is the `currencyID` for the tax accounting currency TaxTotal branch.
- BT-110 and BG-23 use the UBL path predicate `cbc:TaxAmount/@currencyID=/Invoice/cbc:DocumentCurrencyCode`.
- BT-111 uses the UBL path predicate `cbc:TaxAmount/@currencyID=/Invoice/cbc:TaxCurrencyCode`.

The CSV therefore stores semantic amount values and currency code values separately. Reverse conversion writes the required UBL `currencyID` attributes.

## 11. Constraints

- The converter does not validate the XML against UBL schemas internally; the regression test `tests/test_roundtrip_xml_ubl_schema.py` performs UBL 2.1 schema validation.
- The converter does not validate EN 16931 business rules.
- The converter does not run Arelle internally; the regression test `tests/test_xbrl_csv_metadata_arelle.py` validates generated metadata with Arelle.
- The converter does not evaluate full XPath 2.0.
- Supported predicates are intentionally limited to the cases used by the PoC bindings.
- Template columns alone do not create rows; rows require matching bindings.
- Reverse XML element order follows LHM `syntax_sequence` and the supported UBL 2.1 child-order normalization table.
- Reverse XML may omit unbound XML content.
- Reverse XML is generated from bound CSV values and is not intended to be byte-for-byte identical to the source XML.

## 12. Regression Tests

PoC LHM-driven conversion test:

```text
tests/test_lhm_hierarchical_csv_layout.py
```

Package template/binding conversion test:

```text
tests/test_syntax_binding_hierarchical.py
```

OpenPeppol structured conversion test:

```text
tests/test_openpeppol_invoice_conversion.py
```

Reverse conversion round-trip test:

```text
tests/test_syntax_binding_reverse.py
```

Round-trip artifact and metadata test:

```text
tests/test_roundtrip_artifacts.py
```

## 13. Non-Goals

The syntax binding converter does not:

- generate LHM definitions;
- generate XBRL taxonomy files;
- run semantic binding to flat CSV;
- perform full EN 16931 or OpenPeppol validation;
- publish generated `out/` files to GitHub.
