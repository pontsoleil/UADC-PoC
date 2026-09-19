#!/usr/bin/env python3
# coding: utf-8
"""
Convert the tutorial Structured CSV back to UBL Invoice XML.

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


def ensure_structured_csv() -> Path:
    """
    Create the tutorial Structured CSV when it is missing.

    Args:
        None.

    Returns:
        Path to the tutorial Structured CSV.
    """
    structured_csv = ROOT / "out" / "tutorial" / "openpeppol_ubl_invoice_minimal.csv"
    if not structured_csv.exists():
        subprocess.run([str(PYTHON), str(ROOT / "src" / "tutorial" / "01_convert_sample_to_structured_csv.py")], check=True)
    return structured_csv


def main() -> int:
    """
    Run the reverse XML conversion tutorial.

    Args:
        None.

    Returns:
        Process exit status.
    """
    structured_csv = ensure_structured_csv()
    output_xml = ROOT / "out" / "tutorial" / "openpeppol_ubl_invoice_minimal.roundtrip.xml"
    command = [
        str(PYTHON),
        str(ROOT / "src" / "syntax_binding.py"),
        str(structured_csv),
        "--reverse",
        "-b",
        str(ROOT / "specs" / "bindings" / "syntax" / "EN16931_UBL_Invoice_Syntax_Binding.csv"),
        "-o",
        str(output_xml),
    ]
    subprocess.run(command, check=True)
    print(f"Round-trip XML: {output_xml}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

