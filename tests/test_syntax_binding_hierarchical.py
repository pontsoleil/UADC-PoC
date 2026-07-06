#!/usr/bin/env python3
# coding: utf-8
"""
Regression test for dXXX dimension-based hierarchical CSV conversion.
"""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[0]
PYTHON = Path(sys.executable)


def main() -> int:
    out_dir = ROOT / "out" / "hierarchical"
    out_csv = out_dir / "package_invoice_hierarchical.csv"
    package = REPO / "syntax_binding_revised_package"
    cmd = [
        str(PYTHON),
        str(ROOT / "src" / "syntax_binding_hierarchical.py"),
        str(package / "invoice.xml"),
        "-b",
        str(package / "bindings.csv"),
        "--template-csv",
        str(package / "invoice.csv"),
        "-o",
        str(out_csv),
    ]
    subprocess.run(cmd, check=True)

    with (package / "invoice.csv").open(newline="", encoding="utf-8-sig") as f:
        expected_header = next(csv.reader(f))
    with out_csv.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    assert rows, "No hierarchical rows were written."
    assert rows[0].keys() == dict.fromkeys(expected_header).keys(), "Output header should follow template CSV."
    assert rows[0]["dInvoice"] == "1"
    assert rows[0]["invoiceNumber"] == "INV-26-861"
    assert rows[0]["issueDate"] == "2026-06-20"
    assert rows[0]["currencyCode"] == "JPY"
    assert rows[0]["totalTaxAmount"] == "1472"

    parties = {row["partyRole"]: row for row in rows if row["dInvoiceParty"]}
    assert parties["Seller"]["partyName"] == "売手株式会社"
    assert parties["Seller"]["partyTaxID"] == "T1234567890123"
    assert parties["Buyer"]["partyName"] == "買手株式会社"

    references = {row["referenceType"]: row["referenceID"] for row in rows if row["dDocumentReference"]}
    assert references == {"Order": "PO-2026-0001", "Delivery": "DN-2026-0001"}

    payment = [row for row in rows if row["dPayment"]]
    assert len(payment) == 1
    assert payment[0]["paymentDueDate"] == "2026-07-31"
    assert payment[0]["paymentReference"] == "INV-2026-0001"

    tax_rows = [row for row in rows if row["dTaxBreakdown"]]
    assert [(row["dTaxBreakdown"], row["taxCategoryCode"], row["taxRate"], row["taxAmount"]) for row in tax_rows] == [
        ("1", "S", "10", "1232"),
        ("2", "AA", "8", "240"),
    ]

    line_rows = [row for row in rows if row["dInvoiceLine"]]
    assert not line_rows, "InvoiceLine rows require InvoiceLine bindings; template columns alone are not bindings."

    print(f"ok: wrote and checked {out_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
