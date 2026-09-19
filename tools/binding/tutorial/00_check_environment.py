#!/usr/bin/env python3
# coding: utf-8
"""
Check that the tutorial can find the required UADC PoC files.

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

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


REQUIRED_PATHS = [
    ROOT / "src" / "syntax_binding.py",
    ROOT / "src" / "syntax_binding_ads_xbrl_gl.py",
    ROOT / "tools" / "build_roundtrip_test_artifacts.py",
    ROOT / "tools" / "taxonomy" / "xBRLGL_TaxonomyGenerator.py",
    ROOT / "specs" / "lhm" / "EN16931_CIUS_Invoice_LHM.csv",
    ROOT / "specs" / "bindings" / "syntax" / "EN16931_UBL_Invoice_Syntax_Binding.csv",
    ROOT / "specs" / "bindings" / "syntax" / "ADS_Invoices_Received_XBRL_GL_Binding.csv",
    ROOT / "samples" / "input" / "openpeppol_ubl_invoice_minimal.xml",
]


def main() -> int:
    """
    Report whether the tutorial prerequisites are present.

    Args:
        None.

    Returns:
        Process exit status.
    """
    print(f"Python: {sys.executable}")
    print(f"UADC PoC root: {ROOT}")
    missing = [path for path in REQUIRED_PATHS if not path.exists()]
    if missing:
        print("Missing required file(s):")
        for path in missing:
            print(f"  {path}")
        return 1
    taxonomy = ROOT / "out" / "taxonomy" / "plt" / "en16931-oim-2026-07-05.xsd"
    if taxonomy.exists():
        print(f"Taxonomy: found {taxonomy}")
    else:
        print("Taxonomy: not generated yet. Run tests/test_xbrlgl_generator_uadc_lhm.py first.")
    print("ok: tutorial prerequisites are available")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


