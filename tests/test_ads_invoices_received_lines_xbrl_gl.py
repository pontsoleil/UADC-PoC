#!/usr/bin/env python3
# coding: utf-8
"""
Regression test for ADS Invoices Received Lines XBRL GL generation.
"""

from __future__ import annotations

import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path(sys.executable)
SOURCE_XML_NAME = "openpeppol_ubl_invoice_minimal"
TARGET_NAME = "Invoices_Received_Lines"
BINDING_CSV_NAME = f"ADS_{TARGET_NAME}_XBRL_GL_Binding.csv"
PHASE1_CSV_NAME = "openpeppol_ubl_invoice_minimal.csv"
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
    entry_detail = "./gl-cor:accountingEntries/gl-cor:entryHeader/gl-cor:entryDetail"
    assert text(root, f"{entry_detail}/gl-cor:documentReference") == "INV-2026-0001"
    assert text(root, f"{entry_detail}/gl-cor:lineNumber") == "1"
    assert text(root, f"{entry_detail}/gl-cor:amount") == "10000"
    assert text(root, f"{entry_detail}/gl-muc:amountCurrency") == "JPY"
    assert text(root, f"{entry_detail}/gl-bus:measurable/gl-bus:measurableQuantity") == "10"
    assert text(root, f"{entry_detail}/gl-bus:measurable/gl-bus:measurableUnitOfMeasure") == "EA"
    assert text(root, f"{entry_detail}/gl-bus:measurable/gl-bus:measurableID") == "ITEM-001"
    assert text(root, f"{entry_detail}/gl-bus:measurable/gl-bus:measurableDescription") == "Sample item"
    measurable = root.find(f"{entry_detail}/gl-bus:measurable", namespaces=NS)
    assert measurable is not None
    assert [child.tag.rsplit("}", 1)[1] for child in list(measurable)] == [
        "measurableID",
        "measurableDescription",
        "measurableQuantity",
        "measurableUnitOfMeasure",
        "measurableCostPerUnit",
    ]
    quantity = measurable.find("gl-bus:measurableQuantity", namespaces=NS)
    cost_per_unit = measurable.find("gl-bus:measurableCostPerUnit", namespaces=NS)
    amount = root.find(f"{entry_detail}/gl-cor:amount", namespaces=NS)
    assert amount is not None and amount.attrib["unitRef"] == "JPY" and amount.attrib["decimals"] == "0"
    assert quantity is not None and quantity.attrib["unitRef"] == "EA" and quantity.attrib["decimals"] == "2"
    assert cost_per_unit is not None and cost_per_unit.attrib["unitRef"] == "JPY" and cost_per_unit.attrib["decimals"] == "0"

    print(f"ok: generated and checked {xbrl_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())






