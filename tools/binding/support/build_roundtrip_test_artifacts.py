#!/usr/bin/env python3
# coding: utf-8
"""
Build round-trip test artifacts under tests/roundtrip.

The directory layout separates:
  source_xml      original UBL Invoice XML files used as test input
  structured_csv  hierarchical structured CSV generated from source XML
  metadata_json   JSON metadata relating structured CSV columns to taxonomy
  roundtrip_xml   XML regenerated from structured CSV

Creation Date: 2026-07-06
Last Modified: 2026-07-13

Copyright 2026 Sambuichi Professional Engineers Office
Designed by SAMBUICHI, Nobuyuki
Produced by ChatGPT and Codex, edited by SAMBUICHI, Nobuyuki

License:
    This software source code is licensed under the MIT License.

    Non-code materials in the UADC-PoC project, including original mapping
    tables, syntax binding definitions, semantic binding definitions,
    transformation rules, explanatory notes, and documentation, may be licensed
    separately under Creative Commons Attribution-NonCommercial 4.0
    International License (CC BY-NC 4.0), where so indicated.

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

import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEST_ROOT = ROOT / "tests" / "roundtrip"
PYTHON = Path(sys.executable)


DATASETS = [
    (
        "openpeppol-minimal",
        [ROOT / "samples" / "input" / "openpeppol_ubl_invoice_minimal.xml"],
    ),
    (
        "bis-billing3-examples",
        sorted((ROOT / "samples" / "input" / "bis-billing3-examples").glob("*.xml")),
    ),
]


def ensure_taxonomy() -> None:
    taxonomy_base = ROOT / "out" / "taxonomy"
    oim_schema = taxonomy_base / "plt" / "en16931-oim-2026-07-05.xsd"
    module_schema = taxonomy_base / "en16931" / "en16931-2026-07-05.xsd"
    if oim_schema.exists() and module_schema.exists():
        return
    subprocess.run([str(PYTHON), str(ROOT / "tests" / "test_xbrlgl_generator_uadc_lhm.py")], check=True)


def is_invoice_xml(xml_file: Path) -> bool:
    root = ET.parse(xml_file).getroot()
    local_name = root.tag.rsplit("}", 1)[-1] if root.tag.startswith("{") else root.tag
    return local_name == "Invoice"


def clean_directory(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for file in directory.glob("*"):
        if file.is_file():
            file.unlink()


def run_converter(input_file: Path, output_file: Path, reverse: bool = False, metadata_file: Path | None = None) -> None:
    binding = ROOT / "specs" / "bindings" / "syntax" / "EN16931_UBL_Invoice_Syntax_Binding.csv"
    command = [
        str(PYTHON),
        str(ROOT / "src" / "syntax_binding.py"),
        str(input_file),
        "-b",
        str(binding),
        "-o",
        str(output_file),
    ]
    if reverse:
        command.insert(3, "--reverse")
    elif metadata_file:
        command.extend([
            "--metadata-output",
            str(metadata_file),
            "--taxonomy-base",
            str(ROOT / "out" / "taxonomy"),
        ])
    subprocess.run(command, check=True)


def build_dataset(dataset_name: str, source_files: list[Path]) -> int:
    dataset_root = TEST_ROOT / dataset_name
    source_dir = dataset_root / "source_xml"
    csv_dir = dataset_root / "structured_csv"
    metadata_dir = dataset_root / "metadata_json"
    xml_dir = dataset_root / "roundtrip_xml"
    for directory in (source_dir, csv_dir, metadata_dir, xml_dir):
        clean_directory(directory)

    count = 0
    for source in source_files:
        if not is_invoice_xml(source):
            continue
        copied_source = source_dir / source.name
        structured_csv = csv_dir / f"{source.stem}.csv"
        metadata_json = metadata_dir / f"{source.stem}.metadata.json"
        roundtrip_xml = xml_dir / f"{source.stem}.xml"
        shutil.copy2(source, copied_source)
        run_converter(copied_source, structured_csv, metadata_file=metadata_json)
        run_converter(structured_csv, roundtrip_xml, reverse=True)
        count += 1
    return count


def main() -> int:
    ensure_taxonomy()
    total = 0
    for dataset_name, source_files in DATASETS:
        count = build_dataset(dataset_name, source_files)
        print(f"{dataset_name}: built {count} round-trip case(s)")
        total += count
    print(f"ok: built {total} round-trip artifact(s) under {TEST_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
