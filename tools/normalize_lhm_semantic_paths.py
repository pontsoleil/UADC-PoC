#!/usr/bin/env python3
# coding: utf-8
"""
Normalize LHM semantic_path values from business terms.

Purpose:
    Rebuild LHM semantic_path values from row names and hierarchy paths so the
    LHM CSV can be used consistently by UADA binding and conversion tools.

Processing overview:
    The script converts each row name to lowerCamelCaseConcatenated, follows the
    path column to assemble hierarchical semantic path segments, updates the
    semantic_path column, and writes the result in place or to a new file.

Command-line arguments:
    input_csv: Input LHM CSV file.
    -o, --output: Output LHM CSV path; defaults to overwriting input_csv.
    -e, --encoding: CSV encoding used for input and output.

Results:
    Writes the normalized LHM CSV and prints the number of processed rows.
    Returns exit code 0 on success and 1 on failure.

Copyright 2026 Sambuichi Professional Engineers Office
Designed by SAMBUICHI, Nobuyuki
Produced by ChatGPT & Codex, edited by  SAMBUICHI, Nobuyuki
MIT License
CC-BY-NC
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Dict, List


def lower_camel_case_concatenated(term: str) -> str:
    """
    Convert a business term to lowerCamelCaseConcatenated.

    Args:
        term: Input value used by lower_camel_case_concatenated.

    Returns:
        Result produced by lower_camel_case_concatenated.
    """
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
    """
    Update semantic_path values for in-memory LHM rows.

    Args:
        rows: Input value used by normalize_rows.

    Returns:
        Result produced by normalize_rows.
    """
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
    """
    Normalize semantic_path values in an LHM CSV file.

    Args:
        input_csv: Input value used by normalize_file.
        output_csv: Input value used by normalize_file.
        encoding: Input value used by normalize_file.

    Returns:
        Result produced by normalize_file.
    """
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
    """
    Parse command-line arguments, run the script workflow, and return an exit code.

    Args:
        None.

    Returns:
        Process exit status: 0 for success and 1 for handled errors where applicable.
    """
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
