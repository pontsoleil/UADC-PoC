#!/usr/bin/env python3
# coding: utf-8
"""
Normalize LHM semantic_path values from business terms.

Each semantic path element is generated from the row's business term (`name`)
using lowerCamelCaseConcatenated. The hierarchy is taken from the `path` column.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Dict, List


def lower_camel_case_concatenated(term: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", term or "")
    if not words:
        return "unnamed"
    first = words[0].lower()
    rest = [word[:1].upper() + word[1:].lower() for word in words[1:]]
    value = first + "".join(rest)
    if value[0].isdigit():
        value = "n" + value[:1].upper() + value[1:]
    return value


def normalize_rows(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    segment_by_id: Dict[str, str] = {}
    for row in rows:
        row_id = row.get("id", "")
        segment_by_id[row_id] = lower_camel_case_concatenated(row.get("name", ""))

    for row in rows:
        path_ids = [part for part in (row.get("path") or "").split("/") if part]
        segments = [segment_by_id[path_id] for path_id in path_ids if path_id in segment_by_id]
        if not segments:
            segments = [lower_camel_case_concatenated(row.get("name", ""))]
        row["semantic_path"] = "$." + ".".join(segments)
    return rows


def normalize_file(input_csv: Path, output_csv: Path, encoding: str) -> int:
    with input_csv.open(newline="", encoding=encoding) as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("LHM CSV has no header.")
        fieldnames = [name.lstrip("\ufeff") for name in reader.fieldnames]
        rows = [{key.lstrip("\ufeff"): value for key, value in row.items()} for row in reader]

    rows = normalize_rows(rows)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding=encoding) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize LHM semantic_path values.")
    parser.add_argument("input_csv", type=Path, help="Input LHM CSV")
    parser.add_argument("-o", "--output", type=Path, help="Output LHM CSV; defaults to in-place")
    parser.add_argument("-e", "--encoding", default="utf-8-sig", help="CSV encoding")
    args = parser.parse_args()

    output = args.output or args.input_csv
    try:
        count = normalize_file(args.input_csv, output, args.encoding)
    except Exception as exc:
        print(f"normalize_lhm_semantic_paths.py: {exc}", file=sys.stderr)
        return 1
    print(f"Normalized {count} row(s) in {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
