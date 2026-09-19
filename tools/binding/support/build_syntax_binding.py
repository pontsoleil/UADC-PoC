#!/usr/bin/env python3
# coding: utf-8
"""
Build a syntax binding CSV from a semantic_path/xpath binding table.

Purpose:
    Produce a UADA syntax binding file from simple semantic_path and XPath pairs
    so XML-to-CSV conversion scripts can use a consistent binding layout.

Processing overview:
    The script validates the source binding CSV, derives stable output column
    names from semantic paths, and writes either a compact three-column binding
    file or an LHM/HMD-style binding CSV with class and attribute rows.

Command-line arguments:
    bindings_csv: Input binding definition CSV containing semantic_path and xpath.
    -o, --output: Output syntax binding CSV path.
    --simple: Write only column, semantic_path, and xpath columns.
    -e, --encoding: CSV encoding used for input and output.

Results:
    Writes the syntax binding CSV and prints the number of generated rows.
    Returns exit code 0 on success and 1 on validation or conversion failure.

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
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


LHM_HEADER = [
    "sequence",
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
    "semantic_path",
    "label_local",
    "definition_local",
    "element",
    "xpath",
]


def semantic_path_to_column(semantic_path: str) -> str:
    """
    Derive a stable CSV column name from a semantic path.

    Args:
        semantic_path: Input value used by semantic_path_to_column.

    Returns:
        Result produced by semantic_path_to_column.
    """
    path = semantic_path.strip()
    path = re.sub(r"^\$\.?", "", path)
    path = re.sub(r"^Invoice\.?", "", path)
    parts = []
    for raw_part in path.split("."):
        if not raw_part:
            continue
        predicate_values = re.findall(r"\[\?@[^=]+=(.*?)\]", raw_part)
        part = re.sub(r"\[\?@[^]]+\]", "", raw_part)
        if predicate_values:
            parts.extend(clean_token(value) for value in predicate_values)
        if part:
            parts.append(clean_token(part))
    column = "_".join(part for part in parts if part)
    return column or "value"


def split_semantic_path(semantic_path: str) -> List[str]:
    """
    Split a semantic path while preserving predicate expressions.

    Args:
        semantic_path: Input value used by split_semantic_path.

    Returns:
        Result produced by split_semantic_path.
    """
    path = semantic_path.strip()
    path = re.sub(r"^\$\.?", "", path)
    if not path:
        return []
    parts: List[str] = []
    current = []
    bracket_depth = 0
    for char in path:
        if char == "[":
            bracket_depth += 1
        elif char == "]":
            bracket_depth -= 1
        if char == "." and bracket_depth == 0:
            parts.append("".join(current))
            current = []
        else:
            current.append(char)
    if current:
        parts.append("".join(current))
    return parts


def segment_label(segment: str) -> str:
    """
    Return the display label portion of a semantic path segment.

    Args:
        segment: Input value used by segment_label.

    Returns:
        Result produced by segment_label.
    """
    segment = re.sub(r"\[\?@[^]]+\]", "", segment)
    if ":" in segment:
        segment = segment.split(":", 1)[1]
    return segment


def segment_element(segment: str) -> str:
    """
    Return the normalized element token for a semantic path segment.

    Args:
        segment: Input value used by segment_element.

    Returns:
        Result produced by segment_element.
    """
    return clean_token(segment_label(segment))


def clean_token(value: str) -> str:
    """
    Normalize text into a safe identifier token.

    Args:
        value: Input value used by clean_token.

    Returns:
        Result produced by clean_token.
    """
    value = value.strip().strip("'\"")
    value = re.sub(r"[^0-9A-Za-z_]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    if value and value[0].isdigit():
        value = "n_" + value
    return value


def unique_name(name: str, used: Dict[str, int]) -> str:
    """
    Return a unique name by adding a numeric suffix when needed.

    Args:
        name: Input value used by unique_name.
        used: Input value used by unique_name.

    Returns:
        Result produced by unique_name.
    """
    if name not in used:
        used[name] = 1
        return name
    used[name] += 1
    return f"{name}_{used[name]}"


def read_source_rows(source: Path, encoding: str) -> List[Dict[str, str]]:
    """
    Read and validate source semantic_path/xpath binding rows.

    Args:
        source: Input value used by read_source_rows.
        encoding: Input value used by read_source_rows.

    Returns:
        Result produced by read_source_rows.
    """
    with source.open(newline="", encoding=encoding) as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("Binding table has no header.")
        missing = {"semantic_path", "xpath"} - set(name.lstrip("\ufeff") for name in reader.fieldnames)
        if missing:
            raise ValueError(f"Missing required column(s): {', '.join(sorted(missing))}")

        source_rows: List[Dict[str, str]] = []
        for row in reader:
            normalized = {key.lstrip("\ufeff"): (value or "").strip() for key, value in row.items()}
            semantic_path = normalized.get("semantic_path", "")
            xpath = normalized.get("xpath", "")
            if not semantic_path and not xpath:
                continue
            if not semantic_path or not xpath:
                raise ValueError(f"Incomplete binding row: {row!r}")
            source_rows.append({"semantic_path": semantic_path, "xpath": xpath})
    return source_rows


def build_simple_rows(source_rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Build compact syntax binding rows.

    Args:
        source_rows: Input value used by build_simple_rows.

    Returns:
        Result produced by build_simple_rows.
    """
    rows: List[Dict[str, str]] = []
    used: Dict[str, int] = {}
    for row in source_rows:
        column = unique_name(semantic_path_to_column(row["semantic_path"]), used)
        rows.append({"column": column, "semantic_path": row["semantic_path"], "xpath": row["xpath"]})
    return rows


def build_lhm_rows(source_rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Build LHM/HMD-style syntax binding rows.

    Args:
        source_rows: Input value used by build_lhm_rows.

    Returns:
        Result produced by build_lhm_rows.
    """
    rows: List[Dict[str, str]] = []
    seen_classes: Dict[str, str] = {}
    used_elements: Dict[str, int] = {}
    sequence = 1

    def add_class(parts: List[str]) -> None:
        """
        Add one generated LHM class row if it has not already been created.

        Args:
            parts: Input value used by add_class.

        Returns:
            Result produced by add_class.
        """
        nonlocal sequence
        semantic_path = "$." + ".".join(parts)
        if semantic_path in seen_classes:
            return
        level = len(parts)
        element = unique_name(segment_element(parts[-1]), used_elements)
        record_id = f"C{sequence:04d}"
        seen_classes[semantic_path] = record_id
        rows.append(
            {
                "sequence": str(sequence),
                "level": str(level),
                "lhm_level": str(level),
                "type": "C",
                "identifier": "",
                "name": segment_label(parts[-1]),
                "datatype": "",
                "multiplicity": "1..*",
                "domain_name": "",
                "definition": "",
                "module": "syntax",
                "class_term": segment_label(parts[-1]),
                "id": record_id,
                "semantic_path": semantic_path,
                "label_local": "",
                "definition_local": "",
                "element": element,
                "xpath": "",
            }
        )
        sequence += 1

    for source_row in source_rows:
        parts = split_semantic_path(source_row["semantic_path"])
        if len(parts) < 2:
            continue
        for depth in range(1, len(parts)):
            add_class(parts[:depth])

        element = unique_name(semantic_path_to_column(source_row["semantic_path"]), used_elements)
        parent_parts = parts[:-1]
        record_id = f"A{sequence:04d}"
        rows.append(
            {
                "sequence": str(sequence),
                "level": str(len(parts)),
                "lhm_level": str(len(parts)),
                "type": "A",
                "identifier": "",
                "name": segment_label(parts[-1]),
                "datatype": "Text",
                "multiplicity": "0..1",
                "domain_name": "",
                "definition": "",
                "module": "syntax",
                "class_term": segment_label(parent_parts[-1]) if parent_parts else "",
                "id": record_id,
                "semantic_path": source_row["semantic_path"],
                "label_local": "",
                "definition_local": "",
                "element": element,
                "xpath": source_row["xpath"],
            }
        )
        sequence += 1
    return rows


def build_syntax_bindings(source: Path, output: Path, encoding: str, simple: bool) -> int:
    """
    Generate and write a syntax binding CSV.

    Args:
        source: Input value used by build_syntax_bindings.
        output: Input value used by build_syntax_bindings.
        encoding: Input value used by build_syntax_bindings.
        simple: Input value used by build_syntax_bindings.

    Returns:
        Result produced by build_syntax_bindings.
    """
    source_rows = read_source_rows(source, encoding)
    rows = build_simple_rows(source_rows) if simple else build_lhm_rows(source_rows)
    fieldnames = ["column", "semantic_path", "xpath"] if simple else LHM_HEADER

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding=encoding) as f:
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
    parser = argparse.ArgumentParser(
        description="Build syntax binding CSV from semantic_path/xpath bindings."
    )
    parser.add_argument("bindings_csv", type=Path, help="Input binding definition CSV")
    parser.add_argument("-o", "--output", required=True, type=Path, help="Output syntax binding CSV")
    parser.add_argument("--simple", action="store_true", help="Write column,semantic_path,xpath only")
    parser.add_argument("-e", "--encoding", default="utf-8-sig", help="CSV encoding")
    args = parser.parse_args()

    try:
        count = build_syntax_bindings(args.bindings_csv, args.output, args.encoding, args.simple)
    except Exception as exc:
        print(f"build_syntax_binding.py: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {count} syntax binding row(s) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
