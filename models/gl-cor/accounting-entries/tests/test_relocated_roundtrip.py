from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


UNIT = Path(__file__).resolve().parents[1]
SCRIPT = UNIT / "scripts" / "flat_csv.py"
HMD = UNIT / "hmd" / "XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv"
BINDING = UNIT / "bindings" / "flat-csv" / "PCA_GL_XBRL_GL_Next_Flat_CSV_Table_shared_detail_20260815.csv"
SOURCE = UNIT / "fixtures" / "input" / "pca-synthetic-81.csv"
EXPECTED = UNIT / "fixtures" / "expected" / "pca-accounting-entries.csv"
EXPECTED_METADATA = EXPECTED.with_suffix(".json")
ENTRY_POINT = UNIT / "taxonomy" / "cor_accountingEntries" / "cor-all-oim-2026-12-31.xsd"


def rows(path: Path) -> list[list[str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.reader(stream))


def metadata_taxonomy(path: Path) -> Path:
    data = json.loads(path.read_text(encoding="utf-8"))
    uri = data["documentInfo"]["taxonomy"][0]
    if Path(uri).is_absolute():
        raise AssertionError("taxonomy URI must be relative")
    return (path.parent / uri).resolve()


class RelocatedAccountingEntriesTest(unittest.TestCase):
    def test_flat_csv_roundtrip_uses_model_unit_paths(self) -> None:
        self.assertEqual(metadata_taxonomy(EXPECTED_METADATA), ENTRY_POINT.resolve())
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            structured = work / "pca.csv"
            metadata = structured.with_suffix(".json")
            reverse = work / "pca-roundtrip.csv"
            subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(SCRIPT),
                    "to-structured",
                    str(SOURCE),
                    "-o",
                    str(structured),
                    "-m",
                    str(HMD),
                    "-b",
                    str(BINDING),
                    "--profile-width",
                    "81",
                    "--metadata-output",
                    str(metadata),
                    "--taxonomy-entrypoint",
                    str(ENTRY_POINT),
                ],
                check=True,
            )
            self.assertEqual(rows(structured), rows(EXPECTED))
            self.assertEqual(metadata_taxonomy(metadata), ENTRY_POINT.resolve())
            subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(SCRIPT),
                    "to-flat",
                    str(structured),
                    "-o",
                    str(reverse),
                    "-m",
                    str(HMD),
                    "-b",
                    str(BINDING),
                    "--profile-width",
                    "81",
                ],
                check=True,
            )
            self.assertEqual(rows(reverse), rows(SOURCE))


if __name__ == "__main__":
    unittest.main()
