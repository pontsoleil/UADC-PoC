#!/usr/bin/env python3
# coding: utf-8
"""
Convert the minimal sample UBL Invoice XML to Structured CSV and metadata.

Creation Date: 2026-07-10
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

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PYTHON = Path(sys.executable)


def ensure_taxonomy() -> None:
    """
    Generate the local taxonomy when it is not already present.

    Args:
        None.

    Returns:
        None. The taxonomy files are generated under out/taxonomy when needed.
    """
    taxonomy = ROOT / "out" / "taxonomy" / "plt" / "en16931-oim-2026-07-05.xsd"
    if taxonomy.exists():
        return
    subprocess.run([str(PYTHON), str(ROOT / "tests" / "test_xbrlgl_generator_uadc_lhm.py")], check=True)


def main() -> int:
    """
    Run the forward Structured CSV conversion tutorial.

    Args:
        None.

    Returns:
        Process exit status.
    """
    ensure_taxonomy()
    out_dir = ROOT / "out" / "tutorial"
    out_dir.mkdir(parents=True, exist_ok=True)
    output_csv = out_dir / "openpeppol_ubl_invoice_minimal.csv"
    metadata_json = out_dir / "openpeppol_ubl_invoice_minimal.json"
    command = [
        str(PYTHON),
        str(ROOT / "src" / "syntax_binding.py"),
        str(ROOT / "samples" / "input" / "openpeppol_ubl_invoice_minimal.xml"),
        "-b",
        str(ROOT / "specs" / "bindings" / "syntax" / "EN16931_UBL_Invoice_Syntax_Binding.csv"),
        "--metadata-output",
        str(metadata_json),
        "--taxonomy-base",
        str(ROOT / "out" / "taxonomy"),
        "-o",
        str(output_csv),
    ]
    subprocess.run(command, check=True)
    print(f"Structured CSV: {output_csv}")
    print(f"Metadata JSON: {metadata_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

