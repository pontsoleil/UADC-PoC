#!/usr/bin/env python3
# coding: utf-8
"""
Validate regenerated round-trip XML files against the UBL 2.1 Invoice schema.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import xmlschema


ROOT = Path(__file__).resolve().parents[1]
TEST_ROOT = ROOT / "tests" / "roundtrip"
PYTHON = Path(sys.executable)
UBL_INVOICE_SCHEMA = ROOT / "out" / "cache" / "UBL-2.1" / "xsd" / "maindoc" / "UBL-Invoice-2.1.xsd"


def main() -> int:
    subprocess.run([str(PYTHON), str(ROOT / "tools" / "build_roundtrip_test_artifacts.py")], check=True)
    assert UBL_INVOICE_SCHEMA.exists(), f"Missing UBL schema: {UBL_INVOICE_SCHEMA}"
    schema = xmlschema.XMLSchema(str(UBL_INVOICE_SCHEMA))
    xml_files = sorted(TEST_ROOT.glob("*/roundtrip_xml/*.xml"))
    assert xml_files, "No generated round-trip XML files found."

    failures: list[tuple[Path, str]] = []
    for xml_file in xml_files:
        try:
            schema.validate(str(xml_file))
        except Exception as exc:
            failures.append((xml_file, str(exc).splitlines()[0]))

    if failures:
        for xml_file, message in failures:
            print(f"FAIL: {xml_file}: {message}")
        raise AssertionError(f"{len(failures)} round-trip XML file(s) failed UBL 2.1 schema validation.")

    print(f"ok: validated {len(xml_files)} round-trip XML file(s) against UBL 2.1 Invoice schema")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
