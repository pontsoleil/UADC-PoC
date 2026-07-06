#!/usr/bin/env python3
# coding: utf-8
"""
Convert structured CSV to flat CSV using a semantic binding CSV.

The semantic binding CSV maps structured CSV columns to flat CSV columns.
Supported columns:

    column / flat_column / target_column       output flat CSV column
    source_column / structured_column / value  input structured CSV column
    fixedValue / fixed_value / default         fixed or fallback value
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


def first_present(row: Dict[str, str], names: Iterable[str]) -> str:
    for name in names:
        value = row.get(name)
        if value:
            return value.strip()
    return ""


def tail(path: str) -> str:
    if not path:
        return ""
    path = path.strip().strip("/")
    if "/" in path:
        return path.rsplit("/", 1)[-1]
    if "." in path:
        return path.rsplit(".", 1)[-1]
    return path


def read_bindings(binding_csv: Path, encoding: str) -> List[Dict[str, str]]:
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
