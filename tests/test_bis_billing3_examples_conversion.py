#!/usr/bin/env python3
# coding: utf-8
"""
Regression test for OpenPeppol BIS Billing 3 invoice examples.
"""

from __future__ import annotations

import csv
import xml.etree.ElementTree as ET
from pathlib import Path

from phase1_helpers import convert_phase1

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "samples" / "input" / "bis-billing3-examples"
OUT_DIR = ROOT / "out" / "phase1" / "bis-billing3-examples"


def read_rows(csv_file: Path) -> list[dict[str, str]]:
    with csv_file.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def values(rows: list[dict[str, str]], field: str) -> list[str]:
    return [row.get(field, "") for row in rows if row.get(field, "")]


def invoice_samples() -> list[Path]:
    samples: list[Path] = []
    for xml_file in sorted(SAMPLES.glob("*.xml")):
        root = ET.parse(xml_file).getroot()
        local_name = root.tag.rsplit("}", 1)[-1] if root.tag.startswith("{") else root.tag
        if local_name == "Invoice":
            samples.append(xml_file)
    return samples


def main() -> int:
    samples = invoice_samples()
    assert len(samples) == 9, f"Expected 9 Invoice XML samples, found {len(samples)}"

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for xml_file in samples:
        out_csv = convert_phase1(xml_file, OUT_DIR)
        rows = read_rows(out_csv)
        assert rows, f"No rows written for {xml_file.name}"
        assert values(rows, "InvoiceNumber"), f"Missing InvoiceNumber for {xml_file.name}"
        assert values(rows, "DocumentCurrencyCode"), f"Missing DocumentCurrencyCode for {xml_file.name}"
        assert values(rows, "InvoiceLineIdentifier"), f"Missing InvoiceLineIdentifier for {xml_file.name}"
        assert values(rows, "VatCategoryCode"), f"Missing VatCategoryCode for {xml_file.name}"
        assert values(rows, "InvoiceTotalVatAmount"), f"Missing InvoiceTotalVatAmount for {xml_file.name}"

    allowance_rows = read_rows(OUT_DIR / "Allowance-example.csv")
    assert values(allowance_rows, "TaxAccountingCurrencyCode") == ["SEK"]
    assert values(allowance_rows, "InvoiceTotalVatAmountInAccountingCurrency") == ["9324.00"]

    print(f"ok: converted and checked {len(samples)} BIS Billing 3 Invoice example(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())




