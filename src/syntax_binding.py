#!/usr/bin/env python3
# coding: utf-8
"""
Convert XML to structured CSV using a syntax binding CSV.

The binding CSV maps XML locations to structured CSV columns. Supported binding
columns are intentionally permissive so the tool can read existing UADA files:

    column / element / name          output column
    xpath / source_xpath / xml_path  XML XPath
    default / fixedValue             fallback value

Use --row-xpath when one output row should be produced for each repeated XML
element. Without --row-xpath a single row is produced.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


def local_name(name: str) -> str:
    if not name:
        return ""
    if name.startswith("{"):
        return name.rsplit("}", 1)[-1]
    return name.split(":", 1)[-1]


def collect_namespaces(xml_file: Path) -> Dict[str, str]:
    namespaces: Dict[str, str] = {}
    for event, value in ET.iterparse(xml_file, events=("start-ns",)):
        prefix, uri = value
        namespaces[prefix or ""] = uri
    return namespaces


def qualify_step(step: str, namespaces: Dict[str, str]) -> str:
    if not step or step in (".", "*") or step.startswith("@"):
        return step
    if "[" in step:
        base = step.split("[", 1)[0]
    else:
        base = step
    if ":" in base:
        prefix, name = base.split(":", 1)
        uri = namespaces.get(prefix)
        return f"{{{uri}}}{name}" if uri else step
    uri = namespaces.get("")
    return f"{{{uri}}}{base}" if uri else step


def split_step_predicate(step: str) -> Tuple[str, Optional[str]]:
    if "[" not in step:
        return step, None
    base, predicate = step.split("[", 1)
    return base, predicate.rsplit("]", 1)[0].strip()


def path_value(context: ET.Element, path: str, namespaces: Dict[str, str], root: Optional[ET.Element] = None) -> str:
    path = (path or "").strip()
    if not path:
        return ""
    base_context = root if path.startswith("/") and root is not None else context
    if "/@" in path:
        element_xpath, attr_name = path.rsplit("/@", 1)
        nodes = find_nodes(base_context, element_xpath, namespaces, root)
        return nodes[0].attrib.get(attr_name, "") if nodes else ""
    if path.startswith("@"):
        return context.attrib.get(path[1:], "")
    nodes = find_nodes(base_context, path, namespaces, root)
    return " ".join((nodes[0].text or "").split()) if nodes else ""


def predicate_matches(
    child: ET.Element,
    predicate: Optional[str],
    namespaces: Dict[str, str],
    root: Optional[ET.Element] = None,
) -> bool:
    if not predicate:
        return True
    path_pattern = r"([A-Za-z_][\w.-]*:[A-Za-z_][\w.-]*(?:/(?:@[A-Za-z_][\w.-]*|[A-Za-z_][\w.-]*:[A-Za-z_][\w.-]*))*)"
    match = re.fullmatch(path_pattern + r"\s*=\s*(true|false)\(\)", predicate)
    if match:
        element_path, expected = match.groups()
        expected_text = "true" if expected == "true" else "false"
        return path_value(child, element_path, namespaces, root).lower() == expected_text
    match = re.fullmatch(path_pattern + r"\s*(=|!=)\s*'([^']*)'", predicate)
    if match:
        element_path, operator, expected_text = match.groups()
        actual = path_value(child, element_path, namespaces, root)
        return actual == expected_text if operator == "=" else bool(actual) and actual != expected_text
    match = re.fullmatch(path_pattern + r"\s*(=|!=)\s*(/[A-Za-z_][\w.-]*(?::[A-Za-z_][\w.-]*)?(?:/[A-Za-z_][\w.-]*(?::[A-Za-z_][\w.-]*)?)*)", predicate)
    if match:
        element_path, operator, reference_path = match.groups()
        actual = path_value(child, element_path, namespaces, root)
        expected = path_value(root if root is not None else child, reference_path, namespaces, root)
        return actual == expected if operator == "=" else bool(actual) and actual != expected
    return True


def child_matches(child: ET.Element, step: str, namespaces: Dict[str, str], root: Optional[ET.Element] = None) -> bool:
    base_step, predicate = split_step_predicate(step)
    qualified = qualify_step(base_step, namespaces)
    if qualified == "*":
        return predicate_matches(child, predicate, namespaces, root)
    return (
        child.tag == qualified or local_name(child.tag) == local_name(base_step)
    ) and predicate_matches(child, predicate, namespaces, root)


def split_xpath(xpath: str) -> List[str]:
    xpath = (xpath or "").strip()
    xpath = re.sub(r"^/+", "", xpath)
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
            if part and part != ".":
                parts.append(part)
            current = []
        else:
            current.append(char)
    part = "".join(current)
    if part and part != ".":
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


def find_nodes(
    context: ET.Element,
    xpath: str,
    namespaces: Dict[str, str],
    root: Optional[ET.Element] = None,
) -> List[ET.Element]:
    if root is None:
        root = context
    nodes = [context]
    parts = split_xpath(xpath)
    if parts and local_name(parts[0]) == local_name(context.tag):
        parts = parts[1:]
    for part in parts:
        if part.startswith("@"):
            return []
        next_nodes: List[ET.Element] = []
        for node in nodes:
            next_nodes.extend(child for child in list(node) if child_matches(child, part, namespaces, root))
        nodes = next_nodes
    return nodes


def get_value(context: ET.Element, xpath: str, namespaces: Dict[str, str]) -> str:
    xpath = (xpath or "").strip()
    if not xpath:
        return ""
    element_xpath, attr_name = split_terminal_attribute(xpath)
    if attr_name:
        nodes = find_nodes(context, element_xpath, namespaces)
        return nodes[0].attrib.get(attr_name, "") if nodes else ""
    if xpath.startswith("@"):
        return context.attrib.get(xpath[1:], "")
    nodes = find_nodes(context, xpath, namespaces)
    values = [" ".join((node.text or "").split()) for node in nodes if (node.text or "").strip()]
    return "|".join(values)


def first_present(row: Dict[str, str], names: Iterable[str]) -> str:
    for name in names:
        value = row.get(name)
        if value:
            return value.strip()
    return ""


def read_bindings(binding_csv: Path, encoding: str) -> List[Dict[str, str]]:
    with binding_csv.open(newline="", encoding=encoding) as f:
        rows = [dict(row) for row in csv.DictReader(f)]
    bindings = []
    for row in rows:
        column = first_present(row, ("column", "element", "name", "target", "target_column"))
        xpath = first_present(row, ("source_xpath", "xml_path", "source", "xpath"))
        if column and xpath:
            row["_column"] = column.split(":", 1)[-1]
            row["_xpath"] = xpath
            row["_default"] = first_present(row, ("default", "fixedValue", "fixed_value"))
            bindings.append(row)
    return bindings


def write_structured_csv(
    xml_file: Path,
    binding_csv: Path,
    out_csv: Path,
    row_xpath: Optional[str],
    encoding: str,
) -> Tuple[int, List[str]]:
    namespaces = collect_namespaces(xml_file)
    root = ET.parse(xml_file).getroot()
    bindings = read_bindings(binding_csv, encoding)
    if not bindings:
        raise ValueError("No usable bindings found. Provide column/element and xpath/source_xpath columns.")

    contexts = find_nodes(root, row_xpath, namespaces) if row_xpath else [root]
    if not contexts:
        raise ValueError(f"No XML nodes matched --row-xpath {row_xpath!r}.")

    fieldnames = [binding["_column"] for binding in bindings]
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding=encoding) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for context in contexts:
            record = {}
            for binding in bindings:
                value = get_value(context, binding["_xpath"], namespaces) or binding["_default"]
                record[binding["_column"]] = value
            writer.writerow(record)
    return len(contexts), fieldnames


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert XML to structured CSV using syntax bindings.")
    parser.add_argument("xml_file", type=Path, help="Input XML file")
    parser.add_argument("-b", "--binding", required=True, type=Path, help="Syntax binding CSV")
    parser.add_argument("-o", "--output", required=True, type=Path, help="Output structured CSV")
    parser.add_argument("-r", "--row-xpath", help="XPath selecting repeated row/context elements")
    parser.add_argument("-e", "--encoding", default="utf-8-sig", help="CSV encoding")
    args = parser.parse_args()

    try:
        count, fields = write_structured_csv(
            args.xml_file, args.binding, args.output, args.row_xpath, args.encoding
        )
    except Exception as exc:
        print(f"syntax_binding.py: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {count} row(s), {len(fields)} column(s) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
