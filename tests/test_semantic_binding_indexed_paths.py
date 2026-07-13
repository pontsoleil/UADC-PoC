#!/usr/bin/env python3
# coding: utf-8
"""
Regression test for indexed semantic_path handling in ADS semantic bindings.

The [0], [1], [2] notation identifies the zero-based occurrence within a
repeated semantic group, for example VAT breakdown rows expanded into Tax1,
Tax2, and Tax3 ADS PSV columns.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from semantic_binding import load_bindings, transform_rows  # noqa: E402


def main() -> int:
    binding_csv = ROOT / "specs" / "bindings" / "semantic" / "ADS_Invoices_Received_PSV_Binding.csv"
    bindings = load_bindings(binding_csv)
    rows = [
        {"InvoiceNumber": "INV-1", "VatCategoryCode": "", "VatCategoryTaxAmount": "", "dVatBreakdown": ""},
        {"InvoiceNumber": "", "VatCategoryCode": "S", "VatCategoryTaxAmount": "100", "dVatBreakdown": "1"},
        {"InvoiceNumber": "", "VatCategoryCode": "Z", "VatCategoryTaxAmount": "0", "dVatBreakdown": "1"},
    ]

    output_rows = transform_rows(rows, bindings)

    assert len(output_rows) == 1
    row = output_rows[0]
    assert row["Tax1_Type"] == "S"
    assert row["Tax1_Local"] == "100"
    assert row["Tax2_Type"] == "Z"
    assert row["Tax2_Local"] == "0"
    assert row["Tax3_Type"] == ""
    assert row["Tax3_Local"] == ""

    print("ok: indexed semantic_path values are expanded by occurrence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())




