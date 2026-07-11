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
PYTHON = Path(sys.executable)
SOURCE_XML_NAME = "openpeppol_ubl_invoice_minimal"
PHASE1_CSV_NAME = "EN16931_Core_Invoice.csv"


def ensure_taxonomy() -> None:
    taxonomy_base = ROOT / "out" / "taxonomy"
    oim_schema = taxonomy_base / "plt" / "plt-oim-2026-07-05.xsd"
    module_schema = taxonomy_base / "en16931" / "en16931-2026-07-05.xsd"
    if oim_schema.exists() and module_schema.exists():
        return
    subprocess.run([str(PYTHON), str(ROOT / "tests" / "test_xbrlgl_generator_uadc_lhm.py")], check=True)


def main() -> int:
    ensure_taxonomy()
    out_dir = ROOT / "out" / "phase1"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_csv = out_dir / PHASE1_CSV_NAME
    binding = ROOT / "specs" / "bindings" / "syntax" / "EN16931_UBL_Invoice_Syntax_Binding.csv"
    lhm = ROOT / "specs" / "lhm" / "EN16931_CIUS_Invoice_LHM.csv"
    cmd = [
        str(PYTHON),
        str(ROOT / "src" / "syntax_binding_hierarchical.py"),
        str(ROOT / "samples" / "input" / f"{SOURCE_XML_NAME}.xml"),
        "-b",
        str(binding),
        "--lhm-csv",
        str(lhm),
        "-o",
        str(out_csv),
    ]
    subprocess.run(cmd, check=True)

    with out_csv.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    assert rows, "No hierarchical rows were written."
    dimension_fields = [name for name in fieldnames if name.startswith("d") and name[1:2].isupper()]
    assert fieldnames[: len(dimension_fields)] == dimension_fields, "BG dimension columns should be left aligned."

    invoice = rows[0]
    assert invoice["dInvoice"] == "1"
    assert invoice["InvoiceNumber"] == "INV-2026-0001"
    assert invoice["InvoiceIssueDate"] == "2026-07-06"
    assert invoice["DocumentCurrencyCode"] == "JPY"
    assert invoice["SellerName"] == "Seller Co. Ltd."
    assert invoice["BuyerName"] == "Buyer Co. Ltd."
    assert invoice["AmountDueForPayment"] == "11000"

    payment = [row for row in rows if row["dPaymentInstructions"]]
    assert payment
    assert payment[0]["PaymentMeansTypeCode"] == "30"
    assert payment[0]["PaymentRemittanceInformation"] == "INV-2026-0001"

    vat_rows = [row for row in rows if row["dVatBreakdown"]]
    assert [(row["dVatBreakdown"], row["VatCategoryCode"], row["VatCategoryRate"], row["VatCategoryTaxAmount"]) for row in vat_rows] == [
        ("1", "S", "10", "1000"),
    ]

    line_rows = [row for row in rows if row["dInvoiceLine"] and row["InvoiceLineNetAmount"]]
    assert len(line_rows) == 1
    assert line_rows[0]["dInvoice"] == "1"
    assert line_rows[0]["dInvoiceLine"] == "1"
    assert line_rows[0]["InvoiceLineIdentifier"] == "1"
    assert line_rows[0]["InvoiceLineNetAmount"] == "10000"
    assert line_rows[0]["ItemName"] == "Sample item"

    print(f"ok: wrote and checked {out_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
