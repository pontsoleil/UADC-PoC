# Syntax Binding Specifications

This directory contains source syntax binding CSV files.

## Files

- `EN16931_UBL_Invoice_Syntax_Binding.csv` - Active Phase 1 binding from UBL
  Invoice XML to EN 16931 LHM semantic paths.
- `ADS_Invoices_Received_XBRL_GL_Binding.csv` - Binding from EN 16931
  structured CSV columns to the selected XBRL GL tuple taxonomy elements for
  ADS Invoices Received generation.
- `ADS_Invoices_Generated_XBRL_GL_Binding.csv` - Phase 2 binding from
  EN 16931 structured CSV columns to the selected XBRL GL tuple taxonomy
  elements for ADS Invoices Generated generation.
- `ADS_Invoices_Received_Lines_XBRL_GL_Binding.csv` - Phase 2 binding from
  EN 16931 invoice line structured CSV columns to the selected XBRL GL tuple
  taxonomy elements for ADS Invoices Received Lines generation.
- `ADS_Invoices_Generated_Lines_XBRL_GL_Binding.csv` - Phase 2 binding from
  EN 16931 invoice line structured CSV columns to the selected XBRL GL tuple
  taxonomy elements for ADS Invoices Generated Lines generation.
- `ADS_Supplier_Listing_XBRL_GL_Binding.csv` - Phase 2 binding from the
  EN 16931 invoice Seller terms to the selected XBRL GL tuple taxonomy
  elements for ADS Supplier Listing generation.
- `ADS_Customer_Master_XBRL_GL_Binding.csv` - Phase 2 binding from the
  EN 16931 invoice Buyer terms to the selected XBRL GL tuple taxonomy
  elements for ADS Customer Master generation.
- `ADS_XBRL_GL_Bindings.xlsx` - Review workbook for the ADS XBRL GL binding
  set. The authoritative machine-readable definitions are the CSV files in
  this directory.

## Column Layout

Syntax binding CSV files use the common base columns:

```text
sequence,level,type,identifier,name,datatype,multiplicity,domain_name,definition,module,class_term,id,path,semantic_path,abbreviation_path,label_local,definition_local,element,xpath
```

XBRL GL target bindings may append these columns for instance-generation rules:

```text
binding_scope,value_name,value_role,value_source,default_value,unit_ref_rule,decimals
```

`document` rows describe context and unit rules. `fact` rows describe semantic
source terms and their target XBRL GL element/XPath mappings.

For monetary XBRL GL facts, `unit_ref_rule` should name a Structured CSV column
that contains the currency code, such as `DocumentCurrencyCode`. The `decimals`
column is left blank for monetary facts; decimals are resolved from
`specs/Currency.csv`.

Binding rows are sorted by `class_term` hierarchy: document-control rows first,
then each class row followed by its direct fact rows and child classes. Except
for `class_term = Document`, the `name` column uses Title Case for reviewable
business labels.

Current ADS party mapping:

- Invoices Received uses invoice Seller data as Supplier data.
- Invoices Generated uses invoice Buyer data as Customer data.
- Supplier Listing is derived from invoice Seller data.
- Customer Master is derived from invoice Buyer data.

## Role in the Pipeline

The syntax binding identifies the XPath for each bound business term and, where
needed, selector predicates such as currency-specific `TaxTotal` branches. It is
used for both forward conversion from XML to structured CSV and reverse
conversion from structured CSV back to XML.

OpenPeppol-specific syntax binding files are not currently committed. The PoC
uses the EN 16931 binding as the stable baseline, with OpenPeppol CIUS rules
planned as an overlay.
