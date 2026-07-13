#!/usr/bin/env python3
# coding: utf-8
"""
Shared Phase 1 test helpers.

Phase 1 uses one common UBL Invoice syntax binding for all OpenPeppol and BIS
Billing 3 invoice XML samples. Each input XML is written to a same-stem
Structured CSV and metadata JSON under out/phase1/.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path(sys.executable)
PHASE1_BINDING = ROOT / "specs" / "bindings" / "syntax" / "EN16931_UBL_Invoice_Syntax_Binding.csv"
PHASE1_OUTPUT_DIR = ROOT / "out" / "phase1"
PHASE1_TAXONOMY = ROOT / "out" / "taxonomy"


def phase1_output_csv(source_xml: Path, output_dir: Path | None = None) -> Path:
    """Return the same-stem Structured CSV path for one Phase 1 XML input."""

    target_dir = output_dir or PHASE1_OUTPUT_DIR
    return target_dir / f"{source_xml.stem}.csv"


def convert_phase1(source_xml: Path, output_dir: Path | None = None) -> Path:
    """Convert one UBL invoice XML using the shared Phase 1 binding."""

    target_dir = output_dir or PHASE1_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    out_csv = phase1_output_csv(source_xml, target_dir)
    metadata_json = out_csv.with_suffix(".json")
    subprocess.run(
        [
            str(PYTHON),
            str(ROOT / "src" / "syntax_binding.py"),
            str(source_xml),
            "-b",
            str(PHASE1_BINDING),
            "--metadata-output",
            str(metadata_json),
            "--taxonomy-base",
            str(PHASE1_TAXONOMY),
            "-o",
            str(out_csv),
        ],
        check=True,
    )
    return out_csv



