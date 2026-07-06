# BIS Billing 3 Example Inputs

This directory contains selected invoice XML examples from BIS Billing 3 test
material.

## Purpose

The examples exercise syntax binding behavior beyond the minimal invoice sample,
including allowances, VAT categories, negative correction invoices, sales order
references, and tax accounting currency handling.

## Usage

The conversion regression test reads these files and writes generated
hierarchical CSV output under `out/hierarchical/bis-billing3-examples/`.
Round-trip review artifacts are kept under
`tests/roundtrip/bis-billing3-examples/`.
