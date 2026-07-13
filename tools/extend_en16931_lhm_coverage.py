#!/usr/bin/env python3
# coding: utf-8
"""
Add currently missing EN 16931-1 BG/BT identifiers to the PoC LHM CSV.

The rows are intentionally data-driven so coverage additions remain
reviewable while the semantic_path values can be regenerated separately.

Creation Date: 2026-07-05
Last Modified: 2026-07-13

Copyright 2026 Sambuichi Professional Engineers Office
Designed by SAMBUICHI, Nobuyuki
Produced by ChatGPT & Codex, edited by  SAMBUICHI, Nobuyuki
MIT License

(c) 2026 Sambuichi Professional Engineers Office

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
CC-BY-NC
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, Iterable, List


FIELDNAMES = [
    "sequence",
    "syntax_sequence",
    "level",
    "type",
    "identifier",
    "name",
    "datatype",
    "multiplicity",
    "domain_name",
    "definition",
    "module",
    "class_term",
    "id",
    "path",
    "semantic_path",
    "label_local",
    "definition_local",
    "element",
    "xpath",
]


def class_row(identifier: str, name: str, multiplicity: str, path: str, xpath: str) -> Dict[str, str]:
    return row(identifier, name, "", multiplicity, path, xpath, "C")


def attr_row(identifier: str, name: str, datatype: str, multiplicity: str, path: str, xpath: str) -> Dict[str, str]:
    return row(identifier, name, datatype, multiplicity, path, xpath, "A")


def row(
    identifier: str,
    name: str,
    datatype: str,
    multiplicity: str,
    path: str,
    xpath: str,
    row_type: str,
) -> Dict[str, str]:
    return {
        "sequence": "",
        "syntax_sequence": "",
        "level": str(max(0, len([part for part in path.split("/") if part]) - 1)),
        "type": row_type,
        "identifier": "",
        "name": name,
        "datatype": datatype,
        "multiplicity": multiplicity,
        "domain_name": "",
        "definition": "",
        "module": "en16931",
        "class_term": "",
        "id": identifier,
        "path": path,
        "semantic_path": "",
        "label_local": "",
        "definition_local": "",
        "element": "",
        "xpath": xpath,
    }


ROWS = [
    # Header and references
    attr_row("BT-7", "Value added tax point date", "Date", "0..1", "/BG-ROOT/BT-7", "/Invoice/cbc:TaxPointDate"),
    attr_row("BT-8", "Value added tax point date code", "Code", "0..1", "/BG-ROOT/BT-8", "/Invoice/cac:InvoicePeriod/cbc:DescriptionCode"),
    attr_row("BT-11", "Project reference", "Identifier", "0..1", "/BG-ROOT/BT-11", "/Invoice/cac:ProjectReference/cbc:ID"),
    attr_row("BT-12", "Contract reference", "Identifier", "0..1", "/BG-ROOT/BT-12", "/Invoice/cac:ContractDocumentReference/cbc:ID"),
    attr_row("BT-13", "Purchase order reference", "Identifier", "0..1", "/BG-ROOT/BT-13", "/Invoice/cac:OrderReference/cbc:ID"),
    attr_row("BT-14", "Sales order reference", "Identifier", "0..1", "/BG-ROOT/BT-14", "/Invoice/cac:OrderReference/cbc:SalesOrderID"),
    attr_row("BT-15", "Receiving advice reference", "Identifier", "0..1", "/BG-ROOT/BT-15", "/Invoice/cac:ReceiptDocumentReference/cbc:ID"),
    attr_row("BT-16", "Despatch advice reference", "Identifier", "0..1", "/BG-ROOT/BT-16", "/Invoice/cac:DespatchDocumentReference/cbc:ID"),
    attr_row("BT-17", "Tender or lot reference", "Identifier", "0..1", "/BG-ROOT/BT-17", "/Invoice/cac:OriginatorDocumentReference/cbc:ID"),
    attr_row("BT-18", "Invoiced object identifier", "Identifier", "0..1", "/BG-ROOT/BT-18", "/Invoice/cac:AdditionalDocumentReference[cbc:DocumentTypeCode='130']/cbc:ID"),
    attr_row("BT-19", "Buyer accounting reference", "Text", "0..1", "/BG-ROOT/BT-19", "/Invoice/cbc:AccountingCost"),
    class_row("BG-2", "Process control", "1..1", "/BG-ROOT/BG-2", "/Invoice"),
    class_row("BG-1", "Invoice note", "0..*", "/BG-ROOT/BG-1", "/Invoice/cbc:Note"),
    attr_row("BT-21", "Invoice note subject code", "Code", "0..1", "/BG-ROOT/BG-1/BT-21", "/Invoice/cbc:Note/@subjectCode"),
    attr_row("BT-22", "Invoice note", "Text", "1..1", "/BG-ROOT/BG-1/BT-22", "/Invoice/cbc:Note"),

    # Seller
    attr_row("BT-32", "Seller tax registration identifier", "Identifier", "0..1", "/BG-ROOT/BG-4/BT-32", "/Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID!='VAT']/cbc:CompanyID"),
    attr_row("BT-33", "Seller additional legal information", "Text", "0..1", "/BG-ROOT/BG-4/BT-33", "/Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyLegalForm"),
    attr_row("BT-34", "Seller electronic address", "Identifier", "0..1", "/BG-ROOT/BG-4/BT-34", "/Invoice/cac:AccountingSupplierParty/cac:Party/cbc:EndpointID"),
    attr_row("BT-36", "Seller address line 2", "Text", "0..1", "/BG-ROOT/BG-4/BG-5/BT-36", "/Invoice/cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cbc:AdditionalStreetName"),
    attr_row("BT-162", "Seller address line 3", "Text", "0..1", "/BG-ROOT/BG-4/BG-5/BT-162", "/Invoice/cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cac:AddressLine/cbc:Line"),
    attr_row("BT-39", "Seller country subdivision", "Text", "0..1", "/BG-ROOT/BG-4/BG-5/BT-39", "/Invoice/cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cbc:CountrySubentity"),
    class_row("BG-6", "Seller contact", "0..1", "/BG-ROOT/BG-4/BG-6", "/Invoice/cac:AccountingSupplierParty/cac:Party/cac:Contact"),
    attr_row("BT-41", "Seller contact point", "Text", "0..1", "/BG-ROOT/BG-4/BG-6/BT-41", "/Invoice/cac:AccountingSupplierParty/cac:Party/cac:Contact/cbc:Name"),
    attr_row("BT-42", "Seller contact telephone number", "Text", "0..1", "/BG-ROOT/BG-4/BG-6/BT-42", "/Invoice/cac:AccountingSupplierParty/cac:Party/cac:Contact/cbc:Telephone"),
    attr_row("BT-43", "Seller contact email address", "Text", "0..1", "/BG-ROOT/BG-4/BG-6/BT-43", "/Invoice/cac:AccountingSupplierParty/cac:Party/cac:Contact/cbc:ElectronicMail"),

    # Buyer
    attr_row("BT-49", "Buyer electronic address", "Identifier", "0..1", "/BG-ROOT/BG-7/BT-49", "/Invoice/cac:AccountingCustomerParty/cac:Party/cbc:EndpointID"),
    attr_row("BT-51", "Buyer address line 2", "Text", "0..1", "/BG-ROOT/BG-7/BG-8/BT-51", "/Invoice/cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cbc:AdditionalStreetName"),
    attr_row("BT-163", "Buyer address line 3", "Text", "0..1", "/BG-ROOT/BG-7/BG-8/BT-163", "/Invoice/cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cac:AddressLine/cbc:Line"),
    attr_row("BT-54", "Buyer country subdivision", "Text", "0..1", "/BG-ROOT/BG-7/BG-8/BT-54", "/Invoice/cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cbc:CountrySubentity"),
    class_row("BG-9", "Buyer contact", "0..1", "/BG-ROOT/BG-7/BG-9", "/Invoice/cac:AccountingCustomerParty/cac:Party/cac:Contact"),
    attr_row("BT-56", "Buyer contact point", "Text", "0..1", "/BG-ROOT/BG-7/BG-9/BT-56", "/Invoice/cac:AccountingCustomerParty/cac:Party/cac:Contact/cbc:Name"),
    attr_row("BT-57", "Buyer contact telephone number", "Text", "0..1", "/BG-ROOT/BG-7/BG-9/BT-57", "/Invoice/cac:AccountingCustomerParty/cac:Party/cac:Contact/cbc:Telephone"),
    attr_row("BT-58", "Buyer contact email address", "Text", "0..1", "/BG-ROOT/BG-7/BG-9/BT-58", "/Invoice/cac:AccountingCustomerParty/cac:Party/cac:Contact/cbc:ElectronicMail"),

    # Payee and tax representative
    class_row("BG-10", "Payee", "0..1", "/BG-ROOT/BG-10", "/Invoice/cac:PayeeParty"),
    attr_row("BT-59", "Payee name", "Text", "1..1", "/BG-ROOT/BG-10/BT-59", "/Invoice/cac:PayeeParty/cac:PartyName/cbc:Name"),
    attr_row("BT-60", "Payee identifier", "Identifier", "0..1", "/BG-ROOT/BG-10/BT-60", "/Invoice/cac:PayeeParty/cac:PartyIdentification/cbc:ID"),
    attr_row("BT-61", "Payee legal registration identifier", "Identifier", "0..1", "/BG-ROOT/BG-10/BT-61", "/Invoice/cac:PayeeParty/cac:PartyLegalEntity/cbc:CompanyID"),
    class_row("BG-11", "Seller tax representative party", "0..1", "/BG-ROOT/BG-11", "/Invoice/cac:TaxRepresentativeParty"),
    attr_row("BT-62", "Seller tax representative name", "Text", "1..1", "/BG-ROOT/BG-11/BT-62", "/Invoice/cac:TaxRepresentativeParty/cac:PartyName/cbc:Name"),
    attr_row("BT-63", "Seller tax representative VAT identifier", "Identifier", "1..1", "/BG-ROOT/BG-11/BT-63", "/Invoice/cac:TaxRepresentativeParty/cac:PartyTaxScheme/cbc:CompanyID"),
    class_row("BG-12", "Seller tax representative postal address", "1..1", "/BG-ROOT/BG-11/BG-12", "/Invoice/cac:TaxRepresentativeParty/cac:PostalAddress"),
    attr_row("BT-64", "Tax representative address line 1", "Text", "0..1", "/BG-ROOT/BG-11/BG-12/BT-64", "/Invoice/cac:TaxRepresentativeParty/cac:PostalAddress/cbc:StreetName"),
    attr_row("BT-65", "Tax representative address line 2", "Text", "0..1", "/BG-ROOT/BG-11/BG-12/BT-65", "/Invoice/cac:TaxRepresentativeParty/cac:PostalAddress/cbc:AdditionalStreetName"),
    attr_row("BT-164", "Tax representative address line 3", "Text", "0..1", "/BG-ROOT/BG-11/BG-12/BT-164", "/Invoice/cac:TaxRepresentativeParty/cac:PostalAddress/cac:AddressLine/cbc:Line"),
    attr_row("BT-66", "Tax representative city", "Text", "0..1", "/BG-ROOT/BG-11/BG-12/BT-66", "/Invoice/cac:TaxRepresentativeParty/cac:PostalAddress/cbc:CityName"),
    attr_row("BT-67", "Tax representative post code", "Text", "0..1", "/BG-ROOT/BG-11/BG-12/BT-67", "/Invoice/cac:TaxRepresentativeParty/cac:PostalAddress/cbc:PostalZone"),
    attr_row("BT-68", "Tax representative country subdivision", "Text", "0..1", "/BG-ROOT/BG-11/BG-12/BT-68", "/Invoice/cac:TaxRepresentativeParty/cac:PostalAddress/cbc:CountrySubentity"),
    attr_row("BT-69", "Tax representative country code", "Code", "1..1", "/BG-ROOT/BG-11/BG-12/BT-69", "/Invoice/cac:TaxRepresentativeParty/cac:PostalAddress/cac:Country/cbc:IdentificationCode"),

    # Delivery, invoice period and payment
    attr_row("BT-70", "Deliver to party name", "Text", "0..1", "/BG-ROOT/BG-13/BT-70", "/Invoice/cac:Delivery/cac:DeliveryParty/cac:PartyName/cbc:Name"),
    attr_row("BT-71", "Deliver to location identifier", "Identifier", "0..1", "/BG-ROOT/BG-13/BT-71", "/Invoice/cac:Delivery/cac:DeliveryLocation/cbc:ID"),
    class_row("BG-14", "Invoicing period", "0..1", "/BG-ROOT/BG-14", "/Invoice/cac:InvoicePeriod"),
    attr_row("BT-73", "Invoicing period start date", "Date", "0..1", "/BG-ROOT/BG-14/BT-73", "/Invoice/cac:InvoicePeriod/cbc:StartDate"),
    attr_row("BT-74", "Invoicing period end date", "Date", "0..1", "/BG-ROOT/BG-14/BT-74", "/Invoice/cac:InvoicePeriod/cbc:EndDate"),
    class_row("BG-15", "Deliver to address", "0..1", "/BG-ROOT/BG-13/BG-15", "/Invoice/cac:Delivery/cac:DeliveryLocation/cac:Address"),
    attr_row("BT-75", "Deliver to address line 1", "Text", "0..1", "/BG-ROOT/BG-13/BG-15/BT-75", "/Invoice/cac:Delivery/cac:DeliveryLocation/cac:Address/cbc:StreetName"),
    attr_row("BT-76", "Deliver to address line 2", "Text", "0..1", "/BG-ROOT/BG-13/BG-15/BT-76", "/Invoice/cac:Delivery/cac:DeliveryLocation/cac:Address/cbc:AdditionalStreetName"),
    attr_row("BT-165", "Deliver to address line 3", "Text", "0..1", "/BG-ROOT/BG-13/BG-15/BT-165", "/Invoice/cac:Delivery/cac:DeliveryLocation/cac:Address/cac:AddressLine/cbc:Line"),
    attr_row("BT-77", "Deliver to city", "Text", "0..1", "/BG-ROOT/BG-13/BG-15/BT-77", "/Invoice/cac:Delivery/cac:DeliveryLocation/cac:Address/cbc:CityName"),
    attr_row("BT-78", "Deliver to post code", "Text", "0..1", "/BG-ROOT/BG-13/BG-15/BT-78", "/Invoice/cac:Delivery/cac:DeliveryLocation/cac:Address/cbc:PostalZone"),
    attr_row("BT-79", "Deliver to country subdivision", "Text", "0..1", "/BG-ROOT/BG-13/BG-15/BT-79", "/Invoice/cac:Delivery/cac:DeliveryLocation/cac:Address/cbc:CountrySubentity"),
    attr_row("BT-80", "Deliver to country code", "Code", "1..1", "/BG-ROOT/BG-13/BG-15/BT-80", "/Invoice/cac:Delivery/cac:DeliveryLocation/cac:Address/cac:Country/cbc:IdentificationCode"),
    attr_row("BT-82", "Payment means text", "Text", "0..1", "/BG-ROOT/BG-16/BT-82", "/Invoice/cac:PaymentMeans/cbc:PaymentMeansCode/@name"),
    class_row("BG-17", "Credit transfer", "0..*", "/BG-ROOT/BG-16/BG-17", "/Invoice/cac:PaymentMeans/cac:PayeeFinancialAccount"),
    attr_row("BT-85", "Payment account name", "Text", "0..1", "/BG-ROOT/BG-16/BG-17/BT-85", "/Invoice/cac:PaymentMeans/cac:PayeeFinancialAccount/cbc:Name"),
    attr_row("BT-86", "Payment service provider identifier", "Identifier", "0..1", "/BG-ROOT/BG-16/BG-17/BT-86", "/Invoice/cac:PaymentMeans/cac:PayeeFinancialAccount/cac:FinancialInstitutionBranch/cbc:ID"),
    class_row("BG-18", "Payment card information", "0..1", "/BG-ROOT/BG-16/BG-18", "/Invoice/cac:PaymentMeans/cac:CardAccount"),
    attr_row("BT-87", "Payment card primary account number", "Identifier", "1..1", "/BG-ROOT/BG-16/BG-18/BT-87", "/Invoice/cac:PaymentMeans/cac:CardAccount/cbc:PrimaryAccountNumberID"),
    attr_row("BT-88", "Payment card holder name", "Text", "0..1", "/BG-ROOT/BG-16/BG-18/BT-88", "/Invoice/cac:PaymentMeans/cac:CardAccount/cbc:HolderName"),
    class_row("BG-19", "Direct debit", "0..1", "/BG-ROOT/BG-16/BG-19", "/Invoice/cac:PaymentMeans"),
    attr_row("BT-89", "Mandate reference identifier", "Identifier", "0..1", "/BG-ROOT/BG-16/BG-19/BT-89", "/Invoice/cac:PaymentMeans/cac:PaymentMandate/cbc:ID"),
    attr_row("BT-90", "Bank assigned creditor identifier", "Identifier", "0..1", "/BG-ROOT/BG-16/BG-19/BT-90", "/Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID"),
    attr_row("BT-91", "Debited account identifier", "Identifier", "0..1", "/BG-ROOT/BG-16/BG-19/BT-91", "/Invoice/cac:PaymentMeans/cac:PaymentMandate/cac:PayerFinancialAccount/cbc:ID"),

    # Supporting documents and line detail
    class_row("BG-24", "Additional supporting documents", "0..*", "/BG-ROOT/BG-24", "/Invoice/cac:AdditionalDocumentReference"),
    attr_row("BT-122", "Supporting document reference", "Identifier", "1..1", "/BG-ROOT/BG-24/BT-122", "/Invoice/cac:AdditionalDocumentReference/cbc:ID"),
    attr_row("BT-123", "Supporting document description", "Text", "0..1", "/BG-ROOT/BG-24/BT-123", "/Invoice/cac:AdditionalDocumentReference/cbc:DocumentDescription"),
    attr_row("BT-124", "External document location", "Identifier", "0..1", "/BG-ROOT/BG-24/BT-124", "/Invoice/cac:AdditionalDocumentReference/cac:Attachment/cac:ExternalReference/cbc:URI"),
    attr_row("BT-125", "Attached document", "Binary object", "0..1", "/BG-ROOT/BG-24/BT-125", "/Invoice/cac:AdditionalDocumentReference/cac:Attachment/cbc:EmbeddedDocumentBinaryObject"),
    class_row("BG-29", "Price details", "1..1", "/BG-ROOT/BG-25/BG-29", "/Invoice/cac:InvoiceLine/cac:Price"),
    attr_row("BT-147", "Item price discount", "Amount", "0..1", "/BG-ROOT/BG-25/BG-29/BT-147", "/Invoice/cac:InvoiceLine/cac:Price/cac:AllowanceCharge/cbc:Amount"),
    attr_row("BT-148", "Item gross price", "Amount", "0..1", "/BG-ROOT/BG-25/BG-29/BT-148", "/Invoice/cac:InvoiceLine/cac:Price/cac:AllowanceCharge/cbc:BaseAmount"),
    class_row("BG-30", "Line VAT information", "1..1", "/BG-ROOT/BG-25/BG-30", "/Invoice/cac:InvoiceLine/cac:Item/cac:ClassifiedTaxCategory"),
    class_row("BG-31", "Item information", "1..1", "/BG-ROOT/BG-25/BG-31", "/Invoice/cac:InvoiceLine/cac:Item"),
    attr_row("BT-156", "Item buyer identifier", "Identifier", "0..1", "/BG-ROOT/BG-25/BG-31/BT-156", "/Invoice/cac:InvoiceLine/cac:Item/cac:BuyersItemIdentification/cbc:ID"),
    attr_row("BT-157", "Item standard identifier", "Identifier", "0..1", "/BG-ROOT/BG-25/BG-31/BT-157", "/Invoice/cac:InvoiceLine/cac:Item/cac:StandardItemIdentification/cbc:ID"),
    attr_row("BT-158", "Item classification identifier", "Identifier", "0..*", "/BG-ROOT/BG-25/BG-31/BT-158", "/Invoice/cac:InvoiceLine/cac:Item/cac:CommodityClassification/cbc:ItemClassificationCode"),
    attr_row("BT-159", "Item country of origin", "Code", "0..1", "/BG-ROOT/BG-25/BG-31/BT-159", "/Invoice/cac:InvoiceLine/cac:Item/cac:OriginCountry/cbc:IdentificationCode"),
    class_row("BG-32", "Item attributes", "0..*", "/BG-ROOT/BG-25/BG-31/BG-32", "/Invoice/cac:InvoiceLine/cac:Item/cac:AdditionalItemProperty"),
    attr_row("BT-160", "Item attribute name", "Text", "1..1", "/BG-ROOT/BG-25/BG-31/BG-32/BT-160", "/Invoice/cac:InvoiceLine/cac:Item/cac:AdditionalItemProperty/cbc:Name"),
    attr_row("BT-161", "Item attribute value", "Text", "1..1", "/BG-ROOT/BG-25/BG-31/BG-32/BT-161", "/Invoice/cac:InvoiceLine/cac:Item/cac:AdditionalItemProperty/cbc:Value"),
]


UPDATES = {
    "BG-1": {"name": "Invoice note", "multiplicity": "0..*", "path": "/BG-ROOT/BG-1", "xpath": "/Invoice/cbc:Note", "type": "C"},
    "BT-23": {"path": "/BG-ROOT/BG-2/BT-23"},
    "BT-24": {"path": "/BG-ROOT/BG-2/BT-24"},
    "BT-84": {"path": "/BG-ROOT/BG-16/BG-17/BT-84"},
    "BT-146": {"path": "/BG-ROOT/BG-25/BG-29/BT-146"},
    "BT-149": {"path": "/BG-ROOT/BG-25/BG-29/BT-149"},
    "BT-150": {"path": "/BG-ROOT/BG-25/BG-29/BT-150"},
    "BT-151": {"name": "Invoiced item VAT category code", "path": "/BG-ROOT/BG-25/BG-30/BT-151"},
    "BT-152": {"name": "Invoiced item VAT rate", "path": "/BG-ROOT/BG-25/BG-30/BT-152"},
    "BT-153": {"path": "/BG-ROOT/BG-25/BG-31/BT-153"},
    "BT-154": {"path": "/BG-ROOT/BG-25/BG-31/BT-154"},
    "BT-155": {"name": "Item seller identifier", "path": "/BG-ROOT/BG-25/BG-31/BT-155"},
}


def read_rows(csv_file: Path) -> List[Dict[str, str]]:
    with csv_file.open(newline="", encoding="utf-8-sig") as f:
        rows = [{key.lstrip("\ufeff"): value for key, value in row.items()} for row in csv.DictReader(f)]
    return rows


def write_rows(csv_file: Path, rows: Iterable[Dict[str, str]]) -> None:
    with csv_file.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for sequence, row_data in enumerate(rows, start=1):
            row_data["sequence"] = str(sequence)
            row_data["level"] = str(max(0, len([part for part in row_data["path"].split("/") if part]) - 1))
            writer.writerow({field: row_data.get(field, "") for field in FIELDNAMES})


def main() -> int:
    parser = argparse.ArgumentParser(description="Extend EN 16931 LHM coverage.")
    parser.add_argument("lhm_csv", type=Path)
    args = parser.parse_args()

    rows = read_rows(args.lhm_csv)
    by_id = {row_data["id"]: row_data for row_data in rows}

    for identifier, values in UPDATES.items():
        if identifier in by_id:
            by_id[identifier].update(values)

    added = 0
    for row_data in ROWS:
        identifier = row_data["id"]
        if identifier not in by_id:
            rows.append(row_data)
            by_id[identifier] = row_data
            added += 1

    write_rows(args.lhm_csv, rows)
    print(f"Added {added} EN 16931 row(s) to {args.lhm_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
