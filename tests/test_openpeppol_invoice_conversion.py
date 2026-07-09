#!/usr/bin/env python3
# coding: utf-8
"""
Regression test for EN 16931 LHM conversion from a UBL Invoice sample.
"""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path(sys.executable)


def main() -> int:
    out_dir = ROOT / "out" / "structured"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_csv = out_dir / "openpeppol_ubl_invoice_structured.csv"
    cmd = [
        str(PYTHON),
        str(ROOT / "tools" / "syntax_binding.py"),
        str(ROOT / "samples" / "input" / "openpeppol_ubl_invoice_minimal.xml"),
        "-b",
        str(ROOT / "specs" / "bindings" / "syntax" / "EN16931_UBL_Invoice_Syntax_Binding.csv"),
        "-o",
        str(out_csv),
        "--row-xpath",
        "/Invoice",
    ]
    subprocess.run(cmd, check=True)

    with out_csv.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    expected_csv = ROOT / "samples" / "expected" / "openpeppol_ubl_invoice_structured.csv"
    with expected_csv.open(newline="", encoding="utf-8-sig") as f:
        expected_rows = list(csv.DictReader(f))
    assert rows == expected_rows, f"Generated CSV differs from {expected_csv}"

    assert len(rows) == 1
    row = rows[0]
    expected = {
        "invoice_invoiceNumber": "INV-2026-0001",
        "invoice_invoiceIssueDate": "2026-07-06",
        "invoice_invoiceTypeCode": "380",
        "invoice_documentCurrencyCode": "JPY",
        "invoice_seller_sellerName": "Seller Co. Ltd.",
        "invoice_buyer_buyerName": "Buyer Co. Ltd.",
        "invoice_documentTotals_amountDueForPayment": "11000",
        "invoice_invoiceLine_invoiceLineIdentifier": "1",
        "invoice_invoiceLine_itemInformation_itemName": "Sample item",
        "invoice_documentLevelAllowances_documentLevelAllowanceReason": "Document level discount",
        "invoice_documentLevelCharges_documentLevelChargeReason": "Freight service",
        "invoice_invoiceLine_invoiceLineAllowances_invoiceLineAllowanceAmount": "300",
        "invoice_invoiceLine_invoiceLineCharges_invoiceLineChargeAmount": "100",
        "invoice_invoiceLine_invoiceLinePeriod_invoiceLinePeriodStartDate": "2026-07-01",
        "invoice_documentTotals_paidAmount": "1000",
        "invoice_documentTotals_roundingAmount": "0",
    }
    for column, value in expected.items():
        actual = row.get(column)
        assert actual == value, f"{column}: expected {value!r}, got {actual!r}"

    print(f"ok: wrote and checked {out_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
