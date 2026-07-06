#!/usr/bin/env python3
# coding: utf-8
"""
Regression test for running the XBRL-GL taxonomy generator with a UADC LHM CSV.
"""

from __future__ import annotations

import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
PYTHON = Path(sys.executable)


def main() -> int:
    out_dir = ROOT / "out" / "taxonomy"
    script = REPO / "XBRL-GL-2026" / "xBRLGL_TaxonomyGenerator.py"
    lhm = ROOT / "specs" / "lhm" / "EN16931_CIUS_Invoice_LHM.csv"
    cmd = [
        str(PYTHON),
        str(script),
        str(lhm),
        "-b",
        str(out_dir),
        "-p",
        "en16931",
        "-n",
        "https://example.com/uada/en16931/invoice/2026-07-05",
        "-l",
        "ja",
        "-c",
        "JPY",
    ]
    subprocess.run(cmd, check=True)

    oim_xsd = out_dir / "plt" / "plt-oim-2026-07-05.xsd"
    plt_all_xsd = out_dir / "plt" / "plt-all-2026-07-05.xsd"
    content_xsd = out_dir / "plt" / "en16931-content-2026-07-05.xsd"
    definition = out_dir / "plt" / "plt-def-2026-07-05.xml"
    module_xsd = out_dir / "en16931" / "en16931-2026-07-05.xsd"
    gl_gen_xsd = out_dir / "gen" / "gl-gen-2026-07-05.xsd"
    for path in (oim_xsd, content_xsd, definition, module_xsd, gl_gen_xsd):
        assert path.exists(), f"Missing generated file: {path}"
    assert not plt_all_xsd.exists(), f"Tuple entry point must not be generated: {plt_all_xsd}"

    root = ET.parse(oim_xsd).getroot()
    elements = [element for element in root if element.tag.endswith("element")]
    substitution_groups = {element.attrib.get("substitutionGroup", "") for element in elements}
    assert "xbrli:tuple" not in substitution_groups
    assert "xbrli:item" in substitution_groups
    assert "xbrldt:dimensionItem" in substitution_groups
    assert "xbrldt:hypercubeItem" in substitution_groups
    assert any(element.attrib.get("name") == "p_en16931_Invoice" for element in elements)
    element_names = {element.attrib.get("name", "") for element in elements}
    assert "d_en16931_Seller" not in element_names
    assert "d_en16931_Buyer" not in element_names
    assert "d_en16931_SellerPostalAddress" not in element_names
    assert "d_en16931_BuyerPostalAddress" not in element_names
    assert "d_en16931_InvoiceLine" in element_names
    assert "d_en16931_VatBreakdown" in element_names

    item_elements = [element for element in elements if element.attrib.get("substitutionGroup") == "xbrli:item"]
    assert item_elements
    assert all(element.attrib.get("{http://www.xbrl.org/2003/instance}periodType") == "instant" for element in item_elements)

    imports = [element.attrib.get("schemaLocation", "") for element in root if element.tag.endswith("import")]
    assert f"en16931-content-2026-07-05.xsd" not in imports
    assert "../en16931/en16931-2026-07-05.xsd" not in imports

    content_root = ET.parse(content_xsd).getroot()
    content_elements = [element for element in content_root if element.tag.endswith("element")]
    content_imports = [element.attrib.get("schemaLocation", "") for element in content_root if element.tag.endswith("import")]
    assert content_elements
    assert not any(element.tag.endswith("complexType") for element in content_root)
    assert "xbrli:tuple" not in {element.attrib.get("substitutionGroup", "") for element in content_elements}
    assert all(
        element.attrib.get("substitutionGroup") == "xbrli:item"
        for element in content_elements
    )
    assert "../gen/gl-gen-2026-07-05.xsd" in content_imports

    module_root = ET.parse(module_xsd).getroot()
    module_imports = [element.attrib.get("schemaLocation", "") for element in module_root if element.tag.endswith("import")]
    assert "../gen/gl-gen-2026-07-05.xsd" in module_imports

    print(f"ok: XBRL-GL generator accepted UADC LHM CSV and wrote {oim_xsd}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
