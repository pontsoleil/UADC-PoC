#!/usr/bin/env python3
# coding: utf-8
"""
Audit LHM coverage against EN 16931-1 BT/BG identifiers.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

from pypdf import PdfReader


ID_PATTERN = re.compile(r"\b(?:BT|BG)-\d+\b")


def sort_key(identifier: str) -> tuple[str, int]:
    prefix, number = identifier.split("-")
    return prefix, int(number)


def extract_pdf_ids(pdf_file: Path) -> dict[str, int]:
    reader = PdfReader(str(pdf_file))
    ids: dict[str, int] = {}
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        for match in ID_PATTERN.finditer(text):
            ids.setdefault(match.group(0), index)
    return ids


def read_lhm_ids(lhm_csv: Path) -> set[str]:
    with lhm_csv.open(newline="", encoding="utf-8-sig") as f:
        return {
            row["id"]
            for row in csv.DictReader(f)
            if row.get("id") and ID_PATTERN.fullmatch(row["id"])
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit EN 16931 BT/BG coverage in LHM CSV.")
    parser.add_argument("pdf", type=Path, help="EN 16931-1 PDF")
    parser.add_argument("lhm_csv", type=Path, help="LHM CSV")
    args = parser.parse_args()

    pdf_ids = extract_pdf_ids(args.pdf)
    lhm_ids = read_lhm_ids(args.lhm_csv)
    all_pdf_ids = sorted(pdf_ids, key=sort_key)
    missing = [identifier for identifier in all_pdf_ids if identifier not in lhm_ids]
    extra = sorted([identifier for identifier in lhm_ids if identifier not in pdf_ids], key=sort_key)
    report = {
        "pdf_ids": len(all_pdf_ids),
        "lhm_ids": len(lhm_ids),
        "missing_count": len(missing),
        "missing": [{"id": identifier, "pdf_page": pdf_ids[identifier]} for identifier in missing],
        "extra": extra,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
