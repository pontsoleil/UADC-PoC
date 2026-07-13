#!/usr/bin/env python3
# coding: utf-8
"""
Regression test for ADS Invoices Received PSV generation.

The ADS PSV semantic binding maps target pipe-separated columns to UADC
semantic_path values, then resolves those paths to Phase 1 Structured CSV
columns through the LHM.
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
TARGET_NAME = "Invoices_Received"
OUTPUT_PSV_NAME = f"{TARGET_NAME}.psv"


def main() -> int:
    structured_dir = ROOT / "out" / "phase1"
    structured_csv = structured_dir / PHASE1_CSV_NAME
    psv_dir = ROOT / "out" / "phase2" / "ADS_PSV"
    psv_file = psv_dir / Path(PHASE1_CSV_NAME).stem / OUTPUT_PSV_NAME
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
            str(ROOT / "src" / "semantic_binding.py"),
            str(structured_csv),
            "-b",
            str(ROOT / "specs" / "bindings" / "semantic" / "ADS_Invoices_Received_PSV_Binding.csv"),
            "--taxonomy-base",
            str(ROOT / "out" / "taxonomy"),
            "-o",
            str(psv_dir),
        ],
        check=True,
    )

    assert psv_file.exists(), f"Missing generated ADS PSV file: {psv_file}"
    with psv_file.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="|"))

    assert len(rows) == 1
    row = rows[0]
    assert row["Invoice_ID"] == "INV-2026-0001"
    assert row["Invoice_Number"] == "INV-2026-0001"
    assert row["Invoice_Date"] == "2026-07-06"
    assert row["Invoice_Amount_Currency"] == "JPY"
    assert row["Supplier_Account_ID"] == "SELLER-ID"
    assert row["Invoice_Amount"] == "11000"
    assert row["Tax1_Local"] == "1000"
    assert row["Tax1_Type"] == "S"

    print(f"ok: generated and checked {psv_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())






