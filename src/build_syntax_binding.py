#!/usr/bin/env python3
# coding: utf-8
"""
Build a syntax binding CSV from a semantic_path/xpath binding table.

Input columns:
    semantic_path,xpath

Default output columns follow the LHM/HMD style used in XBRL-GL-2026:
    sequence,level,lhm_level,type,identifier,name,datatype,multiplicity,domain_name,
    definition,module,class_term,id,path,semantic_path,abbreviation_path,
    label_local,definition_local,element,xpath

Use --simple to write only:
    column,semantic_path,xpath

The generated column name is derived from the semantic path and includes
predicate values so repeated names such as partyName remain unique.
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
    "path",
    "semantic_path",
    "abbreviation_path",
    "label_local",
    "definition_local",
    "element",
    "xpath",
]


def semantic_path_to_column(semantic_path: str) -> str:
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
    segment = re.sub(r"\[\?@[^]]+\]", "", segment)
    if ":" in segment:
        segment = segment.split(":", 1)[1]
    return segment


def segment_element(segment: str) -> str:
    return clean_token(segment_label(segment))


def clean_token(value: str) -> str:
    value = value.strip().strip("'\"")
    value = re.sub(r"[^0-9A-Za-z_]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    if value and value[0].isdigit():
        value = "n_" + value
    return value


def unique_name(name: str, used: Dict[str, int]) -> str:
    if name not in used:
        used[name] = 1
        return name
    used[name] += 1
    return f"{name}_{used[name]}"


def read_source_rows(source: Path, encoding: str) -> List[Dict[str, str]]:
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
    rows: List[Dict[str, str]] = []
    used: Dict[str, int] = {}
    for row in source_rows:
        column = unique_name(semantic_path_to_column(row["semantic_path"]), used)
        rows.append({"column": column, "semantic_path": row["semantic_path"], "xpath": row["xpath"]})
    return rows


def build_lhm_rows(source_rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    seen_classes: Dict[str, str] = {}
    used_elements: Dict[str, int] = {}
    sequence = 1

    def add_class(parts: List[str]) -> None:
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
                "path": "/" + "/".join(seen_classes["$." + ".".join(parts[:i])] for i in range(1, len(parts) + 1)),
                "semantic_path": semantic_path,
                "abbreviation_path": ".".join(segment_element(part) for part in parts),
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
        parent_path = "$." + ".".join(parent_parts)
        parent_id = seen_classes.get(parent_path, "")
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
                "path": f"/{parent_id}/{record_id}" if parent_id else f"/{record_id}",
                "semantic_path": source_row["semantic_path"],
                "abbreviation_path": ".".join(segment_element(part) for part in parts),
                "label_local": "",
                "definition_local": "",
                "element": element,
                "xpath": source_row["xpath"],
            }
        )
        sequence += 1
    return rows


def build_syntax_bindings(source: Path, output: Path, encoding: str, simple: bool) -> int:
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
