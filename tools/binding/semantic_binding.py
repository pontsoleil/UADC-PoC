#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Generic reversible semantic binding runtime.

The runtime implements the approved 27-column semantic Binding contract,
selector equality/presence/absence, repeatable-ancestor occurrence identity,
source-scoped ordinal reconstruction, EE1 lexical/QName conversion, percentage
conversion and OIM metadata unit handling. Forward conversion is resilient at
the active-fact level: unsupported in-scope source facts are skipped and
reported without aborting unrelated facts. Selector multiplicity is derived only from executable Binding rows, so non-executable review rows cannot block initialization. It contains no model-family branch
and has no task-history loader chain.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import xml.etree.ElementTree as ET
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
EXECUTABLE_STATUSES = {"EXACT", "TRANSFORM", "STRUCTURAL"}
REPORTABLE_NONEXECUTABLE_STATUSES = {"REVIEW_REQUIRED", "NO_TARGET"}
UNSUPPORTED_REPORT_FIELDS = [
    "source_sequence", "source_name", "source_semantic_path", "source_occurrence",
    "source_value", "reason", "mapping_status", "target_semantic_path", "detail",
]

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

def unsupported_reason_for_binding_row(row: dict[str, str]) -> str:
    """Classify a non-executable Binding row for active-fact reporting."""
    if row.get("mapping_status") == "NO_TARGET":
        return "UNMAPPED_CONVERSION_SOURCE_FACT"
    codes = {item.strip() for item in (row.get("reason_codes") or "").split("|") if item.strip()}
    if "R_CURRENT_HMD_TARGET_PATH_UNRESOLVED" in codes:
        return "TARGET_PATH_NOT_IN_CURRENT_HMD"
    if {"R_CURRENT_QNAME_AUTHORITY_UNRESOLVED", "R_ACTIVE_SELECTOR_AUTHORITY_UNRESOLVED"} & codes:
        return "UNRESOLVED_QNAME_FOR_SOURCE_VALUE"
    return "OTHER_ACTIVE_SOURCE_MAPPING_ERROR"

def unsupported_reason_for_error(exc: BindingError) -> str:
    """Classify a fact-local forward error without inventing a mapping."""
    message = str(exc)
    if message.startswith("EE1 member QName missing:"):
        return "UNRESOLVED_QNAME_FOR_SOURCE_VALUE"
    if message.startswith("selector Attribute not found:"):
        return "OTHER_ACTIVE_SOURCE_MAPPING_ERROR"
    if message.startswith("current target path missing:"):
        return "TARGET_PATH_NOT_IN_CURRENT_HMD"
    return "OTHER_ACTIVE_SOURCE_MAPPING_ERROR"

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
        self.report_rules = []
        for row in raw:
            if row.get("source_type") != "A" or row.get("mapping_status") not in REPORTABLE_NONEXECUTABLE_STATUSES:
                continue
            source_path, source_selectors = parse_path(row.get("source_semantic_path", ""))
            source = self.source_by_seq.get(row.get("source_sequence", ""))
            if source is None or source.get("semantic_path") != source_path:
                raise BindingError(f"source sequence/path mismatch: {row.get('source_sequence', '')}")
            for class_path, key, operation, _lexical in source_selectors:
                selected = self.source_by_path.get(class_path + "." + key)
                if selected is None or selected.get("type") != "A":
                    raise BindingError(f"source predicate Attribute missing: {class_path}.{key}")
                if operation not in {"equals", "present", "absent"}:
                    raise BindingError(f"unsupported source predicate: {operation}")
            self.report_rules.append({
                **row,
                "source_binding_semantic_path": row["source_semantic_path"],
                "source_semantic_path": source_path,
                "source_selectors": sorted(source_selectors),
            })
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

def _local_schema_locations(schema: Path) -> list[Path]:
    """Return local XSD import/include/redefine targets for one schema."""
    try:
        root = ET.parse(schema).getroot()
    except (ET.ParseError, OSError) as exc:
        raise BindingError(f"taxonomy schema parse failed: {schema}: {exc}") from exc
    xsd = "{http://www.w3.org/2001/XMLSchema}"
    result = []
    for tag in ("import", "include", "redefine"):
        for node in root.findall(f"{xsd}{tag}"):
            location = (node.get("schemaLocation") or "").strip()
            if not location or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://", location):
                continue
            candidate = (schema.parent / location).resolve()
            if candidate.is_file():
                result.append(candidate)
    return result


def _schema_target_namespace(schema: Path) -> str:
    try:
        root = ET.parse(schema).getroot()
    except (ET.ParseError, OSError) as exc:
        raise BindingError(f"taxonomy schema parse failed: {schema}: {exc}") from exc
    return (root.get("targetNamespace") or "").strip()


def taxonomy_namespace_map(entrypoint: Path, required_modules: set[str]) -> dict[str, str]:
    """Resolve GL module namespaces from the supplied current taxonomy files.

    Resolution first follows local XSD imports/includes from the entry point. If
    that entry point is module-local and does not expose every module required by
    the generated OIM metadata, the surrounding taxonomy family directory is
    scanned. A module is accepted only when all discovered candidates agree on
    one targetNamespace.
    """
    entrypoint = entrypoint.resolve()
    if not entrypoint.is_file():
        raise BindingError(f"taxonomy entry point not found: {entrypoint}")

    visited: set[Path] = set()
    stack = [entrypoint]
    schemas: list[Path] = []
    while stack:
        schema = stack.pop()
        if schema in visited or not schema.is_file():
            continue
        visited.add(schema)
        schemas.append(schema)
        stack.extend(_local_schema_locations(schema))

    def collect(paths: list[Path]) -> dict[str, set[str]]:
        by_tail: dict[str, set[str]] = defaultdict(set)
        by_filename: dict[str, set[str]] = defaultdict(set)
        for schema in paths:
            namespace = _schema_target_namespace(schema)
            if not namespace:
                continue
            tail = namespace.rstrip("/").rsplit("/", 1)[-1]
            stem_prefix = schema.stem.split("-", 1)[0]
            for module in required_modules:
                if tail == module:
                    by_tail[module].add(namespace)
                elif stem_prefix == module:
                    by_filename[module].add(namespace)
        # Namespace-tail identity is authoritative. Filename inference is only a
        # fallback for a module with no tail-identifying schema.
        return {
            module: (by_tail.get(module) or by_filename.get(module) or set())
            for module in required_modules
        }

    found = collect(schemas)
    missing = {module for module in required_modules if not found.get(module)}
    if missing:
        # A module-local OIM entry point may import only itself and gen. Search
        # the surrounding taxonomy family, but still require unique namespace
        # agreement before accepting a module.
        family_root = entrypoint.parent.parent if entrypoint.parent.parent.exists() else entrypoint.parent
        family_schemas = sorted(family_root.rglob("*.xsd"))
        expanded = collect(family_schemas)
        for module, values in expanded.items():
            found[module].update(values)

    result = {}
    for module in sorted(required_modules):
        values = found.get(module, set())
        if not values:
            raise BindingError(
                f"taxonomy namespace not found for module {module}: entrypoint={entrypoint}"
            )
        if len(values) != 1:
            raise BindingError(
                f"taxonomy namespace conflict for module {module}: {sorted(values)}"
            )
        result[module] = next(iter(values))
    return result


def metadata(args, contract, used_classes, logical_dimensions: list[str], concept_columns) -> None:
    path = args.output.with_suffix(".json")
    required_modules = {
        row["module"] for row in used_classes if row.get("module")
    } | {
        row["module"] for row in concept_columns.values() if row.get("module")
    } | {"gen", "plt"}
    namespaces = taxonomy_namespace_map(args.taxonomy, required_modules)
    namespaces.update({
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
        self.master_rows = raw
        self.rows = [
            row for row in raw
            if row["mapping_status"] in {"EXACT", "TRANSFORM"}
            or (row["mapping_status"] == "STRUCTURAL" and row["target_semantic_path"])
        ]
        # Effective selector multiplicity is an execution concern. Non-executable
        # rows such as REVIEW_REQUIRED and NO_TARGET must not block runtime
        # initialization or alter multiplicity for the active execution contract.
        for hmd in (self.source_hmd, self.target_hmd):
            roots = [row for row in hmd if row.get("type") == "C" and row.get("level") == "1"]
            if len(roots) != 1:
                raise BindingError("selector effective multiplicity requires one HMD root")
            for row in hmd:
                row.setdefault("element_id", f"{row.get('module', '')}_{row.get('local_name', '')}")
            selector_multiplicity.derive_from_rows(
                hmd, self.rows, roots[0].get("local_name", "root"), origin=str(args.binding)
            )
        self.report_rules = []
        for row in raw:
            if row.get("source_type") != "A" or row.get("mapping_status") not in REPORTABLE_NONEXECUTABLE_STATUSES:
                continue
            source_path, source_selectors = parse_path(row.get("source_semantic_path", ""))
            source = self.source_by_seq.get(row.get("source_sequence", ""))
            if source is None or source.get("semantic_path") != source_path:
                raise BindingError(f"source sequence/path mismatch: {row.get('source_sequence', '')}")
            for class_path, key, operation, _lexical in source_selectors:
                selected = self.source_by_path.get(class_path + "." + key)
                if selected is None or selected.get("type") != "A":
                    raise BindingError(f"source predicate Attribute missing: {class_path}.{key}")
                if operation not in {"equals", "present", "absent"}:
                    raise BindingError(f"unsupported source predicate: {operation}")
            self.report_rules.append({
                **row,
                "source_binding_semantic_path": row["source_semantic_path"],
                "source_semantic_path": source_path,
                "source_selectors": sorted(source_selectors),
            })
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
            target_contract_error = ""
            effective_target_sequence = row["target_sequence"]
            target_sequence_rebound = False
            if target is None:
                if row["source_type"] == "A":
                    target_contract_error = f"current target path missing: {target_path}"
                else:
                    raise BindingError(f"current target path missing: {row['source_sequence']}: {target_path}")
            else:
                if target["sequence"] != row["target_sequence"]:
                    # semantic_path is the model identity; sequence is ordering metadata
                    # and is rebound to the current target HMD for active Attribute facts.
                    effective_target_sequence = target["sequence"]
                    target_sequence_rebound = True
                if row["source_type"] != source["type"] or row["target_type"] != target["type"]:
                    if row["source_type"] == "A":
                        target_contract_error = f"binding/HMD type mismatch: {row['source_sequence']}"
                    else:
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
                "binding_target_sequence": row["target_sequence"],
                "target_sequence": effective_target_sequence,
                "target_sequence_rebound": target_sequence_rebound,
                "target_contract_error": target_contract_error,
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


def source_occurrence_identity(contract: Contract, source_path: str, source_row: dict[str, str]) -> str:
    """Return stable JSON for repeatable source occurrence dimensions only."""
    identity = {}
    for row in source_repeats(contract, source_path):
        name = dim(row)
        value = (source_row.get(name) or "").strip()
        if value:
            identity[name] = value
    return json.dumps(identity, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def unsupported_fact(contract: Contract, rule: dict[str, object], source_row: dict[str, str], value: str, reason: str, detail: str) -> dict[str, str]:
    return {
        "source_sequence": str(rule.get("source_sequence", "")),
        "source_name": str(rule.get("source_name", "")),
        "source_semantic_path": str(rule.get("source_semantic_path", "")),
        "source_occurrence": source_occurrence_identity(contract, str(rule.get("source_semantic_path", "")), source_row),
        "source_value": value,
        "reason": reason,
        "mapping_status": str(rule.get("mapping_status", "")),
        "target_semantic_path": str(rule.get("target_semantic_path", "")),
        "detail": detail,
    }


def dedupe_unsupported(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    seen = set()
    result = []
    for row in rows:
        key = tuple(row.get(field, "") for field in UNSUPPORTED_REPORT_FIELDS)
        if key not in seen:
            seen.add(key)
            result.append(row)
    return result


def write_unsupported(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=UNSUPPORTED_REPORT_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _occurrence_tuple(contract: Contract, source_path: str, source_row: dict[str, str]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted(
        (dim(row), (source_row.get(dim(row)) or "").strip())
        for row in source_repeats(contract, source_path)
        if (source_row.get(dim(row)) or "").strip()
    ))


def _parse_scope_occurrence(value: str) -> tuple[tuple[str, str], ...] | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise BindingError(f"invalid scope source_occurrence JSON: {value}") from exc
    if isinstance(parsed, dict):
        return tuple(sorted((str(k), str(v)) for k, v in parsed.items() if str(v)))
    if isinstance(parsed, list):
        pairs = []
        for item in parsed:
            if not isinstance(item, (list, tuple)) or len(item) != 2:
                raise BindingError(f"invalid scope source_occurrence pair: {item}")
            if str(item[1]):
                pairs.append((str(item[0]), str(item[1])))
        return tuple(sorted(pairs))
    raise BindingError(f"invalid scope source_occurrence JSON type: {type(parsed).__name__}")


class ConversionScope:
    """Explicit forward conversion scope by semantic path and optional occurrence."""

    PATH_FIELDS = ("source_semantic_path", "Source_Semantic_Path")
    OCCURRENCE_FIELDS = ("source_occurrence", "Source_Occurrence")
    ENABLE_FIELDS = ("in_conversion_scope", "In_Conversion_Scope")

    def __init__(self, path: Path | None, contract: Contract):
        self.enabled = path is not None
        self.entries: dict[str, set[tuple[tuple[str, str], ...] | None]] = defaultdict(set)
        if path is None:
            return
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            fields = reader.fieldnames or []
            path_field = next((name for name in self.PATH_FIELDS if name in fields), None)
            occurrence_field = next((name for name in self.OCCURRENCE_FIELDS if name in fields), None)
            enable_field = next((name for name in self.ENABLE_FIELDS if name in fields), None)
            if path_field is None:
                raise BindingError(
                    "scope file must contain source_semantic_path or Source_Semantic_Path"
                )
            for row in reader:
                if enable_field and (row.get(enable_field) or "").strip().upper() in {"NO", "FALSE", "0"}:
                    continue
                source_path = clean_path((row.get(path_field) or "").strip())
                if not source_path:
                    continue
                if source_path not in contract.source_by_path:
                    raise BindingError(f"scope source path not found in source HMD: {source_path}")
                occurrence = _parse_scope_occurrence(row.get(occurrence_field, "")) if occurrence_field else None
                self.entries[source_path].add(occurrence)
        if not self.entries:
            raise BindingError(f"scope file contains no enabled source facts: {path}")

    def matches(self, contract: Contract, source_path: str, source_row: dict[str, str]) -> bool:
        if not self.enabled:
            return True
        entries = self.entries.get(source_path)
        if not entries:
            return False
        if None in entries:
            return True
        return _occurrence_tuple(contract, source_path, source_row) in entries

    def active_fact_keys(self, contract: Contract, source_rows: list[dict[str, str]]) -> set[tuple[str, str, str]]:
        """Return value-present facts explicitly selected by this scope."""
        result = set()
        if not self.enabled:
            return result
        for source_path in self.entries:
            source = contract.source_by_path[source_path]
            for source_row in source_rows:
                if not self.matches(contract, source_path, source_row):
                    continue
                value = (source_row.get(source["local_name"]) or "").strip()
                if not value:
                    continue
                result.add((
                    source_path,
                    source_occurrence_identity(contract, source_path, source_row),
                    value,
                ))
        return result


def _execution_fact_key(contract: Contract, execution: dict[str, object]) -> tuple[str, str, str]:
    rule = execution["rule"]
    source_row = execution["source_row"]
    return (
        str(rule["source_semantic_path"]),
        source_occurrence_identity(contract, str(rule["source_semantic_path"]), source_row),
        str(execution["value"]),
    )


def _unsupported_fact_key(row: dict[str, str]) -> tuple[str, str, str]:
    return (
        row.get("source_semantic_path", ""),
        row.get("source_occurrence", ""),
        row.get("source_value", ""),
    )


def collect_scope_unmapped(
    contract: Contract,
    source_rows: list[dict[str, str]],
    scope: ConversionScope,
    handled_keys: set[tuple[str, str, str]],
) -> list[dict[str, str]]:
    """Report explicitly scoped, value-present facts with no applicable Binding rule."""
    if not scope.enabled:
        return []
    issues = []
    for source_path in scope.entries:
        source = contract.source_by_path[source_path]
        for source_row in source_rows:
            if not scope.matches(contract, source_path, source_row):
                continue
            value = (source_row.get(source["local_name"]) or "").strip()
            if not value:
                continue
            key = (source_path, source_occurrence_identity(contract, source_path, source_row), value)
            if key in handled_keys:
                continue
            pseudo_rule = {
                "source_sequence": source.get("sequence", ""),
                "source_name": source.get("name", "") or source.get("local_name", ""),
                "source_semantic_path": source_path,
                "mapping_status": "",
                "target_semantic_path": "",
            }
            issues.append(unsupported_fact(
                contract,
                pseudo_rule,
                source_row,
                value,
                "UNMAPPED_CONVERSION_SOURCE_FACT",
                "explicitly scoped source fact has no applicable executable or declared non-executable Binding rule",
            ))
    return issues


def collect_declared_unsupported(contract: Contract, source_rows: list[dict[str, str]], scope: ConversionScope) -> list[dict[str, str]]:
    """Report only declared-scope source facts that actually carry a value."""
    groups = defaultdict(list)
    for rule in contract.report_rules:
        groups[rule["source_semantic_path"]].append(rule)
    issues = []
    for source_row in source_rows:
        for source_path, rules in groups.items():
            source = contract.source_by_path[source_path]
            value = (source_row.get(source["local_name"]) or "").strip()
            if not value or not scope.matches(contract, source_path, source_row):
                continue
            for rule in rules:
                if rule["source_selectors"] and not source_matches(contract, rule, source_row):
                    continue
                reason = unsupported_reason_for_binding_row(rule)
                issues.append(unsupported_fact(
                    contract, rule, source_row, value, reason,
                    "active source fact is declared by the Binding but is not executable in the current mapping",
                ))
    return issues


def select_forward_executions(contract: Contract, source_rows: list[dict[str, str]], scope: ConversionScope) -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    """Select executable active facts; ambiguous active variants are skipped and reported."""
    groups = defaultdict(list)
    for rule in contract.attr_rules:
        groups[rule["source_semantic_path"]].append(rule)
    executions = []
    issues = []
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
            if not value or not scope.matches(contract, source_path, source_row):
                continue
            matches = [rule for rule in rules if source_matches(contract, rule, source_row)]
            variant_driven = any(rule["source_selectors"] for rule in rules)
            if variant_driven and len(matches) > 1:
                issues.append(unsupported_fact(
                    contract, matches[0], source_row, value, "OTHER_ACTIVE_SOURCE_MAPPING_ERROR",
                    f"AMBIGUOUS_VARIANT: {source_path} matched {len(matches)} predicate variants",
                ))
                continue
            if variant_driven and not matches:
                # No Binding predicate selected this value/occurrence, so it is outside
                # the executable variant scope and is not user-facing unsupported data.
                continue
            for rule in matches if variant_driven else rules:
                executions.append({"rule": rule, "source_row": source_row, "value": value})
    return executions, issues


def prepare_forward_executions(contract: Contract, executions: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    """Resolve transforms/QNames per active fact so one unsupported fact cannot abort others."""
    prepared = []
    issues = []
    for execution in executions:
        rule = execution["rule"]
        source_row = execution["source_row"]
        value = str(execution["value"])
        try:
            if rule.get("target_contract_error"):
                raise BindingError(str(rule["target_contract_error"]))
            target = contract.target_by_path[rule["target_clean_path"]]
            serialized_value = contract.serialize_value(
                target, transform(value, rule["transformation"])
            )
            serialized_selectors = []
            for class_path, key, operation, lexical in rule["selectors"]:
                if operation == "absent":
                    continue
                if operation != "equals":
                    raise BindingError(
                        f"present selector serialization requires an explicit value: {class_path}.{key}"
                    )
                selected = contract.selector_row(class_path, key)
                serialized = contract.selector_serialized_value(class_path, key, lexical)
                serialized_selectors.append((class_path, key, selected, serialized))
            prepared.append({
                **execution,
                "serialized_value": serialized_value,
                "serialized_selectors": serialized_selectors,
            })
        except BindingError as exc:
            issues.append(unsupported_fact(
                contract, rule, source_row, value, unsupported_reason_for_error(exc), str(exc)
            ))
    return prepared, issues


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
    scope = ConversionScope(args.scope_file, contract)
    output = {}
    concept_columns = {}

    selected_executions, selection_issues = select_forward_executions(contract, source_rows, scope)
    declared_issues = collect_declared_unsupported(contract, source_rows, scope)
    handled_keys = {_execution_fact_key(contract, execution) for execution in selected_executions}
    handled_keys.update(_unsupported_fact_key(row) for row in selection_issues + declared_issues)
    scope_unmapped_issues = collect_scope_unmapped(contract, source_rows, scope, handled_keys)
    executions, preparation_issues = prepare_forward_executions(contract, selected_executions)
    unsupported = dedupe_unsupported(
        selection_issues + declared_issues + scope_unmapped_issues + preparation_issues
    )

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
        destination[column] = str(execution["serialized_value"])
        for class_path, key, selected, serialized in execution["serialized_selectors"]:
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

    report_path = args.unsupported_report or args.output.with_suffix(".unsupported.csv")
    if report_path.resolve() == args.output.resolve():
        raise BindingError("unsupported report path must differ from output path")
    write_unsupported(report_path, unsupported)
    if unsupported:
        print(
            f"SEMANTIC_BINDING_UNSUPPORTED: {len(unsupported)} active in-scope source fact(s) "
            f"skipped; report={report_path}"
        )

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
            command.add_argument(
                "--unsupported-report", type=Path,
                help="CSV report for active in-scope source facts skipped as unsupported; "
                     "defaults to <output>.unsupported.csv",
            )
            command.add_argument(
                "--scope-file", type=Path,
                help="Optional CSV defining the explicit forward conversion scope. "
                     "Requires source_semantic_path (or Source_Semantic_Path); "
                     "source_occurrence/Source_Occurrence may restrict an occurrence.",
            )
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
