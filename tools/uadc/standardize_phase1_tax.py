#!/usr/bin/env python3
"""Standardize governed Phase 1 Structured Tidy tax rows without using expected reports."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--entries-input", type=Path, required=True)
    parser.add_argument("--balances-input", type=Path, required=True)
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--entries-output", type=Path, required=True)
    parser.add_argument("--balances-output", type=Path, required=True)
    parser.add_argument("--trace-output", type=Path, required=True)
    parser.add_argument("--summary-output", type=Path, required=True)
    args = parser.parse_args()
    fields, rows = read_csv(args.entries_input)
    if fields != [f"C{i}" for i in range(1, 44)]:
        raise SystemExit("PHASE1_SCHEMA_INVALID")
    mf, mapping_rows = read_csv(args.mapping)
    required = ["source_tax_description", "source_tax_category", "uncl5153_tax_type", "uncl5305_tax_category", "tax_rate_ratio", "transaction_classification", "rule_id"]
    if any(field not in mf for field in required):
        raise SystemExit("MAPPING_SCHEMA_INVALID")
    rules = {(r["source_tax_description"], r["source_tax_category"]): r for r in mapping_rows}
    if len(rules) != len(mapping_rows):
        raise SystemExit("MAPPING_AMBIGUOUS")
    out_fields = fields + ["C44", "C45"]
    trace = []
    tax_count = 0
    for row in rows:
        row["C44"] = ""
        row["C45"] = ""
        if row["C8"] != "DetailTax":
            continue
        rule = rules.get((row["C26"], row["C30"]))
        if rule is None:
            raise SystemExit("TAX_MAPPING_UNRESOLVED")
        source_rate = row["C29"]
        expected_source = rule["tax_rate_ratio"].replace("0.", "").lstrip("0")
        if source_rate != expected_source:
            raise SystemExit("TAX_RATE_SOURCE_CONFLICT")
        source_category = row["C30"]
        row["C29"] = rule["tax_rate_ratio"]
        row["C30"] = rule["uncl5305_tax_category"]
        row["C44"] = rule["uncl5153_tax_type"]
        row["C45"] = rule["transaction_classification"]
        payload = {
            "entry_occurrence": row["C2"], "detail_occurrence": row["C3"], "tax_occurrence": row["C6"],
            "source_tax_description": row["C26"], "source_tax_category": source_category,
            "source_tax_rate_lexical": source_rate, "output_tax_type": row["C44"],
            "output_tax_category": row["C30"], "output_tax_rate_ratio": row["C29"],
            "output_transaction_classification": row["C45"], "rule_id": rule["rule_id"],
        }
        digest = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()
        trace.append({**payload, "trace_sha256": digest})
        tax_count += 1
    write_csv(args.entries_output, out_fields, rows)
    bf, br = read_csv(args.balances_input)
    write_csv(args.balances_output, bf, br)
    trace_fields = list(trace[0]) if trace else [*required, "trace_sha256"]
    write_csv(args.trace_output, trace_fields, trace)
    summary = {"status": "PASS", "entry_rows": len(rows), "tax_rows": tax_count, "balance_rows": len(br), "expected_reports_used": False}
    args.summary_output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
