#!/usr/bin/env python3
# coding: utf-8
"""
Regression test for UBL XSD-derived child order generation.

Creation Date: 2026-07-13
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
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.syntax_binding import load_ubl_child_order  # noqa: E402


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        schema_root = Path(directory)
        schema_file = schema_root / "UBL-Invoice-2.1.xsd"
        schema_file.write_text(
            """<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
  xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
  targetNamespace="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
  elementFormDefault="qualified">
  <xs:element name="Invoice" type="InvoiceType"/>
  <xs:complexType name="InvoiceType">
    <xs:sequence>
      <xs:element name="ID"/>
      <xs:element name="IssueDate"/>
      <xs:element name="InvoiceLine"/>
    </xs:sequence>
  </xs:complexType>
</xs:schema>
""",
            encoding="utf-8",
        )
        order = load_ubl_child_order(schema_root, "")
    assert order is not None
    assert order["Invoice"] == ["ID", "IssueDate", "InvoiceLine"]
    print("ok: generated UBL child order from XSD")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
