#!/usr/bin/env python3
# coding: utf-8
"""Validate the locally deployed Canonical EN CIUS OIM dependency closure."""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TAXONOMY = ROOT / "out" / "taxonomy"
VERSION = "2026-07-05"
EN_NAMESPACE = f"http://www.xbrl.org/int/gl/en16931/{VERSION}"
PLT_NAMESPACE = f"http://www.xbrl.org/int/gl/plt/{VERSION}"
XSD = "{http://www.w3.org/2001/XMLSchema}"
XLINK_HREF = "{http://www.w3.org/1999/xlink}href"
XLINK_ARCROLE = "{http://www.w3.org/1999/xlink}arcrole"
XLINK_FROM = "{http://www.w3.org/1999/xlink}from"
XLINK_TO = "{http://www.w3.org/1999/xlink}to"
XLINK_ROLE = "{http://www.w3.org/1999/xlink}role"
LINK = "{http://www.xbrl.org/2003/linkbase}"
HYPERCUBE_DIMENSION = "http://xbrl.org/int/dim/arcrole/hypercube-dimension"
EXPECTED_OCCURRENCE_DIMENSIONS = {
    "d_en16931_Invoice",
    "d_en16931_InvoiceInvoiceNote",
    "d_en16931_InvoicePrecedingInvoiceReference",
    "d_en16931_AdditionalSupportingDocuments",
    "d_en16931_PaymentInstructions",
    "d_en16931_CreditTransfer",
    "d_en16931_DocumentLevelAllowances",
    "d_en16931_DocumentLevelCharges",
    "d_en16931_VatBreakdown",
    "d_en16931_InvoiceLine",
    "d_en16931_InvoiceLineAllowances",
    "d_en16931_InvoiceLineCharges",
    "d_en16931_ItemAttributes",
}


def parse(path: Path) -> ET.Element:
    assert path.is_file(), f"Missing file: {path}"
    return ET.parse(path).getroot()


def local_references(root: ET.Element) -> list[str]:
    references: list[str] = []
    for element in root.iter():
        if element.tag in {f"{XSD}import", f"{XSD}include"}:
            reference = element.attrib.get("schemaLocation", "")
        elif element.tag.endswith("linkbaseRef"):
            reference = element.attrib.get(XLINK_HREF, "")
        else:
            continue
        reference = reference.split("#", 1)[0]
        if reference and not reference.startswith(("http://", "https://")):
            references.append(reference)
    return references


def dependency_closure(entrypoint: Path) -> set[Path]:
    taxonomy_root = TAXONOMY.resolve()
    pending = [entrypoint.resolve()]
    discovered: set[Path] = set()
    while pending:
        current = pending.pop()
        if current in discovered:
            continue
        assert current.is_relative_to(taxonomy_root), current
        root = parse(current)
        discovered.add(current)
        for reference in local_references(root):
            target = (current.parent / reference).resolve()
            assert target.is_relative_to(taxonomy_root), (
                f"Local reference escapes taxonomy root: {current} -> {reference}"
            )
            assert target.is_file(), f"Broken local reference: {current} -> {reference}"
            pending.append(target)
    return discovered


def schema_elements(schema: ET.Element) -> list[ET.Element]:
    return list(schema.findall(f"{XSD}element"))


def main() -> int:
    entrypoint = (
        TAXONOMY
        / "oim"
        / "en16931_Invoice"
        / f"en16931-all-oim-{VERSION}.xsd"
    )
    definition_linkbase = (
        entrypoint.parent / f"en16931-all-dim-{VERSION}.xml"
    )
    module_schema = TAXONOMY / "en16931" / f"en16931-oim-{VERSION}.xsd"
    closure = dependency_closure(entrypoint)

    entry_schema = parse(entrypoint)
    module = parse(module_schema)
    assert entry_schema.attrib["targetNamespace"] == PLT_NAMESPACE
    assert module.attrib["targetNamespace"] == EN_NAMESPACE

    entry_elements = schema_elements(entry_schema)
    hypercubes = [
        element
        for element in entry_elements
        if element.attrib.get("name", "").startswith("h_en16931_")
    ]
    dimensions = [
        element
        for element in entry_elements
        if element.attrib.get("name", "").startswith("d_en16931_")
    ]
    assert len(hypercubes) == 33
    assert {element.attrib["name"] for element in dimensions} == (
        EXPECTED_OCCURRENCE_DIMENSIONS
    )
    assert all(
        element.attrib.get("substitutionGroup") == "xbrldt:hypercubeItem"
        for element in hypercubes
    )
    assert all(
        element.attrib.get("substitutionGroup") == "xbrldt:dimensionItem"
        for element in dimensions
    )
    assert all(
        element.attrib.get("{http://xbrl.org/2005/xbrldt}typedDomainRef") == "#_v"
        for element in dimensions
    )

    definition = parse(definition_linkbase)
    item_attributes_role = (
        "http://www.xbrl.org/xbrl-gl/role/link_en16931_ItemAttributes"
    )
    item_attributes_link = next(
        link
        for link in definition.findall(f"{LINK}definitionLink")
        if link.attrib.get(XLINK_ROLE) == item_attributes_role
    )
    item_attributes_dimensions = {
        arc.attrib[XLINK_TO]
        for arc in item_attributes_link.findall(f"{LINK}definitionArc")
        if arc.attrib.get(XLINK_ARCROLE) == HYPERCUBE_DIMENSION
        and arc.attrib.get(XLINK_FROM) == "h_en16931_ItemAttributes"
    }
    assert item_attributes_dimensions == {
        "d_en16931_Invoice",
        "d_en16931_InvoiceLine",
        "d_en16931_ItemAttributes",
    }
    assert "d_en16931_ItemInformation" not in item_attributes_dimensions

    module_elements = schema_elements(module)
    primary_items = [
        element
        for element in module_elements
        if element.attrib.get("name", "").startswith("p_en16931_")
    ]
    facts = [element for element in module_elements if element not in primary_items]
    assert len(primary_items) == 33
    assert len(facts) == 164
    assert all(
        element.attrib.get("substitutionGroup") == "xbrli:item"
        for element in primary_items + facts
    )

    print(
        "ok: Canonical EN OIM validation passed "
        f"(closure={len(closure)}, hypercubes={len(hypercubes)}, "
        f"dimensions={len(dimensions)}, primary_items={len(primary_items)}, "
        f"facts={len(facts)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
