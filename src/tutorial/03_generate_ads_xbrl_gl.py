#!/usr/bin/env python3
# coding: utf-8
"""
Generate a sample ADS Invoices Received XBRL GL instance from tutorial CSV.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PYTHON = Path(sys.executable)


def ensure_structured_csv() -> Path:
    """
    Create the tutorial Structured CSV when it is missing.

    Args:
        None.

    Returns:
        Path to the tutorial Structured CSV.
    """
    structured_csv = ROOT / "out" / "tutorial" / "openpeppol_ubl_invoice_minimal.csv"
    if not structured_csv.exists():
        subprocess.run([str(PYTHON), str(ROOT / "src" / "tutorial" / "01_convert_sample_to_structured_csv.py")], check=True)
    return structured_csv


def main() -> int:
    """
    Run the ADS XBRL GL instance generation tutorial.

    Args:
        None.

    Returns:
        Process exit status.
    """
    structured_csv = ensure_structured_csv()
    output_dir = ROOT / "out" / "tutorial" / "xbrl-gl"
    command = [
        str(PYTHON),
        str(ROOT / "src" / "ads_invoices_received_xbrl_gl.py"),
        str(structured_csv),
        "-b",
        str(ROOT / "specs" / "bindings" / "syntax" / "ADS_Invoices_Received_syntax_binding.csv"),
        "--lhm-csv",
        str(ROOT / "specs" / "lhm" / "EN16931_CIUS_Invoice_LHM.csv"),
        "-o",
        str(output_dir),
        "--monetary-decimals",
        "2",
    ]
    subprocess.run(command, check=True)
    print(f"XBRL GL output directory: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
