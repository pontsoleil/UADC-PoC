#!/usr/bin/env python3
# coding: utf-8
"""
Order the LHM CSV by EN 16931-1 Table 2 appearance order.

`BG-ROOT` is the Invoice root row. All EN identifiers then follow Table 2 order.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List


TABLE2_ORDER = [
    "BG-ROOT",
    "BT-1",
    "BT-2",
    "BT-3",
    "BT-5",
    "BT-6",
    "BT-7",
    "BT-8",
    "BT-9",
    "BT-10",
    "BT-11",
    "BT-12",
    "BT-13",
    "BT-14",
    "BT-15",
    "BT-16",
    "BT-17",
    "BT-18",
    "BT-19",
    "BT-20",
    "BG-1",
    "BT-21",
    "BT-22",
    "BG-2",
    "BT-23",
    "BT-24",
    "BG-3",
    "BT-25",
    "BT-26",
    "BG-4",
    "BT-27",
    "BT-28",
    "BT-29",
    "BT-30",
    "BT-31",
    "BT-32",
    "BT-33",
    "BT-34",
    "BG-5",
    "BT-35",
    "BT-36",
    "BT-162",
    "BT-37",
    "BT-38",
    "BT-39",
    "BT-40",
    "BG-6",
    "BT-41",
    "BT-42",
    "BT-43",
    "BG-7",
    "BT-44",
    "BT-45",
    "BT-46",
    "BT-47",
    "BT-48",
    "BT-49",
    "BG-8",
    "BT-50",
    "BT-51",
    "BT-163",
    "BT-52",
    "BT-53",
    "BT-54",
    "BT-55",
    "BG-9",
    "BT-56",
    "BT-57",
    "BT-58",
    "BG-10",
    "BT-59",
    "BT-60",
    "BT-61",
    "BG-11",
    "BT-62",
    "BT-63",
    "BG-12",
    "BT-64",
    "BT-65",
    "BT-164",
    "BT-66",
    "BT-67",
    "BT-68",
    "BT-69",
    "BG-13",
    "BT-70",
    "BT-71",
    "BT-72",
    "BG-14",
    "BT-73",
    "BT-74",
    "BG-15",
    "BT-75",
    "BT-76",
    "BT-165",
    "BT-77",
    "BT-78",
    "BT-79",
    "BT-80",
    "BG-16",
    "BT-81",
    "BT-82",
    "BT-83",
    "BG-17",
    "BT-84",
    "BT-85",
    "BT-86",
    "BG-18",
    "BT-87",
    "BT-88",
    "BG-19",
    "BT-89",
    "BT-90",
    "BT-91",
    "BG-20",
    "BT-92",
    "BT-93",
    "BT-94",
    "BT-95",
    "BT-96",
    "BT-97",
    "BT-98",
    "BG-21",
    "BT-99",
    "BT-100",
    "BT-101",
    "BT-102",
    "BT-103",
    "BT-104",
    "BT-105",
    "BG-22",
    "BT-106",
    "BT-107",
    "BT-108",
    "BT-109",
    "BT-110",
    "BT-111",
    "BT-112",
    "BT-113",
    "BT-114",
    "BT-115",
    "BG-23",
    "BT-116",
    "BT-117",
    "BT-118",
    "BT-119",
    "BT-120",
    "BT-121",
    "BG-24",
    "BT-122",
    "BT-123",
    "BT-124",
    "BT-125",
    "BG-25",
    "BT-126",
    "BT-127",
    "BT-128",
    "BT-129",
    "BT-130",
    "BT-131",
    "BT-132",
    "BT-133",
    "BG-26",
    "BT-134",
    "BT-135",
    "BG-27",
    "BT-136",
    "BT-137",
    "BT-138",
    "BT-139",
    "BT-140",
    "BG-28",
    "BT-141",
    "BT-142",
    "BT-143",
    "BT-144",
    "BT-145",
    "BG-29",
    "BT-146",
    "BT-147",
    "BT-148",
    "BT-149",
    "BT-150",
    "BG-30",
    "BT-151",
    "BT-152",
    "BG-31",
    "BT-153",
    "BT-154",
    "BT-155",
    "BT-156",
    "BT-157",
    "BT-158",
    "BT-159",
    "BG-32",
    "BT-160",
    "BT-161",
]


FIXES = {
    "BT-9": {"path": "/BG-ROOT/BT-9"},
    "BT-20": {"path": "/BG-ROOT/BT-20"},
    "BG-17": {
        "name": "Credit transfer",
        "multiplicity": "0..*",
        "path": "/BG-ROOT/BG-16/BG-17",
        "xpath": "/Invoice/cac:PaymentMeans/cac:PayeeFinancialAccount",
        "type": "C",
        "datatype": "",
    },
}


def read_rows(csv_file: Path) -> tuple[List[str], List[Dict[str, str]]]:
    with csv_file.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV has no header.")
        fieldnames = [field.lstrip("\ufeff") for field in reader.fieldnames]
        rows = [{key.lstrip("\ufeff"): value for key, value in row.items()} for row in reader]
    return fieldnames, rows


def write_rows(csv_file: Path, fieldnames: List[str], rows: List[Dict[str, str]]) -> None:
    with csv_file.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for sequence, row in enumerate(rows, start=1):
            row["sequence"] = str(sequence)
            row["level"] = str(max(0, len([part for part in row.get("path", "").split("/") if part]) - 1))
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def main() -> int:
    parser = argparse.ArgumentParser(description="Order LHM rows by EN 16931-1 Table 2.")
    parser.add_argument("lhm_csv", type=Path)
    args = parser.parse_args()

    fieldnames, rows = read_rows(args.lhm_csv)
    by_id = {row["id"]: row for row in rows}

    for identifier, values in FIXES.items():
        if identifier in by_id:
            by_id[identifier].update(values)

    order_index = {identifier: index for index, identifier in enumerate(TABLE2_ORDER)}
    unknown = [row["id"] for row in rows if row["id"] not in order_index]
    if unknown:
        raise ValueError(f"Rows not in Table 2 order list: {', '.join(unknown)}")

    ordered_rows = sorted(rows, key=lambda row: order_index[row["id"]])
    write_rows(args.lhm_csv, fieldnames, ordered_rows)
    print(f"Ordered {len(ordered_rows)} row(s) by EN 16931-1 Table 2.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
