#!/usr/bin/env python3
# coding: utf-8
"""
Normalize LHM class_term and element columns.

Rules:
- BG rows: class_term is the row's Business Term (`name`), singularized.
- BT rows: class_term is the nearest parent BG's Business Term, singularized.
- element is generated from semantic_path, starts with an uppercase letter, and
  is unique within the LHM. The shortest unique suffix of semantic_path is used.

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


def singularize(term: str) -> str:
    words = (term or "").split()
    if not words:
        return ""
    last = words[-1]
    lower = last.lower()
    irregular = {
        "properties": "property",
        "parties": "party",
        "entries": "entry",
        "currencies": "currency",
        "quantities": "quantity",
        "allowances": "allowance",
        "charges": "charge",
        "documents": "document",
        "terms": "term",
        "totals": "total",
        "instructions": "instruction",
        "details": "detail",
        "attributes": "attribute",
    }
    if lower in irregular:
        replacement = irregular[lower]
        words[-1] = replacement[:1].upper() + replacement[1:] if last[:1].isupper() else replacement
    elif lower.endswith("ies") and len(last) > 3:
        words[-1] = last[:-3] + ("Y" if last[-3:].isupper() else "y")
    elif lower.endswith("s") and not lower.endswith("ss"):
        words[-1] = last[:-1]
    return " ".join(words)


def semantic_segments(semantic_path: str) -> List[str]:
    path = (semantic_path or "").strip()
    if not path:
        return []
    path = re.sub(r"^\$\.?", "", path)
    return [part for part in path.split(".") if part]


def upper_camel(segment: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", segment or "")
    if not words:
        return ""
    value = "".join(word[:1].upper() + word[1:] for word in words)
    if value and value[0].isdigit():
        value = "N" + value
    return value


def suffix_element_name(segments: List[str], suffix_len: int) -> str:
    selected = segments[-suffix_len:] if suffix_len > 0 else segments[-1:]
    return "".join(upper_camel(segment) for segment in selected)


def unique_element_names(rows: List[Dict[str, str]]) -> Dict[str, str]:
    candidates: Dict[str, List[tuple[str, List[str]]]] = {}
    for row in rows:
        row_id = row.get("id", "")
        if not (row_id.startswith("BG-") or row_id.startswith("BT-")):
            continue
        segments = semantic_segments(row.get("semantic_path", ""))
        if not segments:
            segments = [row.get("name", "") or row_id]
        base = suffix_element_name(segments, 1)
        candidates.setdefault(base, []).append((row_id, segments))

    result: Dict[str, str] = {}
    used: set[str] = set()
    for base, items in candidates.items():
        if len(items) == 1 and base not in used:
            row_id, _ = items[0]
            result[row_id] = base
            used.add(base)
            continue
        for row_id, segments in items:
            chosen = ""
            for suffix_len in range(1, len(segments) + 1):
                candidate = suffix_element_name(segments, suffix_len)
                if candidate not in used and all(
                    suffix_element_name(other_segments, suffix_len) != candidate or other_id == row_id
                    for other_id, other_segments in items
                ):
                    chosen = candidate
                    break
            if not chosen:
                chosen = f"{suffix_element_name(segments, len(segments))}{row_id.replace('-', '')}"
            result[row_id] = chosen
            used.add(chosen)
    return result


def nearest_parent_bg(row: Dict[str, str]) -> str:
    row_id = row.get("id", "")
    if row_id.startswith("BG-"):
        return row_id
    parts = [part for part in (row.get("path") or "").split("/") if part]
    for part in reversed(parts):
        if part.startswith("BG-"):
            return part
    return ""


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
    parser = argparse.ArgumentParser(description="Normalize LHM class_term and element columns.")
    parser.add_argument("lhm_csv", type=Path)
    args = parser.parse_args()

    fieldnames, rows = read_rows(args.lhm_csv)
    name_by_id = {row.get("id", ""): row.get("name", "") for row in rows}
    element_by_id = unique_element_names(rows)
    updated = 0
    for row in rows:
        row_id = row.get("id", "")
        if not (row_id.startswith("BG-") or row_id.startswith("BT-")):
            continue
        bg_id = nearest_parent_bg(row)
        expected_class = singularize(name_by_id.get(bg_id, ""))
        expected_element = element_by_id.get(row_id, "")
        if row.get("class_term", "") != expected_class:
            row["class_term"] = expected_class
            updated += 1
        if row.get("element", "") != expected_element:
            row["element"] = expected_element
            updated += 1

    write_rows(args.lhm_csv, fieldnames, rows)
    print(f"Normalized class_term/element in {args.lhm_csv}; updated {updated} value(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
