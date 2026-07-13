#!/usr/bin/env python3
"""Local structural checks for the generated EN 16931 xBRL-CSV taxonomy."""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TAXONOMY = ROOT / "out" / "taxonomy"
VERSION = "2026-07-05"


def assert_exists(path: Path) -> None:
    assert path.exists(), f"Missing file: {path}"


def parse(path: Path) -> ET.Element:
    assert_exists(path)
    return ET.parse(path).getroot()


def local_schema_locations(root: ET.Element) -> list[str]:
    locations: list[str] = []
    for element in root.iter():
        if element.tag.endswith("import"):
            location = element.attrib.get("schemaLocation", "")
            if location and not location.startswith(("http://", "https://")):
                locations.append(location)
        if element.tag.endswith("linkbaseRef"):
            href = element.attrib.get("{http://www.w3.org/1999/xlink}href", "")
            if href and not href.startswith(("http://", "https://")):
                locations.append(href)
    return locations


def check_references(base_file: Path, root: ET.Element) -> None:
    for location in local_schema_locations(root):
        target = (base_file.parent / location).resolve()
        assert target.exists(), f"Broken local reference from {base_file}: {location}"


def main() -> int:
    oim_xsd = TAXONOMY / "plt" / f"en16931-oim-{VERSION}.xsd"
    def_linkbase = TAXONOMY / "plt" / f"en16931-def-{VERSION}.xml"
    module_xsd = TAXONOMY / "en16931" / f"en16931-{VERSION}.xsd"
    presentation_linkbase = TAXONOMY / "en16931" / f"en16931-{VERSION}-presentation.xml"
    content_xsd = TAXONOMY / "plt" / f"en16931-content-{VERSION}.xsd"
    gl_gen_xsd = TAXONOMY / "gen" / f"gl-gen-{VERSION}.xsd"
    plt_all_xsd = TAXONOMY / "plt" / f"plt-all-{VERSION}.xsd"

    for path in (oim_xsd, def_linkbase, module_xsd, presentation_linkbase, gl_gen_xsd):
        assert_exists(path)
    assert not plt_all_xsd.exists(), f"Tuple entry point must not exist: {plt_all_xsd}"
    assert not content_xsd.exists(), f"Content schema must not exist: {content_xsd}"

    roots = {
        oim_xsd: parse(oim_xsd),
        def_linkbase: parse(def_linkbase),
        module_xsd: parse(module_xsd),
        presentation_linkbase: parse(presentation_linkbase),
        gl_gen_xsd: parse(gl_gen_xsd),
    }
    for path, root in roots.items():
        check_references(path, root)

    oim_elements = [element for element in roots[oim_xsd] if element.tag.endswith("element")]
    assert roots[oim_xsd].attrib["targetNamespace"] == f"http://www.xbrl.org/int/gl/en16931/{VERSION}"
    oim_groups = {element.attrib.get("substitutionGroup", "") for element in oim_elements}
    assert "xbrldt:hypercubeItem" in oim_groups
    assert "xbrldt:dimensionItem" in oim_groups
    assert "xbrli:item" in oim_groups
    assert "xbrli:tuple" not in oim_groups
    assert not any(element.tag.endswith("complexType") for element in roots[oim_xsd])

    module_imports = local_schema_locations(roots[module_xsd])
    assert f"../gen/gl-gen-{VERSION}.xsd" in module_imports

    item_elements = [
        element for element in oim_elements
        if element.attrib.get("substitutionGroup") == "xbrli:item"
    ]
    assert item_elements
    assert all(
        element.attrib.get("{http://www.xbrl.org/2003/instance}periodType") == "instant"
        for element in item_elements
    )

    print(f"ok: local taxonomy checks passed for {oim_xsd}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())




