#!/usr/bin/env python3
# coding: utf-8
"""
Convert structured CSV to flat CSV using a semantic binding CSV.

Purpose:
    Flatten UADA structured CSV data into a conventional flat CSV layout by
    applying semantic bindings between source columns and target columns.

Processing overview:
    The script reads semantic binding rows, accepts several legacy column names,
    maps each source structured CSV row into target flat CSV columns, applies
    fixed fallback values when configured, and writes the flat CSV output.

Command-line arguments:
    structured_csv: Input structured CSV file.
    -b, --binding: Semantic binding CSV file.
    -o, --output: Output flat CSV path.
    -e, --encoding: CSV encoding used for input and output.

Results:
    Writes the flat CSV and prints the output row and column counts.
    Returns exit code 0 on success and 1 on failure.

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
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


def first_present(row: Dict[str, str], names: Iterable[str]) -> str:
    """
    Return the first non-empty value from a set of candidate field names.

    Args:
        row: Input value used by first_present.
        names: Input value used by first_present.

    Returns:
        Result produced by first_present.
    """
    for name in names:
        value = row.get(name)
        if value:
            return value.strip()
    return ""


def tail(path: str) -> str:
    """
    Return the final segment of a slash- or dot-delimited path.

    Args:
        path: Input value used by tail.

    Returns:
        Result produced by tail.
    """
    if not path:
        return ""
    path = path.strip().strip("/")
    if "/" in path:
        return path.rsplit("/", 1)[-1]
    if "." in path:
        return path.rsplit(".", 1)[-1]
    return path


def read_bindings(binding_csv: Path, encoding: str) -> List[Dict[str, str]]:
    """
    Read usable binding rows from a CSV file.

    Args:
        binding_csv: Input value used by read_bindings.
        encoding: Input value used by read_bindings.

    Returns:
        Result produced by read_bindings.
    """
    with binding_csv.open(newline="", encoding=encoding) as f:
        rows = [dict(row) for row in csv.DictReader(f)]
    bindings = []
    for row in rows:
        target = first_present(row, ("flat_column", "target_column", "column", "name"))
        source = first_present(
            row,
            ("source_column", "structured_column", "source", "value", "semPath", "semantic_path", "path", "id"),
        )
        fixed = first_present(row, ("fixedValue", "fixed_value", "default"))
        if target and (source or fixed):
            row["_target"] = target
            row["_source"] = tail(source)
            row["_fixed"] = fixed
            bindings.append(row)
    return bindings


def convert_structured_to_flat(
    structured_csv: Path,
    binding_csv: Path,
    out_csv: Path,
    encoding: str,
) -> Tuple[int, List[str]]:
    """
    Convert a structured CSV file to a flat CSV file.

    Args:
        structured_csv: Input value used by convert_structured_to_flat.
        binding_csv: Input value used by convert_structured_to_flat.
        out_csv: Input value used by convert_structured_to_flat.
        encoding: Input value used by convert_structured_to_flat.

    Returns:
        Result produced by convert_structured_to_flat.
    """
    bindings = read_bindings(binding_csv, encoding)
    if not bindings:
        raise ValueError("No usable semantic bindings found.")

    with structured_csv.open(newline="", encoding=encoding) as f:
        source_rows = list(csv.DictReader(f))

    fieldnames = [binding["_target"] for binding in bindings]
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding=encoding) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for source_row in source_rows:
            out_row = {}
            for binding in bindings:
                value = binding["_fixed"]
                if binding["_source"]:
                    value = source_row.get(binding["_source"], value)
                out_row[binding["_target"]] = value
            writer.writerow(out_row)
    return len(source_rows), fieldnames


def main() -> int:
    """
    Parse command-line arguments, run the script workflow, and return an exit code.

    Args:
        None.

    Returns:
        Process exit status: 0 for success and 1 for handled errors where applicable.
    """
    parser = argparse.ArgumentParser(description="Convert structured CSV to flat CSV using semantic bindings.")
    parser.add_argument("structured_csv", type=Path, help="Input structured CSV")
    parser.add_argument("-b", "--binding", required=True, type=Path, help="Semantic binding CSV")
    parser.add_argument("-o", "--output", required=True, type=Path, help="Output flat CSV")
    parser.add_argument("-e", "--encoding", default="utf-8-sig", help="CSV encoding")
    args = parser.parse_args()

    try:
        count, fields = convert_structured_to_flat(
            args.structured_csv, args.binding, args.output, args.encoding
        )
    except Exception as exc:
        print(f"semantic_binding.py: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {count} row(s), {len(fields)} column(s) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
