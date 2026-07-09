#!/usr/bin/env python3
# coding: utf-8
"""
Generate XBRL GL tuple instances from UADC structured CSV files.

Purpose:
    Convert UADC proof-of-concept structured CSV data into XBRL GL XML tuple
    instances by applying ADS syntax bindings and LHM semantic column mappings.

Processing overview:
    The script reads one structured CSV file, or all CSV files in a directory,
    resolves semantic paths to source columns through an LHM CSV, applies the
    ADS binding XPath targets, builds XBRL GL contexts, units, document info,
    tax structures, and ordered tuple elements, then writes XML instance files.

Command-line arguments:
    input: Structured CSV file, or directory containing structured CSV files.
    -b, --binding-csv: ADS syntax binding CSV with semantic_path, element, and xpath.
    --lhm-csv: LHM CSV used to resolve semantic_path values to CSV columns.
    -o, --output-dir: Directory for generated XBRL GL XML instance files.
    --schema-href: schemaRef href for the XBRL GL tuple taxonomy entry point.
    --monetary-decimals: Decimals attribute written for monetary facts.

Results:
    Writes one *.xbrl.xml file per input CSV and prints the generated file count.
    Returns exit code 0 on success.

Copyright 2026 Sambuichi Professional Engineers Office
Designed by SAMBUICHI, Nobuyuki
Produced by ChatGPT & Codex, edited by  SAMBUICHI, Nobuyuki
MIT License
CC-BY-NC
"""

from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path
import re
import xml.etree.ElementTree as ET


NS = {
    "xbrli": "http://www.xbrl.org/2003/instance",
    "xbrll": "http://www.xbrl.org/2003/linkbase",
    "xlink": "http://www.w3.org/1999/xlink",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "gl-cor": "http://www.xbrl.org/int/gl/cor/2016-12-01",
    "gl-bus": "http://www.xbrl.org/int/gl/bus/2016-12-01",
    "gl-muc": "http://www.xbrl.org/int/gl/muc/2016-12-01",
    "gl-plt": "http://www.xbrl.org/int/gl/plt/2016-12-01",
    "gl-taf": "http://www.xbrl.org/int/gl/taf/2016-12-01",
    "gl-srcd": "http://www.xbrl.org/int/gl/srcd/2016-12-01",
    "iso4217": "http://www.xbrl.org/2003/iso4217",
    "iso639": "http://www.xbrl.org/2005/iso639",
}

XLINK_TYPE = f"{{{NS['xlink']}}}type"
XLINK_ARCROLE = f"{{{NS['xlink']}}}arcrole"
XLINK_HREF = f"{{{NS['xlink']}}}href"
XSI_SCHEMA_LOCATION = f"{{{NS['xsi']}}}schemaLocation"
SELECTOR_RE = re.compile(r"\[([^=\]]+)=(?:\"([^\"]*)\"|'([^']*)')\]")
SELECTOR_VALUE_ALIASES = {
    ("gl-cor:identifierType", "S"): "V",
    ("gl-taf:originatingDocumentType", "105"): "order-vendor",
}

MONETARY_LOCAL_NAMES = {
    "amount",
    "amountOriginalAmount",
    "taxAmount",
}

ORDER_MAPS = {
    "gl-cor:accountingEntries": ["gl-cor:documentInfo", "gl-cor:entityInformation", "gl-cor:entryHeader"],
    "gl-cor:entityInformation": [
        "gl-bus:entityPhoneNumber",
        "gl-bus:entityFaxNumberStructure",
        "gl-bus:entityEmailAddressStructure",
        "gl-bus:organizationAccountingMethodPurposeDefault",
        "gl-bus:organizationAccountingMethodPurposeDefaultDescription",
        "gl-bus:organizationIdentifiers",
        "gl-bus:organizationAddress",
        "gl-bus:entityWebSite",
        "gl-bus:contactInformation",
        "gl-bus:businessDescription",
        "gl-bus:fiscalYearStart",
        "gl-bus:fiscalYearEnd",
    ],
    "gl-cor:entryHeader": [
        "gl-cor:postedDate",
        "gl-cor:enteredBy",
        "gl-bus:enteredByModified",
        "gl-cor:enteredDate",
        "gl-bus:entryResponsiblePerson",
        "gl-cor:sourceJournalID",
        "gl-bus:sourceJournalDescription",
        "gl-cor:entryType",
        "gl-bus:entryOrigin",
        "gl-cor:entryNumber",
        "gl-cor:entryComment",
        "gl-cor:qualifierEntry",
        "gl-cor:qualifierEntryDescription",
        "gl-bus:postingCode",
        "gl-cor:bookTaxDifference",
        "gl-cor:entryDetail",
    ],
    "gl-cor:entryDetail": [
        "gl-cor:lineNumber",
        "gl-cor:lineNumberCounter",
        "gl-cor:account",
        "gl-cor:amount",
        "gl-muc:amountCurrency",
        "gl-muc:amountOriginalExchangeRateDate",
        "gl-muc:amountOriginalAmount",
        "gl-muc:amountOriginalCurrency",
        "gl-cor:signOfAmount",
        "gl-cor:debitCreditCode",
        "gl-cor:postingDate",
        "gl-bus:amountMemo",
        "gl-cor:identifierReference",
        "gl-cor:documentType",
        "gl-cor:documentTypeDescription",
        "gl-cor:invoiceType",
        "gl-cor:documentNumber",
        "gl-cor:documentApplyToNumber",
        "gl-cor:documentReference",
        "gl-cor:documentDate",
        "gl-cor:maturityDate",
        "gl-cor:terms",
        "gl-cor:taxes",
        "gl-taf:originatingDocumentStructure",
    ],
    "gl-cor:taxes": [
        "gl-cor:taxAuthority",
        "gl-cor:taxTableCode",
        "gl-cor:taxDescription",
        "gl-cor:taxAmount",
        "gl-cor:taxBasis",
        "gl-cor:taxExchangeRate",
        "gl-cor:taxPercentageRate",
        "gl-cor:taxCode",
        "gl-cor:taxCommentExemption",
    ],
    "gl-cor:identifierReference": [
        "gl-cor:identifierCode",
        "gl-cor:identifierExternalReference",
        "gl-cor:identifierOrganizationType",
        "gl-cor:identifierOrganizationTypeDescription",
        "gl-cor:identifierDescription",
        "gl-cor:identifierType",
        "gl-cor:identifierCategory",
        "gl-cor:identifierActive",
    ],
    "gl-taf:originatingDocumentStructure": [
        "gl-taf:originatingDocumentType",
        "gl-taf:originatingDocumentNumber",
        "gl-taf:originatingDocumentDate",
        "gl-taf:originatingDocumentIdentifierType",
        "gl-taf:originatingDocumentIdentifierCode",
        "gl-taf:originatingDocumentIdentifierTaxCode",
    ],
}


for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)


def qname(prefixed_name: str) -> str:
    """
    Build an ElementTree QName from a prefixed XML name.

    Args:
        prefixed_name: Input value used by qname.

    Returns:
        Result produced by qname.
    """
    prefix, local = prefixed_name.split(":", 1)
    return f"{{{NS[prefix]}}}{local}"


def local_name(prefixed_name: str) -> str:
    """
    Return the local component of a qualified or prefixed name.

    Args:
        prefixed_name: Input value used by local_name.

    Returns:
        Result produced by local_name.
    """
    return prefixed_name.split(":", 1)[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    """
    Read a UTF-8-SIG CSV file into dictionaries.

    Args:
        path: Input value used by read_csv.

    Returns:
        Result produced by read_csv.
    """
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def load_lhm_semantic_columns(lhm_csv: Path) -> dict[str, str]:
    """
    Load semantic_path to element-column mappings from an LHM CSV.

    Args:
        lhm_csv: Input value used by load_lhm_semantic_columns.

    Returns:
        Result produced by load_lhm_semantic_columns.
    """
    mapping: dict[str, str] = {}
    for row in read_csv(lhm_csv):
        semantic_path = (row.get("semantic_path") or "").strip()
        element = (row.get("element") or "").strip()
        if semantic_path and element:
            mapping[semantic_path] = element
    return mapping


def load_bindings(binding_csv: Path, lhm_columns: dict[str, str]) -> list[dict[str, str]]:
    """
    Load usable ADS binding rows and attach resolved source columns.

    Args:
        binding_csv: Input value used by load_bindings.
        lhm_columns: Input value used by load_bindings.

    Returns:
        Result produced by load_bindings.
    """
    bindings: list[dict[str, str]] = []
    for row in read_csv(binding_csv):
        semantic_path = (row.get("semantic_path") or "").strip()
        xpath = (row.get("xpath") or "").strip()
        target_element = (row.get("element") or "").strip()
        source_column = lhm_columns.get(semantic_path)
        if not source_column or not xpath or not target_element:
            continue
        bindings.append(
            {
                "semantic_path": semantic_path,
                "source_column": source_column,
                "target_element": target_element,
                "xpath": xpath,
                "datatype": (row.get("datatype") or "").strip(),
                "label": (row.get("label_local") or "").strip(),
            }
        )
    return bindings


def first_non_empty(rows: list[dict[str, str]], column: str) -> str:
    """
    Find the first non-empty value for a column across rows.

    Args:
        rows: Input value used by first_non_empty.
        column: Input value used by first_non_empty.

    Returns:
        Result produced by first_non_empty.
    """
    for row in rows:
        value = (row.get(column) or "").strip()
        if value:
            return value
    return ""


def rows_for_binding(rows: list[dict[str, str]], binding: dict[str, str]) -> list[dict[str, str]]:
    """
    Select structured CSV rows relevant to a binding.

    Args:
        rows: Input value used by rows_for_binding.
        binding: Input value used by rows_for_binding.

    Returns:
        Result produced by rows_for_binding.
    """
    semantic_path = binding["semantic_path"]
    source_column = binding["source_column"]
    value_rows = [row for row in rows if (row.get(source_column) or "").strip()]
    if ".vatBreakdown." in semantic_path:
        return [row for row in value_rows if (row.get("dVatBreakdown") or "").strip()]
    if ".invoiceLine." in semantic_path:
        return [row for row in value_rows if (row.get("dInvoiceLine") or "").strip()]
    return value_rows[:1]


def append_item(parent: ET.Element, target_element: str, value: str, currency: str, monetary_decimals: str) -> None:
    """
    Append an XBRL GL fact element to a parent node.

    Args:
        parent: Input value used by append_item.
        target_element: Input value used by append_item.
        value: Input value used by append_item.
        currency: Input value used by append_item.
        monetary_decimals: Input value used by append_item.

    Returns:
        None. A child element is appended to parent.
    """
    item = ET.SubElement(parent, qname(target_element))
    item.set("contextRef", "now")
    if local_name(target_element) in MONETARY_LOCAL_NAMES:
        item.set("decimals", monetary_decimals)
        item.set("unitRef", currency or "NotUsed")
    item.text = value


def path_parts(xpath: str) -> list[str]:
    """
    Split an XBRL XPath into top-level path steps.

    Args:
        xpath: Input value used by path_parts.

    Returns:
        Result produced by path_parts.
    """
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    for char in xpath.strip():
        if char == "/" and depth == 0:
            part = "".join(current).strip()
            if part:
                parts.append(part)
            current = []
            continue
        if char == "[":
            depth += 1
        elif char == "]" and depth:
            depth -= 1
        current.append(char)
    part = "".join(current).strip()
    if part:
        parts.append(part)
    if not parts or parts[0] != "xbrli:xbrl":
        raise ValueError(f"Binding XPath must start with /xbrli:xbrl: {xpath}")
    return parts[1:]


def parse_path_step(step: str) -> tuple[str, list[tuple[str, str]]]:
    """
    Split one XPath step into its element name and selector predicates.

    Args:
        step: Input value used by parse_path_step.

    Returns:
        Result produced by parse_path_step.
    """
    name = step.split("[", 1)[0]
    selectors = []
    for match in SELECTOR_RE.finditer(step):
        selector_name = match.group(1)
        selector_value = match.group(2) if match.group(2) is not None else match.group(3)
        selectors.append((selector_name, SELECTOR_VALUE_ALIASES.get((selector_name, selector_value), selector_value)))
    return name, selectors


def selector_matches(element: ET.Element, selectors: list[tuple[str, str]]) -> bool:
    """
    Check whether an XML element satisfies selector child values.

    Args:
        element: Input value used by selector_matches.
        selectors: Input value used by selector_matches.

    Returns:
        Result produced by selector_matches.
    """
    for selector_name, selector_value in selectors:
        selector_tag = qname(selector_name)
        matched = False
        for child in list(element):
            if child.tag == selector_tag and (child.text or "") == selector_value:
                matched = True
                break
        if not matched:
            return False
    return True


def add_selector_values(parent: ET.Element, selectors: list[tuple[str, str]], currency: str, monetary_decimals: str) -> None:
    """
    Add selector child elements required by an XPath predicate.

    Args:
        parent: Input value used by add_selector_values.
        selectors: Input value used by add_selector_values.
        currency: Input value used by add_selector_values.
        monetary_decimals: Input value used by add_selector_values.

    Returns:
        None. Selector elements are appended when missing.
    """
    for selector_name, selector_value in selectors:
        if not selector_matches(parent, [(selector_name, selector_value)]):
            append_item(parent, selector_name, selector_value, currency, monetary_decimals)


def ensure_child(parent: ET.Element, path_step: str, currency: str = "", monetary_decimals: str = "2") -> ET.Element:
    """
    Find or create a child matching an XPath step.

    Args:
        parent: Input value used by ensure_child.
        path_step: Input value used by ensure_child.
        currency: Input value used by ensure_child.
        monetary_decimals: Input value used by ensure_child.

    Returns:
        Result produced by ensure_child.
    """
    prefixed_name, selectors = parse_path_step(path_step)
    tag = qname(prefixed_name)
    for child in list(parent):
        if child.tag == tag and selector_matches(child, selectors):
            return child
    child = ET.SubElement(parent, tag)
    add_selector_values(child, selectors, currency, monetary_decimals)
    return child


def container_for_path(root: ET.Element, xpath: str, currency: str = "", monetary_decimals: str = "2") -> ET.Element:
    """
    Resolve the XML container element for the final fact in an XPath.

    Args:
        root: Input value used by container_for_path.
        xpath: Input value used by container_for_path.
        currency: Input value used by container_for_path.
        monetary_decimals: Input value used by container_for_path.

    Returns:
        Result produced by container_for_path.
    """
    parts = path_parts(xpath)
    parent = root
    for part in parts[:-1]:
        parent = ensure_child(parent, part, currency, monetary_decimals)
    return parent


def make_xbrl_root(schema_href: str) -> ET.Element:
    """
    Create the root XBRL instance element and schema reference.

    Args:
        schema_href: Input value used by make_xbrl_root.

    Returns:
        Result produced by make_xbrl_root.
    """
    root = ET.Element(qname("xbrli:xbrl"))
    root.set("xmlns:iso4217", NS["iso4217"])
    root.set("xmlns:iso639", NS["iso639"])
    root.set(XSI_SCHEMA_LOCATION, f"{NS['gl-plt']} {schema_href}")
    schema_ref = ET.SubElement(root, qname("xbrll:schemaRef"))
    schema_ref.set(XLINK_TYPE, "simple")
    schema_ref.set(XLINK_ARCROLE, "http://www.w3.org/1999/xlink/properties/linkbase")
    schema_ref.set(XLINK_HREF, schema_href)
    return root


def add_context_and_units(root: ET.Element, entity: str, instant: str, currency: str) -> None:
    """
    Add XBRL context and unit declarations to an instance.

    Args:
        root: Input value used by add_context_and_units.
        entity: Input value used by add_context_and_units.
        instant: Input value used by add_context_and_units.
        currency: Input value used by add_context_and_units.

    Returns:
        None. The root XML element is modified in place.
    """
    context = ET.SubElement(root, qname("xbrli:context"), {"id": "now"})
    entity_element = ET.SubElement(context, qname("xbrli:entity"))
    identifier = ET.SubElement(entity_element, qname("xbrli:identifier"), {"scheme": "https://example.com/uadc-poc"})
    identifier.text = entity or "UADC-PoC"
    period = ET.SubElement(context, qname("xbrli:period"))
    ET.SubElement(period, qname("xbrli:instant")).text = instant

    if currency:
        unit = ET.SubElement(root, qname("xbrli:unit"), {"id": currency})
        ET.SubElement(unit, qname("xbrli:measure")).text = f"iso4217:{currency}"
    not_used = ET.SubElement(root, qname("xbrli:unit"), {"id": "NotUsed"})
    ET.SubElement(not_used, qname("xbrli:measure")).text = "pure"


def add_document_info(accounting_entries: ET.Element, instant: str, currency: str, monetary_decimals: str) -> None:
    """
    Add default XBRL GL documentInfo metadata.

    Args:
        accounting_entries: Input value used by add_document_info.
        instant: Input value used by add_document_info.
        currency: Input value used by add_document_info.
        monetary_decimals: Input value used by add_document_info.

    Returns:
        None. The accountingEntries element is modified in place.
    """
    document_info = ET.SubElement(accounting_entries, qname("gl-cor:documentInfo"))
    for target, value in (
        ("gl-cor:entriesType", "other"),
        ("gl-cor:language", "iso639:en"),
        ("gl-cor:creationDate", instant),
        ("gl-cor:entriesComment", "Generated UADC PoC ADS Invoices Received XBRL GL instance"),
    ):
        append_item(document_info, target, value, currency, monetary_decimals)
    if currency:
        append_item(document_info, "gl-muc:defaultCurrency", f"iso4217:{currency}", currency, monetary_decimals)


def build_instance(rows: list[dict[str, str]], bindings: list[dict[str, str]], schema_href: str, monetary_decimals: str) -> ET.Element:
    """
    Build one XBRL GL XML instance tree from structured CSV rows.

    Args:
        rows: Input value used by build_instance.
        bindings: Input value used by build_instance.
        schema_href: Input value used by build_instance.
        monetary_decimals: Input value used by build_instance.

    Returns:
        Result produced by build_instance.
    """
    currency = first_non_empty(rows, "DocumentCurrencyCode") or "JPY"
    instant = first_non_empty(rows, "InvoiceIssueDate") or date.today().isoformat()
    entity = first_non_empty(rows, "BuyerName") or first_non_empty(rows, "SellerName")

    root = make_xbrl_root(schema_href)
    add_context_and_units(root, entity, instant, currency)
    accounting_entries = ET.SubElement(root, qname("gl-cor:accountingEntries"))
    add_document_info(accounting_entries, instant, currency, monetary_decimals)

    base_entry_detail = container_for_path(
        root,
        "/xbrli:xbrl/gl-cor:accountingEntries/gl-cor:entryHeader/gl-cor:entryDetail/gl-cor:documentReference",
        currency,
        monetary_decimals,
    )
    tax_parent = ensure_child(base_entry_detail, "gl-cor:taxes", currency, monetary_decimals)

    vat_bindings = [binding for binding in bindings if ".vatBreakdown." in binding["semantic_path"]]
    vat_rows = [row for row in rows if (row.get("dVatBreakdown") or "").strip()]
    for row in vat_rows:
        taxes = ET.SubElement(base_entry_detail, qname("gl-cor:taxes"))
        for binding in vat_bindings:
            value = (row.get(binding["source_column"]) or "").strip()
            if value:
                append_item(taxes, binding["target_element"], value, currency, monetary_decimals)
        if len(list(taxes)) == 0:
            base_entry_detail.remove(taxes)

    for binding in bindings:
        if ".vatBreakdown." in binding["semantic_path"]:
            continue
        target_local = local_name(binding["target_element"])
        selected_rows = rows_for_binding(rows, binding)
        if target_local in {"taxCode", "taxDescription", "taxAmount"}:
            continue
        values = [(row.get(binding["source_column"]) or "").strip() for row in selected_rows]
        values = [value for value in values if value]
        if not values:
            continue
        target_parent = container_for_path(root, binding["xpath"], currency, monetary_decimals)
        for row in selected_rows:
            value = (row.get(binding["source_column"]) or "").strip()
            if value:
                append_item(target_parent, binding["target_element"], value, currency, monetary_decimals)
                break

    if len(list(tax_parent)) == 0:
        base_entry_detail.remove(tax_parent)
    reorder_tree(root)
    return root


def prefixed_tag(element: ET.Element) -> str:
    """
    Convert an ElementTree tag to a registered prefixed tag.

    Args:
        element: Input value used by prefixed_tag.

    Returns:
        Result produced by prefixed_tag.
    """
    for prefix, uri in NS.items():
        if element.tag.startswith(f"{{{uri}}}"):
            return f"{prefix}:{element.tag.rsplit('}', 1)[1]}"
    return element.tag


def reorder_tree(element: ET.Element) -> None:
    """
    Sort selected XBRL GL child elements into schema-friendly order.

    Args:
        element: Input value used by reorder_tree.

    Returns:
        None. The XML tree is reordered in place.
    """
    for child in list(element):
        reorder_tree(child)
    order = ORDER_MAPS.get(prefixed_tag(element))
    if not order:
        return
    priority = {name: index for index, name in enumerate(order)}
    children = list(element)
    children.sort(key=lambda child: priority.get(prefixed_tag(child), len(priority)))
    element[:] = children


def indent(element: ET.Element) -> None:
    """
    Apply readable XML indentation to an ElementTree.

    Args:
        element: Input value used by indent.

    Returns:
        None. The XML tree is formatted in place.
    """
    ET.indent(element, space="  ")


def convert_file(csv_file: Path, output_file: Path, bindings: list[dict[str, str]], schema_href: str, monetary_decimals: str) -> None:
    """
    Convert one structured CSV file into one XBRL GL XML file.

    Args:
        csv_file: Input value used by convert_file.
        output_file: Input value used by convert_file.
        bindings: Input value used by convert_file.
        schema_href: Input value used by convert_file.
        monetary_decimals: Input value used by convert_file.

    Returns:
        None. The XML file is written to output_file.
    """
    rows = read_csv(csv_file)
    root = build_instance(rows, bindings, schema_href, monetary_decimals)
    indent(root)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(output_file, encoding="utf-8", xml_declaration=True)


def input_files(input_path: Path) -> list[Path]:
    """
    Return the CSV files represented by an input file or directory.

    Args:
        input_path: Input value used by input_files.

    Returns:
        Result produced by input_files.
    """
    if input_path.is_dir():
        return sorted(input_path.glob("*.csv"))
    return [input_path]


def main() -> int:
    """
    Parse command-line arguments, run the script workflow, and return an exit code.

    Args:
        None.

    Returns:
        Process exit status: 0 for success and 1 for handled errors where applicable.
    """
    parser = argparse.ArgumentParser(description="Generate XBRL GL tuple instances from structured CSV.")
    parser.add_argument("input", type=Path, help="Structured CSV file or directory containing CSV files")
    parser.add_argument("-b", "--binding-csv", type=Path, required=True, help="ADS syntax binding CSV")
    parser.add_argument("--lhm-csv", type=Path, required=True, help="LHM CSV used to resolve semantic paths to CSV columns")
    parser.add_argument("-o", "--output-dir", type=Path, required=True, help="Output directory for XBRL GL XML instances")
    parser.add_argument(
        "--schema-href",
        default="../../XBRL-GL-PWD-2016-12-01/gl/plt/case-c-b-m-u-e-t-s/gl-plt-all-2016-12-01.xsd",
        help="schemaRef href to the XBRL GL tuple taxonomy entry point",
    )
    parser.add_argument(
        "--monetary-decimals",
        default="2",
        help="decimals attribute for monetary XBRL GL facts generated from Amount bindings",
    )
    args = parser.parse_args()

    lhm_columns = load_lhm_semantic_columns(args.lhm_csv)
    bindings = load_bindings(args.binding_csv, lhm_columns)
    if not bindings:
        raise SystemExit("No usable bindings were found.")

    count = 0
    for csv_file in input_files(args.input):
        output_file = args.output_dir / f"{csv_file.stem}.xbrl.xml"
        convert_file(csv_file, output_file, bindings, args.schema_href, args.monetary_decimals)
        count += 1
        print(f"Wrote {output_file}")
    print(f"ok: generated {count} XBRL GL instance(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
