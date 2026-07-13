#!/usr/bin/env python3
# coding: utf-8
"""
Regression test for LHM-driven hierarchical CSV layout.
"""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path(sys.executable)
SOURCE_XML_NAME = "openpeppol_ubl_invoice_minimal"
PHASE1_CSV_NAME = "openpeppol_ubl_invoice_minimal.csv"


def main() -> int:
    out_csv = ROOT / "out" / "phase1" / PHASE1_CSV_NAME
    cmd = [
        str(PYTHON),
        str(ROOT / "src" / "syntax_binding.py"),
        str(ROOT / "samples" / "input" / f"{SOURCE_XML_NAME}.xml"),
        "-b",
        str(ROOT / "specs" / "bindings" / "syntax" / "EN16931_UBL_Invoice_Syntax_Binding.csv"),
        "-o",
        str(out_csv),
    ]
    subprocess.run(cmd, check=True)

    with out_csv.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    assert rows, "No LHM hierarchical rows were written."
    dimension_fields = [name for name in fieldnames if name.startswith("d") and name[1:2].isupper()]
    fact_fields = [name for name in fieldnames if name not in dimension_fields]
    assert fieldnames[: len(dimension_fields)] == dimension_fields, "BG dimension columns should be left aligned."
    assert fact_fields[0] == "InvoiceNumber", "BT columns should start after all BG dimension columns."

    invoice_row = rows[0]
    assert invoice_row["dInvoice"] == "1"
    assert invoice_row["InvoiceNumber"] == "INV-2026-0001"
    assert invoice_row["InvoiceIssueDate"] == "2026-07-06"

    assert "dSeller" not in fieldnames
    assert "dBuyer" not in fieldnames
    assert "dSellerPostalAddress" not in fieldnames
    assert "dBuyerPostalAddress" not in fieldnames
    assert invoice_row["SellerName"] == "Seller Co. Ltd."
    assert invoice_row["SellerCity"] == "Tokyo"
    assert invoice_row["BuyerName"] == "Buyer Co. Ltd."
    assert invoice_row["BuyerCity"] == "Osaka"

    line_rows = [row for row in rows if row["dInvoiceLine"] and row["InvoiceLineNetAmount"]]
    assert [row["dInvoiceLine"] for row in line_rows] == ["1"]
    assert line_rows[0]["dInvoice"] == "1"
    assert line_rows[0]["InvoiceLineNetAmount"] == "10000"

    vat_rows = [row for row in rows if row["dVatBreakdown"]]
    assert vat_rows, "VAT breakdown BG should be represented as a dimension row."

    print(f"ok: wrote and checked {out_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())




