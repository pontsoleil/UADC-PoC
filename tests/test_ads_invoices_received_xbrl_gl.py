#!/usr/bin/env python3
# coding: utf-8
"""
Regression test for ADS Invoices Received XBRL GL generation.

The Invoices Received view represents purchase-side invoice data, so the
party mapping includes the invoice Seller as the Supplier and does not emit a
Buyer party reference.
"""

from __future__ import annotations

import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path(sys.executable)
SOURCE_XML_NAME = "openpeppol_ubl_invoice_minimal"
TARGET_NAME = "Invoices_Received"
BINDING_CSV_NAME = f"ADS_{TARGET_NAME}_XBRL_GL_Binding.csv"
PHASE1_CSV_NAME = "EN16931_Core_Invoice.csv"
OUTPUT_XBRL_NAME = f"{TARGET_NAME}.xbrl"
NS = {
    "gl-cor": "http://www.xbrl.org/int/gl/cor/2016-12-01",
    "gl-bus": "http://www.xbrl.org/int/gl/bus/2016-12-01",
    "gl-muc": "http://www.xbrl.org/int/gl/muc/2016-12-01",
}


def text(root: ET.Element, xpath: str) -> str:
    value = root.findtext(xpath, namespaces=NS)
    assert value is not None, f"Missing XML value for {xpath}"
    return value


def main() -> int:
    structured_dir = ROOT / "out" / "phase1"
    structured_csv = structured_dir / PHASE1_CSV_NAME
    xbrl_dir = ROOT / "out" / "phase2" / "ADS_XBRL_GL"
    xbrl_file = xbrl_dir / OUTPUT_XBRL_NAME
    structured_dir.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            str(PYTHON),
            str(ROOT / "src" / "syntax_binding_hierarchical.py"),
            str(ROOT / "samples" / "input" / f"{SOURCE_XML_NAME}.xml"),
            "-b",
            str(ROOT / "specs" / "bindings" / "syntax" / "EN16931_UBL_Invoice_Syntax_Binding.csv"),
            "--lhm-csv",
            str(ROOT / "specs" / "lhm" / "EN16931_CIUS_Invoice_LHM.csv"),
            "-o",
            str(structured_csv),
        ],
        check=True,
    )
    subprocess.run(
        [
            str(PYTHON),
            str(ROOT / "src" / "ads_invoices_received_xbrl_gl.py"),
            str(structured_csv),
            "-b",
            str(ROOT / "specs" / "bindings" / "syntax" / BINDING_CSV_NAME),
            "--lhm-csv",
            str(ROOT / "specs" / "lhm" / "EN16931_CIUS_Invoice_LHM.csv"),
            "-o",
            str(xbrl_dir),
            "--monetary-decimals",
            "2",
            "--output-filename",
            OUTPUT_XBRL_NAME,
        ],
        check=True,
    )

    assert xbrl_file.exists(), f"Missing generated XBRL GL instance: {xbrl_file}"
    root = ET.parse(xbrl_file).getroot()
    entry_detail = "./gl-cor:accountingEntries/gl-cor:entryHeader/gl-cor:entryDetail"
    assert text(root, f"{entry_detail}/gl-cor:documentReference") == "INV-2026-0001"
    assert text(root, f"{entry_detail}/gl-cor:documentNumber") == "INV-2026-0001"
    assert text(root, f"{entry_detail}/gl-cor:documentDate") == "2026-07-06"
    assert text(root, f"{entry_detail}/gl-cor:amount") == "11000"
    assert text(root, f"{entry_detail}/gl-muc:amountCurrency") == "JPY"
    assert text(root, f"{entry_detail}/gl-cor:identifierReference/gl-cor:identifierCode") == "SELLER-ID"
    assert text(root, f"{entry_detail}/gl-cor:taxes/gl-cor:taxAmount") == "1000"

    print(f"ok: generated and checked {xbrl_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
