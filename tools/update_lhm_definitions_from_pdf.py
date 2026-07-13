#!/usr/bin/env python3
# coding: utf-8
"""
Update LHM definition values from the EN 16931-1 Table 2 Description column.

This script extracts table cells with pdfplumber. It only updates rows for
which a BT/BG identifier and Description cell can be extracted.

Creation Date: 2026-07-05
Last Modified: 2026-07-13

Copyright 2026 Sambuichi Professional Engineers Office
Designed by SAMBUICHI, Nobuyuki
Produced by ChatGPT and Codex, edited by SAMBUICHI, Nobuyuki

License:
    This software source code is licensed under the MIT License.

    Non-code materials in the UADC-PoC project, including original mapping
    tables, syntax binding definitions, semantic binding definitions,
    transformation rules, explanatory notes, and documentation, may be licensed
    separately under Creative Commons Attribution-NonCommercial 4.0
    International License (CC BY-NC 4.0), where so indicated.

    Third-party standards, schemas, taxonomies, code lists, field names,
    descriptions, and excerpts remain subject to their original copyright
    notices and licenses. This license notice does not relicense third-party
    materials.

MIT License

Copyright (c) 2026 Sambuichi Professional Engineers Office

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Dict, List

import pdfplumber


ID_PATTERN = re.compile(r"\b(?:BT|BG)-\d+\b")

DESCRIPTION_OVERRIDES = {
    # pdfplumber splits this row across visual cells on the source page.
    "BT-10": "An identifier assigned by the Buyer used for internal routing purposes.",
    "BT-18": "An identifier for an object on which the invoice is based, given by the Seller.",
    "BT-19": "A textual value that specifies where to book the relevant data into the Buyer's financial accounts.",
    "BT-33": "Additional legal information relevant for the Seller.",
    "BT-39": "The subdivision of a country.",
    "BT-58": "An e-mail address for the contact point.",
    "BT-62": "The full name of the Seller's tax representative party.",
    "BT-68": "The subdivision of a country.",
    "BT-74": "The date when the Invoice period ends.",
    "BT-88": "The name of the payment card holder.",
    "BT-124": "The URL (Uniform Resource Locator) that identifies where the external document is located.",
    "BG-31": "A group of business terms providing information about the goods and services invoiced.",
    "BT-153": "A name for an item.",
    "BT-154": "A description for an item.",
    "BT-155": "An identifier, assigned by the Seller, for the item.",
    "BT-156": "An identifier, assigned by the Buyer, for the item.",
    "BT-157": "An item identifier based on a registered scheme.",
    "BT-158": "A code for classifying the item by its type or nature.",
    "BT-159": "The code identifying the country from which the item originates.",
    "BG-32": "A group of business terms providing information about properties of the goods and services invoiced.",
    "BT-160": "The name of the attribute or property of the item.",
    "BT-161": "The value of the attribute or property of the item.",
}


def clean_cell(value: str | None) -> str:
    text = " ".join((value or "").split())
    return text.strip()


def clean_description(value: str | None) -> str:
    text = clean_cell(value)
    text = re.sub(r"^Description\s+", "", text)
    return text.strip()


def clean_identifier(value: str | None) -> str:
    text = clean_cell(value)
    match = ID_PATTERN.search(text)
    return match.group(0) if match else ""


def extract_descriptions(pdf_file: Path, first_page: int, last_page: int) -> Dict[str, str]:
    parts_by_id: Dict[str, List[str]] = {}
    with pdfplumber.open(str(pdf_file)) as pdf:
        for page_number in range(first_page, last_page + 1):
            page = pdf.pages[page_number - 1]
            for table in page.extract_tables():
                current_id = ""
                for row in table:
                    if not row or len(row) < 5:
                        continue
                    identifier = clean_identifier(row[0])
                    description = clean_description(row[4])
                    if identifier:
                        current_id = identifier
                        parts_by_id.setdefault(identifier, [])
                    if current_id and description and description != "Description":
                        parts_by_id.setdefault(current_id, []).append(description)
    return {
        identifier: " ".join(parts)
        for identifier, parts in parts_by_id.items()
        if parts
    }


def read_rows(csv_file: Path) -> tuple[List[str], List[Dict[str, str]]]:
    with csv_file.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV has no header.")
        fieldnames = [field.lstrip("\ufeff") for field in reader.fieldnames]
        rows = [{key.lstrip("\ufeff"): value for key, value in row.items()} for row in reader]
    return fieldnames, rows


def write_rows(csv_file: Path, fieldnames: List[str], rows: List[Dict[str, str]]) -> None:
    with csv_file.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Update LHM definitions from EN 16931-1 PDF descriptions.")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("lhm_csv", type=Path)
    parser.add_argument("--first-page", type=int, default=43)
    parser.add_argument("--last-page", type=int, default=75)
    args = parser.parse_args()

    descriptions = extract_descriptions(args.pdf, args.first_page, args.last_page)
    descriptions.update(DESCRIPTION_OVERRIDES)
    fieldnames, rows = read_rows(args.lhm_csv)

    updated = 0
    not_extracted: List[str] = []
    unresolved: List[str] = []
    for row in rows:
        identifier = row.get("id", "")
        if not ID_PATTERN.fullmatch(identifier):
            continue
        description = descriptions.get(identifier)
        if description:
            if row.get("definition", "") != description:
                row["definition"] = description
                updated += 1
        else:
            not_extracted.append(identifier)
            if not row.get("definition", "").strip():
                unresolved.append(identifier)

    write_rows(args.lhm_csv, fieldnames, rows)
    print(f"Extracted {len(descriptions)} description(s); updated {updated} LHM row(s).")
    if not_extracted:
        print("Descriptions not extracted from PDF table cells: " + ", ".join(not_extracted))
    if unresolved:
        print("Unresolved empty definitions: " + ", ".join(unresolved))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
