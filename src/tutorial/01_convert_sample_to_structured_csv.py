#!/usr/bin/env python3
# coding: utf-8
"""
Convert the minimal sample UBL Invoice XML to Structured CSV and metadata.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PYTHON = Path(sys.executable)


def ensure_taxonomy() -> None:
    """
    Generate the local taxonomy when it is not already present.

    Args:
        None.

    Returns:
        None. The taxonomy files are generated under out/taxonomy when needed.
    """
    taxonomy = ROOT / "out" / "taxonomy" / "plt" / "plt-oim-2026-07-05.xsd"
    if taxonomy.exists():
        return
    subprocess.run([str(PYTHON), str(ROOT / "tests" / "test_xbrlgl_generator_uadc_lhm.py")], check=True)


def main() -> int:
    """
    Run the forward Structured CSV conversion tutorial.

    Args:
        None.

    Returns:
        Process exit status.
    """
    ensure_taxonomy()
    out_dir = ROOT / "out" / "tutorial"
    out_dir.mkdir(parents=True, exist_ok=True)
    output_csv = out_dir / "openpeppol_ubl_invoice_minimal.csv"
    metadata_json = out_dir / "openpeppol_ubl_invoice_minimal.json"
    command = [
        str(PYTHON),
        str(ROOT / "src" / "syntax_binding_hierarchical.py"),
        str(ROOT / "samples" / "input" / "openpeppol_ubl_invoice_minimal.xml"),
        "-b",
        str(ROOT / "specs" / "bindings" / "syntax" / "EN16931_UBL_Invoice_Syntax_Binding.csv"),
        "--lhm-csv",
        str(ROOT / "specs" / "lhm" / "EN16931_CIUS_Invoice_LHM.csv"),
        "--metadata-output",
        str(metadata_json),
        "--taxonomy-base",
        str(ROOT / "out" / "taxonomy"),
        "-o",
        str(output_csv),
    ]
    subprocess.run(command, check=True)
    print(f"Structured CSV: {output_csv}")
    print(f"Metadata JSON: {metadata_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
