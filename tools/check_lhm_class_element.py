#!/usr/bin/env python3
# coding: utf-8
"""
Check LHM class_term and element rules.

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
from typing import Dict, List

from normalize_lhm_class_element import nearest_parent_bg, singularize, unique_element_names


def read_rows(csv_file: Path) -> List[Dict[str, str]]:
    with csv_file.open(newline="", encoding="utf-8-sig") as f:
        return [{key.lstrip("\ufeff"): value for key, value in row.items()} for row in csv.DictReader(f)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check LHM class_term and element columns.")
    parser.add_argument("lhm_csv", type=Path)
    args = parser.parse_args()

    rows = read_rows(args.lhm_csv)
    name_by_id = {row.get("id", ""): row.get("name", "") for row in rows}
    element_by_id = unique_element_names(rows)
    bad_class = []
    bad_element = []
    for row in rows:
        row_id = row.get("id", "")
        if not (row_id.startswith("BG-") or row_id.startswith("BT-")):
            continue
        expected_class = singularize(name_by_id.get(nearest_parent_bg(row), ""))
        expected_element = element_by_id.get(row_id, "")
        if row.get("class_term", "") != expected_class:
            bad_class.append((row.get("sequence", ""), row_id, row.get("class_term", ""), expected_class))
        if row.get("element", "") != expected_element:
            bad_element.append((row.get("sequence", ""), row_id, row.get("element", ""), expected_element))

    if bad_class:
        print("class_term mismatches:")
        for item in bad_class[:50]:
            print(item)
    if bad_element:
        print("element mismatches:")
        for item in bad_element[:50]:
            print(item)
    if bad_class or bad_element:
        print(f"bad_class={len(bad_class)} bad_element={len(bad_element)}")
        return 1
    print(f"ok: checked {len(rows)} LHM row(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
