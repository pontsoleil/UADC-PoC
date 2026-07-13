#!/usr/bin/env python3
# coding: utf-8
"""
Regression test for EN 16931 LHM conversion from a UBL Invoice sample.
"""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path(sys.executable)


def main() -> int:
    out_dir = ROOT / "out" / "structured"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_csv = out_dir / "openpeppol_ubl_invoice_structured.csv"
    cmd = [
        str(PYTHON),
        str(ROOT / "tools" / "tutorial" / "syntax_binding_sample.py"),
        str(ROOT / "samples" / "input" / "openpeppol_ubl_invoice_minimal.xml"),
        "-b",
        str(ROOT / "specs" / "bindings" / "syntax" / "EN16931_UBL_Invoice_Syntax_Binding.csv"),
        "-o",
        str(out_csv),
        "--row-xpath",
        "/Invoice",
    ]
    subprocess.run(cmd, check=True)

    with out_csv.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 1
    row = rows[0]
    expected = {
        "InvoiceTypeCode": "380",
        "DocumentCurrencyCode": "JPY",
        "BuyerReference": "BUYER-REF-001",
        "PayableAmount": "11000",
    }
    for column, value in expected.items():
        actual = row.get(column)
        assert actual == value, f"{column}: expected {value!r}, got {actual!r}"

    print(f"ok: wrote and checked {out_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())




