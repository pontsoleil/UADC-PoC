#!/usr/bin/env python3
# coding: utf-8
"""
Regression test for Phase 2 output directory naming.

Each Phase 2 target writes files under a directory named after the input
Structured CSV stem, while the file name remains the Figure 1 target view name.
For example:
out/phase2/ADS_XBRL_GL/Allowance-example/Invoices_Received_Lines.xbrl
"""

from __future__ import annotations

import subprocess
import sys
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path(sys.executable)
PHASE1_DIR = ROOT / "out" / "phase1"
PHASE1_BIS_DIR = PHASE1_DIR / "bis-billing3-examples"
LHM = ROOT / "specs" / "lhm" / "EN16931_CIUS_Invoice_LHM.csv"
XBRL_DIR = ROOT / "out" / "phase2" / "ADS_XBRL_GL"
PSV_DIR = ROOT / "out" / "phase2" / "ADS_PSV"

XBRL_TARGETS = [
    "Invoices_Received",
    "Invoices_Generated",
    "Invoices_Received_Lines",
    "Invoices_Generated_Lines",
    "Supplier_Listing",
    "Customer_Master",
]

PSV_TARGETS = [
    "Invoices_Received",
    "Invoices_Generated",
    "Invoices_Received_Lines",
    "Invoices_Generated_Lines",
    "Supplier_Listing",
    "Customer_Master",
]


def phase1_csv_files() -> list[Path]:
    return sorted(
        path
        for path in [*PHASE1_DIR.glob("*.csv"), *PHASE1_BIS_DIR.glob("*.csv")]
        if not path.stem.endswith("_binding_only")
    )


def run_xbrl_target(input_path: Path, target: str) -> None:
    subprocess.run(
        [
            str(PYTHON),
            str(ROOT / "src" / "syntax_binding_ads_xbrl_gl.py"),
            str(input_path),
            "-b",
            str(ROOT / "specs" / "bindings" / "syntax" / f"ADS_{target}_XBRL_GL_Binding.csv"),
            "-o",
            str(XBRL_DIR),
        ],
        check=True,
    )


def run_psv_target(input_path: Path, target: str) -> None:
    subprocess.run(
        [
            str(PYTHON),
            str(ROOT / "src" / "semantic_binding.py"),
            str(input_path),
            "-b",
            str(ROOT / "specs" / "bindings" / "semantic" / f"ADS_{target}_PSV_Binding.csv"),
            "--format",
            "psv",
            "-o",
            str(PSV_DIR),
        ],
        check=True,
    )


def read_psv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="|"))


def main() -> int:
    csv_files = phase1_csv_files()
    assert len(csv_files) == 10, f"Expected 10 Phase 1 CSV files, found {len(csv_files)}"

    for target in XBRL_TARGETS:
        run_xbrl_target(PHASE1_DIR, target)
        run_xbrl_target(PHASE1_BIS_DIR, target)

    for target in PSV_TARGETS:
        run_psv_target(PHASE1_DIR, target)
        run_psv_target(PHASE1_BIS_DIR, target)

    for csv_file in csv_files:
        for target in XBRL_TARGETS:
            output = XBRL_DIR / csv_file.stem / f"{target}.xbrl"
            assert output.exists(), f"Missing XBRL GL output: {output}"
        for target in PSV_TARGETS:
            output = PSV_DIR / csv_file.stem / f"{target}.psv"
            assert output.exists(), f"Missing ADS PSV output: {output}"

    allowance_lines = XBRL_DIR / "Allowance-example" / "Invoices_Received_Lines.xbrl"
    assert allowance_lines.exists(), f"Missing expected example output: {allowance_lines}"

    sample_dir = PSV_DIR / "openpeppol_ubl_invoice_minimal"
    received_lines = read_psv(sample_dir / "Invoices_Received_Lines.psv")
    assert received_lines[0]["Invoice_ID"] == "INV-2026-0001"
    assert received_lines[0]["Invoice_Line_ID"] == "1"
    assert received_lines[0]["Invoice_Product_ID"] == "ITEM-001"
    assert received_lines[0]["Invoice_Line_Amount"] == "10000"

    supplier = read_psv(sample_dir / "Supplier_Listing.psv")
    assert supplier[0]["Supplier_Account_ID"] == "SELLER-ID"
    assert supplier[0]["Supplier_Account_Name"] == "Seller Co. Ltd."

    customer = read_psv(sample_dir / "Customer_Master.psv")
    assert customer[0]["Customer_Account_ID"] == "BUYER-ID"
    assert customer[0]["Customer_Account_Name"] == "Buyer Co. Ltd."

    print(f"ok: generated Phase 2 outputs for {len(csv_files)} Structured CSV input file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



