#!/usr/bin/env python3
# coding: utf-8
"""
Apply UBL Invoice syntax binding to convert XML to Structured CSV, and reverse it.

Purpose:
    Transform UBL Invoice XML into the dimension-based hierarchical Structured
    CSV format used by the UADC proof of concept, or rebuild UBL XML from that
    CSV format.

Processing overview:
    In forward mode, the script reads the syntax binding table, extracts XML
    facts, assigns dimension columns from the LHM-derived columns embedded in
    the binding table, drops empty columns, and writes CSV plus JSON metadata.
    In reverse mode, it reads the hierarchical CSV and binding table,
    reconstructs XML elements and attributes, applies currency and schema-order
    rules, and writes UBL XML.

Command-line arguments:
    input_file: Input XML file, or input CSV when --reverse is used.
    -b, --binding: Syntax binding CSV file.
    -o, --output: Output hierarchical CSV, or output XML when --reverse is used.
    --template-csv: Optional CSV template for column order and dimension placement.
    --metadata-output: Optional JSON metadata output path.
    --taxonomy-base: Taxonomy directory referenced by generated metadata.
    --reverse: Convert hierarchical CSV back to XML.
    --ubl-schema-root: Optional local UBL XSD directory used for reverse XML child order.
    --ubl-schema-url: Optional UBL Invoice XSD URL used for reverse XML child order.
    --invoice-namespace: Namespace URI used for reverse XML generation.
    --d-invoice: dInvoice dimension value written in forward output rows.
    -e, --encoding: CSV encoding used for input and output.

Results:
    Forward mode writes hierarchical CSV and metadata JSON; reverse mode writes
    XML. The script prints generated row/value counts and returns exit code 0 on
    success or 1 on failure.

Creation Date: 2026-07-05
Last Modified: 2026-07-13

Copyright 2026 Sambuichi Professional Engineers Office
Designed by SAMBUICHI, Nobuyuki
Produced by ChatGPT and Codex, edited by SAMBUICHI, Nobuyuki

License:
    This software source code is licensed under the MIT License.

    Original meaning-bearing content in the UADC-PoC project, including LHM
    definitions, bindings, mappings, transformation rules, semantic definitions,
    schemas, labels, dictionaries, public samples, documentation, and diagrams,
    is licensed under Creative Commons Attribution-ShareAlike 4.0 International
    (CC BY-SA 4.0), as described in LICENSE-CONTENT. This also applies when such
    content appears in constants, dictionaries, lists, tables, comments, or
    docstrings; the surrounding executable logic remains under the MIT License.

    Third-party standards, schemas, taxonomies, code lists, field names,
    descriptions, and excerpts remain subject to their original copyright
    notices and licenses. This license notice does not relicense third-party
    materials.

MIT License

Copyright (c) 2026 Sambuichi Professional Engineers Office

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
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.parse import urljoin
from urllib.request import urlopen


UBL_NAMESPACES = {
    "": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}

XSD_NS = "{http://www.w3.org/2001/XMLSchema}"
SCHEMA_CHILD_ORDER_CACHE: Dict[str, Dict[str, List[str]]] = {}

UBL_CHILD_ORDER = {
    "Invoice": [
        "UBLExtensions", "UBLVersionID", "CustomizationID", "ProfileID", "ProfileExecutionID",
        "ID", "CopyIndicator", "UUID", "IssueDate", "DueDate", "InvoiceTypeCode", "Note",
        "TaxPointDate", "DocumentCurrencyCode", "TaxCurrencyCode", "PricingCurrencyCode",
        "PaymentCurrencyCode", "PaymentAlternativeCurrencyCode", "AccountingCostCode",
        "AccountingCost", "LineCountNumeric", "BuyerReference", "InvoicePeriod",
        "OrderReference", "BillingReference", "DespatchDocumentReference",
        "ReceiptDocumentReference", "StatementDocumentReference", "OriginatorDocumentReference",
        "ContractDocumentReference", "AdditionalDocumentReference", "ProjectReference",
        "Signature", "AccountingSupplierParty", "AccountingCustomerParty", "PayeeParty",
        "BuyerCustomerParty", "SellerSupplierParty", "TaxRepresentativeParty", "Delivery",
        "DeliveryTerms", "PaymentMeans", "PaymentTerms", "PrepaidPayment", "AllowanceCharge",
        "TaxExchangeRate", "PricingExchangeRate", "PaymentExchangeRate",
        "PaymentAlternativeExchangeRate", "TaxTotal", "WithholdingTaxTotal",
        "LegalMonetaryTotal", "InvoiceLine",
    ],
    "Party": [
        "MarkCareIndicator", "MarkCare", "MarkAttentionIndicator", "MarkAttention", "WebsiteURI",
        "LogoReferenceID", "EndpointID", "IndustryClassificationCode", "PartyIdentification",
        "PartyName", "Language", "PostalAddress", "PhysicalLocation", "PartyTaxScheme",
        "PartyLegalEntity", "Contact", "Person", "AgentParty", "ServiceProviderParty",
        "PowerOfAttorney", "FinancialAccount",
    ],
    "Address": [
        "ID", "AddressTypeCode", "AddressFormatCode", "Postbox", "Floor", "Room", "StreetName",
        "AdditionalStreetName", "BlockName", "BuildingName", "BuildingNumber", "InhouseMail",
        "Department", "MarkAttention", "MarkCare", "PlotIdentification",
        "CitySubdivisionName", "CityName", "PostalZone", "CountrySubentity",
        "CountrySubentityCode", "Region", "District", "TimezoneOffset", "AddressLine", "Country",
        "LocationCoordinate",
    ],
    "PartyTaxScheme": [
        "RegistrationName", "CompanyID", "TaxLevelCode", "ExemptionReasonCode",
        "ExemptionReason", "RegistrationAddress", "TaxScheme",
    ],
    "AllowanceCharge": [
        "ChargeIndicator", "AllowanceChargeReasonCode", "AllowanceChargeReason",
        "MultiplierFactorNumeric", "PrepaidIndicator", "SequenceNumeric", "Amount", "BaseAmount",
        "AccountingCostCode", "AccountingCost", "PerUnitAmount", "TaxCategory", "TaxTotal",
        "PaymentMeans",
    ],
    "TaxCategory": [
        "ID", "Name", "Percent", "BaseUnitMeasure", "PerUnitAmount", "TaxExemptionReasonCode",
        "TaxExemptionReason", "TierRange", "TierRatePercent", "TaxScheme",
    ],
    "ClassifiedTaxCategory": [
        "ID", "Name", "Percent", "BaseUnitMeasure", "PerUnitAmount", "TaxExemptionReasonCode",
        "TaxExemptionReason", "TierRange", "TierRatePercent", "TaxScheme",
    ],
    "TaxSubtotal": [
        "TaxableAmount", "TaxAmount", "CalculationSequenceNumeric", "TransactionCurrencyTaxAmount",
        "Percent", "BaseUnitMeasure", "PerUnitAmount", "TierRange", "TierRatePercent",
        "TaxCategory",
    ],
    "TaxTotal": [
        "TaxAmount", "RoundingAmount", "TaxEvidenceIndicator", "TaxIncludedIndicator", "TaxSubtotal",
    ],
    "MonetaryTotal": [
        "LineExtensionAmount", "TaxExclusiveAmount", "TaxInclusiveAmount", "AllowanceTotalAmount",
        "ChargeTotalAmount", "WithholdingTaxTotalAmount", "PrepaidAmount",
        "PayableRoundingAmount", "PayableAmount", "PayableAlternativeAmount",
    ],
    "DocumentReference": [
        "ID", "CopyIndicator", "UUID", "IssueDate", "IssueTime", "DocumentTypeCode",
        "DocumentType", "XPath", "LanguageID", "LocaleCode", "VersionID", "DocumentStatusCode",
        "DocumentDescription", "Attachment", "ValidityPeriod", "IssuerParty",
        "ResultOfVerification",
    ],
    "Delivery": [
        "ID", "Quantity", "MinimumQuantity", "MaximumQuantity", "ActualDeliveryDate",
        "ActualDeliveryTime", "LatestDeliveryDate", "LatestDeliveryTime", "ReleaseID",
        "TrackingID", "DeliveryAddress", "DeliveryLocation", "AlternativeDeliveryLocation",
        "RequestedDeliveryPeriod", "PromisedDeliveryPeriod", "EstimatedDeliveryPeriod",
        "CarrierParty", "DeliveryParty", "NotifyParty", "Despatch", "DeliveryTerms",
        "MinimumDeliveryUnit", "MaximumDeliveryUnit", "Shipment",
    ],
    "InvoiceLine": [
        "ID", "UUID", "Note", "InvoicedQuantity", "LineExtensionAmount", "TaxPointDate",
        "AccountingCostCode", "AccountingCost", "PaymentPurposeCode", "FreeOfChargeIndicator",
        "InvoicePeriod", "OrderLineReference", "DespatchLineReference", "ReceiptLineReference",
        "BillingReference", "DocumentReference", "PricingReference", "OriginatorParty",
        "Delivery", "PaymentTerms", "AllowanceCharge", "TaxTotal", "WithholdingTaxTotal",
        "Item", "Price", "DeliveryTerms", "SubInvoiceLine", "ItemPriceExtension",
    ],
    "Item": [
        "Description", "PackQuantity", "PackSizeNumeric", "CatalogueIndicator", "Name",
        "HazardousRiskIndicator", "AdditionalInformation", "Keyword", "BrandName", "ModelName",
        "BuyersItemIdentification", "SellersItemIdentification", "ManufacturersItemIdentification",
        "StandardItemIdentification", "CatalogueItemIdentification", "AdditionalItemIdentification",
        "CatalogueDocumentReference", "ItemSpecificationDocumentReference", "OriginCountry",
        "CommodityClassification", "TransactionConditions", "HazardousItem",
        "ClassifiedTaxCategory", "AdditionalItemProperty", "ManufacturerParty",
        "InformationContentProviderParty", "OriginAddress", "ItemInstance", "Certificate",
        "Dimension",
    ],
    "Price": [
        "PriceAmount", "BaseQuantity", "PriceChangeReason", "PriceTypeCode", "PriceType",
        "OrderableUnitFactorRate", "ValidityPeriod", "PriceList", "AllowanceCharge",
        "PricingExchangeRate",
    ],
    "Attachment": ["EmbeddedDocumentBinaryObject", "ExternalReference"],
    "ExternalReference": [
        "URI", "DocumentHash", "HashAlgorithmMethod", "ExpiryDate", "ExpiryTime", "MimeCode",
        "FormatCode", "EncodingCode", "CharacterSetCode", "FileName", "Description",
    ],
    "Country": ["IdentificationCode", "Name"],
}


@dataclass(frozen=True)
class UblElementDecl:
    """One global UBL schema element declaration."""

    qname: Tuple[str, str]
    type_qname: Optional[Tuple[str, str]]


class UblSchemaIndex:
    """Index UBL XSD element declarations and complex type child sequences."""

    def __init__(self) -> None:
        self.elements: Dict[Tuple[str, str], UblElementDecl] = {}
        self.types: Dict[Tuple[str, str], List[Tuple[str, str]]] = {}
        self.loaded_sources: set[str] = set()

    @staticmethod
    def nsmap_from_file(path: Path) -> Dict[str, str]:
        namespaces: Dict[str, str] = {}
        for _, item in ET.iterparse(path, events=("start-ns",)):
            prefix, uri = item
            namespaces[prefix or ""] = uri
        return namespaces

    @staticmethod
    def nsmap_from_bytes(data: bytes) -> Dict[str, str]:
        namespaces: Dict[str, str] = {}
        for _, item in ET.iterparse(io.BytesIO(data), events=("start-ns",)):
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
        sequence = parent.find(f"{XSD_NS}sequence")
        if sequence is None:
            extension = parent.find(f"{XSD_NS}complexContent/{XSD_NS}extension")
            sequence = extension.find(f"{XSD_NS}sequence") if extension is not None else None
        if sequence is None:
            return []
        children: List[Tuple[str, str]] = []
        for child in list(sequence):
            if child.tag != f"{XSD_NS}element":
                continue
            ref = child.get("ref")
            name = child.get("name")
            if ref:
                children.append(UblSchemaIndex.resolve_qname(ref, namespaces, target_ns))
            elif name:
                children.append((target_ns, name))
        return children

    def load_xsd_root(self, root: ET.Element, namespaces: Dict[str, str]) -> None:
        target_ns = root.get("targetNamespace", "")
        for element in root.findall(f"{XSD_NS}element"):
            name = element.get("name")
            if not name:
                continue
            type_name = element.get("type")
            type_qname = self.resolve_qname(type_name, namespaces, target_ns) if type_name else None
            qname = (target_ns, name)
            self.elements[qname] = UblElementDecl(qname, type_qname)
            inline_sequence = self.sequence_elements(element, namespaces, target_ns)
            if inline_sequence:
                self.types[qname] = inline_sequence
        for complex_type in root.findall(f"{XSD_NS}complexType"):
            name = complex_type.get("name")
            if not name:
                continue
            qname = (target_ns, name)
            sequence = self.sequence_elements(complex_type, namespaces, target_ns)
            if sequence:
                self.types[qname] = sequence

    def load_xsd_file(self, path: Path) -> None:
        key = str(path.resolve())
        if key in self.loaded_sources:
            return
        self.loaded_sources.add(key)
        namespaces = self.nsmap_from_file(path)
        root = ET.parse(path).getroot()
        self.load_xsd_root(root, namespaces)

    def load_directory(self, schema_root: Path) -> None:
        for path in sorted(schema_root.rglob("*.xsd")):
            self.load_xsd_file(path)

    def load_url(self, url: str) -> None:
        if url in self.loaded_sources:
            return
        self.loaded_sources.add(url)
        with urlopen(url) as response:
            data = response.read()
        namespaces = self.nsmap_from_bytes(data)
        root = ET.fromstring(data)
        for child in root:
            if child.tag not in {f"{XSD_NS}import", f"{XSD_NS}include"}:
                continue
            location = child.get("schemaLocation")
            if location:
                self.load_url(urljoin(url, location))
        self.load_xsd_root(root, namespaces)

    def child_order_by_element_name(self) -> Dict[str, List[str]]:
        order: Dict[str, List[str]] = {}
        for (namespace, local_name), decl in self.elements.items():
            sequence: List[Tuple[str, str]] = []
            if decl.type_qname and decl.type_qname in self.types:
                sequence = self.types[decl.type_qname]
            elif decl.qname in self.types:
                sequence = self.types[decl.qname]
            if sequence:
                order[local_name] = [child_local for _, child_local in sequence]
        return order


def xml_local_name(name: str) -> str:
    """
    Return the local component of a qualified or prefixed XML name.

    Args:
        name: Qualified, prefixed, or local XML name.

    Returns:
        Local XML name without namespace URI or prefix.
    """
    if not name:
        return ""
    if name.startswith("{"):
        return name.rsplit("}", 1)[-1]
    return name.split(":", 1)[-1]


def collect_namespaces(xml_file: Path) -> Dict[str, str]:
    """
    Collect namespace prefix declarations from an XML file.

    Args:
        xml_file: XML file to scan.

    Returns:
        Mapping from namespace prefix to namespace URI.
    """
    namespaces: Dict[str, str] = {}
    for event, value in ET.iterparse(xml_file, events=("start-ns",)):
        prefix, uri = value
        namespaces[prefix or ""] = uri
    return namespaces


def xml_qualify_step(step: str, namespaces: Dict[str, str]) -> str:
    """
    Convert an XPath step into an ElementTree-qualified tag when possible.

    Args:
        step: XPath step, possibly with a namespace prefix.
        namespaces: Namespace prefix map collected from the XML document.

    Returns:
        ElementTree-qualified tag or the original step.
    """
    if not step or step in (".", "*") or step.startswith("@"):
        return step
    base = step.split("[", 1)[0] if "[" in step else step
    if ":" in base:
        prefix, name = base.split(":", 1)
        uri = namespaces.get(prefix)
        return f"{{{uri}}}{name}" if uri else step
    uri = namespaces.get("")
    return f"{{{uri}}}{base}" if uri else step


def xml_split_step_predicate(step: str) -> Tuple[str, Optional[str]]:
    """
    Separate an XPath step from its optional predicate.

    Args:
        step: XPath step such as `cac:Party[cbc:ID='1']`.

    Returns:
        Tuple of base step and predicate text, or None when no predicate exists.
    """
    if "[" not in step:
        return step, None
    base, predicate = step.split("[", 1)
    return base, predicate.rsplit("]", 1)[0].strip()


def xml_split_xpath(xpath: str) -> List[str]:
    """
    Split an XPath into steps while preserving predicate expressions.

    Args:
        xpath: XPath-like path used by the syntax binding CSV.

    Returns:
        Ordered XPath steps.
    """
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


def xml_split_terminal_attribute(xpath: str) -> Tuple[str, str]:
    """
    Separate a terminal attribute selector from an XPath.

    Args:
        xpath: XPath that may end with `/@attribute`.

    Returns:
        Tuple of element XPath and terminal attribute name.
    """
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


def xml_path_value(context: ET.Element, path: str, namespaces: Dict[str, str], root: Optional[ET.Element] = None) -> str:
    """
    Resolve a scalar value from an XML context using a relative path.

    Args:
        context: XML element used as the relative context.
        path: Relative or absolute XPath-like expression.
        namespaces: Namespace prefix map.
        root: Optional document root for absolute lookups.

    Returns:
        Text or attribute value, or an empty string when no match exists.
    """
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


def xml_predicate_matches(
    child: ET.Element,
    predicate: Optional[str],
    namespaces: Dict[str, str],
    root: Optional[ET.Element] = None,
) -> bool:
    """
    Evaluate the supported XPath predicate forms against an XML element.

    Args:
        child: XML child element being tested.
        predicate: Predicate text without square brackets.
        namespaces: Namespace prefix map.
        root: Optional document root for absolute references.

    Returns:
        True when the predicate is absent or matches.
    """
    if not predicate:
        return True
    path_pattern = r"(@[A-Za-z_][\w.-]*|[A-Za-z_][\w.-]*:[A-Za-z_][\w.-]*(?:/(?:@[A-Za-z_][\w.-]*|[A-Za-z_][\w.-]*:[A-Za-z_][\w.-]*))*)"
    match = re.fullmatch(r"not\(\s*" + path_pattern + r"\s*=\s*'([^']*)'\s*\)", predicate)
    if match:
        element_path, excluded_text = match.groups()
        return xml_path_value(child, element_path, namespaces, root) != excluded_text
    match = re.fullmatch(path_pattern + r"\s*=\s*(true|false)\(\)", predicate)
    if match:
        element_path, expected = match.groups()
        expected_text = "true" if expected == "true" else "false"
        return xml_path_value(child, element_path, namespaces, root).lower() == expected_text
    match = re.fullmatch(path_pattern + r"\s*(=|!=)\s*'([^']*)'", predicate)
    if match:
        element_path, operator, expected_text = match.groups()
        actual = xml_path_value(child, element_path, namespaces, root)
        return actual == expected_text if operator == "=" else bool(actual) and actual != expected_text
    match = re.fullmatch(path_pattern + r"\s*(=|!=)\s*(/[A-Za-z_][\w.-]*(?::[A-Za-z_][\w.-]*)?(?:/[A-Za-z_][\w.-]*(?::[A-Za-z_][\w.-]*)?)*)", predicate)
    if match:
        element_path, operator, reference_path = match.groups()
        actual = xml_path_value(child, element_path, namespaces, root)
        expected = xml_path_value(root if root is not None else child, reference_path, namespaces, root)
        return actual == expected if operator == "=" else bool(actual) and actual != expected
    return True


def xml_child_matches(child: ET.Element, step: str, namespaces: Dict[str, str], root: Optional[ET.Element] = None) -> bool:
    """
    Check whether a child element matches an XPath step and predicate.

    Args:
        child: XML child element being tested.
        step: XPath step from the syntax binding.
        namespaces: Namespace prefix map.
        root: Optional document root.

    Returns:
        True when the child matches the step.
    """
    base_step, predicate = xml_split_step_predicate(step)
    qualified = xml_qualify_step(base_step, namespaces)
    if qualified == "*":
        return xml_predicate_matches(child, predicate, namespaces, root)
    return (
        child.tag == qualified or xml_local_name(child.tag) == xml_local_name(base_step)
    ) and xml_predicate_matches(child, predicate, namespaces, root)


def find_nodes(
    context: ET.Element,
    xpath: str,
    namespaces: Dict[str, str],
    root: Optional[ET.Element] = None,
) -> List[ET.Element]:
    """
    Find XML nodes matching the limited XPath subset used by syntax bindings.

    Args:
        context: XML element used as the search context.
        xpath: XPath-like expression.
        namespaces: Namespace prefix map.
        root: Optional document root.

    Returns:
        Matching XML elements.
    """
    if root is None:
        root = context
    nodes = [context]
    parts = xml_split_xpath(xpath)
    if parts and xml_local_name(parts[0]) == xml_local_name(context.tag):
        parts = parts[1:]
    for part in parts:
        if part.startswith("@"):
            return []
        next_nodes: List[ET.Element] = []
        for node in nodes:
            next_nodes.extend(child for child in list(node) if xml_child_matches(child, part, namespaces, root))
        nodes = next_nodes
    return nodes


def get_value(
    context: ET.Element,
    xpath: str,
    namespaces: Dict[str, str],
    root: Optional[ET.Element] = None,
) -> str:
    """
    Extract text or a terminal attribute value from an XML context.

    Args:
        context: XML element used as the extraction context.
        xpath: XPath-like expression from the syntax binding.
        namespaces: Namespace prefix map.
        root: Optional document root for predicates with absolute references.

    Returns:
        Extracted text or attribute value, joined by `|` when multiple text
        nodes match.
    """
    xpath = (xpath or "").strip()
    if not xpath:
        return ""
    # A binding may remain absolute when its fact is selected outside the
    # current semantic-class XML context (for example BT-110/BT-111 select
    # sibling TaxTotal elements by currency).  Absolute paths must always be
    # evaluated from the document root, not from the current class node.
    search_context = root if xpath.startswith("/") and root is not None else context
    element_xpath, attr_name = xml_split_terminal_attribute(xpath)
    if attr_name:
        nodes = find_nodes(search_context, element_xpath, namespaces, root)
        return nodes[0].attrib.get(attr_name, "") if nodes else ""
    if xpath.startswith("@"):
        return context.attrib.get(xpath[1:], "")
    nodes = find_nodes(search_context, xpath, namespaces, root)
    values = [" ".join((node.text or "").split()) for node in nodes if (node.text or "").strip()]
    return "|".join(values)


@dataclass(frozen=True)
class Binding:
    """
    Describe one syntax binding from a semantic field to an XML XPath.

    Args:
        None.

    Returns:
        Dataclass instance storing the described metadata.
    """
    order: int
    syntax_sequence: str
    default_value: str
    semantic_path: str
    xpath: str
    root: str
    dimension: str
    filter_field: str
    filter_value: str
    field: str
    canonical_semantic_path: str = ""
    selector_key: str = ""
    selector_negated: bool = False
    identifier: str = ""
    transformation: str = ""
    selector_conditions: Tuple[Tuple[str, bool], ...] = ()


@dataclass(frozen=True)
class BindingLayout:
    """
    Hold binding-derived dimension, fact, and ordering metadata.

    Args:
        None.

    Returns:
        Dataclass instance storing the described metadata.
    """
    fieldnames: List[str]
    field_dimension: Dict[str, str]
    semantic_path_dimension: Dict[str, str]
    dimension_xpath: Dict[str, str]
    path_dimension: Dict[str, str]
    dimension_ancestors: Dict[str, List[str]]
    dimension_repeats: Dict[str, bool]
    field_by_semantic_path: Dict[str, str]
    syntax_sequence_by_field: Dict[str, str]
    syntax_sequence_by_dimension: Dict[str, str]


@dataclass
class BindingClassAlias:
    """Represent one syntax-specific physical alias of a semantic Class."""

    order: int
    syntax_sequence: str
    semantic_path: str
    xpath: str
    selector_key: str
    selector_negated: bool
    selector_conditions: Tuple[Tuple[str, bool], ...]


@dataclass
class BindingClass:
    """
    Represent one C row in the syntax binding class tree.

    Args:
        None.

    Returns:
        Dataclass instance storing class metadata and child links.
    """
    order: int
    syntax_sequence: str
    semantic_path: str
    name: str
    column: str
    dimension: str
    xpath: str
    repeats: bool
    aliases: List[BindingClassAlias]
    children: List["BindingClass"]


SEMANTIC_SELECTOR_RE = re.compile(
    r"\[(?:(not)\()?([A-Za-z_][A-Za-z0-9_]*)(?:\))?\]"
)


def parse_semantic_selector(semantic_path: str) -> Tuple[str, str, bool]:
    """Return canonical path plus the last syntax-variant selector."""

    selectors = list(SEMANTIC_SELECTOR_RE.finditer(semantic_path or ""))
    canonical_path = SEMANTIC_SELECTOR_RE.sub("", semantic_path or "")
    if not selectors:
        return canonical_path, "", False
    selector = selectors[-1]
    return canonical_path, selector.group(2), bool(selector.group(1))


def parse_semantic_selectors(semantic_path: str) -> Tuple[Tuple[str, bool], ...]:
    """Return every presence/absence selector in left-to-right AND order."""

    return tuple(
        (selector.group(2), bool(selector.group(1)))
        for selector in SEMANTIC_SELECTOR_RE.finditer(semantic_path or "")
    )


def transform_binding_value(
    value: str, transformation: str, reverse: bool = False
) -> Optional[str]:
    """Apply a declared reversible lexical or representation transformation.

    The registry keys are supplied only by the Binding.  ``None`` means that
    a mutually exclusive physical representation is not applicable; it is not
    a silent fallback.
    """

    transformation = (transformation or "").strip()
    if not transformation or not value:
        return value
    if transformation in {"cii_date_format_102", "CII_DATE_102"}:
        if reverse:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                raise ValueError(f"CII_DATE_102 requires ISO date, got {value!r}")
            return value.replace("-", "")
        if not re.fullmatch(r"\d{8}", value):
            raise ValueError(f"CII_DATE_102 requires YYYYMMDD, got {value!r}")
        return f"{value[:4]}-{value[4:6]}-{value[6:]}"
    if transformation == "UNCL2005_TO_UNCL2475":
        forward = {"5": "3", "29": "35", "72": "432"}
        reverse_map = {semantic: syntax for syntax, semantic in forward.items()}
        mapping = reverse_map if reverse else forward
        if value not in mapping:
            direction = "UNCL2005 to UNCL2475" if reverse else "UNCL2475 to UNCL2005"
            raise ValueError(f"{direction} has no declared mapping for {value!r}")
        return mapping[value]
    if transformation == "CII_ACCOUNT_ID_IF_IBAN":
        if not reverse:
            return value
        compact = re.sub(r"\s+", "", value).upper()
        is_iban = bool(re.fullmatch(r"[A-Z]{2}\d{2}[A-Z0-9]{11,30}", compact))
        return compact if is_iban else None
    if transformation == "CII_ACCOUNT_ID_IF_NOT_IBAN":
        if not reverse:
            return value
        compact = re.sub(r"\s+", "", value).upper()
        is_iban = bool(re.fullmatch(r"[A-Z]{2}\d{2}[A-Z0-9]{11,30}", compact))
        return None if is_iban else value
    if transformation in {
        "CII_IDENTIFIER_VARIANT_GLOBAL",
        "CII_IDENTIFIER_VARIANT_LOCAL",
        "CII_TAX_TOTAL_ACCOUNTING_CURRENCY",
        "CII_TAX_TOTAL_DOCUMENT_CURRENCY",
        "cii_header_tax_point_singleton",
        "cii_payment_means_parent_scalar",
        "cii_tax_total_accounting_currency",
        "cii_tax_total_document_currency",
    }:
        return value
    raise ValueError(f"Unknown Syntax Binding transformation: {transformation}")


def tax_total_occurrence_value(
    context: ET.Element,
    xpath: str,
    transformation: str,
    namespaces: Dict[str, str],
    root: ET.Element,
) -> str:
    """Select one same-path tax-total occurrence as declared by a transform."""

    if transformation not in {
        "CII_TAX_TOTAL_DOCUMENT_CURRENCY",
        "CII_TAX_TOTAL_ACCOUNTING_CURRENCY",
    }:
        return get_value(context, xpath, namespaces, root)
    search_context = root if xpath.startswith("/") else context
    nodes = find_nodes(search_context, xpath, namespaces, root)
    index = 0 if transformation.endswith("DOCUMENT_CURRENCY") else 1
    if len(nodes) <= index:
        return ""
    return " ".join((nodes[index].text or "").split())


def tax_total_write_xpath(
    xpath: str,
    transformation: str,
    document_currency: str,
    tax_currency: str,
) -> str:
    """Qualify a same-path tax-total occurrence using declared currency role."""

    if transformation == "CII_TAX_TOTAL_DOCUMENT_CURRENCY":
        currency = document_currency
    elif transformation == "CII_TAX_TOTAL_ACCOUNTING_CURRENCY":
        currency = tax_currency
    else:
        return xpath
    if not currency:
        return ""
    parts = xml_split_xpath(xpath)
    if not parts:
        return xpath
    parts[-1] = f"{parts[-1]}[@currencyID='{currency}']"
    return "/" + "/".join(parts) if xpath.startswith("/") else "/".join(parts)


def first_present(row: Dict[str, str], names: Iterable[str]) -> str:
    """
    Return the first non-empty value from a set of candidate field names.

    Args:
        row: Input value used by first_present.
        names: Input value used by first_present.

    Returns:
        Result produced by first_present.
    """
    for name in names:
        value = row.get(name)
        if value:
            return value.strip()
    return ""


def parse_order(value: str, fallback: int = 0) -> int:
    """
    Parse a row-order value with a fallback for blanks or invalid input.

    Args:
        value: Input value used by parse_order.
        fallback: Input value used by parse_order.

    Returns:
        Result produced by parse_order.
    """
    value = (value or "").strip()
    if not value:
        return fallback
    try:
        return int(value)
    except ValueError:
        return fallback


def syntax_sequence_sort_key(value: str, fallback: int = 0) -> Tuple[int, Tuple[str, ...], int]:
    """Return a stable sort key for an XSD-derived hierarchical syntax sequence."""

    value = (value or "").strip()
    if not value:
        return 1, (), fallback
    normalized: List[str] = []
    for component in value.split("."):
        if component.isdigit():
            normalized.append(component.zfill(8))
        elif component.startswith("@"):
            normalized.append("~" + component[1:])
        else:
            normalized.append("~" + component)
    return 0, tuple(normalized), fallback


def upper_camel(value: str) -> str:
    """
    Convert text to UpperCamelCase.

    Args:
        value: Input value used by upper_camel.

    Returns:
        Result produced by upper_camel.
    """
    value = re.sub(r"[^0-9A-Za-z_]+", "_", value or "").strip("_")
    if not value:
        return ""
    return value[0].upper() + value[1:]


def dimension_name(element: str) -> str:
    """
    Build a d-prefixed dimension column name from an element name.

    Args:
        element: Input value used by dimension_name.

    Returns:
        Result produced by dimension_name.
    """
    return "d" + upper_camel(element)


def effective_structured_column(semantic_path: str, declared: str) -> str:
    """Disambiguate generic child column labels from semantic-path context."""

    if declared not in {"Identifier", "SchemeIdentifier"}:
        return declared
    canonical, _, _ = parse_semantic_selector(semantic_path)
    parts = canonical.split(".")
    leaf = parts[-1] if parts else ""
    if leaf.lower() in {"identifier", "schemeidentifier"} and len(parts) > 1:
        leaf = parts[-2] + upper_camel(leaf)
    return upper_camel(leaf) or declared


def multiplicity_repeats(multiplicity: str) -> bool:
    """
    Return whether an LHM multiplicity allows repeated rows.

    Args:
        multiplicity: Input value used by multiplicity_repeats.

    Returns:
        Result produced by multiplicity_repeats.
    """
    multiplicity = (multiplicity or "").strip().lower()
    if ".." not in multiplicity:
        return False
    upper = multiplicity.rsplit("..", 1)[1]
    if upper in ("*", "n", "unbounded"):
        return True
    try:
        return int(upper) > 1
    except ValueError:
        return False


def read_effective_binding_rows(
    binding_csv: Path,
    encoding: str,
    hmd_file: Optional[Path] = None,
) -> List[Dict[str, str]]:
    """Load Binding rows and supplement semantic columns from an HMD."""

    rows = read_binding_rows(binding_csv, encoding)
    if not hmd_file:
        return rows
    hmd_rows = read_binding_rows(hmd_file, encoding)
    hmd_by_path = {
        first_present(row, ("semantic_path",)): row
        for row in hmd_rows
        if first_present(row, ("semantic_path",))
    }
    for row in rows:
        row_type = first_present(row, ("type", "kind")).upper()
        if not (row_type.startswith("C") or row_type.startswith("A")):
            continue
        canonical_path, _, _ = parse_semantic_selector(first_present(row, ("semantic_path",)))
        semantic = hmd_by_path.get(canonical_path)
        if semantic is None:
            raise ValueError(f"Binding semantic_path does not resolve to HMD: {canonical_path}")
        row.setdefault("structured_csv_column", first_present(semantic, ("local_name", "element", "name")))
        row.setdefault("module", first_present(semantic, ("module",)))
        row.setdefault("class_term", first_present(semantic, ("class_term",)))
        if not first_present(row, ("id", "identifier")):
            row["id"] = first_present(semantic, ("source_bsm_id", "id", "identifier"))
        for field in ("level", "type", "name", "datatype", "multiplicity"):
            if not row.get(field):
                row[field] = first_present(semantic, (field,))
    return rows


def read_binding_layout(
    binding_csv: Path,
    encoding: str,
    hmd_file: Optional[Path] = None,
) -> BindingLayout:
    """
    Read LHM-style class and attribute rows embedded in a syntax binding CSV.

    Args:
        binding_csv: Syntax binding CSV to scan.
        encoding: CSV encoding used for input.

    Returns:
        Layout metadata derived from the binding table itself.
    """
    rows = read_effective_binding_rows(binding_csv, encoding, hmd_file)
    return build_layout_from_rows(rows)


def build_layout_from_rows(rows: List[Dict[str, str]]) -> BindingLayout:
    """
    Build Structured CSV layout metadata from LHM-style C/A rows.

    Args:
        rows: CSV rows containing semantic_path, type, multiplicity,
            structured_csv_column, datatype, and optional XPath columns.

    Returns:
        Layout metadata used by forward and reverse syntax binding.
    """
    dimensions: List[str] = []
    fields: List[str] = []
    field_dimension: Dict[str, str] = {}
    semantic_path_dimension: Dict[str, str] = {}
    dimension_xpath: Dict[str, str] = {}
    path_dimension: Dict[str, str] = {}
    dimension_ancestors: Dict[str, List[str]] = {}
    dimension_repeats: Dict[str, bool] = {}
    field_by_semantic_path: Dict[str, str] = {}
    syntax_sequence_by_field: Dict[str, str] = {}
    syntax_sequence_by_dimension: Dict[str, str] = {}

    for row in rows:
        if first_present(row, ("type", "kind")).upper().startswith("C"):
            full_semantic_path = first_present(row, ("semantic_path",))
            semantic_path, _, _ = parse_semantic_selector(full_semantic_path)
            csv_column = first_present(row, ("structured_csv_column", "source_column", "element", "name"))
            lhm_level = first_present(row, ("lhm_level", "level"))
            repeats = multiplicity_repeats(first_present(row, ("multiplicity", "cardinality")))
            dim = dimension_name(csv_column)
            if semantic_path and dim and (semantic_path == "$.invoice" or repeats):
                path_dimension[semantic_path] = dim
                semantic_path_dimension[semantic_path] = dim
                if dim not in dimensions:
                    dimensions.append(dim)
                xpath = first_present(row, ("syntax_path", "xpath", "source_xpath", "xml_path"))
                if xpath:
                    dimension_xpath[dim] = xpath
                dimension_repeats[dim] = repeats
                syntax_order = first_present(row, ("syntax_sequence",))
                if syntax_order:
                    syntax_sequence_by_dimension[dim] = syntax_order
                ancestors: List[str] = []
                parent_path = semantic_path
                while "." in parent_path:
                    parent_path = parent_path.rsplit(".", 1)[0]
                    parent_dim = path_dimension.get(parent_path)
                    if parent_dim and dimension_repeats.get(parent_dim) and parent_dim not in ancestors:
                        ancestors.insert(0, parent_dim)
                dimension_ancestors[dim] = ancestors

    def nearest_dimension(semantic_path: str) -> str:
        """
        Run the nearest_dimension helper operation.

        Args:
            semantic_path: Input value used by nearest_dimension.

        Returns:
            Result produced by nearest_dimension.
        """
        current = semantic_path
        while current:
            dimension = path_dimension.get(current, "")
            if dimension:
                return dimension
            if "." not in current:
                return ""
            current = current.rsplit(".", 1)[0]
        return ""

    for row in rows:
        if not first_present(row, ("type", "kind")).upper().startswith("A"):
            continue
        full_semantic_path = first_present(row, ("semantic_path",))
        semantic_path, _, _ = parse_semantic_selector(full_semantic_path)
        csv_column = effective_structured_column(
            full_semantic_path,
            first_present(row, ("structured_csv_column", "source_column", "element", "name")),
        )
        if not semantic_path or not csv_column:
            continue
        field_by_semantic_path[semantic_path] = csv_column
        if full_semantic_path != semantic_path:
            field_by_semantic_path[full_semantic_path] = csv_column
        syntax_order = first_present(row, ("syntax_sequence",))
        if syntax_order:
            syntax_sequence_by_field[csv_column] = syntax_order
        if csv_column not in fields:
            fields.append(csv_column)
        parent_path = semantic_path.rsplit(".", 1)[0] if "." in semantic_path else ""
        parent_dimension = nearest_dimension(parent_path)
        if parent_dimension:
            field_dimension[csv_column] = parent_dimension
            semantic_path_dimension[semantic_path] = parent_dimension

    return BindingLayout(
        dimensions + fields,
        field_dimension,
        semantic_path_dimension,
        dimension_xpath,
        path_dimension,
        dimension_ancestors,
        dimension_repeats,
        field_by_semantic_path,
        syntax_sequence_by_field,
        syntax_sequence_by_dimension,
    )


def read_template(template_csv: Optional[Path], encoding: str) -> Tuple[List[str], Dict[str, str]]:
    """
    Read an optional template CSV and infer dimension placement rules.

    Args:
        template_csv: Input value used by read_template.
        encoding: Input value used by read_template.

    Returns:
        Result produced by read_template.
    """
    if not template_csv:
        return [], {}
    with template_csv.open(newline="", encoding=encoding) as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("Template CSV has no header.")
        fieldnames = [name.lstrip("\ufeff") for name in reader.fieldnames]
        rows = [{key.lstrip("\ufeff"): (value or "").strip() for key, value in row.items()} for row in reader]

    dimension_columns = [name for name in fieldnames if is_dimension_column(name)]
    field_dimension: Dict[str, str] = {}
    for field in fieldnames:
        if field in dimension_columns:
            continue
        dimensions = []
        for row in rows:
            if not row.get(field):
                continue
            row_dimensions = [dim for dim in dimension_columns if dim != "dInvoice" and row.get(dim)]
            if len(row_dimensions) == 1:
                dimensions.append(row_dimensions[0])
        if dimensions and len(set(dimensions)) == 1:
            field_dimension[field] = dimensions[0]
    return fieldnames, field_dimension


def is_dimension_column(name: str) -> bool:
    """
    Return whether a column name represents a dimension column.

    Args:
        name: Input value used by is_dimension_column.

    Returns:
        Result produced by is_dimension_column.
    """
    return bool(re.fullmatch(r"d[A-Z][A-Za-z0-9_]*", name or ""))


def parse_semantic_path(
    semantic_path: str,
    xpath: str,
    order: int,
    syntax_sequence: str = "",
    default_value: str = "",
    path_dimension: Optional[Dict[str, str]] = None,
    field_by_semantic_path: Optional[Dict[str, str]] = None,
    semantic_path_dimension: Optional[Dict[str, str]] = None,
) -> Optional[Binding]:
    """
    Parse a semantic path into hierarchy parts and a leaf field.

    Args:
        semantic_path: Input value used by parse_semantic_path.
        xpath: Input value used by parse_semantic_path.
        order: Input value used by parse_semantic_path.
        path_dimension: Input value used by parse_semantic_path.
        field_by_semantic_path: Input value used by parse_semantic_path.
        semantic_path_dimension: Input value used by parse_semantic_path.

    Returns:
        Result produced by parse_semantic_path.
    """
    def nearest_dimension(semantic_path_value: str) -> str:
        """
        Run the nearest_dimension helper operation.

        Args:
            semantic_path_value: Input value used by nearest_dimension.

        Returns:
            Result produced by nearest_dimension.
        """
        current = semantic_path_value
        dimensions = path_dimension or {}
        while current:
            dimension = dimensions.get(current, "")
            if dimension:
                return dimension
            if "." not in current:
                return ""
            current = current.rsplit(".", 1)[0]
        return ""

    full_semantic_path = semantic_path
    canonical_semantic_path, selector_key, selector_negated = parse_semantic_selector(semantic_path)
    semantic_path = canonical_semantic_path
    if semantic_path.startswith("const:"):
        return Binding(
            order, syntax_sequence, default_value, full_semantic_path, xpath,
            "", "", "", "", "", canonical_semantic_path, selector_key, selector_negated,
        )
    root_match = re.fullmatch(r"\$\.([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)", semantic_path)
    if root_match:
        root, field = root_match.groups()
        field = (field_by_semantic_path or {}).get(semantic_path, field)
        dimension = (semantic_path_dimension or {}).get(semantic_path) or (path_dimension or {}).get(f"$.{root}", "")
        return Binding(
            order, syntax_sequence, default_value, full_semantic_path, xpath, root,
            dimension, "", "", field, canonical_semantic_path, selector_key, selector_negated,
        )

    dim_match = re.fullmatch(
        r"\$\.([A-Za-z_][A-Za-z0-9_]*)\."
        r"(d[A-Za-z_][A-Za-z0-9_]*)"
        r"(?:\[\?@\.([A-Za-z_][A-Za-z0-9_]*)=(?:\"([^\"]+)\"|'([^']+)'|([^\]]+))\])?"
        r"\.([A-Za-z_][A-Za-z0-9_]*)",
        semantic_path,
    )
    if dim_match:
        root, dimension, filter_field, quoted, single_quoted, bare, field = dim_match.groups()
        field = (field_by_semantic_path or {}).get(semantic_path, field)
        dimension = (semantic_path_dimension or {}).get(semantic_path) or dimension
        filter_value = quoted or single_quoted or bare or ""
        return Binding(
            order, syntax_sequence, default_value, full_semantic_path, xpath, root,
            dimension, filter_field or "", filter_value, field,
            canonical_semantic_path, selector_key, selector_negated,
        )
    generic_match = re.fullmatch(r"\$\.([A-Za-z_][A-Za-z0-9_]*)(?:\..+)?\.([A-Za-z_][A-Za-z0-9_]*)", semantic_path)
    if generic_match:
        root, field = generic_match.groups()
        field = (field_by_semantic_path or {}).get(semantic_path, field)
        parent_path = semantic_path.rsplit(".", 1)[0]
        dimension = (semantic_path_dimension or {}).get(semantic_path) or nearest_dimension(parent_path)
        return Binding(
            order, syntax_sequence, default_value, full_semantic_path, xpath, root,
            dimension, "", "", field, canonical_semantic_path, selector_key, selector_negated,
        )
    return None


def read_bindings(
    binding_csv: Path,
    encoding: str,
    path_dimension: Optional[Dict[str, str]] = None,
    field_by_semantic_path: Optional[Dict[str, str]] = None,
    semantic_path_dimension: Optional[Dict[str, str]] = None,
    rows: Optional[List[Dict[str, str]]] = None,
) -> List[Binding]:
    """
    Read usable binding rows from a CSV file.

    Args:
        binding_csv: Input value used by read_bindings.
        encoding: Input value used by read_bindings.
        path_dimension: Input value used by read_bindings.
        field_by_semantic_path: Input value used by read_bindings.
        semantic_path_dimension: Input value used by read_bindings.

    Returns:
        Result produced by read_bindings.
    """
    if rows is None:
        rows = read_binding_rows(binding_csv, encoding)

    bindings: List[Binding] = []
    for fallback_order, row in enumerate(rows, start=1):
        if first_present(row, ("type", "kind")).upper() == "F":
            continue
        semantic_path = first_present(row, ("semantic_path",))
        xpath = first_present(row, ("syntax_path", "xpath", "source_xpath", "xml_path"))
        if not semantic_path or not xpath:
            continue
        order = parse_order(first_present(row, ("sequence",)), fallback_order)
        syntax_sequence = first_present(row, ("syntax_sequence",))
        default_value = first_present(row, ("default_value", "default"))
        binding = parse_semantic_path(
            semantic_path,
            xpath,
            order,
            syntax_sequence,
            default_value,
            path_dimension,
            field_by_semantic_path,
            semantic_path_dimension,
        )
        if binding:
            bindings.append(
                replace(
                    binding,
                    identifier=first_present(row, ("id", "identifier")),
                    transformation=first_present(row, ("transformation",)),
                    selector_conditions=parse_semantic_selectors(semantic_path),
                )
            )
    return bindings


def read_binding_rows(binding_csv: Path, encoding: str) -> List[Dict[str, str]]:
    """
    Read normalized rows from a binding CSV.

    Args:
        binding_csv: Syntax binding CSV file.
        encoding: CSV encoding used for input.

    Returns:
        Rows with UTF-8 BOM removed from header names and trimmed values.
    """
    with binding_csv.open(newline="", encoding=encoding) as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("Binding CSV has no header.")
        return [{key.lstrip("\ufeff"): (value or "").strip() for key, value in row.items()} for row in reader]


def build_binding_class_tree(rows: List[Dict[str, str]]) -> Optional[BindingClass]:
    """
    Build a semantic class tree from C rows in the syntax binding table.

    Args:
        rows: Binding CSV rows.

    Returns:
        Root class node, or None when no C row is available.
    """
    classes_by_path: Dict[str, BindingClass] = {}
    ordered_classes: List[BindingClass] = []
    for fallback_order, row in enumerate(rows, start=1):
        if not first_present(row, ("type", "kind")).upper().startswith("C"):
            continue
        full_semantic_path = first_present(row, ("semantic_path",))
        if not full_semantic_path:
            continue
        semantic_path, selector_key, selector_negated = parse_semantic_selector(full_semantic_path)
        column = first_present(row, ("structured_csv_column", "source_column", "element", "name"))
        repeats = multiplicity_repeats(first_present(row, ("multiplicity", "cardinality")))
        dimension = dimension_name(column) if semantic_path == "$.invoice" or repeats else ""
        alias = BindingClassAlias(
            order=parse_order(first_present(row, ("sequence",)), fallback_order),
            syntax_sequence=first_present(row, ("syntax_sequence",)),
            semantic_path=full_semantic_path,
            xpath=first_present(row, ("syntax_path", "xpath", "source_xpath", "xml_path")),
            selector_key=selector_key,
            selector_negated=selector_negated,
            selector_conditions=parse_semantic_selectors(full_semantic_path),
        )
        node = classes_by_path.get(semantic_path)
        if node is None:
            node = BindingClass(
                order=alias.order,
                syntax_sequence=alias.syntax_sequence,
                semantic_path=semantic_path,
                name=first_present(row, ("name", "business_term")),
                column=column,
                dimension=dimension,
                xpath=alias.xpath,
                repeats=repeats,
                aliases=[alias],
                children=[],
            )
            classes_by_path[semantic_path] = node
            ordered_classes.append(node)
        else:
            if node.column != column or node.repeats != repeats:
                raise ValueError(
                    f"Class alias metadata differs for {semantic_path}: "
                    f"column/multiplicity must match the canonical Class."
                )
            identity = (alias.semantic_path, alias.xpath, alias.syntax_sequence)
            if any(
                (item.semantic_path, item.xpath, item.syntax_sequence) == identity
                for item in node.aliases
            ):
                raise ValueError(f"Duplicate Class Binding row identity: {identity}")
            node.aliases.append(alias)

    roots: List[BindingClass] = []
    for node in ordered_classes:
        parent_path = node.semantic_path.rsplit(".", 1)[0] if "." in node.semantic_path else ""
        parent = classes_by_path.get(parent_path)
        if parent and parent is not node:
            parent.children.append(node)
        else:
            roots.append(node)

    for node in ordered_classes:
        node.aliases.sort(key=lambda alias: syntax_sequence_sort_key(alias.syntax_sequence, alias.order))
        node.children.sort(key=lambda child: syntax_sequence_sort_key(child.syntax_sequence, child.order))
    if not roots:
        return None
    roots.sort(key=lambda child: syntax_sequence_sort_key(child.syntax_sequence, child.order))
    invoice_root = classes_by_path.get("$.invoice")
    return invoice_root or roots[0]


def direct_class_fields(class_path: str, bindings: List[Binding]) -> List[Binding]:
    """
    Return A-row bindings whose direct semantic parent is a class path.

    Args:
        class_path: Semantic path for a C row.
        bindings: Parsed A-row bindings.

    Returns:
        Bindings directly contained by the class path.
    """
    prefix = class_path + "."
    direct: List[Binding] = []
    for binding in bindings:
        semantic_path = binding.canonical_semantic_path or binding.semantic_path
        if not semantic_path.startswith(prefix):
            continue
        remainder = semantic_path[len(prefix):]
        if "." not in remainder:
            direct.append(binding)
    return sorted(direct, key=lambda binding: syntax_sequence_sort_key(binding.syntax_sequence, binding.order))


def binding_applies_to_alias(binding: Binding, alias: BindingClassAlias) -> bool:
    """Return whether an Attribute Binding belongs to a selected Class alias."""

    if binding.selector_conditions:
        return all(condition in alias.selector_conditions for condition in binding.selector_conditions)
    canonical_path = binding.canonical_semantic_path or binding.semantic_path
    if alias.selector_key and canonical_path.endswith("." + alias.selector_key):
        return not alias.selector_negated
    return True


def walk_binding_classes(root: BindingClass) -> List[BindingClass]:
    """
    Return binding class nodes in pre-order.

    Args:
        root: Root binding class.

    Returns:
        List of class nodes in document/model order.
    """
    nodes = [root]
    for child in root.children:
        nodes.extend(walk_binding_classes(child))
    return nodes


def xpath_element_path(xpath: str) -> str:
    """
    Return the element portion of an XPath without a terminal attribute.

    Args:
        xpath: Input value used by xpath_element_path.

    Returns:
        Result produced by xpath_element_path.
    """
    xpath = xpath.strip()
    element_xpath, _ = split_terminal_attribute(xpath)
    return element_xpath


def xpath_parent(xpath: str) -> str:
    """
    Return the parent XPath for an element or attribute XPath.

    Args:
        xpath: Input value used by xpath_parent.

    Returns:
        Result produced by xpath_parent.
    """
    parts = split_xpath_steps(xpath_element_path(xpath))
    if len(parts) <= 1:
        return "/" + "/".join(parts)
    return "/" + "/".join(parts[:-1])


def common_xpath_prefix(xpaths: List[str]) -> str:
    """
    Find the common path prefix across XPath strings.

    Args:
        xpaths: Input value used by common_xpath_prefix.

    Returns:
        Result produced by common_xpath_prefix.
    """
    split_paths = [split_xpath_steps(xpath_element_path(xpath)) for xpath in xpaths]
    if not split_paths:
        return ""
    prefix: List[str] = []
    for parts in zip(*split_paths):
        if len(set(parts)) != 1:
            break
        prefix.append(parts[0])
    return "/" + "/".join(prefix)


def infer_repeat_path(bindings: List[Binding]) -> str:
    """
    Infer the repeated XML context path from binding rows.

    Args:
        bindings: Input value used by infer_repeat_path.

    Returns:
        Result produced by infer_repeat_path.
    """
    if len(bindings) == 1:
        return xpath_parent(bindings[0].xpath)
    common = common_xpath_prefix([binding.xpath for binding in bindings])
    if any(common == xpath_element_path(binding.xpath) for binding in bindings):
        return xpath_parent(common)
    return common


def relative_xpath(full_xpath: str, context_xpath: str) -> str:
    """
    Make a binding XPath relative to a context XPath.

    Args:
        full_xpath: Input value used by relative_xpath.
        context_xpath: Input value used by relative_xpath.

    Returns:
        Result produced by relative_xpath.
    """
    full = xpath_element_path(full_xpath) if "/@" not in full_xpath else full_xpath
    context = context_xpath.rstrip("/")
    if full == context:
        return "."
    if full.startswith(context + "/"):
        return full[len(context) + 1 :]
    return full


def qname(name: str, namespaces: Dict[str, str]) -> str:
    """
    Build an ElementTree QName from a prefixed XML name.

    Args:
        name: Input value used by qname.
        namespaces: Input value used by qname.

    Returns:
        Result produced by qname.
    """
    if ":" in name:
        prefix, local = name.split(":", 1)
        uri = namespaces.get(prefix)
        return f"{{{uri}}}{local}" if uri else name
    uri = namespaces.get("")
    return f"{{{uri}}}{name}" if uri else name


def element_local_name(tag: str) -> str:
    """
    Return the local XML element name from a tag or step.

    Args:
        tag: Input value used by element_local_name.

    Returns:
        Result produced by element_local_name.
    """
    if tag.startswith("{"):
        return tag.rsplit("}", 1)[-1]
    return tag.split(":", 1)[-1]


def step_base_and_predicate(step: str) -> Tuple[str, str]:
    """
    Split an XPath step into its base name and predicate text.

    Args:
        step: Input value used by step_base_and_predicate.

    Returns:
        Result produced by step_base_and_predicate.
    """
    if "[" not in step:
        return step, ""
    base, predicate = step.split("[", 1)
    return base, predicate.rsplit("]", 1)[0].strip()


def predicate_child_value(predicate: str) -> Tuple[str, str, str]:
    """
    Parse a simple child-equals-literal predicate.

    Args:
        predicate: Input value used by predicate_child_value.

    Returns:
        Result produced by predicate_child_value.
    """
    path_pattern = r"(@[A-Za-z_][\w.-]*|[A-Za-z_][\w.-]*:[A-Za-z_][\w.-]*(?:/(?:@[A-Za-z_][\w.-]*|[A-Za-z_][\w.-]*:[A-Za-z_][\w.-]*))*)"
    match = re.fullmatch(r"not\(\s*" + path_pattern + r"\s*=\s*'([^']*)'\s*\)", predicate)
    if match:
        child_name, value = match.groups()
        return child_name, "not=", value
    match = re.fullmatch(r'not\(\s*' + path_pattern + r'\s*=\s*"([^"]*)"\s*\)', predicate)
    if match:
        child_name, value = match.groups()
        return child_name, "not=", value
    match = re.fullmatch(path_pattern + r"\s*(!=|=)\s*(true|false)\(\)", predicate)
    if match:
        child_name, operator, value = match.groups()
        return child_name, operator, value
    match = re.fullmatch(path_pattern + r"\s*(!=|=)\s*'([^']*)'", predicate)
    if match:
        child_name, operator, value = match.groups()
        return child_name, operator, value
    match = re.fullmatch(path_pattern + r'\s*(!=|=)\s*"([^"]*)"', predicate)
    if match:
        child_name, operator, value = match.groups()
        return child_name, operator, value
    return "", "", ""


def find_predicate_value(parent: ET.Element, relative_path: str, namespaces: Dict[str, str]) -> str:
    """
    Read the value referenced by a predicate child path.

    Args:
        parent: Input value used by find_predicate_value.
        relative_path: Input value used by find_predicate_value.
        namespaces: Input value used by find_predicate_value.

    Returns:
        Result produced by find_predicate_value.
    """
    current = parent
    parts = relative_path.split("/")
    for index, step in enumerate(parts):
        if step.startswith("@"):
            return current.attrib.get(step[1:], "") if index == len(parts) - 1 else ""
        wanted = qname(step, namespaces)
        next_child = None
        for child in list(current):
            if child.tag == wanted or element_local_name(child.tag) == element_local_name(step):
                next_child = child
                break
        if next_child is None:
            return ""
        current = next_child
    return (current.text or "").strip()


def set_predicate_value(parent: ET.Element, relative_path: str, value: str, namespaces: Dict[str, str]) -> None:
    """
    Write the value referenced by a predicate child path.

    Args:
        parent: Input value used by set_predicate_value.
        relative_path: Input value used by set_predicate_value.
        value: Input value used by set_predicate_value.
        namespaces: Input value used by set_predicate_value.

    Returns:
        None. The XML parent subtree is modified in place.
    """
    current = parent
    parts = relative_path.split("/")
    for index, step in enumerate(parts):
        if step.startswith("@"):
            if index == len(parts) - 1:
                current.set(step[1:], value)
            return
        current = find_or_create_child(current, step, namespaces)
    current.text = value


def split_xpath_steps(xpath: str) -> List[str]:
    """
    Split an XML path into steps while preserving predicates.

    Args:
        xpath: Input value used by split_xpath_steps.

    Returns:
        Result produced by split_xpath_steps.
    """
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
    """
    Separate a terminal XML attribute from an XPath.

    Args:
        xpath: Input value used by split_terminal_attribute.

    Returns:
        Result produced by split_terminal_attribute.
    """
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


def child_satisfies_predicate(child: ET.Element, predicate: str, namespaces: Dict[str, str]) -> bool:
    """
    Check whether a child element satisfies a simple predicate.

    Args:
        child: Input value used by child_satisfies_predicate.
        predicate: Input value used by child_satisfies_predicate.
        namespaces: Input value used by child_satisfies_predicate.

    Returns:
        Result produced by child_satisfies_predicate.
    """
    predicate_name, operator, predicate_value = predicate_child_value(predicate)
    if not predicate_name:
        return True
    actual_value = find_predicate_value(child, predicate_name, namespaces)
    if operator == "=":
        return actual_value == predicate_value
    if operator == "!=":
        return bool(actual_value) and actual_value != predicate_value
    if operator == "not=":
        return actual_value != predicate_value
    return True


def find_or_create_child(parent: ET.Element, step: str, namespaces: Dict[str, str], force_new: bool = False) -> ET.Element:
    """
    Find an existing matching child or create a new XML child.

    Args:
        parent: Input value used by find_or_create_child.
        step: Input value used by find_or_create_child.
        namespaces: Input value used by find_or_create_child.
        force_new: Input value used by find_or_create_child.

    Returns:
        Result produced by find_or_create_child.
    """
    base, predicate = step_base_and_predicate(step)
    tag = qname(base, namespaces)
    if not force_new:
        for child in list(parent):
            if child.tag == tag and child_satisfies_predicate(child, predicate, namespaces):
                return child
    child = ET.SubElement(parent, tag)
    predicate_name, operator, predicate_value = predicate_child_value(predicate)
    if predicate_name and operator == "=":
        set_predicate_value(child, predicate_name, predicate_value, namespaces)
    return child


def split_xml_path(xpath: str) -> Tuple[List[str], str]:
    """
    Split an XML path into element steps and terminal attribute name.

    Args:
        xpath: Input value used by split_xml_path.

    Returns:
        Result produced by split_xml_path.
    """
    xpath = (xpath or "").strip()
    xpath, attribute = split_terminal_attribute(xpath)
    parts = split_xpath_steps(xpath)
    return parts, attribute


def ensure_path(root: ET.Element, xpath: str, namespaces: Dict[str, str], force_new_leaf: bool = False) -> Tuple[ET.Element, str]:
    """
    Ensure an XML path exists and return its final element and attribute.

    Args:
        root: Input value used by ensure_path.
        xpath: Input value used by ensure_path.
        namespaces: Input value used by ensure_path.
        force_new_leaf: Input value used by ensure_path.

    Returns:
        Result produced by ensure_path.
    """
    parts, attribute = split_xml_path(xpath)
    if parts and element_local_name(parts[0]) == element_local_name(root.tag):
        parts = parts[1:]
    current = root
    for index, part in enumerate(parts):
        current = find_or_create_child(current, part, namespaces, force_new_leaf and index == len(parts) - 1)
    return current, attribute


def set_xml_value(root: ET.Element, xpath: str, value: str, namespaces: Dict[str, str]) -> None:
    """
    Set an XML element text or attribute value by XPath.

    Args:
        root: Input value used by set_xml_value.
        xpath: Input value used by set_xml_value.
        value: Input value used by set_xml_value.
        namespaces: Input value used by set_xml_value.

    Returns:
        None. The XML tree is modified in place.
    """
    if not value:
        return
    element, attribute = ensure_path(root, xpath, namespaces)
    if attribute:
        element.set(attribute, value)
    else:
        element.text = value


def find_existing_elements(root: ET.Element, parts: List[str], namespaces: Dict[str, str]) -> List[ET.Element]:
    """Find existing elements for an absolute binding path without creating nodes."""

    if parts and element_local_name(parts[0]) == element_local_name(root.tag):
        parts = parts[1:]
    current = [root]
    for part in parts:
        base, predicate = step_base_and_predicate(part)
        tag = qname(base, namespaces)
        current = [
            child
            for parent in current
            for child in list(parent)
            if child.tag == tag and child_satisfies_predicate(child, predicate, namespaces)
        ]
        if not current:
            break
    return current


def apply_default_to_existing_contexts(
    root: ET.Element,
    xpath: str,
    value: str,
    namespaces: Dict[str, str],
) -> int:
    """Apply a syntax-only default only where the bound parent context already exists."""

    if not value:
        return 0
    parts, attribute = split_xml_path(xpath)
    if attribute:
        targets = find_existing_elements(root, parts, namespaces)
        applied = 0
        for target in targets:
            if not target.get(attribute):
                target.set(attribute, value)
                applied += 1
        return applied
    if not parts:
        return 0
    parents = find_existing_elements(root, parts[:-1], namespaces)
    applied = 0
    for parent in parents:
        base, predicate = step_base_and_predicate(parts[-1])
        existing = next(
            (
                child
                for child in list(parent)
                if child.tag == qname(base, namespaces)
                and child_satisfies_predicate(child, predicate, namespaces)
            ),
            None,
        )
        if existing is None:
            existing = find_or_create_child(parent, parts[-1], namespaces)
        if not (existing.text or "").strip():
            existing.text = value
            applied += 1
    return applied


def is_amount_xpath(xpath: str) -> bool:
    """
    Return whether an XPath points to an amount element.

    Args:
        xpath: Input value used by is_amount_xpath.

    Returns:
        Result produced by is_amount_xpath.
    """
    parts, attribute = split_xml_path(xpath)
    if attribute:
        return False
    return bool(parts) and element_local_name(parts[-1]).endswith("Amount")


def apply_currency_attribute(element: ET.Element, xpath: str, document_currency: str, tax_currency: str) -> None:
    """
    Set currencyID on amount elements when appropriate.

    Args:
        element: Input value used by apply_currency_attribute.
        xpath: Input value used by apply_currency_attribute.
        document_currency: Input value used by apply_currency_attribute.
        tax_currency: Input value used by apply_currency_attribute.

    Returns:
        None. The XML element is modified in place.
    """
    if not is_amount_xpath(xpath) or element.get("currencyID"):
        return
    currency = tax_currency if "TaxCurrencyCode" in xpath else document_currency
    if currency:
        element.set("currencyID", currency)


def resolve_currency_references(xpath: str, document_currency: str, tax_currency: str) -> str:
    """
    Replace currency reference paths with currency codes.

    Args:
        xpath: Input value used by resolve_currency_references.
        document_currency: Input value used by resolve_currency_references.
        tax_currency: Input value used by resolve_currency_references.

    Returns:
        Result produced by resolve_currency_references.
    """
    if document_currency:
        xpath = xpath.replace("=/Invoice/cbc:DocumentCurrencyCode", f"='{document_currency}'")
        xpath = xpath.replace("!=/Invoice/cbc:DocumentCurrencyCode", f"!='{document_currency}'")
    if tax_currency:
        xpath = xpath.replace("=/Invoice/cbc:TaxCurrencyCode", f"='{tax_currency}'")
        xpath = xpath.replace("!=/Invoice/cbc:TaxCurrencyCode", f"!='{tax_currency}'")
    return xpath


def create_context(
    root: ET.Element,
    xpath: str,
    namespaces: Dict[str, str],
    document_currency: str = "",
    tax_currency: str = "",
) -> ET.Element:
    """
    Create the root XML context for reverse hierarchical conversion.

    Args:
        root: Input value used by create_context.
        xpath: Input value used by create_context.
        namespaces: Input value used by create_context.
        document_currency: Input value used by create_context.
        tax_currency: Input value used by create_context.

    Returns:
        Result produced by create_context.
    """
    resolved_xpath = resolve_currency_references(xpath, document_currency, tax_currency)
    element, _ = ensure_path(root, resolved_xpath, namespaces, force_new_leaf=True)
    return element


def set_xml_value_with_currency(
    root: ET.Element,
    xpath: str,
    value: str,
    namespaces: Dict[str, str],
    document_currency: str,
    tax_currency: str,
) -> None:
    """
    Set an XML value and apply currency attributes or references.

    Args:
        root: Input value used by set_xml_value_with_currency.
        xpath: Input value used by set_xml_value_with_currency.
        value: Input value used by set_xml_value_with_currency.
        namespaces: Input value used by set_xml_value_with_currency.
        document_currency: Input value used by set_xml_value_with_currency.
        tax_currency: Input value used by set_xml_value_with_currency.

    Returns:
        None. The XML tree is modified in place.
    """
    if not value:
        return
    resolved_xpath = resolve_currency_references(xpath, document_currency, tax_currency)
    element, attribute = ensure_path(root, resolved_xpath, namespaces)
    if attribute:
        element.set(attribute, value)
    else:
        element.text = value
        apply_currency_attribute(element, resolved_xpath, document_currency, tax_currency)


def set_relative_xml_value(
    context: ET.Element,
    xpath: str,
    value: str,
    namespaces: Dict[str, str],
    document_currency: str = "",
    tax_currency: str = "",
) -> None:
    """
    Set a value below a row-specific XML context.

    Args:
        context: Input value used by set_relative_xml_value.
        xpath: Input value used by set_relative_xml_value.
        value: Input value used by set_relative_xml_value.
        namespaces: Input value used by set_relative_xml_value.
        document_currency: Input value used by set_relative_xml_value.
        tax_currency: Input value used by set_relative_xml_value.

    Returns:
        None. The XML context subtree is modified in place.
    """
    if not value:
        return
    if xpath == ".":
        context.text = value
        apply_currency_attribute(context, xpath, document_currency, tax_currency)
        return
    if xpath.startswith("@"):
        context.set(xpath[1:], value)
        return
    resolved_xpath = resolve_currency_references(xpath, document_currency, tax_currency)
    element, attribute = ensure_path(context, resolved_xpath, namespaces)
    if attribute:
        element.set(attribute, value)
    else:
        element.text = value
        apply_currency_attribute(element, resolved_xpath, document_currency, tax_currency)


def load_ubl_child_order(
    schema_root: Optional[Path] = None,
    schema_url: str = "",
) -> Optional[Dict[str, List[str]]]:
    """
    Load UBL child element order from a local schema root or schema URL.

    Args:
        schema_root: Directory containing extracted UBL XSD files.
        schema_url: URL of the UBL Invoice schema entry point.

    Returns:
        Mapping from parent element local name to ordered child local names, or
        None when no schema source is supplied.
    """
    if not schema_root and not schema_url:
        return None
    local_schema = Path(schema_url) if schema_url else None
    if local_schema and local_schema.is_file():
        cache_key = str(local_schema.resolve())
        if cache_key in SCHEMA_CHILD_ORDER_CACHE:
            return SCHEMA_CHILD_ORDER_CACHE[cache_key]
        try:
            import xmlschema  # type: ignore
        except ImportError as exc:
            raise RuntimeError("Local generic XSD ordering requires xmlschema.") from exc
        schema = xmlschema.XMLSchema(str(local_schema))
        orders: Dict[str, List[str]] = {}
        ambiguous: set[str] = set()
        for schema_type in schema.maps.types.values():
            content = getattr(schema_type, "content", None)
            if content is None:
                continue
            try:
                declarations = list(content.iter_elements())
            except (AttributeError, TypeError):
                continue
            for declaration in declarations:
                child_content = getattr(getattr(declaration, "type", None), "content", None)
                if child_content is None:
                    continue
                try:
                    child_order = [child.local_name for child in child_content.iter_elements()]
                except (AttributeError, TypeError):
                    continue
                name = declaration.local_name
                if not name or not child_order:
                    continue
                if name in orders and orders[name] != child_order:
                    ambiguous.add(name)
                else:
                    orders[name] = child_order
        for name in ambiguous:
            orders.pop(name, None)
        root_element = next(
            (item for item in schema.elements.values() if getattr(item, "local_name", "")), None
        )
        if root_element is not None:
            root_content = getattr(root_element.type, "content", None)
            if root_content is not None:
                orders[root_element.local_name] = [
                    child.local_name for child in root_content.iter_elements()
                ]
        SCHEMA_CHILD_ORDER_CACHE[cache_key] = orders
        return orders
    index = UblSchemaIndex()
    if schema_root:
        index.load_directory(schema_root)
    if schema_url:
        index.load_url(schema_url)
    return index.child_order_by_element_name()


def child_order_for(element: ET.Element, schema_child_order: Optional[Dict[str, List[str]]] = None) -> Dict[str, int]:
    """
    Return the schema child-order map for an element.

    Args:
        element: Input value used by child_order_for.
        schema_child_order: Child order generated from UBL XSD, if available.

    Returns:
        Result produced by child_order_for.
    """
    local = element_local_name(element.tag)
    order_source = schema_child_order or UBL_CHILD_ORDER
    order = order_source.get(local)
    if order is None and local.endswith("Address"):
        order = order_source.get("Address")
    if order is None and local.endswith("DocumentReference"):
        order = order_source.get("DocumentReference")
    if order is None and local.endswith("MonetaryTotal"):
        order = order_source.get("MonetaryTotal")
    return {name: index for index, name in enumerate(order or [])}


def sort_children_for_ubl_schema(
    element: ET.Element,
    schema_child_order: Optional[Dict[str, List[str]]] = None,
) -> None:
    """
    Recursively sort UBL children according to schema order.

    Args:
        element: Input value used by sort_children_for_ubl_schema.
        schema_child_order: Child order generated from UBL XSD, if available.

    Returns:
        None. The XML tree is sorted in place.
    """
    for child in list(element):
        sort_children_for_ubl_schema(child, schema_child_order)
    order = child_order_for(element, schema_child_order)
    if not order:
        return
    children = list(element)
    if len(children) < 2:
        return
    original_position = {id(child): index for index, child in enumerate(children)}
    children.sort(key=lambda child: (order.get(element_local_name(child.tag), 10_000), original_position[id(child)]))
    element[:] = children


def find_child_by_local_name(element: ET.Element, local_name: str) -> Optional[ET.Element]:
    """
    Find the first direct child with a local element name.

    Args:
        element: Input value used by find_child_by_local_name.
        local_name: Input value used by find_child_by_local_name.

    Returns:
        Result produced by find_child_by_local_name.
    """
    for child in list(element):
        if element_local_name(child.tag) == local_name:
            return child
    return None


def ensure_tax_scheme_defaults(root: ET.Element, namespaces: Dict[str, str]) -> None:
    """
    Add required TaxScheme ID defaults when missing.

    Args:
        root: Input value used by ensure_tax_scheme_defaults.
        namespaces: Input value used by ensure_tax_scheme_defaults.

    Returns:
        None. Missing default XML children are added in place.
    """
    for element in root.iter():
        local = element_local_name(element.tag)
        if local == "AllowanceCharge" and find_child_by_local_name(element, "ChargeIndicator") is None:
            charge_indicator = ET.Element(qname("cbc:ChargeIndicator", namespaces))
            charge_indicator.text = "false"
            element.insert(0, charge_indicator)
        if local not in {"PartyTaxScheme", "TaxCategory", "ClassifiedTaxCategory"}:
            continue
        if find_child_by_local_name(element, "TaxScheme") is not None:
            continue
        tax_scheme = ET.SubElement(element, qname("cac:TaxScheme", namespaces))
        tax_id = ET.SubElement(tax_scheme, qname("cbc:ID", namespaces))
        tax_id.text = "VAT"


def indent_xml(element: ET.Element, level: int = 0) -> None:
    """
    Apply readable indentation to XML elements.

    Args:
        element: Input value used by indent_xml.
        level: Input value used by indent_xml.

    Returns:
        None. The XML tree is formatted in place.
    """
    indentation = "\n" + level * "  "
    if len(element):
        if not element.text or not element.text.strip():
            element.text = indentation + "  "
        for child in list(element):
            indent_xml(child, level + 1)
        if not element.tail or not element.tail.strip():
            element.tail = indentation
    elif level and (not element.tail or not element.tail.strip()):
        element.tail = indentation


def new_row(fieldnames: List[str], d_invoice: str) -> Dict[str, str]:
    """
    Create an empty hierarchical CSV row with an invoice dimension value.

    Args:
        fieldnames: Input value used by new_row.
        d_invoice: Input value used by new_row.

    Returns:
        Result produced by new_row.
    """
    row = {field: "" for field in fieldnames}
    if "dInvoice" in row:
        row["dInvoice"] = d_invoice
    return row


def row_has_values(row: Dict[str, str], dimension_columns: List[str]) -> bool:
    """
    Return whether a row has any non-dimension fact values.

    Args:
        row: Input value used by row_has_values.
        dimension_columns: Input value used by row_has_values.

    Returns:
        Result produced by row_has_values.
    """
    return any(value for field, value in row.items() if field not in dimension_columns)


def validate_hierarchical_row_scopes(
    rows: List[Dict[str, str]],
    fieldnames: List[str],
    field_dimension: Dict[str, str],
) -> None:
    """Reject rows that mix facts belonging to different row scopes.

    A non-repeated child class shares its nearest repeated ancestor's row.  A
    repeated child class owns separate rows, even for its first occurrence.
    Therefore every populated fact on a row must belong to that row's deepest
    populated dimension.
    """
    dimensions = [field for field in fieldnames if is_dimension_column(field)]
    for row_number, row in enumerate(rows, start=2):
        active_dimensions = [dimension for dimension in dimensions if row.get(dimension)]
        if not active_dimensions:
            continue
        row_scope = active_dimensions[-1]
        for field in fieldnames:
            if field in dimensions or not row.get(field):
                continue
            owner = field_dimension.get(field, "")
            if owner and owner != row_scope:
                raise ValueError(
                    f"Invalid hierarchical CSV row {row_number}: {field} belongs to {owner}, "
                    f"but the row scope is {row_scope}. Repeated child facts must be written "
                    "on separate child rows."
                )


def drop_empty_columns(rows: List[Dict[str, str]], fieldnames: List[str]) -> Tuple[List[Dict[str, str]], List[str]]:
    """
    Remove columns that are empty across all rows.

    Args:
        rows: Input value used by drop_empty_columns.
        fieldnames: Input value used by drop_empty_columns.

    Returns:
        Result produced by drop_empty_columns.
    """
    used = {
        field
        for field in fieldnames
        if any((row.get(field) or "").strip() for row in rows)
    }
    revised_fields = [field for field in fieldnames if field in used]
    revised_rows = [{field: row.get(field, "") for field in revised_fields} for row in rows]
    return revised_rows, revised_fields


def add_derived_fieldnames(fieldnames: List[str], bindings: List[Binding]) -> List[str]:
    """
    Add binding-derived field names missing from a template.

    Args:
        fieldnames: Input value used by add_derived_fieldnames.
        bindings: Input value used by add_derived_fieldnames.

    Returns:
        Result produced by add_derived_fieldnames.
    """
    if fieldnames:
        return fieldnames
    names = ["dInvoice"]
    for binding in bindings:
        if binding.dimension and binding.dimension not in names:
            names.append(binding.dimension)
    for binding in bindings:
        for name in (binding.filter_field, binding.field):
            if name and name not in names:
                names.append(name)
    return names


def relative_metadata_path(path: Optional[Path], metadata_file: Path) -> str:
    """
    Format a metadata path relative to its JSON metadata file.

    Args:
        path: Input value used by relative_metadata_path.
        metadata_file: Input value used by relative_metadata_path.

    Returns:
        Result produced by relative_metadata_path.
    """
    if not path:
        return ""
    try:
        return Path(os.path.relpath(path.resolve(), metadata_file.parent.resolve())).as_posix()
    except OSError:
        return path.as_posix()


def latest_file(directory: Path, pattern: str) -> Optional[Path]:
    """
    Find the latest matching file in a directory.

    Args:
        directory: Input value used by latest_file.
        pattern: Input value used by latest_file.

    Returns:
        Result produced by latest_file.
    """
    files = sorted(directory.glob(pattern))
    return files[-1] if files else None


def taxonomy_entrypoints(taxonomy_base: Optional[Path], metadata_file: Path) -> Dict[str, str]:
    """
    Build metadata links to available taxonomy entrypoint files.

    Args:
        taxonomy_base: Input value used by taxonomy_entrypoints.
        metadata_file: Input value used by taxonomy_entrypoints.

    Returns:
        Result produced by taxonomy_entrypoints.
    """
    if not taxonomy_base:
        raise ValueError("--taxonomy-base is required when writing xBRL-CSV metadata.")
    # HMD-centric model units flatten the public OIM entry point directly
    # below taxonomy/. Keep the legacy runtime layout as a fallback while
    # retained pre-reorganization paths remain available.
    oim_directory = taxonomy_base / "en16931_Invoice"
    if not oim_directory.is_dir():
        oim_directory = taxonomy_base / "oim" / "en16931_Invoice"
    xbrl_csv_schema = latest_file(oim_directory, "en16931-all-oim-*.xsd")
    module_schema = latest_file(taxonomy_base / "en16931", "en16931-*.xsd")
    if not xbrl_csv_schema:
        raise ValueError(f"Missing xBRL-CSV taxonomy schema under {oim_directory}.")
    return {
        "xbrlCsvSchema": relative_metadata_path(xbrl_csv_schema, metadata_file),
        "definitionLinkbase": relative_metadata_path(latest_file(oim_directory, "en16931-all-dim-*.xml"), metadata_file),
        "moduleSchema": relative_metadata_path(module_schema, metadata_file),
    }


def taxonomy_version(entrypoints: Dict[str, str]) -> str:
    """
    Infer a taxonomy version label from entrypoint file names.

    Args:
        entrypoints: Input value used by taxonomy_version.

    Returns:
        Result produced by taxonomy_version.
    """
    for value in entrypoints.values():
        match = re.search(r"(\d{4}-\d{2}-\d{2})", value or "")
        if match:
            return match.group(1)
    return "2026-07-05"


def xbrl_csv_column_definition(column: Dict[str, str]) -> Dict[str, Dict[str, str]]:
    """
    Build one XBRL CSV metadata column definition.

    Args:
        column: Input value used by xbrl_csv_column_definition.

    Returns:
        Result produced by xbrl_csv_column_definition.
    """
    dimensions = {"concept": column["taxonomyConcept"]}
    datatype = (column.get("datatype") or "").lower()
    if "amount" in datatype or column.get("name", "").endswith("Amount"):
        dimensions["unit"] = "iso4217:JPY"
    return {"dimensions": dimensions}


def binding_column_metadata(
    binding_csv: Path,
    encoding: str,
    rows: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Dict[str, str]]:
    """
    Build column metadata from a syntax binding CSV file.

    Args:
        binding_csv: Syntax binding CSV to read.
        encoding: CSV encoding used for input.

    Returns:
        Column metadata keyed by Structured CSV column name.
    """
    if rows is None:
        rows = read_binding_rows(binding_csv, encoding)

    metadata: Dict[str, Dict[str, str]] = {}
    for row in rows:
        row_type = first_present(row, ("type", "kind")).upper()
        # The binding's ``element`` field is the source XML QName (for example
        # ``cbc:ID``).  xBRL-CSV metadata must instead use the actual Structured
        # CSV header and the corresponding generated taxonomy concept name.
        element = first_present(row, ("structured_csv_column", "column", "name", "element"))
        module = first_present(row, ("module",)) or "en16931"
        if not element:
            continue
        common = {
            "lhmId": first_present(row, ("id",)),
            "lhmName": first_present(row, ("name", "business_term")),
            "semanticPath": first_present(row, ("semantic_path",)),
            "xpath": first_present(row, ("syntax_path", "xpath", "source_xpath", "xml_path")),
            "datatype": first_present(row, ("datatype", "semantic_data_type")),
            "multiplicity": first_present(row, ("multiplicity", "cardinality")),
            "lhmLevel": first_present(row, ("lhm_level",)),
            "classTerm": first_present(row, ("class_term",)),
            "module": module,
        }
        if row_type.startswith("C") or row_type.startswith("G"):
            dimension = dimension_name(element)
            dimension_prefix = "plt" if module == "en16931" else "en16931"
            metadata[dimension] = {
                **common,
                "kind": "dimension",
                "taxonomyConcept": f"{dimension_prefix}:d_{module}_{element}",
                "primaryItem": f"en16931:p_{module}_{element}",
            }
        elif row_type.startswith("A") or row_type.startswith("F"):
            metadata[element] = {
                **common,
                "kind": "fact",
                "taxonomyConcept": f"{module}:{element}",
            }
    return metadata


def write_csv_metadata(
    metadata_file: Path,
    csv_file: Path,
    xml_file: Path,
    binding_csv: Path,
    fieldnames: List[str],
    row_count: int,
    taxonomy_base: Optional[Path],
    encoding: str,
    binding_rows: Optional[List[Dict[str, str]]] = None,
) -> None:
    """
    Write JSON metadata for a hierarchical CSV file.

    Args:
        metadata_file: Input value used by write_csv_metadata.
        csv_file: Input value used by write_csv_metadata.
        xml_file: Input value used by write_csv_metadata.
        binding_csv: Input value used by write_csv_metadata.
        fieldnames: Input value used by write_csv_metadata.
        row_count: Input value used by write_csv_metadata.
        taxonomy_base: Input value used by write_csv_metadata.
        encoding: Input value used by write_csv_metadata.

    Returns:
        None. The JSON metadata file is written.
    """
    columns = binding_column_metadata(binding_csv, encoding, binding_rows)
    entrypoints = taxonomy_entrypoints(taxonomy_base, metadata_file)
    version = taxonomy_version(entrypoints)
    template_dimensions = {
        columns[field]["taxonomyConcept"]: f"${field}"
        for field in fieldnames
        if field in columns and columns[field].get("kind") == "dimension"
    }
    template_columns = {}
    for field in fieldnames:
        column = {**columns.get(field, {}), "name": field}
        if column.get("kind") == "dimension":
            template_columns[field] = {}
        elif column.get("kind") == "fact" and column.get("taxonomyConcept"):
            template_columns[field] = xbrl_csv_column_definition(column)
    taxonomy_files = [
        entrypoints.get("xbrlCsvSchema", ""),
    ]
    metadata = {
        "documentInfo": {
            "documentType": "https://xbrl.org/2021/xbrl-csv",
            "namespaces": {
                "en16931": f"http://www.xbrl.org/int/gl/en16931/{version}",
                "plt": f"http://www.xbrl.org/int/gl/plt/{version}",
                "iso4217": "http://www.xbrl.org/2003/iso4217",
                "scheme": "http://www.example.com",
                "xbrl": "https://xbrl.org/2021",
            },
            "taxonomy": [path for path in taxonomy_files if path],
        },
        "tables": {
            "structured": {
                "template": "structured",
                "url": relative_metadata_path(csv_file, metadata_file),
            },
        },
        "tableTemplates": {
            "structured": {
                "dimensions": {
                    "period": "2026-07-06T00:00:00",
                    "entity": "scheme:UADC-PoC",
                    **template_dimensions,
                },
                "columns": template_columns,
            },
        },
    }
    metadata_file.parent.mkdir(parents=True, exist_ok=True)
    with metadata_file.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
        f.write("\n")


def write_hierarchical_csv(
    xml_file: Path,
    binding_csv: Path,
    out_csv: Path,
    template_csv: Optional[Path],
    metadata_output: Optional[Path],
    taxonomy_base: Optional[Path],
    encoding: str,
    d_invoice: str = "1",
    drop_empty: bool = False,
    hmd_file: Optional[Path] = None,
) -> Tuple[int, List[str]]:
    """
    Extract XML data and write hierarchical CSV plus metadata.

    Args:
        xml_file: Input value used by write_hierarchical_csv.
        binding_csv: Input value used by write_hierarchical_csv.
        out_csv: Input value used by write_hierarchical_csv.
        template_csv: Input value used by write_hierarchical_csv.
        metadata_output: Input value used by write_hierarchical_csv.
        taxonomy_base: Input value used by write_hierarchical_csv.
        encoding: Input value used by write_hierarchical_csv.
        d_invoice: Input value used by write_hierarchical_csv.
        drop_empty: Input value used by write_hierarchical_csv.

    Returns:
        Result produced by write_hierarchical_csv.
    """
    namespaces = collect_namespaces(xml_file)
    root = ET.parse(xml_file).getroot()
    effective_rows = read_effective_binding_rows(binding_csv, encoding, hmd_file)
    binding_layout = build_layout_from_rows(effective_rows)
    if not binding_layout.fieldnames:
        raise ValueError("The syntax binding table has no usable C/A rows.")
    bindings = read_bindings(
        binding_csv,
        encoding,
        binding_layout.path_dimension,
        binding_layout.field_by_semantic_path,
        binding_layout.semantic_path_dimension,
        effective_rows,
    )
    if not bindings:
        raise ValueError("No usable semantic_path/xpath bindings found.")

    _, field_dimension = read_template(template_csv, encoding)
    fieldnames = binding_layout.fieldnames
    field_dimension = {**binding_layout.field_dimension, **field_dimension}
    dimension_columns = [name for name in fieldnames if is_dimension_column(name)]

    class_root = build_binding_class_tree(effective_rows)
    if class_root is None:
        raise ValueError("No C rows found in the syntax binding table.")

    direct_fields_by_class = {
        node.semantic_path: direct_class_fields(node.semantic_path, bindings)
        for node in walk_binding_classes(class_root)
    }
    rows: List[Dict[str, str]] = []

    def alias_nodes(
        parent_context: ET.Element,
        parent_alias: Optional[BindingClassAlias],
        alias: BindingClassAlias,
    ) -> List[ET.Element]:
        """Find physical nodes represented by one Class alias."""

        if not alias.xpath:
            return [parent_context]
        rel = relative_xpath(alias.xpath, parent_alias.xpath) if parent_alias and parent_alias.xpath else alias.xpath
        contexts = find_nodes(parent_context, rel, namespaces, root)
        if contexts or rel != alias.xpath:
            return contexts
        return find_nodes(root, alias.xpath, namespaces, root)

    def selector_fact_present(
        context: ET.Element,
        class_node: BindingClass,
        alias: BindingClassAlias,
        selector_key: Optional[str] = None,
    ) -> bool:
        """Evaluate a positive selector from same-occurrence semantic facts."""

        key = selector_key or alias.selector_key
        selector_path = class_node.semantic_path + "." + key
        selector_bindings = [
            binding
            for binding in direct_fields_by_class.get(class_node.semantic_path, [])
            if (binding.canonical_semantic_path or binding.semantic_path) == selector_path
        ]
        for binding in selector_bindings:
            rel = relative_xpath(binding.xpath, alias.xpath) if alias.xpath else binding.xpath
            if get_value(context, rel, namespaces, root):
                return True
        return False

    def class_contexts(
        parent_context: ET.Element,
        parent_alias: Optional[BindingClassAlias],
        child_class: BindingClass,
    ) -> List[Tuple[ET.Element, BindingClassAlias]]:
        """
        Find XML contexts for a child class inside its parent class context.

        Args:
            parent_context: XML context of the parent class.
            parent_class: Parent binding class.
            child_class: Child binding class.

        Returns:
            Matching child XML contexts.
        """
        physical: Dict[int, Tuple[ET.Element, List[BindingClassAlias]]] = {}
        for alias in child_class.aliases:
            for context in alias_nodes(parent_context, parent_alias, alias):
                conditions = alias.selector_conditions
                matches = all(
                    selector_fact_present(context, child_class, alias, key) != negated
                    for key, negated in conditions
                )
                if matches:
                    physical.setdefault(id(context), (context, []))[1].append(alias)
        selected: List[Tuple[ET.Element, BindingClassAlias]] = []
        for context, aliases in physical.values():
            if len(aliases) != 1:
                identities = [alias.semantic_path for alias in aliases]
                raise ValueError(
                    f"Class alias selection for {child_class.semantic_path} matched "
                    f"{len(aliases)} aliases: {identities}"
                )
            selected.append((context, aliases[0]))
        if not selected and len(child_class.aliases) == 1:
            alias = child_class.aliases[0]
            external_fact_present = any(
                relative_xpath(binding.xpath, alias.xpath).startswith("/")
                and get_value(root, binding.xpath, namespaces, root)
                for binding in direct_fields_by_class.get(child_class.semantic_path, [])
            )
            if external_fact_present:
                selected.append((parent_context, alias))
        return selected

    def fill_direct_fields(
        row: Dict[str, str],
        context: ET.Element,
        class_node: BindingClass,
        alias: BindingClassAlias,
    ) -> None:
        """
        Fill direct A-row fields for one class context into one CSV row.

        Args:
            row: Structured CSV row being populated.
            context: XML context for the class.
            class_node: Binding class whose direct fields are processed.

        Returns:
            None. The row is modified in place.
        """
        direct_bindings = direct_fields_by_class.get(class_node.semantic_path, [])
        grouped: Dict[str, List[Binding]] = {}
        for binding in direct_bindings:
            if binding_applies_to_alias(binding, alias):
                grouped.setdefault(binding.canonical_semantic_path or binding.semantic_path, []).append(binding)

        def extracted_value(binding: Binding) -> str:
            rel = relative_xpath(binding.xpath, alias.xpath) if alias.xpath else binding.xpath
            raw_value = tax_total_occurrence_value(
                context, rel, binding.transformation, namespaces, root
            )
            return transform_binding_value(raw_value, binding.transformation) or ""

        def selector_present(binding: Binding) -> bool:
            selector_path = class_node.semantic_path + "." + binding.selector_key
            candidates = [
                item for item in direct_bindings
                if (item.canonical_semantic_path or item.semantic_path) == selector_path
            ]
            if binding.identifier:
                candidates.extend(
                    item for item in direct_bindings
                    if item.identifier == binding.identifier + "-1"
                )
            return any(extracted_value(item) for item in dict.fromkeys(candidates))

        for group in grouped.values():
            selected = group
            if any(binding.selector_key for binding in group):
                positive = [
                    binding for binding in group
                    if binding.selector_key and not binding.selector_negated
                    and extracted_value(binding)
                    and selector_present(binding)
                ]
                selected = positive or [
                    binding for binding in group
                    if binding.selector_key and binding.selector_negated and extracted_value(binding)
                ]
                if len(selected) > 1:
                    raise ValueError(
                        f"Attribute alias selection for {group[0].canonical_semantic_path} "
                        f"matched {len(selected)} rows."
                    )
            for binding in selected:
                if binding.field not in fieldnames:
                    continue
                value = extracted_value(binding)
                if value and not row.get(binding.field):
                    row[binding.field] = value
                if binding.filter_field and binding.filter_field in fieldnames and binding.filter_value:
                    row[binding.filter_field] = binding.filter_value

    def process_class(
        context: ET.Element,
        class_node: BindingClass,
        alias: BindingClassAlias,
        dimension_values: Dict[str, str],
        current_row: Optional[Dict[str, str]],
    ) -> None:
        """
        Recursively extract XML values by semantic class context.

        Args:
            context: XML context for the current class.
            class_node: Current binding class.
            dimension_values: Active dimension values inherited from ancestors.
            current_row: Row scope inherited by non-repeated classes.

        Returns:
            None. Extracted rows are appended to `rows`.
        """
        row = current_row
        owns_row = current_row is None or class_node.repeats
        if row is None:
            row = new_row(fieldnames, d_invoice)
            for dimension, value in dimension_values.items():
                if dimension in row:
                    row[dimension] = value

        fill_direct_fields(row, context, class_node, alias)

        repeated_children: List[Tuple[BindingClass, List[Tuple[ET.Element, BindingClassAlias]]]] = []
        for child_class in class_node.children:
            child_contexts = class_contexts(context, alias, child_class)
            if not child_contexts:
                continue
            if child_class.repeats and child_class.dimension:
                repeated_children.append((child_class, child_contexts))
            else:
                child_context, child_alias = child_contexts[0]
                process_class(child_context, child_class, child_alias, dimension_values, row)

        if owns_row and row_has_values(row, dimension_columns):
            rows.append(row)

        for child_class, child_contexts in repeated_children:
            for index, (child_context, child_alias) in enumerate(child_contexts, start=1):
                child_dimensions = dict(dimension_values)
                child_dimensions[child_class.dimension] = str(index)
                child_row = new_row(fieldnames, d_invoice)
                for dimension, value in child_dimensions.items():
                    if dimension in child_row:
                        child_row[dimension] = value
                process_class(child_context, child_class, child_alias, child_dimensions, child_row)

    root_contexts = class_contexts(root, None, class_root)
    if not root_contexts:
        raise ValueError(f"Root Class alias not found for {class_root.semantic_path}")
    root_context, root_alias = root_contexts[0]
    process_class(root_context, class_root, root_alias, {"dInvoice": d_invoice}, None)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    if drop_empty:
        rows, fieldnames = drop_empty_columns(rows, fieldnames)
    with out_csv.open("w", newline="", encoding=encoding) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    metadata_file = metadata_output or out_csv.with_suffix(".json")
    write_csv_metadata(
        metadata_file, out_csv, xml_file, binding_csv, fieldnames, len(rows),
        taxonomy_base, encoding, effective_rows,
    )
    return len(rows), fieldnames


def row_value(row: Dict[str, str], field: str) -> str:
    """
    Return a stripped value from a CSV row field.

    Args:
        row: Input value used by row_value.
        field: Input value used by row_value.

    Returns:
        Result produced by row_value.
    """
    return (row.get(field) or "").strip()


def row_has_dimension(row: Dict[str, str], dimension: str) -> bool:
    """
    Return whether a row has a value for a dimension column.

    Args:
        row: Input value used by row_has_dimension.
        dimension: Input value used by row_has_dimension.

    Returns:
        Result produced by row_has_dimension.
    """
    return bool(row_value(row, dimension))


def first_row_value(rows: List[Dict[str, str]], fields: Iterable[str]) -> str:
    """
    Return the first non-empty value among fields across rows.

    Args:
        rows: Input value used by first_row_value.
        fields: Input value used by first_row_value.

    Returns:
        Result produced by first_row_value.
    """
    for row in rows:
        for field in fields:
            value = row_value(row, field)
            if value:
                return value
    return ""


def write_xml_from_hierarchical_csv(
    input_csv: Path,
    binding_csv: Path,
    out_xml: Path,
    template_csv: Optional[Path],
    encoding: str,
    namespaces: Optional[Dict[str, str]] = None,
    ubl_schema_root: Optional[Path] = None,
    ubl_schema_url: str = "",
    hmd_file: Optional[Path] = None,
) -> int:
    """
    Rebuild XML from hierarchical CSV rows and bindings.

    Args:
        input_csv: Input value used by write_xml_from_hierarchical_csv.
        binding_csv: Input value used by write_xml_from_hierarchical_csv.
        out_xml: Input value used by write_xml_from_hierarchical_csv.
        template_csv: Input value used by write_xml_from_hierarchical_csv.
        encoding: Input value used by write_xml_from_hierarchical_csv.
        namespaces: Input value used by write_xml_from_hierarchical_csv.
        ubl_schema_root: Local UBL XSD root used to derive child element order.
        ubl_schema_url: UBL Invoice schema URL used to derive child element order.

    Returns:
        Result produced by write_xml_from_hierarchical_csv.
    """
    ns = namespaces or UBL_NAMESPACES
    for prefix, uri in ns.items():
        ET.register_namespace(prefix, uri)

    effective_rows = read_effective_binding_rows(binding_csv, encoding, hmd_file)
    binding_layout = build_layout_from_rows(effective_rows)
    if not binding_layout.fieldnames:
        raise ValueError("The syntax binding table has no usable C/A rows.")
    bindings = read_bindings(
        binding_csv,
        encoding,
        binding_layout.path_dimension,
        binding_layout.field_by_semantic_path,
        binding_layout.semantic_path_dimension,
        effective_rows,
    )
    if not bindings:
        raise ValueError("No usable semantic_path/xpath bindings found.")

    template_fields, template_field_dimension = read_template(template_csv, encoding)
    field_dimension = {**binding_layout.field_dimension, **template_field_dimension}

    with input_csv.open(newline="", encoding=encoding) as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("Input CSV has no header.")
        fieldnames = [field.lstrip("\ufeff") for field in reader.fieldnames]
        rows = [{key.lstrip("\ufeff"): (value or "").strip() for key, value in row.items()} for row in reader]

    if not rows:
        raise ValueError("Input CSV has no data rows.")

    validate_hierarchical_row_scopes(rows, fieldnames, field_dimension)

    class_root = build_binding_class_tree(effective_rows)
    if class_root is None:
        raise ValueError("No C rows found in the syntax binding table.")

    def select_alias(class_node: BindingClass, row: Dict[str, str]) -> BindingClassAlias:
        """Select exactly one physical alias from same-occurrence semantic facts."""

        matched: List[BindingClassAlias] = []
        for alias in class_node.aliases:
            if not alias.selector_conditions:
                matched.append(alias)
                continue
            conditions_match = True
            for selector_key, selector_negated in alias.selector_conditions:
                selector_path = class_node.semantic_path + "." + selector_key
                selector_fields = [
                    item.field
                    for item in bindings
                    if item.field
                    and (item.canonical_semantic_path or item.semantic_path) == selector_path
                ]
                present = any(row_value(row, field) for field in dict.fromkeys(selector_fields))
                if present == selector_negated:
                    conditions_match = False
                    break
            if conditions_match:
                matched.append(alias)
        if len(matched) != 1:
            identities = [alias.semantic_path for alias in matched]
            raise ValueError(
                f"Class alias selection for {class_node.semantic_path} matched "
                f"{len(matched)} aliases: {identities}"
            )
        return matched[0]

    root_alias = select_alias(class_root, rows[0])
    root_parts = xml_split_xpath(root_alias.xpath)
    if not root_parts:
        raise ValueError(f"Root Class alias has no element path: {root_alias.xpath}")
    root_step, _ = xml_split_step_predicate(root_parts[-1])
    root = ET.Element(xml_qualify_step(root_step, ns))
    written = 0
    document_currency = first_row_value(rows, ("DocumentCurrencyCode", "documentCurrencyCode", "currencyCode"))
    tax_currency = first_row_value(rows, ("TaxAccountingCurrencyCode", "taxAccountingCurrencyCode", "TaxCurrencyCode"))

    dimension_bindings: Dict[str, List[Binding]] = {}
    for binding in bindings:
        if binding.field not in fieldnames:
            continue
        dimension = binding.dimension or field_dimension.get(binding.field, "")
        if dimension and dimension != "dInvoice" and dimension in fieldnames:
            dimension_bindings.setdefault(dimension, []).append(binding)

    binding_sequence = {
        binding: (
            binding.syntax_sequence
            or binding_layout.syntax_sequence_by_field.get(binding.field, "")
            or binding_layout.syntax_sequence_by_dimension.get(binding.dimension, "")
        )
        for binding in bindings
    }
    context_by_dimension_row: Dict[Tuple[Tuple[str, str], ...], ET.Element] = {}
    context_path_by_dimension_row: Dict[Tuple[Tuple[str, str], ...], str] = {}
    alias_by_dimension_row: Dict[Tuple[Tuple[str, str], ...], BindingClassAlias] = {}
    class_by_dimension = {
        node.dimension: node
        for node in walk_binding_classes(class_root)
        if node.dimension
    }
    repeat_path_by_dimension = {
        dimension: (
            class_by_dimension[dimension].aliases[0].xpath
            if dimension in class_by_dimension
            else binding_layout.dimension_xpath.get(dimension) or infer_repeat_path(group_bindings)
        )
        for dimension, group_bindings in dimension_bindings.items()
    }

    def occurrence_key(dimension: str, row: Dict[str, str]) -> Tuple[Tuple[str, str], ...]:
        """Identify a repeated occurrence within its complete repeated-parent scope."""
        lineage = [*binding_layout.dimension_ancestors.get(dimension, []), dimension]
        return tuple((item, row_value(row, item)) for item in lineage)

    def ensure_repeated_context(dimension: str, row: Dict[str, str]) -> ET.Element:
        """Create a repeated context relative to its nearest repeated parent."""
        key = occurrence_key(dimension, row)
        if key in context_by_dimension_row:
            return context_by_dimension_row[key]

        class_node = class_by_dimension.get(dimension)
        alias = select_alias(class_node, row) if class_node else None
        repeat_path = alias.xpath if alias else repeat_path_by_dimension[dimension]
        ancestors = [
            item
            for item in binding_layout.dimension_ancestors.get(dimension, [])
            if item in repeat_path_by_dimension
        ]
        parent_dimension = ancestors[-1] if ancestors else ""
        if parent_dimension:
            parent_context = ensure_repeated_context(parent_dimension, row)
            parent_key = occurrence_key(parent_dimension, row)
            parent_path = context_path_by_dimension_row[parent_key]
            context_path = relative_xpath(repeat_path, parent_path)
            if context_path.startswith("/"):
                parent_context = root
                context_path = repeat_path
        else:
            parent_context = root
            context_path = repeat_path
        context = create_context(
            parent_context,
            context_path,
            ns,
            document_currency,
            tax_currency,
        )
        context_by_dimension_row[key] = context
        context_path_by_dimension_row[key] = repeat_path
        if alias:
            alias_by_dimension_row[key] = alias
        return context

    def binding_selector_matches(binding: Binding, row: Dict[str, str]) -> bool:
        """Evaluate an Attribute-level selector against the same semantic scope."""

        if not binding.selector_conditions:
            return True
        class_path = (binding.canonical_semantic_path or binding.semantic_path).rsplit(".", 1)[0]
        for selector_key, selector_negated in binding.selector_conditions:
            candidate_fields = [
                item.field
                for item in bindings
                if item.field
                and (
                    item.identifier == binding.identifier + "-1"
                    or (item.canonical_semantic_path or item.semantic_path)
                    == class_path + "." + selector_key
                )
            ]
            present = any(row_value(row, field) for field in dict.fromkeys(candidate_fields))
            if present == selector_negated:
                return False
        return True

    syntax_only_rows = sorted(
        [row for row in effective_rows if first_present(row, ("type",)).upper() == "F"],
        key=lambda row: syntax_sequence_sort_key(
            first_present(row, ("syntax_sequence",)),
            parse_order(first_present(row, ("sequence",))),
        ),
    )
    syntax_only_index = 0

    def emit_syntax_only_before(limit: Optional[Tuple[int, Tuple[str, ...], int]]) -> None:
        """Emit Binding-declared syntax-only nodes in syntax-sequence order."""

        nonlocal syntax_only_index, written
        while syntax_only_index < len(syntax_only_rows):
            row = syntax_only_rows[syntax_only_index]
            key = syntax_sequence_sort_key(
                first_present(row, ("syntax_sequence",)),
                parse_order(first_present(row, ("sequence",))),
            )
            if limit is not None and key > limit:
                break
            syntax_only_index += 1
            xpath = first_present(row, ("syntax_path", "xpath", "source_xpath", "xml_path"))
            default = first_present(row, ("default_value", "default"))
            if not xpath:
                raise ValueError(
                    f"Syntax-only Binding row {first_present(row, ('sequence',))} has no XPath."
                )
            _, attribute = xml_split_terminal_attribute(xpath)
            if attribute:
                written += apply_default_to_existing_contexts(root, xpath, default, ns)
            elif default == "NA":
                create_context(root, xpath, ns, document_currency, tax_currency)
                written += 1
            elif default:
                set_xml_value_with_currency(
                    root, xpath, default, ns, document_currency, tax_currency
                )
                written += 1

    for binding in sorted(
        bindings,
        key=lambda item: syntax_sequence_sort_key(binding_sequence.get(item, ""), item.order),
    ):
        emit_syntax_only_before(
            syntax_sequence_sort_key(binding_sequence.get(binding, ""), binding.order)
        )
        if binding.default_value and not binding.field:
            written += apply_default_to_existing_contexts(
                root,
                binding.xpath,
                binding.default_value,
                ns,
            )
            continue
        if binding.field not in fieldnames:
            continue
        dimension = binding.dimension or field_dimension.get(binding.field, "")
        if dimension and dimension != "dInvoice" and dimension in fieldnames:
            repeat_path = repeat_path_by_dimension.get(dimension, "")
            dimension_rows = [
                row for row in rows
                if row_has_dimension(row, dimension)
                and row_value(row, binding.field)
            ]
            dimension_rows.sort(key=lambda row: int(row_value(row, dimension) or "0"))
            for row in dimension_rows:
                context = ensure_repeated_context(dimension, row)
                key = occurrence_key(dimension, row)
                selected_alias = alias_by_dimension_row.get(key)
                if selected_alias and not binding_applies_to_alias(binding, selected_alias):
                    continue
                selected_path = context_path_by_dimension_row.get(key, repeat_path)
                relative = relative_xpath(binding.xpath, selected_path)
                if relative.startswith("/"):
                    # Some semantic children of a repeated class are stored
                    # elsewhere in the source syntax.  EN 16931 BT-90, for
                    # example, belongs to payment instructions semantically
                    # but is represented under AccountingSupplierParty in
                    # UBL.  Keep such absolute, out-of-context paths rooted at
                    # the document instead of creating a nested Invoice below
                    # the repeated context.
                    transformed = transform_binding_value(
                        row_value(row, binding.field), binding.transformation, reverse=True
                    )
                    write_xpath = tax_total_write_xpath(
                        binding.xpath, binding.transformation, document_currency, tax_currency
                    )
                    if transformed and write_xpath:
                        set_xml_value_with_currency(
                            root, write_xpath, transformed, ns, document_currency, tax_currency
                        )
                        written += 1
                else:
                    transformed = transform_binding_value(
                        row_value(row, binding.field), binding.transformation, reverse=True
                    )
                    write_xpath = tax_total_write_xpath(
                        relative, binding.transformation, document_currency, tax_currency
                    )
                    if transformed and write_xpath:
                        set_relative_xml_value(
                            context, write_xpath, transformed, ns, document_currency, tax_currency
                        )
                        written += 1
            continue

        for row in rows:
            value = row_value(row, binding.field)
            if value and binding_selector_matches(binding, row):
                transformed = transform_binding_value(
                    value, binding.transformation, reverse=True
                )
                write_xpath = tax_total_write_xpath(
                    binding.xpath, binding.transformation, document_currency, tax_currency
                )
                if transformed and write_xpath:
                    set_xml_value_with_currency(
                        root, write_xpath, transformed, ns, document_currency, tax_currency
                    )
                    written += 1
                break

    emit_syntax_only_before(None)

    schema_child_order = load_ubl_child_order(ubl_schema_root, ubl_schema_url)
    if xml_local_name(root.tag) == "Invoice" and "cac" in ns and "cbc" in ns:
        ensure_tax_scheme_defaults(root, ns)
        sort_children_for_ubl_schema(root, schema_child_order)
    elif schema_child_order:
        sort_children_for_ubl_schema(root, schema_child_order)
    indent_xml(root)
    out_xml.parent.mkdir(parents=True, exist_ok=True)
    tree = ET.ElementTree(root)
    tree.write(out_xml, encoding="utf-8", xml_declaration=True)
    return written


def main() -> int:
    """
    Parse command-line arguments, run the script workflow, and return an exit code.

    Args:
        None.

    Returns:
        Process exit status: 0 for success and 1 for handled errors where applicable.
    """
    parser = argparse.ArgumentParser(
        description="Apply UBL Invoice syntax binding between XML and Structured CSV."
    )
    parser.add_argument("input_file", type=Path, help="Input XML file, or input CSV when --reverse is used")
    parser.add_argument("-b", "--binding", required=True, type=Path, help="Syntax binding CSV")
    parser.add_argument("-o", "--output", required=True, type=Path, help="Output hierarchical CSV, or output XML when --reverse is used")
    parser.add_argument("--template-csv", type=Path, help="CSV template defining column order and dimension placement")
    parser.add_argument("--hmd-file", type=Path, help="Canonical HMD used with the 14-column Syntax Binding contract")
    parser.add_argument("--metadata-output", type=Path, help="Output JSON metadata path. Default is OUTPUT_CSV with .json suffix")
    parser.add_argument("--taxonomy-base", type=Path, default=Path("out/taxonomy"), help="Taxonomy output directory referenced by JSON metadata")
    parser.add_argument("--reverse", action="store_true", help="Convert hierarchical CSV back to XML")
    parser.add_argument(
        "--ubl-schema-root",
        type=Path,
        help="Directory containing extracted UBL XSD files used for reverse XML child order",
    )
    parser.add_argument(
        "--ubl-schema-url",
        default="",
        help="URL of the UBL Invoice XSD entry point used for reverse XML child order",
    )
    parser.add_argument(
        "--drop-empty-columns",
        action="store_true",
        help="Drop columns that have no values in the generated Structured CSV.",
    )
    parser.add_argument("--d-invoice", default="1", help="dInvoice value written to output rows")
    parser.add_argument("-e", "--encoding", default="utf-8-sig", help="CSV encoding")
    args = parser.parse_args()

    try:
        if args.reverse:
            count = write_xml_from_hierarchical_csv(
                args.input_file,
                args.binding,
                args.output,
                args.template_csv,
                args.encoding,
                None,
                args.ubl_schema_root,
                args.ubl_schema_url,
                args.hmd_file,
            )
            print(f"Wrote XML with {count} value(s) to {args.output}")
            return 0
        count, fields = write_hierarchical_csv(
            args.input_file,
            args.binding,
            args.output,
            args.template_csv,
            args.metadata_output,
            args.taxonomy_base,
            args.encoding,
            args.d_invoice,
            args.drop_empty_columns,
            args.hmd_file,
        )
    except Exception as exc:
        print(f"syntax_binding.py: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {count} hierarchical row(s), {len(fields)} column(s) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
