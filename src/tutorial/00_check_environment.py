#!/usr/bin/env python3
# coding: utf-8
"""
Check that the tutorial can find the required UADC PoC files.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


REQUIRED_PATHS = [
    ROOT / "src" / "syntax_binding_hierarchical.py",
    ROOT / "src" / "ads_invoices_received_xbrl_gl.py",
    ROOT / "tools" / "build_roundtrip_test_artifacts.py",
    ROOT / "tools" / "taxonomy" / "xBRLGL_TaxonomyGenerator.py",
    ROOT / "specs" / "lhm" / "EN16931_CIUS_Invoice_LHM.csv",
    ROOT / "specs" / "bindings" / "syntax" / "EN16931_UBL_Invoice_Syntax_Binding.csv",
    ROOT / "specs" / "bindings" / "syntax" / "ADS_Invoices_Received_syntax_binding.csv",
    ROOT / "samples" / "input" / "openpeppol_ubl_invoice_minimal.xml",
]


def main() -> int:
    """
    Report whether the tutorial prerequisites are present.

    Args:
        None.

    Returns:
        Process exit status.
    """
    print(f"Python: {sys.executable}")
    print(f"UADC PoC root: {ROOT}")
    missing = [path for path in REQUIRED_PATHS if not path.exists()]
    if missing:
        print("Missing required file(s):")
        for path in missing:
            print(f"  {path}")
        return 1
    taxonomy = ROOT / "out" / "taxonomy" / "plt" / "plt-oim-2026-07-05.xsd"
    if taxonomy.exists():
        print(f"Taxonomy: found {taxonomy}")
    else:
        print("Taxonomy: not generated yet. Run tests/test_xbrlgl_generator_uadc_lhm.py first.")
    print("ok: tutorial prerequisites are available")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
