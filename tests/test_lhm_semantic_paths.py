#!/usr/bin/env python3
# coding: utf-8
"""
Check that LHM semantic_path elements use lowerCamelCaseConcatenated.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATTERN = re.compile(r"^\$\.([a-z][A-Za-z0-9]*)(\.[a-z][A-Za-z0-9]*)*$")


def main() -> int:
    lhm = ROOT / "specs" / "lhm" / "EN16931_CIUS_Invoice_LHM.csv"
    with lhm.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    assert all(None not in row for row in rows), "LHM CSV has rows with extra columns"
    bad = [row["semantic_path"] for row in rows if not PATTERN.match(row["semantic_path"])]
    assert not bad, "Non-lowerCamelCase semantic paths: " + ", ".join(bad[:10])

    by_id = {row["id"]: row for row in rows}
    assert by_id["BG-ROOT"]["semantic_path"] == "$.invoice"
    assert "BG-0" not in by_id
    assert by_id["BG-ROOT"]["level"] == "0"
    assert by_id["BG-ROOT"]["lhm_level"] == "0"
    assert by_id["BT-1"]["level"] == "1"
    assert by_id["BT-1"]["lhm_level"] == "1"
    assert by_id["BT-1"]["class_term"] == "Invoice"
    assert by_id["BT-1"]["semantic_path"] == "$.invoice.invoiceNumber"
    assert by_id["BT-1"]["element"] == "InvoiceNumber"
    assert by_id["BT-2"]["semantic_path"] == "$.invoice.invoiceIssueDate"
    assert by_id["BT-2"]["element"] == "InvoiceIssueDate"
    assert by_id["BG-3"]["semantic_path"] == "$.invoice.precedingInvoiceReference"
    assert by_id["BG-3"]["element"] == "InvoicePrecedingInvoiceReference"
    assert by_id["BT-25"]["element"] == "PrecedingInvoiceReferencePrecedingInvoiceReference"
    assert by_id["BT-27"]["semantic_path"] == "$.invoice.seller.sellerName"
    assert by_id["BT-27"]["element"] == "SellerName"
    assert by_id["BG-4"]["lhm_level"] == ""
    assert by_id["BT-27"]["lhm_level"] == "1"
    assert by_id["BG-25"]["lhm_level"] == "1"
    assert by_id["BT-126"]["lhm_level"] == "2"
    elements = [row["element"] for row in rows if row.get("element")]
    assert len(elements) == len(set(elements)), "LHM element names must be unique."
    allowed_multiplicities = {"0..1", "0..*", "1..1", "1..*"}
    bad_multiplicities = [
        f"{row['id']}={row['multiplicity']}"
        for row in rows
        if row.get("id", "").startswith(("BG-", "BT-"))
        and row.get("multiplicity") not in allowed_multiplicities
    ]
    assert not bad_multiplicities, "Invalid multiplicities: " + ", ".join(bad_multiplicities[:10])
    print(f"ok: checked {len(rows)} semantic path(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
