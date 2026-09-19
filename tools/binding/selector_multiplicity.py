# SPDX-License-Identifier: MIT
"""Selector-aware effective multiplicity derivation for one-HMD/one-DTS generation."""

from __future__ import annotations

import csv
import json
from collections import Counter, OrderedDict
from pathlib import Path


class SelectorMultiplicityError(ValueError):
    pass


def _error(code: str, detail: str) -> SelectorMultiplicityError:
    return SelectorMultiplicityError(f"{code}: {detail}")


def split_segments(path: str) -> list[str]:
    if not path or not path.startswith("$"):
        raise _error("INVALID_SEMANTIC_PATH_SELECTOR", repr(path))
    segments, token = [], []
    bracket_depth = paren_depth = 0
    quote = None
    escaped = False
    for char in path:
        if escaped:
            token.append(char)
            escaped = False
            continue
        if char == "\\" and quote:
            token.append(char)
            escaped = True
            continue
        if quote:
            token.append(char)
            if char == quote:
                quote = None
            continue
        if char in {'"', "'"}:
            quote = char
            token.append(char)
        elif char == "[":
            bracket_depth += 1
            token.append(char)
        elif char == "]":
            bracket_depth -= 1
            if bracket_depth < 0:
                raise _error("INVALID_SEMANTIC_PATH_SELECTOR", path)
            token.append(char)
        elif char == "(" and bracket_depth:
            paren_depth += 1
            token.append(char)
        elif char == ")" and bracket_depth:
            paren_depth -= 1
            if paren_depth < 0:
                raise _error("INVALID_SEMANTIC_PATH_SELECTOR", path)
            token.append(char)
        elif char == "." and bracket_depth == 0:
            if token:
                segments.append("".join(token))
                token = []
        else:
            token.append(char)
    if quote or bracket_depth or paren_depth:
        raise _error("INVALID_SEMANTIC_PATH_SELECTOR", path)
    if token:
        segments.append("".join(token))
    if not segments or segments[0] != "$" or any(not segment for segment in segments):
        raise _error("INVALID_SEMANTIC_PATH_SELECTOR", path)
    return segments


def parse_segment(segment: str, full_path: str) -> tuple[str, tuple[str, ...]]:
    name, selectors, index = [], [], 0
    while index < len(segment) and segment[index] != "[":
        name.append(segment[index])
        index += 1
    if not name:
        raise _error("INVALID_SEMANTIC_PATH_SELECTOR", full_path)
    while index < len(segment):
        if segment[index] != "[":
            raise _error("INVALID_SEMANTIC_PATH_SELECTOR", full_path)
        start = index + 1
        index += 1
        depth, quote, escaped = 1, None, False
        while index < len(segment) and depth:
            char = segment[index]
            if escaped:
                escaped = False
            elif char == "\\" and quote:
                escaped = True
            elif quote:
                if char == quote:
                    quote = None
            elif char in {'"', "'"}:
                quote = char
            elif char == "[":
                depth += 1
            elif char == "]":
                depth -= 1
            index += 1
        if depth or quote:
            raise _error("INVALID_SEMANTIC_PATH_SELECTOR", full_path)
        expression = segment[start:index - 1].strip()
        if not expression:
            raise _error("INVALID_SEMANTIC_PATH_SELECTOR", full_path)
        if expression.startswith("not("):
            if not expression.endswith(")") or not expression[4:-1].strip():
                raise _error("INVALID_SEMANTIC_PATH_SELECTOR", full_path)
            normalized = f"not({expression[4:-1].strip()})"
        elif "=" in expression:
            key, value = expression.split("=", 1)
            key, value = key.strip(), value.strip()
            if not key or len(value) < 2 or value[0] not in {'"', "'"} or value[-1] != value[0]:
                raise _error("INVALID_SEMANTIC_PATH_SELECTOR", full_path)
            normalized = f"{key}={value}"
        else:
            normalized = expression
        selectors.append(normalized)
    return "".join(name), tuple(sorted(selectors))


def parse_semantic_path(path: str) -> tuple[str, list[tuple[str, tuple[str, ...]]]]:
    base_segments, selected = [], []
    for raw_segment in split_segments(path):
        name, selectors = parse_segment(raw_segment, path)
        base_segments.append(name)
        if selectors:
            selected.append((".".join(base_segments), selectors))
    return ".".join(base_segments), selected


def read_selector_paths(paths: list[str | Path], encoding: str = "utf-8-sig") -> list[dict[str, str]]:
    evidence = []
    counts: Counter[tuple[str, str]] = Counter()
    origins: dict[tuple[str, str], str] = {}
    for supplied in paths:
        path = Path(supplied)
        with path.open("r", encoding=encoding, newline="") as handle:
            reader = csv.DictReader(handle)
            semantic_columns = [name for name in (reader.fieldnames or []) if name.endswith("semantic_path")]
            if not semantic_columns:
                raise _error("SELECTOR_EVIDENCE_SEMANTIC_PATH_MISSING", str(path))
            for line, row in enumerate(reader, 2):
                for column in semantic_columns:
                    value = (row.get(column) or "").strip()
                    if "[" not in value:
                        continue
                    parse_semantic_path(value)
                    key = (column, value)
                    counts[key] += 1
                    origins.setdefault(key, f"{path}:{line}")
                    evidence.append({"file": str(path), "line": str(line), "column": column, "path": value})
    duplicates = [(column, value) for (column, value), count in counts.items() if count > 1]
    if duplicates:
        column, value = sorted(duplicates)[0]
        raise _error("DUPLICATE_SELECTOR_QUALIFIED_PATH", f"{origins[(column, value)]}:{column}:{value}")
    return evidence


def effective_multiplicity(source: str) -> str:
    mapping = {"0..1": "0..*", "1": "1..*", "1..1": "1..*", "0..*": "0..*", "1..*": "1..*"}
    if source not in mapping:
        raise _error("UNSUPPORTED_SOURCE_MULTIPLICITY", source)
    return mapping[source]


def derive(records: list[dict[str, str]], evidence_paths: list[str | Path], dts_root: str,
           encoding: str = "utf-8-sig") -> list[dict[str, str]]:
    by_path = {record["semantic_path"]: record for record in records}
    class_paths = [record["semantic_path"] for record in records if record["type"] == "C"]
    root_path = min(class_paths, key=lambda path: (path.count("."), len(path)))
    groups: OrderedDict[tuple[str, str, str, str], dict[str, object]] = OrderedDict()
    for item in read_selector_paths(evidence_paths, encoding):
        _base, selected_segments = parse_semantic_path(item["path"])
        for selected_base, selectors in selected_segments:
            selected_record = by_path.get(selected_base)
            if selected_record and selected_record["type"] == "C":
                owner_path = selected_base
            elif selected_record:
                candidates = [path for path in class_paths if selected_base.startswith(path + ".")]
                if not candidates:
                    raise _error("SELECTOR_OCCURRENCE_OWNER_UNRESOLVED", item["path"])
                owner_path = max(candidates, key=len)
            else:
                # The evidence belongs to another HMD/DTS (for example the source side of a binding).
                if selected_base.startswith(root_path + "."):
                    raise _error("SELECTOR_OCCURRENCE_OWNER_UNRESOLVED", item["path"])
                continue
            owner = by_path[owner_path]
            selector = " && ".join(selectors)
            key = (dts_root, owner["module"], owner_path, selected_base)
            group = groups.setdefault(key, {"selectors": set(), "source_paths": set()})
            group["selectors"].add(selector)
            group["source_paths"].add(item["path"])

    diagnostics = []
    for (root, module, owner_path, base_path), group in groups.items():
        selectors = sorted(group["selectors"])
        if len(selectors) < 2:
            continue
        owner = by_path.get(owner_path)
        if owner is None or owner["type"] != "C":
            raise _error("SELECTOR_OCCURRENCE_OWNER_UNRESOLVED", owner_path)
        source = owner["multiplicity"]
        effective = effective_multiplicity(source)
        owner["source_multiplicity"] = source
        owner["effective_multiplicity"] = effective
        owner["effective_multiplicity_reason"] = "multiple selector-qualified occurrences"
        owner["multiplicity"] = effective
        diagnostics.append({
            "dts_root": root, "module": module, "occurrence_owner": owner["local_name"],
            "occurrence_owner_semantic_path": owner_path, "base_semantic_path": base_path,
            "source_multiplicity": source, "effective_multiplicity": effective,
            "effective_multiplicity_reason": "multiple selector-qualified occurrences",
            "distinct_selector_count": str(len(selectors)), "selectors": json.dumps(selectors, ensure_ascii=False),
            "source_paths": json.dumps(sorted(group["source_paths"]), ensure_ascii=False),
            "dimension": f"d_{owner['element_id']}",
        })
    return diagnostics


def validate_generated_dimensions(package_root: str | Path, rows: list[dict[str, str]]) -> None:
    root = Path(package_root)
    schemas = "\n".join(path.read_text(encoding="utf-8-sig") for path in sorted((root / "oim").rglob("*.xsd")))
    linkbases = "\n".join(path.read_text(encoding="utf-8-sig") for path in sorted((root / "oim").rglob("*.xml")))
    for row in rows:
        dimension = row["dimension"]
        if (
            f'name="{dimension}"' not in schemas
            or f'#{dimension}"' not in linkbases
            or f'xlink:to="{dimension}"' not in linkbases
        ):
            raise _error("EFFECTIVE_REPEATABLE_DIMENSION_MISSING", dimension)


def write_diagnostics(path: str | Path, rows: list[dict[str, str]]) -> None:
    fields = ["dts_root", "module", "occurrence_owner", "occurrence_owner_semantic_path",
              "base_semantic_path", "source_multiplicity", "effective_multiplicity",
              "effective_multiplicity_reason", "distinct_selector_count", "selectors",
              "source_paths", "dimension"]
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda row: (row["dts_root"], row["module"], row["occurrence_owner_semantic_path"])))
