#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Generic reversible semantic binding runtime.

The runtime implements the approved 27-column semantic Binding contract,
selector equality/presence/absence, repeatable-ancestor occurrence identity,
source-scoped ordinal reconstruction, EE1 lexical/QName conversion, percentage
conversion and OIM metadata unit handling.  It contains no model-family branch
and has no task-history loader chain.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

import selector_multiplicity


class BindingError(RuntimeError):
    pass


V10_FIELDS = {
    "source_sequence", "source_module", "source_level", "source_type",
    "source_identifier", "source_name", "source_datatype", "source_multiplicity",
    "source_definition", "source_semantic_path", "source_class_term",
    "target_sequence", "target_module", "target_level", "target_type",
    "target_identifier", "target_name", "target_datatype", "target_multiplicity",
    "target_definition", "target_semantic_path", "target_class_term",
    "transformation", "mapping_status", "confidence", "reason_codes", "review_note",
}
SELECTOR = re.compile(r'\[(?:not\(([^)]+)\)|([^=\]]+)="([^"]*)"|([^=\]]+))\]')
PREDICATE = SELECTOR

def read(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))

def write(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def clean_path(path: str) -> str:
    return SELECTOR.sub("", path)

def parse_path(path: str) -> tuple[str, list[tuple[str, str, str, str]]]:
    """Return selector-free path and (Class path, key, operation, lexical)."""
    selectors = []
    prefix = ""
    for segment in path.split("."):
        if not segment:
            continue
        plain = SELECTOR.sub("", segment)
        prefix = f"{prefix}.{plain}" if prefix else plain
        for match in SELECTOR.finditer(segment):
            if match.group(1):
                selectors.append((prefix, match.group(1), "absent", ""))
            elif match.group(4):
                selectors.append((prefix, match.group(4), "present", ""))
            else:
                selectors.append((prefix, match.group(2), "equals", match.group(3)))
    return clean_path(path), selectors

def repeatable(row: dict[str, str]) -> bool:
    return row.get("type") == "C" and "*" in row.get("multiplicity", "")

def dim(row: dict[str, str]) -> str:
    name = row.get("local_name", "")
    if not name:
        raise BindingError(f"Class local_name missing: {row.get('semantic_path', '')}")
    return "d" + name[:1].upper() + name[1:]

def concept(row: dict[str, str]) -> str:
    if not row.get("module") or not row.get("local_name"):
        raise BindingError(f"QName incomplete: {row.get('semantic_path', '')}")
    return f"{row['module']}:{row['local_name']}"

def ancestors(hmd: list[dict[str, str]], path: str) -> list[dict[str, str]]:
    return [
        row for row in hmd
        if row.get("type") == "C"
        and (path == row.get("semantic_path") or path.startswith(row.get("semantic_path", "") + "."))
    ]

def relative_uri(target: Path, metadata: Path) -> str:
    return Path(os.path.relpath(target.resolve(), metadata.resolve().parent)).as_posix()

def decimal_text(value: Decimal) -> str:
    if value == 0:
        return "0"
    rendered = format(value, "f")
    return rendered.rstrip("0").rstrip(".") if "." in rendered else rendered


def transform(value: str, operation: str, inverse: bool = False) -> str:
    if operation == "identity":
        return value
    if operation == "date_to_midnight":
        if inverse:
            if value and not value.endswith("T00:00:00"):
                raise BindingError(f"non-reversible midnight value: {value}")
            return value[:-9] if value else value
        return value + "T00:00:00" if value else value
    if operation == "percentage_to_pure":
        try:
            number = Decimal(value)
        except InvalidOperation as exc:
            raise BindingError(f"invalid decimal percentage: {value}") from exc
        return decimal_text(number * Decimal(100) if inverse else number / Decimal(100))
    raise BindingError(f"unsupported explicit transformation: {operation}")

class _BaseContract:
    def __init__(self, args: argparse.Namespace):
        self.source_hmd = read(args.source_hmd)
        self.target_hmd = read(args.target_hmd)
        self.source_by_path = {row["semantic_path"]: row for row in self.source_hmd}
        self.source_by_seq = {row["sequence"]: row for row in self.source_hmd}
        self.target_by_path = {row["semantic_path"]: row for row in self.target_hmd}
        self.target_by_seq = {row["sequence"]: row for row in self.target_hmd}
        self.overlay_by_path: dict[str, dict[str, str]] = {}
        for row in read(args.overlay):
            path = row["parent_semantic_path"] + "." + row["selector_field"]
            self.overlay_by_path[path] = row
        self.lexical_to_member = {}
        self.member_to_lexical = {}
        for row in read(args.qname_map):
            key = (row["value_domain_id"], row["value"])
            self.lexical_to_member[key] = row["member_qname"]
            self.member_to_lexical[(row["value_domain_id"], row["member_qname"])] = row["value"]

        raw = read(args.binding)
        if not raw or set(raw[0]) != V10_FIELDS:
            raise BindingError("binding must use the exact 27-column semantic Binding contract")
        self.master_rows = raw
        self.rows = [
            row for row in raw
            if row["mapping_status"] in {"EXACT", "TRANSFORM"}
            or (row["mapping_status"] == "STRUCTURAL" and row["target_semantic_path"])
        ]
        self.structural = {}
        for row in self.rows:
            if row["mapping_status"] == "STRUCTURAL":
                self.structural[row["source_semantic_path"]] = clean_path(row["target_semantic_path"])
        self.rules = []
        for row in self.rows:
            if not row["transformation"]:
                raise BindingError(f"blank executable transformation: {row['source_sequence']}")
            source = self.source_by_seq.get(row["source_sequence"])
            if source is None or source["semantic_path"] != row["source_semantic_path"]:
                raise BindingError(f"source sequence/path mismatch: {row['source_sequence']}")
            target_path, selectors = parse_path(row["target_semantic_path"])
            target = self.target_by_path.get(target_path)
            if target is None or target["sequence"] != row["target_sequence"]:
                raise BindingError(f"current target sequence/path mismatch: {row['source_sequence']}")
            if row["source_type"] != source["type"] or row["target_type"] != target["type"]:
                raise BindingError(f"binding/HMD type mismatch: {row['source_sequence']}")
            if row["source_type"] == "A" and row["mapping_status"] == "EXACT" and row["transformation"] != "identity":
                raise BindingError(f"EXACT must use identity: {row['source_sequence']}")
            self.rules.append({**row, "target_clean_path": target_path, "selectors": selectors})
        self.attr_rules = [row for row in self.rules if row["source_type"] == "A"]
        if len({row["target_semantic_path"] for row in self.attr_rules}) != len(self.attr_rules):
            raise BindingError("selector-qualified executable target paths must be unique")

    def selector_row(self, class_path: str, key: str) -> dict[str, str]:
        path = class_path + "." + key
        # Overlay is the generated taxonomy contract for these selector facts;
        # it can intentionally replace context-specific HMD local_names with a
        # shared taxonomy concept (for example adjustmentType and taxType).
        row = self.overlay_by_path.get(path) or self.target_by_path.get(path)
        if row is None:
            raise BindingError(f"selector Attribute not found: {path}")
        return row

    def selector_serialized_value(self, class_path: str, key: str, lexical: str) -> str:
        row = self.selector_row(class_path, key)
        domain = row.get("value_domain", "") or row.get("value_domain_id", "")
        member = self.lexical_to_member.get((domain, lexical))
        if not member:
            raise BindingError(f"EE1 member QName missing: {domain}={lexical}")
        return member

    def selector_lexical_value(self, class_path: str, key: str, serialized: str) -> str:
        row = self.selector_row(class_path, key)
        domain = row.get("value_domain", "") or row.get("value_domain_id", "")
        lexical = self.member_to_lexical.get((domain, serialized))
        if lexical is None:
            raise BindingError(f"EE1 member QName is not reversible: {domain}={serialized}")
        return lexical

    def serialize_value(self, row: dict[str, str], lexical: str) -> str:
        domain = row.get("value_domain", "") or row.get("value_domain_id", "")
        if not domain:
            return lexical
        member = self.lexical_to_member.get((domain, lexical))
        if not member:
            raise BindingError(f"EE1 member QName missing: {domain}={lexical}")
        return member

    def deserialize_value(self, row: dict[str, str], serialized: str) -> str:
        domain = row.get("value_domain", "") or row.get("value_domain_id", "")
        if not domain:
            return serialized
        lexical = self.member_to_lexical.get((domain, serialized))
        if lexical is None:
            raise BindingError(f"EE1 member QName is not reversible: {domain}={serialized}")
        return lexical

def source_repeats(contract: Contract, path: str) -> list[dict[str, str]]:
    return [row for row in ancestors(contract.source_hmd, path) if repeatable(row)]

def target_repeats(contract: Contract, path: str) -> list[dict[str, str]]:
    return [row for row in ancestors(contract.target_hmd, path) if repeatable(row)]

def selector_signature(rule: dict[str, object], class_path: str) -> tuple[tuple[str, str, str], ...]:
    return tuple(
        (key, operation, lexical)
        for selected_class, key, operation, lexical in rule["selectors"]
        if selected_class == class_path
    )

def structural_source_for_target(contract: Contract, target_class_path: str, rule: dict[str, object]) -> str:
    candidates = [
        source_path for source_path, target_path in contract.structural.items()
        if target_path == target_class_path
        and (str(rule["source_semantic_path"]) == source_path
             or str(rule["source_semantic_path"]).startswith(source_path + "."))
    ]
    return max(candidates, key=len) if candidates else ""

def normalized_selector_path(path: str) -> str:
    """Normalize predicate order per path segment without changing lexical values."""
    normalized = []
    for segment in path.split("."):
        if not segment:
            continue
        plain = PREDICATE.sub("", segment)
        predicates = []
        for match in PREDICATE.finditer(segment):
            if match.group(1):
                predicates.append((match.group(1).strip(), "absent", ""))
            elif match.group(4):
                predicates.append((match.group(4).strip(), "present", ""))
            else:
                predicates.append((match.group(2).strip(), "equals", match.group(3)))
        rendered = []
        for key, operation, value in sorted(predicates):
            if operation == "absent":
                rendered.append(f"[not({key})]")
            elif operation == "present":
                rendered.append(f"[{key}]")
            else:
                rendered.append(f'[{key}="{value}"]')
        normalized.append(plain + "".join(rendered))
    return ".".join(normalized)

def selector_qualified_class_identity(path: str, class_path: str) -> str:
    """Return normalized full identity through the selected Class segment."""
    wanted = clean_path(class_path)
    cumulative = []
    for segment in path.split("."):
        if not segment:
            continue
        cumulative.append(segment)
        candidate = ".".join(cumulative)
        if clean_path(candidate) == wanted:
            return normalized_selector_path(candidate)
    raise BindingError(f"Class is not an ancestor of path: {class_path}")

class SelectorOccurrenceRegistry:
    """Multiplicity registry keyed by parent plus normalized selector identity."""

    def __init__(self) -> None:
        self.counts: Counter[tuple[str, str]] = Counter()

    def register(self, parent_identity: str, qualified_class_path: str, maximum: int = 1) -> str:
        identity = normalized_selector_path(qualified_class_path)
        key = (parent_identity, identity)
        self.counts[key] += 1
        if maximum >= 0 and self.counts[key] > maximum:
            raise BindingError(f"selector-qualified multiplicity violation: {identity}")
        return identity

def has_oim_occurrence_carrier(contract, selected_class_path: str) -> bool:
    """True only when the selected Class itself contributes an OIM dimension."""
    selected = contract.target_by_path[clean_path(selected_class_path)]
    return repeatable(selected)

def logical_selector_classes(contract, rule) -> list[str]:
    result = []
    for class_path, _key, _operation, _lexical in rule["selectors"]:
        if not repeatable(contract.target_by_path[class_path]) and class_path not in result:
            result.append(class_path)
    return sorted(result, key=lambda path: int(contract.target_by_path[path]["sequence"]))

def logical_dimension(contract, class_path: str) -> str:
    return dim(contract.target_by_path[class_path])

def dimensions_through(contract, rule, dimensions: dict[str, str], class_path: str) -> dict[str, str]:
    result = {
        dim(row): dimensions[dim(row)]
        for row in target_repeats(contract, class_path)
    }
    for logical_path in logical_selector_classes(contract, rule):
        if class_path == logical_path or class_path.startswith(logical_path + "."):
            result[logical_dimension(contract, logical_path)] = dimensions[logical_dimension(contract, logical_path)]
    return result

def metadata(args, contract, used_classes, logical_dimensions: list[str], concept_columns) -> None:
    path = args.output.with_suffix(".json")
    modules = sorted({row["module"] for row in contract.target_hmd if row.get("module")})
    namespace_base = "https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/experimental/2026-12-31"
    namespaces = {module: f"{namespace_base}/{module}" for module in modules}
    namespaces.update({
        "gen": f"{namespace_base}/gen",
        "plt": f"{namespace_base}/plt",
        "iso4217": "http://www.xbrl.org/2003/iso4217",
        "xbrli": "http://www.xbrl.org/2003/instance",
        "scheme": "http://www.example.com",
        "xbrl": "https://xbrl.org/2021",
    })
    dimensions = {"period": args.period, "entity": args.entity}
    columns = {}
    for row in used_classes:
        name = dim(row)
        dimensions[f"plt:d_{row['module']}_{row['local_name']}"] = "$" + name
        columns[name] = {}
    target_classes_by_dimension = {
        dim(row): row for row in contract.target_hmd if row.get("type") == "C"
    }
    for name in logical_dimensions:
        selected_class = target_classes_by_dimension.get(name)
        if selected_class is None:
            raise BindingError(f"logical selector dimension Class missing: {name}")
        dimensions[
            f"plt:d_{selected_class['module']}_{selected_class['local_name']}"
        ] = "$" + name
        columns[name] = {}
    for name, row in concept_columns.items():
        fact_dimensions = {"concept": concept(row)}
        if row.get("datatype") == "Monetary":
            fact_dimensions["unit"] = "iso4217:EUR"
        # OIM 1.0 forbids explicitly serializing the single numerator unit
        # xbrli:pure. Pure/Decimal/Integer facts therefore omit unit.
        columns[name] = {"dimensions": fact_dimensions}
    payload = {
        "documentInfo": {
            "documentType": "https://xbrl.org/2021/xbrl-csv",
            "namespaces": namespaces,
            "taxonomy": [relative_uri(args.taxonomy, path)],
        },
        "tables": {"structured": {"template": "structured", "url": args.output.name}},
        "tableTemplates": {"structured": {"dimensions": dimensions, "columns": columns}},
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

class Contract(_BaseContract):
    """27-column contract with generic predicates on both semantic paths."""

    def __init__(self, args):
        self.source_hmd = read(args.source_hmd)
        self.target_hmd = read(args.target_hmd)
        self.source_by_path = {row["semantic_path"]: row for row in self.source_hmd}
        self.source_by_seq = {row["sequence"]: row for row in self.source_hmd}
        self.target_by_path = {row["semantic_path"]: row for row in self.target_hmd}
        self.target_by_seq = {row["sequence"]: row for row in self.target_hmd}
        self.overlay_by_path = {}
        for row in read(args.overlay):
            self.overlay_by_path[row["parent_semantic_path"] + "." + row["selector_field"]] = row
        self.lexical_to_member = {}
        self.member_to_lexical = {}
        for row in read(args.qname_map):
            identity = (row["value_domain_id"], row["value"])
            self.lexical_to_member[identity] = row["member_qname"]
            self.member_to_lexical[(row["value_domain_id"], row["member_qname"])] = row["value"]

        raw = read(args.binding)
        if not raw or set(raw[0]) != V10_FIELDS:
            raise BindingError("binding must use the exact 27-column semantic Binding contract")
        for hmd in (self.source_hmd, self.target_hmd):
            roots = [row for row in hmd if row.get("type") == "C" and row.get("level") == "1"]
            if len(roots) != 1:
                raise BindingError("selector effective multiplicity requires one HMD root")
            for row in hmd:
                row.setdefault("element_id", f"{row.get('module', '')}_{row.get('local_name', '')}")
            selector_multiplicity.derive(
                hmd, [args.binding], roots[0].get("local_name", "root")
            )
        self.master_rows = raw
        self.rows = [
            row for row in raw
            if row["mapping_status"] in {"EXACT", "TRANSFORM"}
            or (row["mapping_status"] == "STRUCTURAL" and row["target_semantic_path"])
        ]
        self.structural = {}
        for row in self.rows:
            if row["mapping_status"] == "STRUCTURAL":
                source_path, _source_selectors = parse_path(row["source_semantic_path"])
                target_path, _target_selectors = parse_path(row["target_semantic_path"])
                previous = self.structural.get(source_path)
                if previous is not None and previous != target_path:
                    raise BindingError(f"conflicting structural variants: {source_path}")
                self.structural[source_path] = target_path
        self.rules = []
        for row in self.rows:
            if not row["transformation"]:
                raise BindingError(f"blank executable transformation: {row['source_sequence']}")
            source_path, source_selectors = parse_path(row["source_semantic_path"])
            source_selectors = sorted(source_selectors)
            source = self.source_by_seq.get(row["source_sequence"])
            if source is None or source["semantic_path"] != source_path:
                raise BindingError(f"source sequence/path mismatch: {row['source_sequence']}")
            for class_path, key, operation, _lexical in source_selectors:
                selected = self.source_by_path.get(class_path + "." + key)
                if selected is None or selected.get("type") != "A":
                    raise BindingError(f"source predicate Attribute missing: {class_path}.{key}")
                if operation not in {"equals", "present", "absent"}:
                    raise BindingError(f"unsupported source predicate: {operation}")
            target_path, selectors = parse_path(row["target_semantic_path"])
            target = self.target_by_path.get(target_path)
            if target is None or target["sequence"] != row["target_sequence"]:
                raise BindingError(f"current target sequence/path mismatch: {row['source_sequence']}")
            if row["source_type"] != source["type"] or row["target_type"] != target["type"]:
                raise BindingError(f"binding/HMD type mismatch: {row['source_sequence']}")
            if row["source_type"] == "A" and row["mapping_status"] == "EXACT" and row["transformation"] != "identity":
                raise BindingError(f"EXACT must use identity: {row['source_sequence']}")
            self.rules.append({
                **row,
                "source_binding_semantic_path": row["source_semantic_path"],
                "source_semantic_path": source_path,
                "source_selectors": source_selectors,
                "target_clean_path": target_path,
                "selectors": selectors,
            })
        self.attr_rules = [row for row in self.rules if row["source_type"] == "A"]
        source_identities = [
            (row["source_semantic_path"], tuple(row["source_selectors"]))
            for row in self.attr_rules
        ]
        if len(source_identities) != len(set(source_identities)):
            raise BindingError("overlapping normalized source predicate variants")
        target_identities = [
            normalized_selector_path(row["target_semantic_path"])
            for row in self.attr_rules
        ]
        if len(target_identities) != len(set(target_identities)):
            raise BindingError("selector-qualified executable target paths must be unique")

def source_matches(contract: Contract, rule, source_row: dict[str, str]) -> bool:
    """Evaluate every predicate inside the current physical source row/occurrence."""
    for class_path, key, operation, lexical in rule["source_selectors"]:
        selected = contract.source_by_path[class_path + "." + key]
        value = (source_row.get(selected["local_name"]) or "").strip()
        if operation == "present" and not value:
            return False
        if operation == "absent" and value:
            return False
        if operation == "equals" and value != lexical:
            return False
    return True


def occurrence_ordinal_sort_key(value: str) -> tuple[int, object]:
    """Sort positive integer ordinals numerically and other stable tokens lexically."""
    return (0, int(value)) if value.isdigit() else (1, value)


def source_anchor(contract: Contract, rule, target_class_path: str = "") -> tuple[str, int, str]:
    """Return source Class path, HMD sequence and physical occurrence column name."""
    class_path = (
        structural_source_for_target(contract, target_class_path, rule)
        if target_class_path else ""
    )
    if class_path:
        record = contract.source_by_path[class_path]
        return class_path, int(record["sequence"]), dim(record) if repeatable(record) else ""
    # A target Class without an explicit STRUCTURAL source mapping is one
    # shared occurrence under its already-qualified parent.  Falling back to
    # each source Attribute sequence would incorrectly split that Class once
    # per fact.
    return "", 0, ""


def occurrence_descriptor_sort_key(
    contract: Contract, descriptor: tuple, source_fact_sequence: dict[tuple, int]
) -> tuple:
    """Stable order independent of physical source-row encounter order."""
    kind, target_path, parent, source_sequence, source_ordinal, source_class_path, signature = descriptor
    parent_key = (
        occurrence_descriptor_sort_key(contract, parent, source_fact_sequence)
        if parent else ()
    )
    return (
        parent_key,
        int(contract.target_by_path[target_path]["sequence"]),
        source_sequence,
        occurrence_ordinal_sort_key(source_ordinal),
        source_fact_sequence.get(descriptor, 0),
        signature,
        source_class_path,
        kind,
    )


def select_forward_executions(contract: Contract, source_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    """Select executable facts before allocating any target occurrence."""
    groups = defaultdict(list)
    for rule in contract.attr_rules:
        groups[rule["source_semantic_path"]].append(rule)
    executions = []
    source_dimensions = sorted(
        (row for row in contract.source_hmd if repeatable(row)),
        key=lambda row: int(row["sequence"]),
    )

    def physical_row_key(source_row):
        # Canonical HMD hierarchy/ordinal order replaces CSV encounter order.
        # Rows for the same occurrence may tie; rule order below then remains
        # the only observable order and does not depend on fact values.
        return tuple(
            (int(row["sequence"]), occurrence_ordinal_sort_key(source_row.get(dim(row), "")))
            for row in source_dimensions
            if source_row.get(dim(row), "")
        )

    for source_row in sorted(source_rows, key=physical_row_key):
        for source_path, rules in groups.items():
            source = contract.source_by_path[source_path]
            value = (source_row.get(source["local_name"]) or "").strip()
            if not value:
                continue
            matches = [rule for rule in rules if source_matches(contract, rule, source_row)]
            variant_driven = any(rule["source_selectors"] for rule in rules)
            if variant_driven and len(matches) != 1:
                raise BindingError(
                    f"AMBIGUOUS_VARIANT: {source_path} matched {len(matches)} predicate variants"
                )
            for rule in matches if variant_driven else rules:
                executions.append({"rule": rule, "source_row": source_row, "value": value})
    return executions


def plan_forward_occurrences(contract: Contract, executions: list[dict[str, object]]) -> tuple[dict[str, dict[tuple, str]], dict[str, dict[str, str]], set[str]]:
    """Collect every occurrence identity, sort it, then allocate 1..N ordinals."""
    descriptors_by_target: dict[str, set[tuple]] = defaultdict(set)
    source_fact_sequence: dict[tuple, int] = {}
    used_classes: dict[str, dict[str, str]] = {}
    used_logical_classes: set[str] = set()
    for execution in executions:
        rule = execution["rule"]
        source_row = execution["source_row"]
        parent = None
        physical = []
        for target_class in target_repeats(contract, str(rule["target_clean_path"])):
            target_path = target_class["semantic_path"]
            source_class_path, source_sequence, occurrence_column = source_anchor(
                contract, rule, target_path
            )
            source_ordinal = ""
            if occurrence_column:
                source_ordinal = (source_row.get(occurrence_column) or "").strip()
                if not source_ordinal:
                    raise BindingError(
                        f"missing source occurrence {occurrence_column}: {rule['source_sequence']}"
                    )
            signature = tuple(sorted(selector_signature(rule, target_path)))
            descriptor = (
                "physical", target_path, parent, source_sequence,
                source_ordinal, source_class_path, signature,
            )
            descriptors_by_target[target_path].add(descriptor)
            source_fact_sequence[descriptor] = min(
                source_fact_sequence.get(descriptor, int(rule["source_sequence"])),
                int(rule["source_sequence"]),
            )
            physical.append(descriptor)
            parent = descriptor
            used_classes[target_path] = target_class
        logical = []
        for class_path in logical_selector_classes(contract, rule):
            source_class_path, source_sequence, occurrence_column = source_anchor(
                contract, rule, class_path
            )
            source_ordinal = (source_row.get(occurrence_column) or "").strip() if occurrence_column else ""
            if occurrence_column and not source_ordinal:
                raise BindingError(
                    f"missing source occurrence {occurrence_column}: {rule['source_sequence']}"
                )
            identity = selector_qualified_class_identity(str(rule["target_semantic_path"]), class_path)
            descriptor = (
                "logical", class_path, parent, source_sequence,
                source_ordinal, source_class_path, (normalized_selector_path(identity),),
            )
            descriptors_by_target[class_path].add(descriptor)
            source_fact_sequence[descriptor] = min(
                source_fact_sequence.get(descriptor, int(rule["source_sequence"])),
                int(rule["source_sequence"]),
            )
            logical.append(descriptor)
            parent = descriptor
            used_logical_classes.add(class_path)
        execution["physical_descriptors"] = physical
        execution["logical_descriptors"] = logical
    ordinals = {}
    for target_path, descriptors in descriptors_by_target.items():
        ordered = sorted(
            descriptors,
            key=lambda item: occurrence_descriptor_sort_key(
                contract, item, source_fact_sequence
            ),
        )
        ordinals[target_path] = {
            descriptor: str(index)
            for index, descriptor in enumerate(ordered, 1)
        }
    return ordinals, used_classes, used_logical_classes


def forward(args) -> None:
    contract = Contract(args)
    source_rows = read(args.input)
    output = {}
    concept_columns = {}
    executions = select_forward_executions(contract, source_rows)
    contexts, used_classes, used_logical_classes = plan_forward_occurrences(
        contract, executions
    )

    def context_for(execution):
        dimensions = {}
        for descriptor in execution["physical_descriptors"]:
            target_path = descriptor[1]
            target_class = contract.target_by_path[target_path]
            dimensions[dim(target_class)] = contexts[target_path][descriptor]
        for descriptor in execution["logical_descriptors"]:
            class_path = descriptor[1]
            name = logical_dimension(contract, class_path)
            dimensions[name] = contexts[class_path][descriptor]
        return dimensions

    for execution in executions:
        rule = execution["rule"]
        dimensions = context_for(execution)
        target = contract.target_by_path[rule["target_clean_path"]]
        row_key = tuple(sorted(dimensions.items()))
        destination = output.setdefault(row_key, dict(dimensions))
        column = target["local_name"]
        concept_columns[column] = target
        if destination.get(column):
            raise BindingError(f"duplicate selector-qualified target fact: {column}, {row_key}")
        destination[column] = contract.serialize_value(
            target, transform(str(execution["value"]), rule["transformation"])
        )
        for class_path, key, operation, lexical in rule["selectors"]:
            if operation == "absent":
                continue
            if operation != "equals":
                raise BindingError(f"present selector serialization requires an explicit value: {class_path}.{key}")
            selected = contract.selector_row(class_path, key)
            serialized = contract.selector_serialized_value(class_path, key, lexical)
            column = selected["local_name"]
            concept_columns[column] = selected
            selector_dimensions = dimensions_through(
                contract, rule, dimensions, class_path
            )
            selector_row_key = tuple(sorted(selector_dimensions.items()))
            selector_destination = output.setdefault(
                selector_row_key, dict(selector_dimensions)
            )
            existing = selector_destination.get(column)
            if existing and existing != serialized:
                raise BindingError(f"conflicting selector fact: {class_path}.{key}")
            selector_destination[column] = serialized

    dimension_rows = sorted(used_classes.values(), key=lambda row: int(row["sequence"]))
    logical_fields = [
        logical_dimension(contract, path)
        for path in sorted(
            used_logical_classes,
            key=lambda item: int(contract.target_by_path[item]["sequence"]),
        )
    ]
    concept_fields = [
        name for name, _row in sorted(concept_columns.items(), key=lambda item: int(item[1].get("sequence", "0") or 0))
    ]
    dimension_fields = [dim(row) for row in dimension_rows] + logical_fields
    fields = dimension_fields + concept_fields
    ordered = sorted(output.values(), key=lambda row: tuple(int(row.get(field, "0") or 0) for field in dimension_fields))
    write(args.output, ordered, fields)
    metadata(args, contract, dimension_rows, logical_fields, concept_columns)

def reverse(args) -> None:
    contract = Contract(args)
    target_rows = read(args.input)

    def matches(rule, target_row):
        for class_path, key, operation, lexical in rule["selectors"]:
            selector = contract.selector_row(class_path, key)
            scope = dimensions_through(contract, rule, target_row, class_path)
            values = [
                row.get(selector["local_name"], "")
                for row in target_rows
                if all(row.get(name, "") == value for name, value in scope.items())
                and row.get(selector["local_name"], "")
            ]
            values = list(dict.fromkeys(values))
            if operation == "equals":
                decoded = [contract.selector_lexical_value(class_path, key, value) for value in values]
                if decoded != [lexical]:
                    return False
            elif operation == "absent" and values:
                return False
            elif operation == "present" and not values:
                return False
        return True

    # Collect every reverse execution and every target occurrence before
    # assigning source ordinals.  Allocation must not depend on target CSV row
    # encounter order.
    executions = []
    occurrence_candidates: dict[
        str, dict[tuple[tuple[str, str], ...], set[tuple[tuple[str, str], ...]]]
    ] = defaultdict(lambda: defaultdict(set))
    for target_row in target_rows:
        for rule in contract.attr_rules:
            target = contract.target_by_path[rule["target_clean_path"]]
            value = target_row.get(target["local_name"], "")
            if not value or not matches(rule, target_row):
                continue
            executions.append((target_row, rule, target, value))
            for source_class in source_repeats(contract, rule["source_semantic_path"]):
                target_path = contract.structural.get(source_class["semantic_path"])
                target_class = contract.target_by_path.get(target_path or "")
                if target_class is None:
                    raise BindingError(f"source repeat Class lacks target Class: {source_class['semantic_path']}")
                target_chain = target_repeats(contract, target_path)
                target_identity = tuple((dim(row), target_row.get(dim(row), "")) for row in target_chain)
                if any(not value for _name, value in target_identity):
                    raise BindingError(f"target occurrence identity is incomplete: {target_path}")
                occurrence_candidates[source_class["semantic_path"]][target_identity[:-1]].add(target_identity)

    # source Class path -> parent target identity -> target occurrence -> source ordinal
    occurrence_registry: dict[
        str, dict[tuple[tuple[str, str], ...], dict[tuple[tuple[str, str], ...], str]]
    ] = defaultdict(lambda: defaultdict(dict))
    for source_path, parent_groups in occurrence_candidates.items():
        for parent_identity, identities in parent_groups.items():
            ordered = sorted(
                identities,
                key=lambda identity: tuple(
                    occurrence_ordinal_sort_key(value) for _name, value in identity
                ),
            )
            occurrence_registry[source_path][parent_identity] = {
                identity: str(index) for index, identity in enumerate(ordered, 1)
            }

    output = {}
    for target_row, rule, target, value in executions:
        source_dimensions = {}
        for source_class in source_repeats(contract, rule["source_semantic_path"]):
            target_path = contract.structural.get(source_class["semantic_path"])
            target_chain = target_repeats(contract, target_path)
            target_identity = tuple((dim(row), target_row.get(dim(row), "")) for row in target_chain)
            parent_identity = target_identity[:-1]
            source_dimensions[dim(source_class)] = occurrence_registry[
                source_class["semantic_path"]
            ][parent_identity][target_identity]
        row_key = tuple(sorted(source_dimensions.items()))
        destination = output.setdefault(row_key, dict(source_dimensions))
        source = contract.source_by_path[rule["source_semantic_path"]]
        column = source["local_name"]
        if destination.get(column):
            raise BindingError(f"duplicate reconstructed source fact: {rule['source_semantic_path']}")
        destination[column] = transform(
            contract.deserialize_value(target, value),
            rule["transformation"], inverse=True,
        )
    columns = []
    for rule in sorted(contract.attr_rules, key=lambda item: int(item["source_sequence"])):
        column = contract.source_by_path[rule["source_semantic_path"]]["local_name"]
        if column not in columns:
            columns.append(column)
    valid_source_dims = {dim(row) for row in contract.source_hmd if repeatable(row)}
    used_source_dims = {name for row in output.values() for name in row if name in valid_source_dims}
    source_dims = [
        dim(row) for row in sorted(
            (row for row in contract.source_hmd if repeatable(row) and dim(row) in used_source_dims),
            key=lambda item: int(item["sequence"]),
        )
    ]
    ordered = sorted(
        output.values(),
        key=lambda row: tuple(int(row.get(name, "0") or 0) for name in source_dims),
    )
    write(args.output, ordered, source_dims + columns)

def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    commands = result.add_subparsers(dest="command", required=True)
    for name, handler in (("forward", forward), ("reverse", reverse)):
        command = commands.add_parser(name)
        command.add_argument("input", type=Path)
        command.add_argument("--binding", type=Path, required=True)
        command.add_argument("--source-hmd", type=Path, required=True)
        command.add_argument("--target-hmd", type=Path, required=True)
        command.add_argument("--overlay", type=Path, required=True)
        command.add_argument("--qname-map", type=Path, required=True)
        command.add_argument("--output", type=Path, required=True)
        command.set_defaults(handler=handler)
        if name == "forward":
            command.add_argument("--taxonomy", type=Path, required=True)
            command.add_argument("--entity", default="scheme:UADC-PoC")
            command.add_argument("--period", default="2026-08-25T00:00:00")
    return result

def main() -> int:
    args = parser().parse_args()
    try:
        args.handler(args)
    except (OSError, UnicodeError, csv.Error, json.JSONDecodeError, BindingError) as exc:
        print(f"SEMANTIC_BINDING_ERROR: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
