#!/usr/bin/env python3
# coding: utf-8
"""
Regression test for ADS Supplier Listing XBRL GL generation.

Supplier Listing is derived from the invoice Seller terms in the Phase 1
Structured CSV and maps them to the XBRL GL vendor identifier reference.
"""

from __future__ import annotations

import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path(sys.executable)
SOURCE_XML_NAME = "openpeppol_ubl_invoice_minimal"
TARGET_NAME = "Supplier_Listing"
BINDING_CSV_NAME = f"ADS_{TARGET_NAME}_XBRL_GL_Binding.csv"
PHASE1_CSV_NAME = "openpeppol_ubl_invoice_minimal.csv"
OUTPUT_XBRL_NAME = f"{TARGET_NAME}.xbrl"
NS = {
    "gl-cor": "http://www.xbrl.org/int/gl/cor/2016-12-01",
    "gl-bus": "http://www.xbrl.org/int/gl/bus/2016-12-01",
}


def text(root: ET.Element, xpath: str) -> str:
    value = root.findtext(xpath, namespaces=NS)
    assert value is not None, f"Missing XML value for {xpath}"
    return value


def main() -> int:
    structured_dir = ROOT / "out" / "phase1"
    structured_csv = structured_dir / PHASE1_CSV_NAME
    xbrl_dir = ROOT / "out" / "phase2" / "ADS_XBRL_GL"
    xbrl_file = xbrl_dir / Path(PHASE1_CSV_NAME).stem / OUTPUT_XBRL_NAME
    structured_dir.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            str(PYTHON),
            str(ROOT / "src" / "syntax_binding.py"),
            str(ROOT / "samples" / "input" / f"{SOURCE_XML_NAME}.xml"),
            "-b",
            str(ROOT / "specs" / "bindings" / "syntax" / "EN16931_UBL_Invoice_Syntax_Binding.csv"),
            "--taxonomy-base",
            str(ROOT / "out" / "taxonomy"),
            "-o",
            str(structured_csv),
        ],
        check=True,
    )
    subprocess.run(
        [
            str(PYTHON),
            str(ROOT / "src" / "syntax_binding_ads_xbrl_gl.py"),
            str(structured_csv),
            "-b",
            str(ROOT / "specs" / "bindings" / "syntax" / BINDING_CSV_NAME),
            "--taxonomy-base",
            str(ROOT / "out" / "taxonomy"),
            "-o",
            str(xbrl_dir),
            "--monetary-decimals",
            "2",
        ],
        check=True,
    )

    assert xbrl_file.exists(), f"Missing generated XBRL GL instance: {xbrl_file}"
    root = ET.parse(xbrl_file).getroot()
    seller = (
        "./gl-cor:accountingEntries/gl-cor:entryHeader/gl-cor:entryDetail/"
        "gl-cor:identifierReference"
    )
    assert text(root, f"{seller}/gl-cor:identifierType") == "V"
    assert text(root, f"{seller}/gl-cor:identifierCode") == "SELLER-ID"
    assert text(root, f"{seller}/gl-cor:identifierDescription") == "Seller Co. Ltd."
    address = f"{seller}/gl-bus:identifierAddress"
    assert text(root, f"{address}/gl-bus:identifierStreet") == "1-1-1 Chiyoda"
    assert text(root, f"{address}/gl-bus:identifierCity") == "Tokyo"
    assert text(root, f"{address}/gl-bus:identifierCountry") == "JP"
    assert text(root, f"{address}/gl-bus:identifierZipOrPostalCode") == "100-0001"

    print(f"ok: generated and checked {xbrl_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())






