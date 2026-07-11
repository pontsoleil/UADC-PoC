#!/usr/bin/env python3
# coding: utf-8
"""
Regression test for hierarchical CSV to XML reverse conversion.
"""

from __future__ import annotations

import csv
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path(sys.executable)
SOURCE_XML_NAME = "openpeppol_ubl_invoice_minimal"
PHASE1_CSV_NAME = "EN16931_Core_Invoice.csv"


def read_rows(csv_file: Path) -> list[dict[str, str]]:
    with csv_file.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def first_row_with(rows: list[dict[str, str]], field: str) -> dict[str, str]:
    for row in rows:
        if row.get(field):
            return row
    raise AssertionError(f"No row has a value in {field}")


def main() -> int:
    out_dir = ROOT / "out" / "reverse"
    source_csv = ROOT / "out" / "phase1" / PHASE1_CSV_NAME
    reverse_xml = out_dir / "en16931_reverse_invoice.xml"
    roundtrip_csv = out_dir / "en16931_reverse_roundtrip.csv"
    binding = ROOT / "specs" / "bindings" / "syntax" / "EN16931_UBL_Invoice_Syntax_Binding.csv"
    lhm = ROOT / "specs" / "lhm" / "EN16931_CIUS_Invoice_LHM.csv"

    subprocess.run(
        [
            str(PYTHON),
            str(ROOT / "src" / "syntax_binding_hierarchical.py"),
            str(ROOT / "samples" / "input" / f"{SOURCE_XML_NAME}.xml"),
            "-b",
            str(binding),
            "--lhm-csv",
            str(lhm),
            "-o",
            str(source_csv),
        ],
        check=True,
    )
    subprocess.run(
        [
            str(PYTHON),
            str(ROOT / "src" / "syntax_binding_hierarchical.py"),
            str(source_csv),
            "--reverse",
            "-b",
            str(binding),
            "--lhm-csv",
            str(lhm),
            "-o",
            str(reverse_xml),
        ],
        check=True,
    )
    subprocess.run(
        [
            str(PYTHON),
            str(ROOT / "src" / "syntax_binding_hierarchical.py"),
            str(reverse_xml),
            "-b",
            str(binding),
            "--lhm-csv",
            str(lhm),
            "-o",
            str(roundtrip_csv),
        ],
        check=True,
    )

    original = read_rows(source_csv)
    roundtrip = read_rows(roundtrip_csv)
    assert reverse_xml.exists(), f"Missing reverse XML: {reverse_xml}"

    original_invoice = original[0]
    roundtrip_invoice = roundtrip[0]
    for field in ("InvoiceNumber", "InvoiceIssueDate", "InvoiceTypeCode", "DocumentCurrencyCode", "BuyerReference"):
        assert roundtrip_invoice[field] == original_invoice[field], field

    for field in ("SellerName", "SellerCity", "BuyerName", "BuyerCity", "PaymentDueDate"):
        assert first_row_with(roundtrip, field)[field] == first_row_with(original, field)[field], field

    original_line = first_row_with(original, "InvoiceLineNetAmount")
    roundtrip_line = first_row_with(roundtrip, "InvoiceLineNetAmount")
    assert roundtrip_line["InvoiceLineIdentifier"] == original_line["InvoiceLineIdentifier"]
    assert roundtrip_line["InvoiceLineNetAmount"] == original_line["InvoiceLineNetAmount"]
    assert roundtrip_line["ItemName"] == original_line["ItemName"]

    original_vat = first_row_with(original, "VatCategoryTaxAmount")
    roundtrip_vat = first_row_with(roundtrip, "VatCategoryTaxAmount")
    assert roundtrip_vat["VatCategoryTaxAmount"] == original_vat["VatCategoryTaxAmount"]
    assert roundtrip_vat["VatCategoryCode"] == original_vat["VatCategoryCode"]

    tree = ET.parse(reverse_xml)
    ns = {
        "inv": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }
    tax_amount = tree.find("./cac:TaxTotal/cbc:TaxAmount", ns)
    assert tax_amount is not None
    assert tax_amount.attrib.get("currencyID") == original_invoice["DocumentCurrencyCode"]
    allowance_amount = tree.find("./cac:AllowanceCharge[cbc:ChargeIndicator='false']/cbc:Amount", ns)
    charge_amount = tree.find("./cac:AllowanceCharge[cbc:ChargeIndicator='true']/cbc:Amount", ns)
    assert allowance_amount is not None and allowance_amount.attrib.get("currencyID") == original_invoice["DocumentCurrencyCode"]
    assert charge_amount is not None and charge_amount.attrib.get("currencyID") == original_invoice["DocumentCurrencyCode"]

    print(f"ok: reversed {source_csv} to {reverse_xml} and checked {roundtrip_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
