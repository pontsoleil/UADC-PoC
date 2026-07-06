#!/usr/bin/env python3
# coding: utf-8
"""
Validate generated xBRL-CSV metadata files with Arelle.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEST_ROOT = ROOT / "tests" / "roundtrip"
PYTHON = Path(sys.executable)


def arelle_command() -> str:
    found = shutil.which("arelleCmdLine.exe") or shutil.which("arelleCmdLine")
    if found:
        return found
    user_install = Path.home() / "AppData" / "Local" / "Programs" / "Python" / "Python310" / "Scripts" / "arelleCmdLine.exe"
    if user_install.exists():
        return str(user_install)
    raise RuntimeError("Arelle command line executable was not found.")


def main() -> int:
    subprocess.run([str(PYTHON), str(ROOT / "tests" / "build_roundtrip_test_artifacts.py")], check=True)
    arelle = arelle_command()
    metadata_files = sorted(TEST_ROOT.glob("*/metadata_json/*.metadata.json"))
    assert metadata_files, "No generated metadata files found."

    failures: list[tuple[Path, str]] = []
    error_pattern = re.compile(r"\[(?:error|xbrlce|oime|xmlSchema)", re.IGNORECASE)
    for metadata_file in metadata_files:
        result = subprocess.run(
            [arelle, "--plugins", "loadFromOIM", "--file", str(metadata_file), "--validate"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        output = result.stdout or ""
        if result.returncode != 0 or error_pattern.search(output):
            failures.append((metadata_file, output))

    if failures:
        for metadata_file, output in failures:
            print(f"FAIL: {metadata_file}")
            print(output)
        raise AssertionError(f"{len(failures)} xBRL-CSV metadata file(s) failed Arelle validation.")

    print(f"ok: validated {len(metadata_files)} xBRL-CSV metadata file(s) with Arelle")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
