#!/usr/bin/env python3
# coding: utf-8
"""
Convert the tutorial Structured CSV back to UBL Invoice XML.
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
    Run the reverse XML conversion tutorial.

    Args:
        None.

    Returns:
        Process exit status.
    """
    structured_csv = ensure_structured_csv()
    output_xml = ROOT / "out" / "tutorial" / "openpeppol_ubl_invoice_minimal.roundtrip.xml"
    command = [
        str(PYTHON),
        str(ROOT / "src" / "syntax_binding_hierarchical.py"),
        str(structured_csv),
        "--reverse",
        "-b",
        str(ROOT / "specs" / "bindings" / "syntax" / "EN16931_UBL_Invoice_Syntax_Binding.csv"),
        "--lhm-csv",
        str(ROOT / "specs" / "lhm" / "EN16931_CIUS_Invoice_LHM.csv"),
        "-o",
        str(output_xml),
    ]
    subprocess.run(command, check=True)
    print(f"Round-trip XML: {output_xml}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
