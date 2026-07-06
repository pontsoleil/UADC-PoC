#!/usr/bin/env python3
# coding: utf-8
"""
Populate LHM syntax_sequence values from the UBL 2.1 XML Schema sequence order.

The script expects an extracted OASIS UBL 2.1 XSD directory, for example:
  xsd/maindoc/UBL-Invoice-2.1.xsd
  xsd/common/UBL-CommonAggregateComponents-2.1.xsd
  xsd/common/UBL-CommonBasicComponents-2.1.xsd

It does not download schemas. Keep downloaded schema packages under out/cache or
another local test directory if they should not be committed.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


XSD = "{http://www.w3.org/2001/XMLSchema}"
UBL_NAMESPACES = {
    "": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
}


@dataclass(frozen=True)
class ElementDecl:
    qname: Tuple[str, str]
    type_qname: Optional[Tuple[str, str]]


class SchemaIndex:
    def __init__(self) -> None:
        self.elements: Dict[Tuple[str, str], ElementDecl] = {}
        self.types: Dict[Tuple[str, str], List[Tuple[str, str]]] = {}

    @staticmethod
    def nsmap(path: Path) -> Dict[str, str]:
        namespaces: Dict[str, str] = {}
        for event, item in ET.iterparse(path, events=("start-ns",)):
            prefix, uri = item
            namespaces[prefix or ""] = uri
        return namespaces

    @staticmethod
    def resolve_qname(value: str, namespaces: Dict[str, str], default_ns: str) -> Tuple[str, str]:
        if ":" in value:
            prefix, local = value.split(":", 1)
            return namespaces.get(prefix, ""), local
        return default_ns, value

    @staticmethod
    def sequence_elements(parent: ET.Element, namespaces: Dict[str, str], target_ns: str) -> List[Tuple[str, str]]:
        sequence = parent.find(f"{XSD}sequence")
        if sequence is None:
            extension = parent.find(f"{XSD}complexContent/{XSD}extension")
            sequence = extension.find(f"{XSD}sequence") if extension is not None else None
        if sequence is None:
            return []
        children: List[Tuple[str, str]] = []
        for child in list(sequence):
            if child.tag != f"{XSD}element":
                continue
            ref = child.get("ref")
            name = child.get("name")
            if ref:
                children.append(SchemaIndex.resolve_qname(ref, namespaces, target_ns))
            elif name:
                children.append((target_ns, name))
        return children

    def load_xsd_tree(self, path: Path) -> None:
        namespaces = self.nsmap(path)
        tree = ET.parse(path)
        root = tree.getroot()
        target_ns = root.get("targetNamespace", "")
        for element in root.findall(f"{XSD}element"):
            name = element.get("name")
            if not name:
                continue
            type_name = element.get("type")
            type_qname = self.resolve_qname(type_name, namespaces, target_ns) if type_name else None
            qname = (target_ns, name)
            self.elements[qname] = ElementDecl(qname, type_qname)
            inline_sequence = self.sequence_elements(element, namespaces, target_ns)
            if inline_sequence:
                self.types[qname] = inline_sequence
        for complex_type in root.findall(f"{XSD}complexType"):
            name = complex_type.get("name")
            if not name:
                continue
            qname = (target_ns, name)
            sequence = self.sequence_elements(complex_type, namespaces, target_ns)
            if sequence:
                self.types[qname] = sequence

    def load_directory(self, schema_root: Path) -> None:
        for path in sorted(schema_root.rglob("*.xsd")):
            self.load_xsd_tree(path)

    def find_element(self, ns: str, local: str) -> Optional[ElementDecl]:
        found = self.elements.get((ns, local))
        if found:
            return found
        matches = [decl for key, decl in self.elements.items() if key[1] == local]
        return matches[0] if len(matches) == 1 else None

    def child_sequence(self, element: ElementDecl) -> List[Tuple[str, str]]:
        if element.type_qname and element.type_qname in self.types:
            return self.types[element.type_qname]
        return self.types.get(element.qname, [])


def clean_xpath_step(step: str) -> str:
    return re.sub(r"\[.*?\]", "", step)


def split_xpath_steps(xpath: str) -> List[str]:
    xpath = (xpath or "").strip().strip("/")
    parts: List[str] = []
    current: List[str] = []
    bracket_depth = 0
    for char in xpath:
        if char == "[":
            bracket_depth += 1
        elif char == "]":
            bracket_depth -= 1
        if char == "/" and bracket_depth == 0:
            part = "".join(current)
            if part:
                parts.append(part)
            current = []
        else:
            current.append(char)
    part = "".join(current)
    if part:
        parts.append(part)
    return parts


def split_terminal_attribute(xpath: str) -> Tuple[str, str]:
    bracket_depth = 0
    last_attribute_at = -1
    for index in range(len(xpath) - 1):
        char = xpath[index]
        if char == "[":
            bracket_depth += 1
        elif char == "]":
            bracket_depth -= 1
        elif char == "/" and bracket_depth == 0 and xpath[index + 1] == "@":
            last_attribute_at = index
    if last_attribute_at >= 0:
        return xpath[:last_attribute_at], xpath[last_attribute_at + 2 :]
    return xpath, ""


def xpath_steps(xpath: str) -> Tuple[List[str], str]:
    xpath = (xpath or "").strip()
    xpath, attribute = split_terminal_attribute(xpath)
    steps = [clean_xpath_step(step) for step in split_xpath_steps(xpath)]
    return steps, attribute


def step_qname(step: str) -> Tuple[str, str]:
    if ":" in step:
        prefix, local = step.split(":", 1)
        return UBL_NAMESPACES.get(prefix, ""), local
    return UBL_NAMESPACES[""], step


def syntax_sequence_for_xpath(index: SchemaIndex, xpath: str) -> str:
    steps, attribute = xpath_steps(xpath)
    if not steps:
        return ""
    root_ns, root_local = step_qname(steps[0])
    current = index.find_element(root_ns, root_local)
    if not current:
        return ""
    sequence = ["0000"]
    for step in steps[1:]:
        child_ns, child_local = step_qname(step)
        children = index.child_sequence(current)
        match_position = 0
        match_qname: Optional[Tuple[str, str]] = None
        for position, child_qname in enumerate(children, start=1):
            if child_qname == (child_ns, child_local) or child_qname[1] == child_local:
                match_position = position
                match_qname = child_qname
                break
        if not match_position or not match_qname:
            return ""
        sequence.append(f"{match_position:04d}")
        current = index.find_element(*match_qname)
        if not current:
            break
    if attribute:
        sequence.append(f"@{attribute}")
    return ".".join(sequence)


def sort_key(row: Dict[str, str], fallback: int) -> Tuple[str, int]:
    sequence = (row.get("syntax_sequence") or "").strip()
    if sequence:
        return sequence, fallback
    return "9999", fallback


def update_lhm(input_csv: Path, output_csv: Path, schema_root: Path, encoding: str) -> Tuple[int, int]:
    index = SchemaIndex()
    index.load_directory(schema_root)
    with input_csv.open(newline="", encoding=encoding) as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("LHM CSV has no header.")
        fieldnames = [name.lstrip("\ufeff") for name in reader.fieldnames]
        rows = [{key.lstrip("\ufeff"): value or "" for key, value in row.items()} for row in reader]
    if "syntax_sequence" not in fieldnames:
        insert_at = fieldnames.index("sequence") + 1 if "sequence" in fieldnames else 0
        fieldnames.insert(insert_at, "syntax_sequence")
    resolved = 0
    for row in rows:
        sequence = syntax_sequence_for_xpath(index, row.get("xpath", ""))
        row["syntax_sequence"] = sequence
        if sequence:
            resolved += 1
    rows = [row for _, row in sorted(enumerate(rows, start=1), key=lambda item: sort_key(item[1], item[0]))]
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding=encoding) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return resolved, len(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Update LHM syntax_sequence values from extracted UBL 2.1 XSD files.")
    parser.add_argument("input_csv", type=Path, help="Input LHM CSV")
    parser.add_argument("-o", "--output", required=True, type=Path, help="Output LHM CSV")
    parser.add_argument("--schema-root", required=True, type=Path, help="Directory containing extracted OASIS UBL 2.1 XSD files")
    parser.add_argument("-e", "--encoding", default="utf-8-sig", help="CSV encoding")
    args = parser.parse_args()
    try:
        resolved, total = update_lhm(args.input_csv, args.output, args.schema_root, args.encoding)
    except Exception as exc:
        print(f"update_lhm_syntax_sequence_from_ubl_xsd.py: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {args.output}; resolved syntax_sequence for {resolved}/{total} row(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
