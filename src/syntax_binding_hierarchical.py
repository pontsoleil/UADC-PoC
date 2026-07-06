#!/usr/bin/env python3
# coding: utf-8
"""
Convert XML to dimension-based hierarchical CSV using a syntax binding CSV.

This format follows syntax_binding_revised_package/invoice.csv: hierarchy is
represented by dXXX dimension columns, while facts remain in wide CSV columns.
The binding CSV provides semantic_path,xpath rows. A template CSV may be used to
fix the output column order and to infer that root-level semantic fields such as
paymentDueDate belong to a dPayment row.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from syntax_binding import collect_namespaces, find_nodes, get_value


UBL_NAMESPACES = {
    "": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}

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
class Binding:
    order: int
    semantic_path: str
    xpath: str
    root: str
    dimension: str
    filter_field: str
    filter_value: str
    field: str


@dataclass(frozen=True)
class LhmLayout:
    fieldnames: List[str]
    field_dimension: Dict[str, str]
    semantic_path_dimension: Dict[str, str]
    dimension_xpath: Dict[str, str]
    path_dimension: Dict[str, str]
    dimension_ancestors: Dict[str, List[str]]
    dimension_repeats: Dict[str, bool]
    field_by_semantic_path: Dict[str, str]
    syntax_sequence_by_field: Dict[str, int]
    syntax_sequence_by_dimension: Dict[str, int]


def first_present(row: Dict[str, str], names: Iterable[str]) -> str:
    for name in names:
        value = row.get(name)
        if value:
            return value.strip()
    return ""


def parse_order(value: str, fallback: int = 0) -> int:
    value = (value or "").strip()
    if not value:
        return fallback
    try:
        return int(value)
    except ValueError:
        return fallback


def upper_camel(value: str) -> str:
    value = re.sub(r"[^0-9A-Za-z_]+", "_", value or "").strip("_")
    if not value:
        return ""
    return value[0].upper() + value[1:]


def dimension_name(element: str) -> str:
    return "d" + upper_camel(element)


def multiplicity_repeats(multiplicity: str) -> bool:
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


def read_lhm_layout(lhm_csv: Optional[Path], encoding: str) -> LhmLayout:
    if not lhm_csv:
        return LhmLayout([], {}, {}, {}, {}, {}, {}, {}, {}, {})
    with lhm_csv.open(newline="", encoding=encoding) as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("LHM CSV has no header.")
        rows = [{key.lstrip("\ufeff"): (value or "").strip() for key, value in row.items()} for row in reader]

    dimensions: List[str] = []
    fields: List[str] = []
    field_dimension: Dict[str, str] = {}
    semantic_path_dimension: Dict[str, str] = {}
    dimension_xpath: Dict[str, str] = {}
    path_dimension: Dict[str, str] = {}
    dimension_ancestors: Dict[str, List[str]] = {}
    dimension_repeats: Dict[str, bool] = {}
    field_by_semantic_path: Dict[str, str] = {}
    syntax_sequence_by_field: Dict[str, int] = {}
    syntax_sequence_by_dimension: Dict[str, int] = {}

    for row in rows:
        if first_present(row, ("type", "kind")).upper().startswith("C"):
            semantic_path = first_present(row, ("semantic_path", "path"))
            element = first_present(row, ("element", "name"))
            lhm_level = first_present(row, ("lhm_level",))
            repeats = multiplicity_repeats(first_present(row, ("multiplicity", "cardinality")))
            dim = dimension_name(element)
            if semantic_path and dim and (semantic_path == "$.invoice" or lhm_level):
                path_dimension[semantic_path] = dim
                semantic_path_dimension[semantic_path] = dim
                if dim not in dimensions:
                    dimensions.append(dim)
                xpath = first_present(row, ("xpath", "source_xpath", "xml_path"))
                if xpath:
                    dimension_xpath[dim] = xpath
                dimension_repeats[dim] = repeats
                syntax_order = parse_order(first_present(row, ("syntax_sequence",)), 0)
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
        semantic_path = first_present(row, ("semantic_path", "path"))
        element = first_present(row, ("element", "name"))
        if not semantic_path or not element:
            continue
        field_by_semantic_path[semantic_path] = element
        syntax_order = parse_order(first_present(row, ("syntax_sequence",)), 0)
        if syntax_order:
            syntax_sequence_by_field[element] = syntax_order
        if element not in fields:
            fields.append(element)
        parent_path = semantic_path.rsplit(".", 1)[0] if "." in semantic_path else ""
        parent_dimension = nearest_dimension(parent_path)
        if parent_dimension:
            field_dimension[element] = parent_dimension
            semantic_path_dimension[semantic_path] = parent_dimension

    return LhmLayout(
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
    return bool(re.fullmatch(r"d[A-Z][A-Za-z0-9_]*", name or ""))


def parse_semantic_path(
    semantic_path: str,
    xpath: str,
    order: int,
    path_dimension: Optional[Dict[str, str]] = None,
    field_by_semantic_path: Optional[Dict[str, str]] = None,
    semantic_path_dimension: Optional[Dict[str, str]] = None,
) -> Optional[Binding]:
    def nearest_dimension(semantic_path_value: str) -> str:
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

    if semantic_path.startswith("const:"):
        return None
    root_match = re.fullmatch(r"\$\.([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)", semantic_path)
    if root_match:
        root, field = root_match.groups()
        field = (field_by_semantic_path or {}).get(semantic_path, field)
        dimension = (semantic_path_dimension or {}).get(semantic_path) or (path_dimension or {}).get(f"$.{root}", "")
        return Binding(order, semantic_path, xpath, root, dimension, "", "", field)

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
        return Binding(order, semantic_path, xpath, root, dimension, filter_field or "", filter_value, field)
    generic_match = re.fullmatch(r"\$\.([A-Za-z_][A-Za-z0-9_]*)(?:\..+)?\.([A-Za-z_][A-Za-z0-9_]*)", semantic_path)
    if generic_match:
        root, field = generic_match.groups()
        field = (field_by_semantic_path or {}).get(semantic_path, field)
        parent_path = semantic_path.rsplit(".", 1)[0]
        dimension = (semantic_path_dimension or {}).get(semantic_path) or nearest_dimension(parent_path)
        return Binding(order, semantic_path, xpath, root, dimension, "", "", field)
    return None


def read_bindings(
    binding_csv: Path,
    encoding: str,
    path_dimension: Optional[Dict[str, str]] = None,
    field_by_semantic_path: Optional[Dict[str, str]] = None,
    semantic_path_dimension: Optional[Dict[str, str]] = None,
) -> List[Binding]:
    with binding_csv.open(newline="", encoding=encoding) as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("Binding CSV has no header.")
        rows = [{key.lstrip("\ufeff"): (value or "").strip() for key, value in row.items()} for row in reader]

    bindings: List[Binding] = []
    for fallback_order, row in enumerate(rows, start=1):
        semantic_path = first_present(row, ("semantic_path", "path"))
        xpath = first_present(row, ("xpath", "source_xpath", "xml_path"))
        if not semantic_path or not xpath:
            continue
        order = parse_order(first_present(row, ("syntax_sequence", "sequence")), fallback_order)
        binding = parse_semantic_path(
            semantic_path,
            xpath,
            order,
            path_dimension,
            field_by_semantic_path,
            semantic_path_dimension,
        )
        if binding:
            bindings.append(binding)
    return bindings


def xpath_element_path(xpath: str) -> str:
    xpath = xpath.strip()
    element_xpath, _ = split_terminal_attribute(xpath)
    return element_xpath


def xpath_parent(xpath: str) -> str:
    parts = split_xpath_steps(xpath_element_path(xpath))
    if len(parts) <= 1:
        return "/" + "/".join(parts)
    return "/" + "/".join(parts[:-1])


def common_xpath_prefix(xpaths: List[str]) -> str:
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
    if len(bindings) == 1:
        return xpath_parent(bindings[0].xpath)
    common = common_xpath_prefix([binding.xpath for binding in bindings])
    if any(common == xpath_element_path(binding.xpath) for binding in bindings):
        return xpath_parent(common)
    return common


def relative_xpath(full_xpath: str, context_xpath: str) -> str:
    full = xpath_element_path(full_xpath) if "/@" not in full_xpath else full_xpath
    context = context_xpath.rstrip("/")
    if full == context:
        return "."
    if full.startswith(context + "/"):
        return full[len(context) + 1 :]
    return full


def qname(name: str, namespaces: Dict[str, str]) -> str:
    if ":" in name:
        prefix, local = name.split(":", 1)
        uri = namespaces.get(prefix)
        return f"{{{uri}}}{local}" if uri else name
    uri = namespaces.get("")
    return f"{{{uri}}}{name}" if uri else name


def element_local_name(tag: str) -> str:
    if tag.startswith("{"):
        return tag.rsplit("}", 1)[-1]
    return tag.split(":", 1)[-1]


def step_base_and_predicate(step: str) -> Tuple[str, str]:
    if "[" not in step:
        return step, ""
    base, predicate = step.split("[", 1)
    return base, predicate.rsplit("]", 1)[0].strip()


def predicate_child_value(predicate: str) -> Tuple[str, str, str]:
    path_pattern = r"([A-Za-z_][\w.-]*:[A-Za-z_][\w.-]*(?:/(?:@[A-Za-z_][\w.-]*|[A-Za-z_][\w.-]*:[A-Za-z_][\w.-]*))*)"
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


def child_satisfies_predicate(child: ET.Element, predicate: str, namespaces: Dict[str, str]) -> bool:
    predicate_name, operator, predicate_value = predicate_child_value(predicate)
    if not predicate_name:
        return True
    actual_value = find_predicate_value(child, predicate_name, namespaces)
    if operator == "=":
        return actual_value == predicate_value
    if operator == "!=":
        return bool(actual_value) and actual_value != predicate_value
    return True


def find_or_create_child(parent: ET.Element, step: str, namespaces: Dict[str, str], force_new: bool = False) -> ET.Element:
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
    xpath = (xpath or "").strip()
    xpath, attribute = split_terminal_attribute(xpath)
    parts = split_xpath_steps(xpath)
    return parts, attribute


def ensure_path(root: ET.Element, xpath: str, namespaces: Dict[str, str], force_new_leaf: bool = False) -> Tuple[ET.Element, str]:
    parts, attribute = split_xml_path(xpath)
    if parts and element_local_name(parts[0]) == element_local_name(root.tag):
        parts = parts[1:]
    current = root
    for index, part in enumerate(parts):
        current = find_or_create_child(current, part, namespaces, force_new_leaf and index == len(parts) - 1)
    return current, attribute


def set_xml_value(root: ET.Element, xpath: str, value: str, namespaces: Dict[str, str]) -> None:
    if not value:
        return
    element, attribute = ensure_path(root, xpath, namespaces)
    if attribute:
        element.set(attribute, value)
    else:
        element.text = value


def is_amount_xpath(xpath: str) -> bool:
    parts, attribute = split_xml_path(xpath)
    if attribute:
        return False
    return bool(parts) and element_local_name(parts[-1]).endswith("Amount")


def apply_currency_attribute(element: ET.Element, xpath: str, document_currency: str, tax_currency: str) -> None:
    if not is_amount_xpath(xpath) or element.get("currencyID"):
        return
    currency = tax_currency if "TaxCurrencyCode" in xpath else document_currency
    if currency:
        element.set("currencyID", currency)


def resolve_currency_references(xpath: str, document_currency: str, tax_currency: str) -> str:
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
    if not value:
        return
    if xpath == ".":
        context.text = value
        apply_currency_attribute(context, xpath, document_currency, tax_currency)
        return
    resolved_xpath = resolve_currency_references(xpath, document_currency, tax_currency)
    element, attribute = ensure_path(context, resolved_xpath, namespaces)
    if attribute:
        element.set(attribute, value)
    else:
        element.text = value
        apply_currency_attribute(element, resolved_xpath, document_currency, tax_currency)


def child_order_for(element: ET.Element) -> Dict[str, int]:
    local = element_local_name(element.tag)
    order = UBL_CHILD_ORDER.get(local)
    if order is None and local.endswith("Address"):
        order = UBL_CHILD_ORDER["Address"]
    if order is None and local.endswith("DocumentReference"):
        order = UBL_CHILD_ORDER["DocumentReference"]
    if order is None and local.endswith("MonetaryTotal"):
        order = UBL_CHILD_ORDER["MonetaryTotal"]
    return {name: index for index, name in enumerate(order or [])}


def sort_children_for_ubl_schema(element: ET.Element) -> None:
    for child in list(element):
        sort_children_for_ubl_schema(child)
    order = child_order_for(element)
    if not order:
        return
    children = list(element)
    if len(children) < 2:
        return
    original_position = {id(child): index for index, child in enumerate(children)}
    children.sort(key=lambda child: (order.get(element_local_name(child.tag), 10_000), original_position[id(child)]))
    element[:] = children


def find_child_by_local_name(element: ET.Element, local_name: str) -> Optional[ET.Element]:
    for child in list(element):
        if element_local_name(child.tag) == local_name:
            return child
    return None


def ensure_tax_scheme_defaults(root: ET.Element, namespaces: Dict[str, str]) -> None:
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
    row = {field: "" for field in fieldnames}
    if "dInvoice" in row:
        row["dInvoice"] = d_invoice
    return row


def row_has_values(row: Dict[str, str], dimension_columns: List[str]) -> bool:
    return any(value for field, value in row.items() if field not in dimension_columns)


def drop_empty_columns(rows: List[Dict[str, str]], fieldnames: List[str]) -> Tuple[List[Dict[str, str]], List[str]]:
    used = {
        field
        for field in fieldnames
        if any((row.get(field) or "").strip() for row in rows)
    }
    revised_fields = [field for field in fieldnames if field in used]
    revised_rows = [{field: row.get(field, "") for field in revised_fields} for row in rows]
    return revised_rows, revised_fields


def add_derived_fieldnames(fieldnames: List[str], bindings: List[Binding]) -> List[str]:
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
    if not path:
        return ""
    try:
        return Path(os.path.relpath(path.resolve(), metadata_file.parent.resolve())).as_posix()
    except OSError:
        return path.as_posix()


def latest_file(directory: Path, pattern: str) -> Optional[Path]:
    files = sorted(directory.glob(pattern))
    return files[-1] if files else None


def taxonomy_entrypoints(taxonomy_base: Optional[Path], metadata_file: Path) -> Dict[str, str]:
    if not taxonomy_base:
        return {}
    return {
        "xbrlCsvSchema": relative_metadata_path(latest_file(taxonomy_base / "plt", "plt-oim-*.xsd"), metadata_file),
        "definitionLinkbase": relative_metadata_path(latest_file(taxonomy_base / "plt", "plt-def-*.xml"), metadata_file),
        "moduleSchema": relative_metadata_path(latest_file(taxonomy_base / "en16931", "en16931-*.xsd"), metadata_file),
    }


def taxonomy_version(entrypoints: Dict[str, str]) -> str:
    for value in entrypoints.values():
        match = re.search(r"(\d{4}-\d{2}-\d{2})", value or "")
        if match:
            return match.group(1)
    return "2026-07-05"


def xbrl_csv_column_definition(column: Dict[str, str]) -> Dict[str, Dict[str, str]]:
    dimensions = {"concept": column["taxonomyConcept"]}
    datatype = (column.get("datatype") or "").lower()
    if "amount" in datatype or column.get("name", "").endswith("Amount"):
        dimensions["unit"] = "iso4217:JPY"
    return {"dimensions": dimensions}


def lhm_column_metadata(lhm_csv: Optional[Path], encoding: str) -> Dict[str, Dict[str, str]]:
    if not lhm_csv:
        return {}
    with lhm_csv.open(newline="", encoding=encoding) as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return {}
        rows = [{key.lstrip("\ufeff"): (value or "").strip() for key, value in row.items()} for row in reader]

    metadata: Dict[str, Dict[str, str]] = {}
    for row in rows:
        row_type = first_present(row, ("type", "kind")).upper()
        element = first_present(row, ("element", "name"))
        module = first_present(row, ("module",)) or "en16931"
        if not element:
            continue
        common = {
            "lhmId": first_present(row, ("id",)),
            "lhmName": first_present(row, ("name", "business_term")),
            "semanticPath": first_present(row, ("semantic_path", "path")),
            "xpath": first_present(row, ("xpath", "source_xpath", "xml_path")),
            "datatype": first_present(row, ("datatype", "semantic_data_type")),
            "multiplicity": first_present(row, ("multiplicity", "cardinality")),
            "lhmLevel": first_present(row, ("lhm_level",)),
            "classTerm": first_present(row, ("class_term",)),
            "module": module,
        }
        if row_type.startswith("C") or row_type.startswith("G"):
            dimension = dimension_name(element)
            metadata[dimension] = {
                **common,
                "kind": "dimension",
                "taxonomyConcept": f"plt:d_{module}_{element}",
                "primaryItem": f"plt:p_{module}_{element}",
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
    lhm_csv: Optional[Path],
    fieldnames: List[str],
    row_count: int,
    taxonomy_base: Optional[Path],
    encoding: str,
) -> None:
    columns = lhm_column_metadata(lhm_csv, encoding)
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
        entrypoints.get("moduleSchema", ""),
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
    lhm_csv: Optional[Path],
    metadata_output: Optional[Path],
    taxonomy_base: Optional[Path],
    encoding: str,
    d_invoice: str = "1",
    drop_empty: bool = False,
) -> Tuple[int, List[str]]:
    namespaces = collect_namespaces(xml_file)
    root = ET.parse(xml_file).getroot()
    lhm_layout = read_lhm_layout(lhm_csv, encoding)
    bindings = read_bindings(
        binding_csv,
        encoding,
        lhm_layout.path_dimension,
        lhm_layout.field_by_semantic_path,
        lhm_layout.semantic_path_dimension,
    )
    if not bindings:
        raise ValueError("No usable semantic_path/xpath bindings found.")

    template_fields, field_dimension = read_template(template_csv, encoding)
    if lhm_layout.fieldnames:
        fieldnames = lhm_layout.fieldnames
        field_dimension = {**lhm_layout.field_dimension, **field_dimension}
    else:
        fieldnames = add_derived_fieldnames(template_fields, bindings)
    dimension_columns = [name for name in fieldnames if is_dimension_column(name)]

    rows: List[Dict[str, str]] = []
    root_row = new_row(fieldnames, d_invoice)
    dimension_rows: Dict[Tuple[str, str, str], Dict[str, str]] = {}
    dimension_counts: Dict[str, int] = {}

    def get_dimension_row(dimension: str, discriminator: str) -> Dict[str, str]:
        key = (dimension, discriminator, d_invoice)
        if key not in dimension_rows:
            dimension_counts[dimension] = dimension_counts.get(dimension, 0) + 1
            row = new_row(fieldnames, d_invoice)
            for ancestor in lhm_layout.dimension_ancestors.get(dimension, []):
                if ancestor in row and not row[ancestor]:
                    row[ancestor] = "1"
            row[dimension] = str(dimension_counts[dimension])
            dimension_rows[key] = row
            rows.append(row)
        return dimension_rows[key]

    repeated_groups: Dict[str, List[Binding]] = {}
    for binding in bindings:
        if binding.dimension and binding.dimension != "dInvoice" and not binding.filter_field:
            repeated_groups.setdefault(binding.dimension, []).append(binding)

    repeated_bindings = {binding for group in repeated_groups.values() for binding in group}
    for binding in bindings:
        if binding in repeated_bindings:
            continue
        if binding.field not in fieldnames:
            continue
        value = get_value(root, binding.xpath, namespaces)
        if not value:
            continue
        if binding.dimension and binding.filter_field:
            row = get_dimension_row(binding.dimension, f"{binding.filter_field}={binding.filter_value}")
            if binding.filter_field in fieldnames:
                row[binding.filter_field] = binding.filter_value
            row[binding.field] = value
            continue
        hinted_dimension = field_dimension.get(binding.field, "")
        if hinted_dimension and hinted_dimension != "dInvoice":
            row = get_dimension_row(hinted_dimension, "template")
            row[binding.field] = value
            continue
        if not root_row.get(binding.field):
            root_row[binding.field] = value

    if row_has_values(root_row, dimension_columns):
        rows.insert(0, root_row)

    for dimension, group_bindings in repeated_groups.items():
        if dimension not in fieldnames:
            continue
        repeat_path = lhm_layout.dimension_xpath.get(dimension) or infer_repeat_path(group_bindings)
        contexts = find_nodes(root, repeat_path, namespaces)
        for index, context in enumerate(contexts, start=1):
            row = new_row(fieldnames, d_invoice)
            for ancestor in lhm_layout.dimension_ancestors.get(dimension, []):
                if ancestor in row and not row[ancestor]:
                    row[ancestor] = "1"
            row[dimension] = str(index)
            for binding in group_bindings:
                if binding.field not in fieldnames:
                    continue
                rel = relative_xpath(binding.xpath, repeat_path)
                row[binding.field] = get_value(context, rel, namespaces)
            if row_has_values(row, dimension_columns):
                rows.append(row)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    if drop_empty:
        rows, fieldnames = drop_empty_columns(rows, fieldnames)
    with out_csv.open("w", newline="", encoding=encoding) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    metadata_file = metadata_output or out_csv.with_suffix(out_csv.suffix + ".metadata.json")
    write_csv_metadata(metadata_file, out_csv, xml_file, binding_csv, lhm_csv, fieldnames, len(rows), taxonomy_base, encoding)
    return len(rows), fieldnames


def row_value(row: Dict[str, str], field: str) -> str:
    return (row.get(field) or "").strip()


def row_has_dimension(row: Dict[str, str], dimension: str) -> bool:
    return bool(row_value(row, dimension))


def first_row_value(rows: List[Dict[str, str]], fields: Iterable[str]) -> str:
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
    lhm_csv: Optional[Path],
    encoding: str,
    namespaces: Optional[Dict[str, str]] = None,
) -> int:
    ns = namespaces or UBL_NAMESPACES
    for prefix, uri in ns.items():
        ET.register_namespace(prefix, uri)

    lhm_layout = read_lhm_layout(lhm_csv, encoding)
    bindings = read_bindings(
        binding_csv,
        encoding,
        lhm_layout.path_dimension,
        lhm_layout.field_by_semantic_path,
        lhm_layout.semantic_path_dimension,
    )
    if not bindings:
        raise ValueError("No usable semantic_path/xpath bindings found.")

    template_fields, template_field_dimension = read_template(template_csv, encoding)
    field_dimension = {**lhm_layout.field_dimension, **template_field_dimension}

    with input_csv.open(newline="", encoding=encoding) as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("Input CSV has no header.")
        fieldnames = [field.lstrip("\ufeff") for field in reader.fieldnames]
        rows = [{key.lstrip("\ufeff"): (value or "").strip() for key, value in row.items()} for row in reader]

    if not rows:
        raise ValueError("Input CSV has no data rows.")

    root = ET.Element(qname("Invoice", ns))
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

    binding_order = {
        binding: (
            lhm_layout.syntax_sequence_by_field.get(binding.field)
            or lhm_layout.syntax_sequence_by_dimension.get(binding.dimension)
            or binding.order
        )
        for binding in bindings
    }
    context_by_dimension_row: Dict[Tuple[str, str], ET.Element] = {}
    repeat_path_by_dimension = {
        dimension: lhm_layout.dimension_xpath.get(dimension) or infer_repeat_path(group_bindings)
        for dimension, group_bindings in dimension_bindings.items()
    }

    for binding in sorted(bindings, key=lambda item: binding_order.get(item, item.order)):
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
                key = (dimension, row_value(row, dimension))
                if key not in context_by_dimension_row:
                    context_by_dimension_row[key] = create_context(root, repeat_path, ns, document_currency, tax_currency)
                relative = relative_xpath(binding.xpath, repeat_path)
                set_relative_xml_value(
                    context_by_dimension_row[key],
                    relative,
                    row_value(row, binding.field),
                    ns,
                    document_currency,
                    tax_currency,
                )
                written += 1
            continue

        for row in rows:
            value = row_value(row, binding.field)
            if value:
                set_xml_value_with_currency(root, binding.xpath, value, ns, document_currency, tax_currency)
                written += 1
                break

    ensure_tax_scheme_defaults(root, ns)
    sort_children_for_ubl_schema(root)
    indent_xml(root)
    out_xml.parent.mkdir(parents=True, exist_ok=True)
    tree = ET.ElementTree(root)
    tree.write(out_xml, encoding="utf-8", xml_declaration=True)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert XML to dXXX dimension-based hierarchical CSV using syntax bindings."
    )
    parser.add_argument("input_file", type=Path, help="Input XML file, or input CSV when --reverse is used")
    parser.add_argument("-b", "--binding", required=True, type=Path, help="Syntax binding CSV")
    parser.add_argument("-o", "--output", required=True, type=Path, help="Output hierarchical CSV, or output XML when --reverse is used")
    parser.add_argument("--template-csv", type=Path, help="CSV template defining column order and dimension placement")
    parser.add_argument("--lhm-csv", type=Path, help="LHM CSV defining BG dimension columns and BT value columns")
    parser.add_argument("--metadata-output", type=Path, help="Output JSON metadata path. Default is OUTPUT_CSV.metadata.json")
    parser.add_argument("--taxonomy-base", type=Path, default=Path("out/taxonomy"), help="Taxonomy output directory referenced by JSON metadata")
    parser.add_argument("--reverse", action="store_true", help="Convert hierarchical CSV back to XML")
    parser.add_argument(
        "--drop-empty-columns",
        action="store_true",
        help="Drop columns that have no values, matching the Japan_core xml2tidy/fillTable behavior.",
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
                args.lhm_csv,
                args.encoding,
            )
            print(f"Wrote XML with {count} value(s) to {args.output}")
            return 0
        count, fields = write_hierarchical_csv(
            args.input_file,
            args.binding,
            args.output,
            args.template_csv,
            args.lhm_csv,
            args.metadata_output,
            args.taxonomy_base,
            args.encoding,
            args.d_invoice,
            args.drop_empty_columns,
        )
    except Exception as exc:
        print(f"syntax_binding_hierarchical.py: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {count} hierarchical row(s), {len(fields)} column(s) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
