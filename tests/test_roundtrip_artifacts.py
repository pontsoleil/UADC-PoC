#!/usr/bin/env python3
# coding: utf-8
"""
Check round-trip artifacts under tests/roundtrip.
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEST_ROOT = ROOT / "tests" / "roundtrip"
PYTHON = Path(sys.executable)
NS = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


def read_rows(csv_file: Path) -> list[dict[str, str]]:
    with csv_file.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def values(rows: list[dict[str, str]], field: str) -> list[str]:
    return [row.get(field, "") for row in rows if row.get(field, "")]


def check_case(source_xml: Path, structured_csv: Path, metadata_json: Path, roundtrip_xml: Path) -> None:
    assert source_xml.exists(), f"Missing source XML: {source_xml}"
    assert structured_csv.exists(), f"Missing structured CSV: {structured_csv}"
    assert metadata_json.exists(), f"Missing JSON metadata: {metadata_json}"
    assert roundtrip_xml.exists(), f"Missing round-trip XML: {roundtrip_xml}"

    rows = read_rows(structured_csv)
    assert rows, f"No rows in {structured_csv}"
    assert values(rows, "InvoiceNumber"), f"Missing InvoiceNumber in {structured_csv}"
    assert values(rows, "DocumentCurrencyCode"), f"Missing DocumentCurrencyCode in {structured_csv}"
    assert values(rows, "InvoiceLineIdentifier"), f"Missing InvoiceLineIdentifier in {structured_csv}"

    document_currency = values(rows, "DocumentCurrencyCode")[0]
    tree = ET.parse(roundtrip_xml)
    xml_invoice_number = tree.findtext("./cbc:ID", namespaces=NS)
    assert xml_invoice_number == values(rows, "InvoiceNumber")[0], roundtrip_xml

    amount = tree.find(".//cbc:PayableAmount", NS)
    if amount is None:
        amount = tree.find(".//cbc:LineExtensionAmount", NS)
    assert amount is not None, f"Missing amount element in {roundtrip_xml}"
    assert amount.attrib.get("currencyID") == document_currency, roundtrip_xml

    metadata = json.loads(metadata_json.read_text(encoding="utf-8"))
    assert "metadataType" not in metadata
    document_taxonomy = metadata["documentInfo"]["taxonomy"]
    assert document_taxonomy, metadata_json
    assert document_taxonomy == ["../../../../out/taxonomy/plt/plt-oim-2026-07-05.xsd"], metadata_json
    assert all("plt-all" not in entry and "content" not in entry for entry in document_taxonomy)
    assert metadata["tables"]["structured"]["url"].endswith(structured_csv.name)
    template = metadata["tableTemplates"]["structured"]
    assert template["dimensions"]["plt:d_en16931_Invoice"] == "$dInvoice"
    assert template["columns"]["dInvoice"] == {}
    assert template["columns"]["InvoiceNumber"]["dimensions"]["concept"] == "en16931:InvoiceNumber"
    assert template["columns"]["DocumentCurrencyCode"]["dimensions"]["concept"] == "en16931:DocumentCurrencyCode"


def main() -> int:
    subprocess.run([str(PYTHON), str(ROOT / "tools" / "build_roundtrip_test_artifacts.py")], check=True)

    cases = 0
    for dataset_dir in sorted(TEST_ROOT.iterdir()):
        if not dataset_dir.is_dir():
            continue
        source_dir = dataset_dir / "source_xml"
        csv_dir = dataset_dir / "structured_csv"
        metadata_dir = dataset_dir / "metadata_json"
        xml_dir = dataset_dir / "roundtrip_xml"
        for source_xml in sorted(source_dir.glob("*.xml")):
            check_case(
                source_xml,
                csv_dir / f"{source_xml.stem}.csv",
                metadata_dir / f"{source_xml.stem}.metadata.json",
                xml_dir / source_xml.name,
            )
            cases += 1
    assert cases == 10, f"Expected 10 round-trip cases, checked {cases}"
    print(f"ok: checked {cases} round-trip artifact case(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())




