# SPDX-License-Identifier: MIT
"""Selector-aware effective multiplicity derivation for one-HMD/one-DTS generation."""

from __future__ import annotations

import csv
import json
from collections import Counter, OrderedDict
from pathlib import Path
from typing import Mapping


class SelectorMultiplicityError(ValueError):
    pass


def _error(code: str, detail: str) -> SelectorMultiplicityError:
    return SelectorMultiplicityError(f"{code}: {detail}")




# ---------------------------------------------------------------------------
# Limited Semantic Path predicate grammar shared by current Binding runtimes.
#
# Grammar (intentionally small):
#   expr  := or_expr
#   or_expr := and_expr ("or" and_expr)*
#   and_expr := unary_expr ("and" unary_expr)*
#   unary_expr := "not" unary_expr | "(" expr ")" | atom
#   atom := property | property "=" quoted_literal
#
# Comparison operators other than equality, functions, arithmetic, axes and
# cross-occurrence references are outside the current contract.
# ---------------------------------------------------------------------------

PredicateAst = tuple


def _predicate_tokens(expression: str) -> list[tuple[str, str]]:
    tokens: list[tuple[str, str]] = []
    i = 0
    n = len(expression)
    while i < n:
        ch = expression[i]
        if ch.isspace():
            i += 1
            continue
        if ch in "()=":
            tokens.append((ch, ch))
            i += 1
            continue
        if ch in {"'", '"'}:
            quote = ch
            i += 1
            value = []
            escaped = False
            while i < n:
                c = expression[i]
                if escaped:
                    value.append(c)
                    escaped = False
                    i += 1
                    continue
                if c == "\\":
                    escaped = True
                    i += 1
                    continue
                if c == quote:
                    i += 1
                    break
                value.append(c)
                i += 1
            else:
                raise _error("INVALID_SEMANTIC_PATH_SELECTOR", expression)
            tokens.append(("STRING", "".join(value)))
            continue
        if ch.isalpha() or ch == "_":
            start = i
            i += 1
            while i < n and (expression[i].isalnum() or expression[i] in "_-"):
                i += 1
            word = expression[start:i]
            lower = word.lower()
            if lower in {"and", "or", "not"}:
                tokens.append((lower.upper(), lower))
            else:
                tokens.append(("NAME", word))
            continue
        raise _error("INVALID_SEMANTIC_PATH_SELECTOR", expression)
    tokens.append(("EOF", ""))
    return tokens


class _PredicateParser:
    def __init__(self, expression: str):
        self.expression = expression
        self.tokens = _predicate_tokens(expression)
        self.index = 0

    def peek(self, kind: str) -> bool:
        return self.tokens[self.index][0] == kind

    def take(self, kind: str) -> tuple[str, str]:
        token = self.tokens[self.index]
        if token[0] != kind:
            raise _error("INVALID_SEMANTIC_PATH_SELECTOR", self.expression)
        self.index += 1
        return token

    def parse(self) -> PredicateAst:
        node = self.parse_or()
        if not self.peek("EOF"):
            raise _error("INVALID_SEMANTIC_PATH_SELECTOR", self.expression)
        return node

    def parse_or(self) -> PredicateAst:
        nodes = [self.parse_and()]
        while self.peek("OR"):
            self.take("OR")
            nodes.append(self.parse_and())
        return nodes[0] if len(nodes) == 1 else ("or", tuple(nodes))

    def parse_and(self) -> PredicateAst:
        nodes = [self.parse_unary()]
        while self.peek("AND"):
            self.take("AND")
            nodes.append(self.parse_unary())
        return nodes[0] if len(nodes) == 1 else ("and", tuple(nodes))

    def parse_unary(self) -> PredicateAst:
        if self.peek("NOT"):
            self.take("NOT")
            return ("not", self.parse_unary())
        if self.peek("("):
            self.take("(")
            node = self.parse_or()
            self.take(")")
            return node
        return self.parse_atom()

    def parse_atom(self) -> PredicateAst:
        name = self.take("NAME")[1]
        if self.peek("="):
            self.take("=")
            value = self.take("STRING")[1]
            return ("eq", name, value)
        return ("present", name)


def parse_predicate(expression: str) -> PredicateAst:
    expression = (expression or "").strip()
    if not expression:
        raise _error("INVALID_SEMANTIC_PATH_SELECTOR", expression)
    return _PredicateParser(expression).parse()


def render_predicate(node: PredicateAst) -> str:
    kind = node[0]
    if kind == "eq":
        value = str(node[2]).replace("\\", "\\\\").replace("'", "\\'")
        return f"{node[1]}='{value}'"
    if kind == "present":
        return str(node[1])
    if kind == "not":
        child = render_predicate(node[1])
        return f"not ({child})"
    if kind in {"and", "or"}:
        joiner = f" {kind} "
        parts = []
        for child in node[1]:
            rendered = render_predicate(child)
            if child[0] in {"and", "or"} and child[0] != kind:
                rendered = f"({rendered})"
            parts.append(rendered)
        # AND/OR are commutative in the supported Boolean subset. Canonicalise
        # order so syntactic reordering does not create a false new selector.
        return joiner.join(sorted(parts))
    raise _error("INVALID_SEMANTIC_PATH_SELECTOR", repr(node))


def predicate_properties(node: PredicateAst) -> set[str]:
    kind = node[0]
    if kind in {"eq", "present"}:
        return {str(node[1])}
    if kind == "not":
        return predicate_properties(node[1])
    if kind in {"and", "or"}:
        result: set[str] = set()
        for child in node[1]:
            result.update(predicate_properties(child))
        return result
    raise _error("INVALID_SEMANTIC_PATH_SELECTOR", repr(node))


def implied_equalities(node: PredicateAst) -> dict[str, str] | None:
    """Return deterministic equality facts only for pure equality/AND predicates.

    OR, NOT and presence predicates are selection-only and therefore do not imply
    one value that may be materialised as a discriminator fact.
    """
    kind = node[0]
    if kind == "eq":
        return {str(node[1]): str(node[2])}
    if kind == "and":
        result: dict[str, str] = {}
        for child in node[1]:
            part = implied_equalities(child)
            if part is None:
                return None
            for key, value in part.items():
                if key in result and result[key] != value:
                    raise _error("CONTRADICTORY_SEMANTIC_PATH_SELECTOR", f"{key}: {result[key]} != {value}")
                result[key] = value
        return result
    return None


def evaluate_predicate(node: PredicateAst, values: Mapping[str, str | None]) -> bool | None:
    """Evaluate with a conservative three-valued rule.

    Missing equality operands evaluate UNKNOWN rather than false so that
    `not(property='x')` does not accidentally select an occurrence that has no
    property at all. Explicit `not property` remains the way to select absence.
    A Binding matches only when the final result is True.
    """
    kind = node[0]
    if kind == "eq":
        value = values.get(str(node[1]))
        return None if value is None else value == str(node[2])
    if kind == "present":
        return bool(values.get(str(node[1])))
    if kind == "not":
        child = evaluate_predicate(node[1], values)
        return None if child is None else not child
    if kind == "and":
        unknown = False
        for child in node[1]:
            value = evaluate_predicate(child, values)
            if value is False:
                return False
            if value is None:
                unknown = True
        return None if unknown else True
    if kind == "or":
        unknown = False
        for child in node[1]:
            value = evaluate_predicate(child, values)
            if value is True:
                return True
            if value is None:
                unknown = True
        return None if unknown else False
    raise _error("INVALID_SEMANTIC_PATH_SELECTOR", repr(node))


def parse_binding_path(path: str) -> tuple[str, list[tuple[str, PredicateAst]]]:
    """Return selector-neutral path and predicates scoped to their Class segment."""
    selected: list[tuple[str, PredicateAst]] = []
    base_segments: list[str] = []
    for raw_segment in split_segments(path):
        name, expressions = _parse_segment_expressions(raw_segment, path)
        base_segments.append(name)
        owner = ".".join(base_segments)
        for expression in expressions:
            if expression.isdigit():
                # [n] remains an occurrence-index selector; predicate evaluation is separate.
                continue
            selected.append((owner, parse_predicate(expression)))
    return ".".join(base_segments), selected


def _parse_segment_expressions(segment: str, full_path: str) -> tuple[str, tuple[str, ...]]:
    name, expressions, index = [], [], 0
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
        expressions.append(expression)
    return "".join(name), tuple(expressions)


def normalize_semantic_path(path: str) -> str:
    parts: list[str] = []
    for raw_segment in split_segments(path):
        name, expressions = _parse_segment_expressions(raw_segment, path)
        rendered = []
        for expression in expressions:
            if expression.isdigit():
                rendered.append(f"[{int(expression)}]")
            else:
                rendered.append(f"[{render_predicate(parse_predicate(expression))}]")
        parts.append(name + "".join(rendered))
    return ".".join(parts)


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
    name, expressions = _parse_segment_expressions(segment, full_path)
    normalized: list[str] = []
    for expression in expressions:
        if expression.isdigit():
            normalized.append(str(int(expression)))
        else:
            normalized.append(render_predicate(parse_predicate(expression)))
    return name, tuple(sorted(normalized))


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
                    normalized_value = normalize_semantic_path(value)
                    key = (column, normalized_value)
                    counts[key] += 1
                    origins.setdefault(key, f"{path}:{line}")
                    evidence.append({"file": str(path), "line": str(line), "column": column, "path": normalized_value})
    duplicates = [(column, value) for (column, value), count in counts.items() if count > 1]
    if duplicates:
        column, value = sorted(duplicates)[0]
        raise _error("DUPLICATE_SELECTOR_QUALIFIED_PATH", f"{origins[(column, value)]}:{column}:{value}")
    return evidence


def selector_evidence_from_rows(rows: list[dict[str, str]], origin: str = "<rows>") -> list[dict[str, str]]:
    """Collect selector-qualified semantic paths from supplied rows only.

    This is used by runtimes that intentionally restrict multiplicity evidence
    to executable Binding rows. It preserves the same duplicate and syntax
    checks as :func:`read_selector_paths` without re-reading non-executable
    rows from the source Binding file.
    """
    if not rows:
        return []
    semantic_columns = [name for name in rows[0] if name.endswith("semantic_path")]
    if not semantic_columns:
        raise _error("SELECTOR_EVIDENCE_SEMANTIC_PATH_MISSING", origin)
    evidence = []
    counts: Counter[tuple[str, str]] = Counter()
    origins: dict[tuple[str, str], str] = {}
    for line, row in enumerate(rows, 2):
        for column in semantic_columns:
            value = (row.get(column) or "").strip()
            if "[" not in value:
                continue
            parse_semantic_path(value)
            normalized_value = normalize_semantic_path(value)
            key = (column, normalized_value)
            counts[key] += 1
            origins.setdefault(key, f"{origin}:{line}")
            evidence.append({"file": origin, "line": str(line), "column": column, "path": normalized_value})
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


def _derive_from_evidence(records: list[dict[str, str]], evidence: list[dict[str, str]],
                          dts_root: str) -> list[dict[str, str]]:
    by_path = {record["semantic_path"]: record for record in records}
    class_paths = [record["semantic_path"] for record in records if record["type"] == "C"]
    root_path = min(class_paths, key=lambda path: (path.count("."), len(path)))
    groups: OrderedDict[tuple[str, str, str, str], dict[str, object]] = OrderedDict()
    for item in evidence:
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


def derive(records: list[dict[str, str]], evidence_paths: list[str | Path], dts_root: str,
           encoding: str = "utf-8-sig") -> list[dict[str, str]]:
    """Derive multiplicity from every selector path in the supplied evidence files."""
    return _derive_from_evidence(records, read_selector_paths(evidence_paths, encoding), dts_root)


def derive_from_rows(records: list[dict[str, str]], evidence_rows: list[dict[str, str]],
                     dts_root: str, origin: str = "<rows>") -> list[dict[str, str]]:
    """Derive multiplicity from selector paths in the supplied rows only."""
    return _derive_from_evidence(records, selector_evidence_from_rows(evidence_rows, origin), dts_root)


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
