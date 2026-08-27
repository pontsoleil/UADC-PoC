#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Generic Structured CSV <-> XBRL 2.1 Tuple binding.

Copyright (c) 2026 Nobuyuki Kinoshita

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

The module has no model-family branch and imports no task-history program.
Hierarchy, occurrence identity, QName validation, units, entity, period and
taxonomy references are supplied through explicit inputs.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable
import xml.etree.ElementTree as ET


XBRLI = "http://www.xbrl.org/2003/instance"
LINK = "http://www.xbrl.org/2003/linkbase"
XLINK = "http://www.w3.org/1999/xlink"
XSI = "http://www.w3.org/2001/XMLSchema-instance"
XSD = "http://www.w3.org/2001/XMLSchema"


class TupleBindingError(RuntimeError):
    """Raised when injected model, metadata, taxonomy or instance disagree."""


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = [name.lstrip("\ufeff") for name in (reader.fieldnames or [])]
        rows = [
            {key.lstrip("\ufeff"): (value or "").strip() for key, value in row.items()}
            for row in reader
        ]
    if not fields:
        raise TupleBindingError(f"CSV has no header: {path}")
    return fields, rows


def write_csv(path: Path, fields: list[str], rows: Iterable[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        document = json.load(handle)
    try:
        template = document["tableTemplates"]["structured"]
        template["dimensions"]
        template["columns"]
        document["documentInfo"]["namespaces"]
    except (KeyError, TypeError) as exc:
        raise TupleBindingError("metadata does not contain the structured-table OIM contract") from exc
    return document


@dataclass
class Model:
    records: list[dict[str, str]]
    by_path: dict[str, dict[str, str]] = field(init=False)
    parent: dict[str, str] = field(init=False)
    children: dict[str, list[dict[str, str]]] = field(init=False)

    @classmethod
    def load(cls, hmd_path: Path, overlay_path: Path | None) -> "Model":
        _fields, records = read_csv(hmd_path)
        required = {"sequence", "module", "level", "type", "datatype", "multiplicity",
                    "value_domain", "semantic_path", "local_name"}
        if not records or not required.issubset(records[0]):
            raise TupleBindingError("HMD does not satisfy the required contract")
        paths = [row["semantic_path"] for row in records]
        if len(paths) != len(set(paths)):
            raise TupleBindingError("HMD semantic_path values are not unique")
        model = cls(records)
        if overlay_path is not None:
            model.add_overlay(overlay_path)
        return model

    def __post_init__(self) -> None:
        self.by_path = {row["semantic_path"]: row for row in self.records}
        self.parent = {}
        self.children = defaultdict(list)
        stack: list[dict[str, str]] = []
        for row in self.records:
            try:
                level = int(row["level"])
            except ValueError as exc:
                raise TupleBindingError(f"invalid HMD level: {row.get('sequence')}") from exc
            while stack and int(stack[-1]["level"]) >= level:
                stack.pop()
            if stack:
                self.parent[row["semantic_path"]] = stack[-1]["semantic_path"]
                self.children[stack[-1]["semantic_path"]].append(row)
            if row["type"] == "C":
                stack.append(row)
        roots = [row for row in self.records if row["type"] == "C" and row["semantic_path"] not in self.parent]
        if len(roots) != 1:
            raise TupleBindingError(f"exactly one HMD root is required, found {len(roots)}")

    def add_overlay(self, overlay_path: Path) -> None:
        _fields, overlay_rows = read_csv(overlay_path)
        for index, source in enumerate(overlay_rows, 1):
            parent_path = source["parent_semantic_path"]
            parent = self.by_path.get(parent_path)
            if parent is None or parent["type"] != "C":
                raise TupleBindingError(f"overlay parent is not a Class: {parent_path}")
            path = parent_path + "." + source["selector_field"]
            row = {
                "sequence": f"overlay-{index}",
                "module": source["module"],
                "level": str(int(parent["level"]) + 1),
                "type": "A",
                "datatype": source["datatype"],
                "multiplicity": source["multiplicity"],
                "value_domain": source["value_domain_id"],
                "semantic_path": path,
                "local_name": source["local_name"],
                "name": source.get("name", ""),
            }
            self.records.append(row)
            # An overlay may intentionally re-project an existing selector
            # semantic path under the taxonomy's physical local name.  Keep
            # the HMD record authoritative in by_path while adding this
            # serialization projection to the same parent content model.
            self.parent.setdefault(path, parent_path)
            self.children[parent_path].append(row)

    def class_chain(self, path: str) -> list[dict[str, str]]:
        row = self.by_path[path]
        current = path if row["type"] == "C" else self.parent[path]
        chain = []
        while current:
            chain.append(self.by_path[current])
            current = self.parent.get(current, "")
        return list(reversed(chain))


@dataclass
class Contract:
    model: Model
    metadata: dict
    qname_members: dict[str, set[str]]
    namespaces: dict[str, str] = field(init=False)
    dimension_columns: list[str] = field(init=False)
    column_to_class: dict[str, str] = field(init=False)
    class_to_column: dict[str, str] = field(init=False)
    fact_columns: list[str] = field(init=False)
    column_candidates: dict[str, list[dict[str, str]]] = field(init=False)

    @classmethod
    def load(cls, model: Model, metadata_path: Path, qname_map_path: Path) -> "Contract":
        metadata = load_json(metadata_path)
        _fields, qname_rows = read_csv(qname_map_path)
        members: dict[str, set[str]] = defaultdict(set)
        for row in qname_rows:
            members[row["value_domain_id"]].add(row["member_qname"])
        return cls(model, metadata, dict(members))

    def __post_init__(self) -> None:
        self.namespaces = dict(self.metadata["documentInfo"]["namespaces"])
        template = self.metadata["tableTemplates"]["structured"]
        class_by_dimension = {
            f"d_{row['module']}_{row['local_name']}": row["semantic_path"]
            for row in self.model.records if row["type"] == "C"
        }
        self.column_to_class = {}
        self.class_to_column = {}
        for qname, reference in template["dimensions"].items():
            if not isinstance(reference, str) or not reference.startswith("$") or ":" not in qname:
                continue
            path = class_by_dimension.get(qname.split(":", 1)[1])
            if path is None:
                raise TupleBindingError(f"metadata dimension cannot resolve to HMD Class: {qname}")
            column = reference[1:]
            if path in self.class_to_column or column in self.column_to_class:
                raise TupleBindingError(f"duplicate occurrence dimension: {qname}")
            self.column_to_class[column] = path
            self.class_to_column[path] = column
        columns = template["columns"]
        self.dimension_columns = [name for name in columns if name in self.column_to_class]
        self.fact_columns = []
        self.column_candidates = {}
        for column, definition in columns.items():
            concept = definition.get("dimensions", {}).get("concept") if isinstance(definition, dict) else None
            if not concept:
                continue
            if ":" not in concept:
                raise TupleBindingError(f"fact concept is not a QName: {column}")
            module, local_name = concept.split(":", 1)
            candidates = [
                row for row in self.model.records
                if row["type"] == "A" and row["module"] == module and row["local_name"] == local_name
            ]
            if not candidates:
                raise TupleBindingError(f"metadata fact cannot resolve to HMD/overlay: {column} -> {concept}")
            self.fact_columns.append(column)
            self.column_candidates[column] = candidates

    def record_for(self, column: str, physical_row: dict[str, str]) -> dict[str, str]:
        applicable = []
        for candidate in self.column_candidates[column]:
            owner = self.model.parent[candidate["semantic_path"]]
            required = [
                self.class_to_column[item["semantic_path"]]
                for item in self.model.class_chain(owner)
                if item["semantic_path"] in self.class_to_column
            ]
            if all(physical_row.get(name, "") for name in required):
                applicable.append(candidate)
        if len(applicable) != 1:
            raise TupleBindingError(f"{column} resolves to {len(applicable)} HMD/overlay records")
        return applicable[0]

    def validate_value(self, record: dict[str, str], value: str) -> None:
        if not value:
            return
        if ":" in value:
            prefix = value.split(":", 1)[0]
            domain = record.get("value_domain", "")
            # A colon can also occur in dateTime and URI lexical values.  It is
            # an EE1 QName only when its prefix is declared by the metadata.
            if prefix in self.namespaces and domain and value not in self.qname_members.get(domain, set()):
                raise TupleBindingError(f"QName is not a member of {domain}: {value}")

    def qname(self, record: dict[str, str]) -> str:
        uri = self.namespaces.get(record["module"])
        if uri is None:
            raise TupleBindingError(f"namespace is missing for module {record['module']}")
        return f"{{{uri}}}{record['local_name']}"


@dataclass
class Occurrence:
    record: dict[str, str]
    identity: tuple[tuple[str, str], ...]
    facts: dict[str, tuple[dict[str, str], str]] = field(default_factory=dict)
    children: dict[str, list["Occurrence"]] = field(default_factory=lambda: defaultdict(list))


def _ordinal_key(identity: tuple[tuple[str, str], ...]) -> tuple:
    return tuple((0, int(value)) if value.isdigit() else (1, value) for _name, value in identity)


def build_occurrences(rows: list[dict[str, str]], contract: Contract) -> list[Occurrence]:
    nodes: dict[tuple[str, tuple[tuple[str, str], ...]], Occurrence] = {}

    def identity(class_path: str, row: dict[str, str]) -> tuple[tuple[str, str], ...]:
        pairs = []
        for ancestor in contract.model.class_chain(class_path):
            column = contract.class_to_column.get(ancestor["semantic_path"])
            if column:
                value = row.get(column, "")
                if not value:
                    raise TupleBindingError(f"missing occurrence column {column} for {class_path}")
                if not value.isdigit() or int(value) < 1:
                    raise TupleBindingError(f"occurrence ordinal must be a positive integer: {column}={value}")
                pairs.append((column, value))
        return tuple(pairs)

    for row in rows:
        for column in contract.fact_columns:
            value = row.get(column, "")
            if not value:
                continue
            attribute = contract.record_for(column, row)
            contract.validate_value(attribute, value)
            owner_path = contract.model.parent[attribute["semantic_path"]]
            parent_node = None
            for class_record in contract.model.class_chain(owner_path):
                node_key = (class_record["semantic_path"], identity(class_record["semantic_path"], row))
                node = nodes.setdefault(node_key, Occurrence(class_record, node_key[1]))
                if parent_node is not None and node not in parent_node.children[class_record["semantic_path"]]:
                    parent_node.children[class_record["semantic_path"]].append(node)
                parent_node = node
            assert parent_node is not None
            previous = parent_node.facts.get(attribute["local_name"])
            if previous is not None and previous[1] != value:
                raise TupleBindingError(f"fact collision at {attribute['semantic_path']}")
            parent_node.facts[attribute["local_name"]] = (attribute, value)
    roots = [node for (path, _identity), node in nodes.items() if path not in contract.model.parent]
    return sorted(roots, key=lambda item: _ordinal_key(item.identity))


def load_content_order(entry_point: Path) -> dict[tuple[str, str], list[tuple[str, bool]]]:
    directory = entry_point.resolve().parent
    schemas = sorted(directory.glob("*-content-*.xsd"))
    if not schemas:
        raise TupleBindingError(f"Tuple content schemas not found beside entry point: {entry_point}")
    result = {}
    ns = {"xs": XSD}
    for schema in schemas:
        module = schema.name.split("-", 1)[0]
        root = ET.parse(schema).getroot()
        for complex_type in root.findall("xs:complexType", ns):
            sequence = complex_type.find("xs:sequence", ns)
            if sequence is None:
                continue
            result[(module, complex_type.get("name", ""))] = [
                (element.get("ref", "").split(":", 1)[-1], element.get("minOccurs", "1") != "0")
                for element in sequence.findall("xs:element", ns)
            ]
    return result


def _entity_and_period(root: ET.Element, contract: Contract) -> None:
    dimensions = contract.metadata["tableTemplates"]["structured"]["dimensions"]
    entity_value = str(dimensions.get("entity", ""))
    if ":" not in entity_value:
        raise TupleBindingError("metadata entity must use prefix:identifier")
    prefix, identifier_value = entity_value.split(":", 1)
    scheme = contract.namespaces.get(prefix)
    if not scheme or not identifier_value:
        raise TupleBindingError("metadata entity prefix or identifier is unresolved")
    context = ET.SubElement(root, f"{{{XBRLI}}}context", {"id": "c-1"})
    entity = ET.SubElement(context, f"{{{XBRLI}}}entity")
    ET.SubElement(entity, f"{{{XBRLI}}}identifier", {"scheme": scheme}).text = identifier_value
    period = ET.SubElement(context, f"{{{XBRLI}}}period")
    period_value = str(dimensions.get("period", ""))
    if period_value == "forever":
        ET.SubElement(period, f"{{{XBRLI}}}forever")
    elif "/" in period_value:
        start, end = period_value.split("/", 1)
        ET.SubElement(period, f"{{{XBRLI}}}startDate").text = start[:10]
        ET.SubElement(period, f"{{{XBRLI}}}endDate").text = end[:10]
    elif period_value:
        ET.SubElement(period, f"{{{XBRLI}}}instant").text = period_value[:10]
    else:
        raise TupleBindingError("metadata period is empty")


def _unit_id(unit_qname: str) -> str:
    return "u-" + re.sub(r"[^A-Za-z0-9_.-]", "-", unit_qname)


def serialize(
    input_csv: Path,
    metadata_json: Path,
    hmd: Path,
    qname_map: Path,
    taxonomy: Path,
    output_xml: Path,
    *,
    overlay: Path | None = None,
    nil_manifest: Path | None = None,
) -> dict[str, int]:
    """Serialize semantic Structured CSV into one XBRL 2.1 Tuple instance."""
    model = Model.load(hmd, overlay)
    contract = Contract.load(model, metadata_json, qname_map)
    fields, rows = read_csv(input_csv)
    unknown = [name for name in fields if name not in contract.dimension_columns + contract.fact_columns]
    if unknown:
        raise TupleBindingError(f"CSV columns are absent from metadata: {unknown}")
    if not taxonomy.is_file():
        raise TupleBindingError(f"Tuple taxonomy entry point not found: {taxonomy}")
    content_order = load_content_order(taxonomy)
    for prefix, uri in contract.namespaces.items():
        if prefix not in {"xml", "xmlns", "xbrl"}:
            ET.register_namespace(prefix, uri)
    ET.register_namespace("xbrli", XBRLI)
    ET.register_namespace("link", LINK)
    ET.register_namespace("xlink", XLINK)
    ET.register_namespace("xsi", XSI)
    root = ET.Element(f"{{{XBRLI}}}xbrl")
    # QName-valued facts and unit measures require visible prefix declarations.
    used_text_prefixes = {value.split(":", 1)[0] for row in rows for value in row.values() if ":" in value}
    for prefix in sorted(used_text_prefixes):
        uri = contract.namespaces.get(prefix)
        if uri and prefix not in {"xbrli", "link", "xlink", "xsi"}:
            root.set(f"xmlns:{prefix}", uri)
    relative_entry = Path(os.path.relpath(taxonomy.resolve(), output_xml.resolve().parent)).as_posix()
    ET.SubElement(root, f"{{{LINK}}}schemaRef", {
        f"{{{XLINK}}}type": "simple", f"{{{XLINK}}}href": relative_entry,
    })
    _entity_and_period(root, contract)
    column_definitions = contract.metadata["tableTemplates"]["structured"]["columns"]
    units = {
        definition.get("dimensions", {}).get("unit")
        for definition in column_definitions.values() if isinstance(definition, dict)
    }
    units.discard(None)
    numeric_records = [candidate for values in contract.column_candidates.values() for candidate in values]
    if any(record.get("datatype", "").lower() in {"decimal", "integer", "pure"} for record in numeric_records):
        units.add("xbrli:pure")
    for unit_qname in sorted(units):
        if ":" not in unit_qname or unit_qname.split(":", 1)[0] not in contract.namespaces:
            raise TupleBindingError(f"unit QName cannot resolve: {unit_qname}")
        unit_prefix = unit_qname.split(":", 1)[0]
        if unit_prefix not in {"xbrli", "link", "xlink", "xsi"}:
            root.set(f"xmlns:{unit_prefix}", contract.namespaces[unit_prefix])
        unit = ET.SubElement(root, f"{{{XBRLI}}}unit", {"id": _unit_id(unit_qname)})
        ET.SubElement(unit, f"{{{XBRLI}}}measure").text = unit_qname

    nil_rows: list[dict[str, str]] = []
    fact_count = 0
    tuple_count = 0

    def fact_attributes(record: dict[str, str], column: str) -> dict[str, str]:
        datatype = record.get("datatype", "").lower()
        unit = column_definitions.get(column, {}).get("dimensions", {}).get("unit", "")
        result = {"contextRef": "c-1"}
        if unit:
            result.update({"unitRef": _unit_id(unit), "decimals": "2" if "amount" in datatype else "INF"})
        elif datatype in {"decimal", "integer", "pure"}:
            result.update({"unitRef": _unit_id("xbrli:pure"), "decimals": "INF"})
        return result

    def emit(parent: ET.Element, occurrence: Occurrence) -> None:
        nonlocal fact_count, tuple_count
        tuple_count += 1
        element = ET.SubElement(parent, contract.qname(occurrence.record))
        available = contract.model.children.get(occurrence.record["semantic_path"], [])
        by_local = {row["local_name"]: row for row in available}
        order = content_order.get((occurrence.record["module"], occurrence.record["local_name"] + "ComplexType"))
        if order is None:
            raise TupleBindingError(f"Tuple content model is unresolved: {occurrence.record['semantic_path']}")
        for local_name, required in order:
            child = by_local.get(local_name)
            if child is None:
                continue
            if child["type"] == "A":
                pair = occurrence.facts.get(local_name)
                if pair is None and not required:
                    continue
                value = pair[1] if pair else ""
                contract.validate_value(child, value)
                attributes = fact_attributes(child, local_name)
                if not value:
                    attributes[f"{{{XSI}}}nil"] = "true"
                    nil_rows.append({
                        "semantic_path": child["semantic_path"],
                        "occurrence_dimensions": json.dumps(dict(occurrence.identity), ensure_ascii=False, sort_keys=True),
                        "reason": "required by Tuple content model; semantic fact absent",
                    })
                fact = ET.SubElement(element, contract.qname(child), attributes)
                if value:
                    fact.text = value
                    fact_count += 1
            else:
                nested = sorted(occurrence.children.get(child["semantic_path"], []), key=lambda item: _ordinal_key(item.identity))
                for item in nested:
                    emit(element, item)
                if required and not nested:
                    emit(element, Occurrence(child, occurrence.identity))

    for occurrence in build_occurrences(rows, contract):
        emit(root, occurrence)
    output_xml.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(root, space="  ")
    ET.ElementTree(root).write(output_xml, encoding="utf-8", xml_declaration=True)
    if nil_manifest is not None:
        write_csv(nil_manifest, ["semantic_path", "occurrence_dimensions", "reason"], nil_rows)
    return {"input_rows": len(rows), "fact_count": fact_count, "nil_count": len(nil_rows), "tuple_count": tuple_count}


def _verify_context(root: ET.Element, contract: Contract) -> None:
    contexts = root.findall(f"{{{XBRLI}}}context")
    if len(contexts) != 1 or contexts[0].get("id") != "c-1":
        raise TupleBindingError("exactly one context c-1 is required")
    identifier = contexts[0].find(f"{{{XBRLI}}}entity/{{{XBRLI}}}identifier")
    if identifier is None:
        raise TupleBindingError("context entity identifier is missing")
    dimensions = contract.metadata["tableTemplates"]["structured"]["dimensions"]
    prefix, value = str(dimensions["entity"]).split(":", 1)
    if identifier.get("scheme") != contract.namespaces.get(prefix) or (identifier.text or "") != value:
        raise TupleBindingError("instance entity does not match metadata")


def deserialize(
    input_xml: Path,
    metadata_json: Path,
    hmd: Path,
    qname_map: Path,
    taxonomy: Path,
    output_csv: Path,
    *,
    overlay: Path | None = None,
    nil_manifest: Path | None = None,
) -> dict[str, int]:
    """Restore Structured CSV facts and occurrence ordinals from a Tuple instance."""
    model = Model.load(hmd, overlay)
    contract = Contract.load(model, metadata_json, qname_map)
    root = ET.parse(input_xml).getroot()
    if root.tag != f"{{{XBRLI}}}xbrl":
        raise TupleBindingError("input is not an XBRL 2.1 instance")
    schema_refs = root.findall(f"{{{LINK}}}schemaRef")
    if len(schema_refs) != 1:
        raise TupleBindingError("exactly one schemaRef is required")
    href = schema_refs[0].get(f"{{{XLINK}}}href", "")
    if (input_xml.resolve().parent / href).resolve() != taxonomy.resolve():
        raise TupleBindingError("instance schemaRef does not resolve to the injected Tuple entry point")
    _verify_context(root, contract)
    class_by_qname = {contract.qname(row): row for row in model.records if row["type"] == "C"}
    rows: list[dict[str, str]] = []
    nil_rows: list[dict[str, str]] = []
    # Structured CSV occurrence ordinals are document-wide within each Class
    # dimension column.  Tuple document order therefore deterministically
    # reconstructs 1..N for that column, including nested Classes whose parent
    # occurrences differ.
    counters: Counter[str] = Counter()
    tuple_count = 0
    fact_count = 0

    def walk(element: ET.Element, class_record: dict[str, str], inherited: dict[str, str]) -> None:
        nonlocal tuple_count, fact_count
        tuple_count += 1
        dimensions = dict(inherited)
        dimension_column = contract.class_to_column.get(class_record["semantic_path"])
        if dimension_column:
            counters[dimension_column] += 1
            dimensions[dimension_column] = str(counters[dimension_column])
        direct_attributes = {
            contract.qname(row): row
            for row in model.children.get(class_record["semantic_path"], []) if row["type"] == "A"
        }
        values: dict[str, str] = {}
        nested: list[tuple[ET.Element, dict[str, str]]] = []
        for child in list(element):
            attribute = direct_attributes.get(child.tag)
            if attribute is not None:
                if child.get(f"{{{XSI}}}nil") == "true":
                    nil_rows.append({
                        "semantic_path": attribute["semantic_path"],
                        "occurrence_dimensions": json.dumps(dimensions, ensure_ascii=False, sort_keys=True),
                        "reason": "xsi:nil fact in Tuple instance",
                    })
                    continue
                value = (child.text or "").strip()
                if not value:
                    raise TupleBindingError(f"non-nil fact has an empty lexical value: {attribute['semantic_path']}")
                contract.validate_value(attribute, value)
                values[attribute["local_name"]] = value
                fact_count += 1
            elif child.tag in class_by_qname:
                nested.append((child, class_by_qname[child.tag]))
            else:
                raise TupleBindingError(f"unexpected Tuple child: {child.tag}")
        if values:
            rows.append({**dimensions, **values})
        for child, child_record in nested:
            if model.parent.get(child_record["semantic_path"]) != class_record["semantic_path"]:
                raise TupleBindingError(f"Tuple parent mismatch: {child_record['semantic_path']}")
            walk(child, child_record, dimensions)

    ignored = {f"{{{LINK}}}schemaRef", f"{{{XBRLI}}}context", f"{{{XBRLI}}}unit"}
    roots = []
    for child in list(root):
        if child.tag in ignored:
            continue
        record = class_by_qname.get(child.tag)
        if record is None or record["semantic_path"] in model.parent:
            raise TupleBindingError(f"unexpected instance-root child: {child.tag}")
        roots.append((child, record))
    for element, record in roots:
        walk(element, record, {})
    fields = contract.dimension_columns + contract.fact_columns
    # Match the Canonical semantic runtime's Structured CSV ordering contract:
    # compare every declared dimension in metadata order and treat absence as
    # zero.  Reverse semantic occurrence reconstruction depends on this stable
    # physical order when several target Classes feed separate source Classes.
    rows.sort(key=lambda row: tuple(int(row.get(name, "0") or 0) for name in contract.dimension_columns))
    write_csv(output_csv, fields, rows)
    if nil_manifest is not None:
        write_csv(nil_manifest, ["semantic_path", "occurrence_dimensions", "reason"], nil_rows)
    return {"output_rows": len(rows), "fact_count": fact_count, "nil_count": len(nil_rows), "tuple_count": tuple_count}


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    for name in ("serialize", "deserialize"):
        command = commands.add_parser(name)
        command.add_argument("input", type=Path)
        command.add_argument("--metadata", type=Path, required=True)
        command.add_argument("--hmd", type=Path, required=True)
        command.add_argument("--overlay", type=Path)
        command.add_argument("--qname-map", type=Path, required=True)
        command.add_argument("--taxonomy", type=Path, required=True)
        command.add_argument("--output", type=Path, required=True)
        command.add_argument("--nil-manifest", type=Path)
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        common = dict(
            metadata_json=args.metadata,
            hmd=args.hmd,
            overlay=args.overlay,
            qname_map=args.qname_map,
            taxonomy=args.taxonomy,
            nil_manifest=args.nil_manifest,
        )
        if args.command == "serialize":
            result = serialize(args.input, output_xml=args.output, **common)
        else:
            result = deserialize(args.input, output_csv=args.output, **common)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    except (OSError, UnicodeError, csv.Error, json.JSONDecodeError, ET.ParseError, TupleBindingError) as exc:
        print(f"TUPLE_BINDING_ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
