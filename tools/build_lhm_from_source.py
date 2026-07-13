#!/usr/bin/env python3
# coding: utf-8
"""
Build the EN 16931 LHM CSV from an editable source CSV.

The source CSV is the hand-adjustable input for LHM generation. It keeps the
PDF-derived table fields plus optional override columns, while the generated
LHM CSV keeps the normalized columns consumed by the PoC scripts.

Creation Date: 2026-07-05
Last Modified: 2026-07-13

Copyright 2026 Sambuichi Professional Engineers Office
Designed by SAMBUICHI, Nobuyuki
Produced by ChatGPT & Codex, edited by  SAMBUICHI, Nobuyuki
MIT License

(c) 2026 Sambuichi Professional Engineers Office

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
CC-BY-NC
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Dict, Iterable, List

from normalize_lhm_class_element import singularize, unique_element_names


SOURCE_FIELDS = [
    "sequence",
    "syntax_sequence",
    "id",
    "level",
    "type",
    "cardinality",
    "business_term",
    "description",
    "usage_note",
    "req_id",
    "semantic_data_type",
    "path",
    "xpath",
    "semantic_path_override",
    "class_term_override",
    "element_override",
    "label_local",
    "definition_local",
    "source_ref",
    "adjustment_note",
]

LHM_FIELDS = [
    "sequence",
    "syntax_sequence",
    "level",
    "lhm_level",
    "type",
    "identifier",
    "name",
    "datatype",
    "multiplicity",
    "domain_name",
    "definition",
    "module",
    "class_term",
    "id",
    "path",
    "semantic_path",
    "label_local",
    "definition_local",
    "element",
    "xpath",
]

TYPE_BY_ID_PREFIX = {
    "BG-": "Group",
    "BT-": "Field",
}

ALLOWED_MULTIPLICITIES = {"0..1", "0..*", "1..1", "1..*"}


def normalize_multiplicity(value: str) -> str:
    multiplicity = (value or "").strip()
    if multiplicity in {"0..n", "0..N"}:
        return "0..*"
    if multiplicity in {"1..n", "1..N"}:
        return "1..*"
    return multiplicity


def read_rows(csv_file: Path) -> tuple[List[str], List[Dict[str, str]]]:
    with csv_file.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError(f"{csv_file} has no header.")
        fields = [field.lstrip("\ufeff") for field in reader.fieldnames]
        return fields, [{key.lstrip("\ufeff"): value for key, value in row.items()} for row in reader]


def write_rows(csv_file: Path, fieldnames: List[str], rows: Iterable[Dict[str, str]]) -> None:
    csv_file.parent.mkdir(parents=True, exist_ok=True)
    with csv_file.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def type_from_id(row_id: str) -> str:
    for prefix, value in TYPE_BY_ID_PREFIX.items():
        if row_id.startswith(prefix):
            return value
    return ""


def lower_camel_case_concatenated(text: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", text or "")
    if not words:
        return ""
    first, rest = words[0].lower(), words[1:]
    return first + "".join(word[:1].upper() + word[1:].lower() for word in rest)


def source_from_lhm(lhm_csv: Path, source_csv: Path) -> None:
    _, rows = read_rows(lhm_csv)
    source_rows: List[Dict[str, str]] = []
    for row in rows:
        source_rows.append(
            {
                "sequence": row.get("sequence", ""),
                "syntax_sequence": row.get("syntax_sequence", ""),
                "id": row.get("id", ""),
                "level": row.get("level", ""),
                "type": row.get("type", ""),
                "cardinality": normalize_multiplicity(row.get("multiplicity", "")),
                "business_term": row.get("name", ""),
                "description": row.get("definition", "") or row.get("definition_local", ""),
                "usage_note": "",
                "req_id": "",
                "semantic_data_type": row.get("datatype", ""),
                "path": row.get("path", ""),
                "xpath": row.get("xpath", ""),
                "semantic_path_override": row.get("semantic_path", ""),
                "class_term_override": row.get("class_term", ""),
                "element_override": row.get("element", ""),
                "label_local": row.get("label_local", ""),
                "definition_local": row.get("definition_local", ""),
                "source_ref": "EN 16931-1 Table 2",
                "adjustment_note": "",
            }
        )
    write_rows(source_csv, SOURCE_FIELDS, source_rows)
    print(f"Wrote editable LHM source CSV: {source_csv}")


def path_ids(row: Dict[str, str]) -> List[str]:
    values = [part for part in (row.get("path") or "").split("/") if part]
    row_id = row.get("id", "")
    if row_id and (not values or values[-1] != row_id):
        values.append(row_id)
    return values


def semantic_path(row: Dict[str, str], segment_by_id: Dict[str, str]) -> str:
    override = (row.get("semantic_path_override") or "").strip()
    if override:
        return override
    segments = [segment_by_id.get(row_id, "") for row_id in path_ids(row)]
    segments = [segment for segment in segments if segment]
    return "$." + ".".join(segments)


def nearest_bg_id(row: Dict[str, str]) -> str:
    row_id = row.get("id", "")
    if row_id.startswith("BG-"):
        return row_id
    for value in reversed(path_ids(row)):
        if value.startswith("BG-"):
            return value
    return ""


def lhm_effective_levels(rows: List[Dict[str, str]]) -> Dict[str, str]:
    effective: Dict[str, str] = {}

    def nearest_effective_parent_level(row: Dict[str, str]) -> int:
        for parent_id in reversed(path_ids(row)[:-1]):
            parent_level = effective.get(parent_id, "")
            if parent_level != "":
                return int(parent_level)
        return -1

    for row in rows:
        row_id = row.get("id", "")
        row_type = row.get("type", "")
        multiplicity = normalize_multiplicity(row.get("multiplicity", ""))
        if row_id == "BG-ROOT":
            effective[row_id] = "0"
        elif row_type == "C":
            if multiplicity in {"0..*", "1..*"}:
                effective[row_id] = str(nearest_effective_parent_level(row) + 1)
            else:
                effective[row_id] = ""
        elif row_type == "A":
            effective[row_id] = str(nearest_effective_parent_level(row) + 1)
        else:
            effective[row_id] = ""
    return effective


def build_lhm(source_csv: Path, output_csv: Path) -> None:
    _, source_rows = read_rows(source_csv)
    rows = sorted(source_rows, key=lambda row: int(row.get("sequence") or 0))
    segment_by_id = {
        row.get("id", ""): lower_camel_case_concatenated(row.get("business_term", ""))
        for row in rows
    }
    name_by_id = {row.get("id", ""): row.get("business_term", "") for row in rows}

    lhm_rows: List[Dict[str, str]] = []
    for row in rows:
        row_id = row.get("id", "")
        lhm_type = row.get("type") or type_from_id(row_id)
        path = row.get("path", "")
        sem_path = semantic_path(row, segment_by_id)
        class_term = row.get("class_term_override") or singularize(name_by_id.get(nearest_bg_id(row), ""))
        lhm_rows.append(
            {
                "sequence": row.get("sequence", ""),
                "syntax_sequence": row.get("syntax_sequence", ""),
                "level": row.get("level", ""),
                "type": lhm_type,
                "identifier": "",
                "name": row.get("business_term", ""),
                "datatype": row.get("semantic_data_type", ""),
                "multiplicity": normalize_multiplicity(row.get("cardinality", "")),
                "domain_name": "",
                "definition": row.get("description", ""),
                "module": "en16931",
                "class_term": class_term,
                "id": row_id,
                "path": path,
                "semantic_path": sem_path,
                "label_local": row.get("label_local", ""),
                "definition_local": row.get("definition_local", ""),
                "element": row.get("element_override", ""),
                "xpath": row.get("xpath", ""),
            }
        )

    effective_levels = lhm_effective_levels(lhm_rows)
    for row in lhm_rows:
        row["lhm_level"] = effective_levels.get(row.get("id", ""), "")

    generated_elements = unique_element_names(lhm_rows)
    for row in lhm_rows:
        if not row.get("element"):
            row["element"] = generated_elements.get(row.get("id", ""), "")

    validate_unique_elements(lhm_rows)
    validate_multiplicities(lhm_rows)
    write_rows(output_csv, LHM_FIELDS, lhm_rows)
    print(f"Wrote generated LHM CSV: {output_csv}")


def validate_unique_elements(rows: List[Dict[str, str]]) -> None:
    seen: Dict[str, str] = {}
    duplicates: List[str] = []
    for row in rows:
        element = row.get("element", "")
        if not element:
            continue
        if element in seen:
            duplicates.append(f"{element} ({seen[element]}, {row.get('id', '')})")
        else:
            seen[element] = row.get("id", "")
    if duplicates:
        raise ValueError("Duplicate LHM element values: " + "; ".join(duplicates))


def validate_multiplicities(rows: List[Dict[str, str]]) -> None:
    invalid = [
        f"{row.get('id', '')}={row.get('multiplicity', '')}"
        for row in rows
        if row.get("id", "").startswith(("BG-", "BT-"))
        and row.get("multiplicity", "") not in ALLOWED_MULTIPLICITIES
    ]
    if invalid:
        raise ValueError(
            "LHM multiplicity must be one of "
            + ", ".join(sorted(ALLOWED_MULTIPLICITIES))
            + ": "
            + "; ".join(invalid)
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build LHM CSV from an editable source CSV.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init-source", help="Create an editable source CSV from an LHM CSV.")
    init_parser.add_argument("lhm_csv", type=Path)
    init_parser.add_argument("source_csv", type=Path)

    build_parser = subparsers.add_parser("build", help="Generate an LHM CSV from the editable source CSV.")
    build_parser.add_argument("source_csv", type=Path)
    build_parser.add_argument("output_csv", type=Path)

    args = parser.parse_args()
    if args.command == "init-source":
        source_from_lhm(args.lhm_csv, args.source_csv)
    elif args.command == "build":
        build_lhm(args.source_csv, args.output_csv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
