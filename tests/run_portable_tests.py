#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Portable CLI-only regression driver for semantic and Tuple bindings."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import subprocess
from pathlib import Path


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def resolved(config_file: Path, value: str) -> Path:
    if value.startswith("<") and value.endswith(">"):
        raise ValueError(f"replace placeholder in local configuration: {value}")
    path = Path(value)
    return path if path.is_absolute() else (config_file.parent / path).resolve()


def run(command: list[str], log: Path | None = None) -> None:
    result = subprocess.run(command, text=True, encoding="utf-8", errors="replace",
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if log:
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text(result.stdout, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(command)}\n{result.stdout}")


def semantic_rows(path: Path) -> set[tuple[tuple[str, str], ...]]:
    fields, rows = read_csv(path)
    return {
        tuple(sorted((field, row.get(field, "")) for field in fields if row.get(field, "")))
        for row in rows
    }


def semantic_facts(path: Path, metadata: Path) -> set[tuple]:
    value = json.loads(metadata.read_text(encoding="utf-8"))
    template = value["tableTemplates"]["structured"]
    dimensions = {
        reference[1:]
        for qname, reference in template["dimensions"].items()
        if ":" in qname and isinstance(reference, str) and reference.startswith("$")
    }
    facts = set()
    _, rows = read_csv(path)
    for row in rows:
        identity = tuple(sorted((name, row[name]) for name in dimensions if row.get(name)))
        for column, lexical in row.items():
            if column not in dimensions and lexical:
                facts.add((identity, column, lexical))
    return facts


def count_source_facts(path: Path, source_hmd: Path, excluded: set[str] | None = None) -> int:
    _, hmd = read_csv(source_hmd)
    dimensions = {
        "d" + row["local_name"][:1].upper() + row["local_name"][1:]
        for row in hmd if row.get("type") == "C" and "*" in row.get("multiplicity", "")
    }
    _, rows = read_csv(path)
    excluded = excluded or set()
    return sum(
        1 for row in rows for name, lexical in row.items()
        if name not in dimensions and name not in excluded and lexical
    )


def metadata_identity(path: Path) -> dict:
    """Compare metadata semantics after resolving its two location references."""
    value = json.loads(path.read_text(encoding="utf-8"))
    value["documentInfo"]["taxonomy"] = [
        str((path.parent / item).resolve()) for item in value["documentInfo"]["taxonomy"]
    ]
    for table in value["tables"].values():
        table["url"] = str((path.parent / table["url"]).resolve())
    return value


def forward(cfg: dict, source: Path, destination: Path) -> Path:
    run([
        str(cfg["python"]), str(cfg["semantic_binding"]), "forward", str(source),
        "--binding", str(cfg["binding"]), "--source-hmd", str(cfg["source_hmd"]),
        "--target-hmd", str(cfg["target_hmd"]), "--overlay", str(cfg["overlay"]),
        "--qname-map", str(cfg["qname_map"]), "--taxonomy", str(cfg["oim_entry"]),
        "--output", str(destination), "--entity", cfg["entity"], "--period", cfg["period"],
    ])
    return destination.with_suffix(".json")


def reverse(cfg: dict[str, Path], source: Path, destination: Path) -> None:
    run([
        str(cfg["python"]), str(cfg["semantic_binding"]), "reverse", str(source),
        "--binding", str(cfg["binding"]), "--source-hmd", str(cfg["source_hmd"]),
        "--target-hmd", str(cfg["target_hmd"]), "--overlay", str(cfg["overlay"]),
        "--qname-map", str(cfg["qname_map"]), "--output", str(destination),
    ])


def serialize_tuple(cfg: dict[str, Path], source: Path, metadata: Path, destination: Path) -> None:
    run([
        str(cfg["python"]), str(cfg["tuple_binding"]), "serialize", str(source),
        "--metadata", str(metadata), "--hmd", str(cfg["target_hmd"]),
        "--overlay", str(cfg["overlay"]), "--qname-map", str(cfg["qname_map"]),
        "--taxonomy", str(cfg["tuple_entry"]), "--output", str(destination),
        "--nil-manifest", str(destination.with_name("tuple_nil_manifest.csv")),
    ])


def deserialize_tuple(cfg: dict[str, Path], source: Path, metadata: Path, destination: Path) -> None:
    run([
        str(cfg["python"]), str(cfg["tuple_binding"]), "deserialize", str(source),
        "--metadata", str(metadata), "--hmd", str(cfg["target_hmd"]),
        "--overlay", str(cfg["overlay"]), "--qname-map", str(cfg["qname_map"]),
        "--taxonomy", str(cfg["tuple_entry"]), "--output", str(destination),
        "--nil-manifest", str(destination.with_name("tuple_recovered_nil_manifest.csv")),
    ])


def permute_fixture(source: Path, output: Path, mode: str) -> None:
    fields, rows = read_csv(source)
    if mode == "reverse":
        rows.reverse()
    elif mode == "shuffle":
        random.Random(20260827).shuffle(rows)
    write_csv(output, fields, rows)


def extended_selector_fixture(source: Path, output: Path) -> None:
    """Add multiple Header/Detail adjustment occurrences."""
    fields, rows = read_csv(source)
    additions: list[dict[str, str]] = []
    repeat_specs = [
        ("dDocumentLevelAllowances", "DocumentLevelAllowanceAmount", "501"),
        ("dDocumentLevelCharges", "DocumentLevelChargeAmount", "201"),
        ("dInvoiceLineAllowances", "InvoiceLineAllowanceAmount", "301"),
        ("dInvoiceLineCharges", "InvoiceLineChargeAmount", "101"),
    ]
    for dimension, amount, replacement in repeat_specs:
        match = next(row for row in rows if row.get(dimension) == "1")
        clone = dict(match)
        clone[dimension] = "2"
        clone[amount] = replacement
        additions.append(clone)
    write_csv(output, fields, rows + additions)


def synthetic_presence_contract(cfg: dict, directory: Path) -> tuple[dict, Path]:
    """Create a minimal public-contract fixture for present/not(present)."""
    directory.mkdir(parents=True, exist_ok=True)
    hmd_fields, _ = read_csv(cfg["target_hmd"])

    def hmd_row(sequence, module, level, row_type, name, multiplicity, path, local, domain=""):
        row = {field: "" for field in hmd_fields}
        row.update({"sequence": str(sequence), "module": module, "level": str(level),
                    "type": row_type, "name": name, "datatype": "String" if row_type == "A" else "",
                    "multiplicity": multiplicity, "semantic_path": path,
                    "class_term": "Item" if level > 1 else "Root", "local_name": local,
                    "value_domain": domain})
        return row

    source_hmd = directory / "source_hmd.csv"
    target_hmd = directory / "target_hmd.csv"
    write_csv(source_hmd, hmd_fields, [
        hmd_row(1, "src", 1, "C", "Root", "1", "$.root", "root"),
        hmd_row(2, "src", 2, "C", "Item", "0..*", "$.root.item", "item"),
        hmd_row(3, "src", 3, "A", "Marker", "0..1", "$.root.item.marker", "marker"),
        hmd_row(4, "src", 3, "A", "Value", "1", "$.root.item.value", "value"),
    ])
    write_csv(target_hmd, hmd_fields, [
        hmd_row(1, "tgt", 1, "C", "Root", "1", "$.target", "target"),
        hmd_row(2, "tgt", 2, "C", "Entry", "0..*", "$.target.entry", "entry"),
        hmd_row(3, "tgt", 3, "A", "Kind", "1", "$.target.entry.kind", "kind", "KindDomain"),
        hmd_row(4, "tgt", 3, "A", "Value", "1", "$.target.entry.value", "value"),
    ])
    binding_fields, _ = read_csv(cfg["binding"])

    def binding_row(source_path, target_path, source_type, target_type, status, source_seq, target_seq):
        row = {field: "" for field in binding_fields}
        row.update({"source_sequence": str(source_seq), "source_module": "src",
                    "source_level": "2" if source_type == "C" else "3", "source_type": source_type,
                    "source_name": "Item" if source_type == "C" else "Value",
                    "source_datatype": "" if source_type == "C" else "String",
                    "source_multiplicity": "0..*" if source_type == "C" else "1",
                    "source_semantic_path": source_path, "source_class_term": "Item",
                    "target_sequence": str(target_seq), "target_module": "tgt",
                    "target_level": "2" if target_type == "C" else "3", "target_type": target_type,
                    "target_name": "Entry" if target_type == "C" else "Value",
                    "target_datatype": "" if target_type == "C" else "String",
                    "target_multiplicity": "0..*" if target_type == "C" else "1",
                    "target_semantic_path": target_path, "target_class_term": "Entry",
                    "transformation": "identity", "mapping_status": status, "confidence": "HIGH"})
        return row

    binding = directory / "binding.csv"
    write_csv(binding, binding_fields, [
        binding_row("$.root.item[marker]", "$.target.entry[kind=\"present\"]", "C", "C", "STRUCTURAL", 2, 2),
        binding_row("$.root.item[not(marker)]", "$.target.entry[kind=\"absent\"]", "C", "C", "STRUCTURAL", 2, 2),
        binding_row("$.root.item[marker].value", "$.target.entry[kind=\"present\"].value", "A", "A", "EXACT", 4, 4),
        binding_row("$.root.item[not(marker)].value", "$.target.entry[kind=\"absent\"].value", "A", "A", "EXACT", 4, 4),
    ])
    overlay = directory / "overlay.csv"
    write_csv(overlay, ["parent_semantic_path", "selector_field"], [])
    qname = directory / "qname.csv"
    write_csv(qname, ["value_domain_id", "value", "member_qname"], [
        {"value_domain_id": "KindDomain", "value": "present", "member_qname": "tgt:present"},
        {"value_domain_id": "KindDomain", "value": "absent", "member_qname": "tgt:absent"},
    ])
    source = directory / "source.csv"
    write_csv(source, ["dRoot", "dItem", "marker", "value"], [
        {"dRoot": "1", "dItem": "1", "marker": "x", "value": "P1"},
        {"dRoot": "1", "dItem": "2", "marker": "", "value": "A1"},
        {"dRoot": "1", "dItem": "3", "marker": "y", "value": "P2"},
        {"dRoot": "1", "dItem": "4", "marker": "", "value": "A2"},
    ])
    mini = dict(cfg)
    mini.update({"source_hmd": source_hmd, "target_hmd": target_hmd,
                 "binding": binding, "overlay": overlay, "qname_map": qname})
    return mini, source


def require(condition: bool, name: str, details: str, results: list[dict[str, str]]) -> None:
    status = "PASS" if condition else "FAIL"
    results.append({"test": name, "status": status, "details": details})
    if not condition:
        raise AssertionError(f"{name}: {details}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    raw = json.loads(args.config.read_text(encoding="utf-8"))
    settings = {"entity", "period"}
    cfg = {
        name: value if name in settings else resolved(args.config, value)
        for name, value in raw.items()
    }
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, str]] = []

    # Original, reverse-row, and seeded-shuffle inputs use equal-depth output
    # directories and identical basenames so byte SHA is a meaningful gate.
    variant_outputs = []
    for mode in ("original", "reverse", "shuffle"):
        run_dir = out / "row-order" / mode
        source = cfg["source_csv"]
        if mode != "original":
            source = run_dir / "en.csv"
            permute_fixture(cfg["source_csv"], source, mode)
        target = run_dir / "gl_btx.csv"
        metadata = forward(cfg, source, target)
        variant_outputs.append((target, metadata))
    csv_shas = {sha256(item[0]) for item in variant_outputs}
    json_shas = {sha256(item[1]) for item in variant_outputs}
    require(len(csv_shas) == 1 and len(json_shas) == 1, "forward_row_order_invariance",
            f"CSV={sorted(csv_shas)} JSON={sorted(json_shas)}", results)
    require(sha256(variant_outputs[0][0]) == sha256(cfg["baseline_forward_csv"]),
            "first_forward_csv_unchanged", sha256(variant_outputs[0][0]), results)
    current_metadata = metadata_identity(variant_outputs[0][1])
    baseline_metadata = metadata_identity(cfg["baseline_forward_json"])
    # Different task output directories necessarily change the resolved table
    # location; compare taxonomy and all non-location metadata directly.
    current_metadata["tables"] = baseline_metadata["tables"]
    require(current_metadata == baseline_metadata,
            "first_forward_metadata_unchanged", "non-location metadata equal", results)

    gl_source, metadata = variant_outputs[0]
    route = out / "tuple-route"
    tuple_xml = route / "invoice.xml"
    recovered_gl = route / "gl_btx.csv"
    recovered_en = route / "en.csv"
    reforward_gl = route / "reforward" / "gl_btx.csv"
    serialize_tuple(cfg, gl_source, metadata, tuple_xml)
    deserialize_tuple(cfg, tuple_xml, metadata, recovered_gl)
    reverse(cfg, recovered_gl, recovered_en)
    forward(cfg, recovered_en, reforward_gl)
    require(semantic_facts(gl_source, metadata) == semantic_facts(recovered_gl, metadata),
            "gl_btx_direct_tuple_roundtrip", "semantic/ordinal diff 0", results)
    require(semantic_facts(gl_source, metadata) == semantic_facts(reforward_gl, metadata),
            "gl_btx_reforward", "missing 0 / unexpected 0", results)

    # Reverse must be independent of target CSV row order, and re-forward must
    # consequently produce the same byte output.
    reverse_outputs = []
    _, recovered_rows = read_csv(recovered_gl)
    recovered_fields, _ = read_csv(recovered_gl)
    for mode in ("original", "reverse", "shuffle"):
        run_dir = out / "reverse-row-order" / mode
        source = run_dir / "gl_btx.csv"
        rows = list(recovered_rows)
        if mode == "reverse":
            rows.reverse()
        elif mode == "shuffle":
            random.Random(20260827).shuffle(rows)
        write_csv(source, recovered_fields, rows)
        en = run_dir / "en.csv"
        gl = run_dir / "reforward" / "gl_btx.csv"
        reverse(cfg, source, en)
        forward(cfg, en, gl)
        reverse_outputs.append((en, gl, gl.with_suffix(".json")))
    require(len({sha256(item[0]) for item in reverse_outputs}) == 1,
            "reverse_row_order_invariance", "EN output SHA equal", results)
    require(len({sha256(item[1]) for item in reverse_outputs}) == 1,
            "reforward_row_order_invariance", "GL-BTX output SHA equal", results)

    historical = out / "historical-62"
    historical_gl = historical / "forward" / "gl_btx.csv"
    historical_metadata = forward(cfg, cfg["historical_62_source_csv"], historical_gl)
    historical_en = historical / "reverse" / "en.csv"
    reverse(cfg, historical_gl, historical_en)
    historical_reforward = historical / "reforward" / "gl_btx.csv"
    forward(cfg, historical_en, historical_reforward)
    historical_count = count_source_facts(historical_en, cfg["source_hmd"])
    historical_legacy_count = count_source_facts(
        historical_en, cfg["source_hmd"], {"InvoiceTypeCode"}
    )
    require(historical_legacy_count == 62 and historical_count == 63,
            "historical_62_fact_reverse",
            f"legacy facts={historical_legacy_count}; plus approved 380=1; total={historical_count}", results)
    require(semantic_facts(historical_gl, historical_metadata) ==
            semantic_facts(historical_reforward, historical_metadata),
            "historical_62_fact_roundtrip", "semantic/ordinal diff 0", results)

    # Extended selector/multiplicity fixture is independently permuted.
    extended_outputs = []
    extended_base = out / "selector-unit" / "base" / "en.csv"
    extended_selector_fixture(cfg["source_csv"], extended_base)
    for mode in ("original", "reverse", "shuffle"):
        run_dir = out / "selector-unit" / mode
        source = run_dir / "en.csv"
        if mode == "original":
            fields, rows = read_csv(extended_base)
            write_csv(source, fields, rows)
        else:
            permute_fixture(extended_base, source, mode)
        target = run_dir / "gl_btx.csv"
        forward(cfg, source, target)
        extended_outputs.append((target, target.with_suffix(".json")))
    require(len({sha256(item[0]) for item in extended_outputs}) == 1 and
            len({sha256(item[1]) for item in extended_outputs}) == 1,
            "selector_variant_multiple_occurrence_permutations",
            "equality and nested adjustment output SHA equal", results)

    mini_cfg, mini_source = synthetic_presence_contract(cfg, out / "presence-unit" / "contract")
    mini_outputs = []
    for mode in ("original", "reverse", "shuffle"):
        run_dir = out / "presence-unit" / mode
        source = run_dir / "source.csv"
        permute_fixture(mini_source, source, mode if mode != "original" else "original")
        target = run_dir / "target.csv"
        forward(mini_cfg, source, target)
        mini_outputs.append((target, target.with_suffix(".json")))
    require(len({sha256(item[0]) for item in mini_outputs}) == 1 and
            len({sha256(item[1]) for item in mini_outputs}) == 1,
            "presence_absence_multiple_occurrence_permutations",
            "present/not(present) output SHA equal", results)

    # Concrete accepted features remain visible without selector-value-specific
    # allocation logic in either runtime.
    _, final_rows = read_csv(gl_source)
    require(any(row.get("headerInvoiceType") == "gen:vdN1001InvoiceCreditNoteTypeN380" for row in final_rows),
            "invoice_type_380_ee1", "QName retained", results)
    parties = [(row.get("dEntityParty"), row.get("entityPartyType")) for row in final_rows if row.get("entityPartyType")]
    require(parties == [("1", "gen:vdPartyTypeSeller"), ("2", "gen:vdPartyTypeBuyer")],
            "entity_party_seller_buyer", str(parties), results)
    for selector in ("gen:vdAdjustmentTypeAllowance", "gen:vdAdjustmentTypeCharge"):
        require(any(selector in row.values() for row in final_rows),
                f"adjustment_{selector.rsplit('Type', 1)[-1].lower()}", "header/detail selector retained", results)

    arelle_log = out / "tuple-route" / "arelle.log"
    run([str(cfg["arelle"]), "--file", str(tuple_xml), "--validate", "--logFile", str(arelle_log)])
    log_text = arelle_log.read_text(encoding="utf-8-sig", errors="replace")
    errors = sum(1 for line in log_text.splitlines() if "[error]" in line.lower())
    warnings = sum(1 for line in log_text.splitlines() if "[warning]" in line.lower())
    require(errors == 0 and warnings == 0, "arelle_tuple", f"error {errors} / warning {warnings}", results)

    with (out / "PORTABLE_TEST_RESULTS.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["test", "status", "details"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(results)
    (out / "PORTABLE_TEST_SUMMARY.json").write_text(
        json.dumps({"status": "PASS", "tests": len(results)}, indent=2) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
