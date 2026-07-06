# Syntax Binding Specifications

This directory contains source syntax binding CSV files.

## Files

- `EN16931_UBL_Invoice_Syntax_Binding.csv` - Active Phase 1 binding from UBL
  Invoice XML to EN 16931 LHM semantic paths.

## Role in the Pipeline

The syntax binding identifies the XPath for each bound business term and, where
needed, selector predicates such as currency-specific `TaxTotal` branches. It is
used for both forward conversion from XML to structured CSV and reverse
conversion from structured CSV back to XML.

OpenPeppol-specific syntax binding files are not currently committed. The PoC
uses the EN 16931 binding as the stable baseline, with OpenPeppol CIUS rules
planned as an overlay.
