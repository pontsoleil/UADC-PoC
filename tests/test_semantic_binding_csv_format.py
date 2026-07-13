#!/usr/bin/env python3
# coding: utf-8
"""
Regression test for CSV-format semantic binding output.

The semantic binding converter is a target tabular-file generator, not only an
ADS PSV generator. This test verifies that --format csv switches the delimiter,
extension, and output file name while using the same semantic binding table.
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
    structured_dir = ROOT / "out" / "phase1"
    structured_csv = structured_dir / PHASE1_CSV_NAME
    output_dir = ROOT / "out" / "phase2" / "CSV_FORMAT_TEST"
    output_csv = output_dir / Path(PHASE1_CSV_NAME).stem / "Invoices_Received.csv"
    iso_output_dir = ROOT / "out" / "phase2" / "ISO21378_ADC_CSV_TEST"
    iso_output_csv = iso_output_dir / Path(PHASE1_CSV_NAME).stem / "PUR_Invoice_Received.csv"
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
            "--format",
            "csv",
            "-o",
            str(output_dir),
        ],
        check=True,
    )

    assert output_csv.exists(), f"Missing generated CSV file: {output_csv}"
    with output_csv.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 1
    row = rows[0]
    assert row["Invoice_ID"] == "INV-2026-0001"
    assert row["Supplier_Account_ID"] == "SELLER-ID"
    assert row["Invoice_Amount_Currency"] == "JPY"

    subprocess.run(
        [
            str(PYTHON),
            str(ROOT / "src" / "semantic_binding.py"),
            str(structured_csv),
            "-b",
            str(
                ROOT
                / "specs"
                / "bindings"
                / "semantic"
                / "ISO21378_PUR_Invoice_Received_CSV_Binding.csv"
            ),
            "--format",
            "csv",
            "-o",
            str(iso_output_dir),
        ],
        check=True,
    )

    assert iso_output_csv.exists(), f"Missing generated ISO 21378 CSV file: {iso_output_csv}"
    with iso_output_csv.open(newline="", encoding="utf-8") as handle:
        iso_rows = list(csv.DictReader(handle))

    assert len(iso_rows) == 1
    iso_row = iso_rows[0]
    assert iso_row["Invoice_ID"] == "INV-2026-0001"
    assert iso_row["Supplier_Account_ID"] == "SELLER-ID"
    assert iso_row["Invoice_Transaction_CUR_Code"] == "JPY"
    assert iso_row["Invoice_Transaction_Amount"] == "11000"

    print(f"ok: generated and checked {output_csv} and {iso_output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
