#!/usr/bin/env python3
"""Build the public PCA FY2021 evaluation package from accepted annual inputs."""

from __future__ import annotations

import argparse
import calendar
import csv
import hashlib
import json
import shutil
from pathlib import Path


DATASET_ID = "pca-synthetic-fy2021-v1"
MONTHS = [
    "2021-04", "2021-05", "2021-06", "2021-07", "2021-08", "2021-09",
    "2021-10", "2021-11", "2021-12", "2022-01", "2022-02", "2022-03",
]
EXPECTED = {
    "pca": "874909A8AE812DFE7B26A73AAD34C1B9381C3403506071566BEDCAB5B4A463A0",
    "structured": "FD9C87A7F0CB8B5B436E6DB80527697438E8A1D1857EF77B8E1767D53F480769",
    "metadata": "4F0BFA9B971E9A586947862769B3B71EE1E92F79A0487987099B5747A44A7701",
    "accounts": "AF8F30AC0E87B9BDC8F4336683A6D82E8F62360FCD1FA2E848CB40994C5D0715",
    "opening": "FD9F8802C9D92469D24F7B6CC68000F1C7CFDA828C2611E38EEDC186E55F9E49",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def require_hash(path: Path, expected: str) -> None:
    actual = sha256(path)
    if actual != expected:
        raise ValueError(f"Unexpected input hash for {path.name}: {actual}")


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def split_pca(annual_path: Path, april_path: Path) -> int:
    with annual_path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    if len(rows) < 3 or rows[0][0] != "Column1" or rows[1][0] != "伝票日付":
        raise ValueError("Unexpected PCA two-row header")
    april = [row for row in rows[2:] if row and row[0].startswith("202104")]
    april_path.parent.mkdir(parents=True, exist_ok=True)
    with april_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerows(rows[:2] + april)
    return len(april)


def split_structured(csv_path: Path, metadata_path: Path, root: Path) -> dict[str, int]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        facts = list(reader)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    grouped: dict[str, list[dict[str, str]]] = {month: [] for month in MONTHS}
    entries: dict[str, str] = {}
    for row in facts:
        header = row.get("d_cor_entryHeader", "")
        try:
            date_key, _voucher = json.loads(header)
        except Exception as exc:
            raise ValueError(f"Invalid entry-header dimension: {header!r}") from exc
        month = f"{date_key[:4]}-{date_key[4:6]}"
        if month not in grouped:
            raise ValueError(f"Out-of-scope month: {month}")
        previous = entries.setdefault(header, month)
        if previous != month:
            raise ValueError(f"Entry split across months: {header}")
        grouped[month].append(row)

    for month, month_rows in grouped.items():
        csv_name = f"{month}.csv"
        write_csv(root / csv_name, fields, month_rows)
        year, number = (int(part) for part in month.split("-"))
        last_day = calendar.monthrange(year, number)[1]
        monthly = json.loads(json.dumps(metadata))
        monthly["documentInfo"]["taxonomy"] = [
            "../../../../XBRL-GL-Next/taxonomy/accounting-entries/oim/"
            "cor_accountingEntries/cor-all-oim-2026-12-31.xsd"
        ]
        monthly["tables"] = {
            f"{DATASET_ID}-{month}": {"template": "structured", "url": csv_name}
        }
        monthly["tableTemplates"]["structured"]["dimensions"]["period"] = (
            f"{year:04d}-{number:02d}-{last_day:02d}T00:00:00"
        )
        (root / f"{month}.json").write_text(
            json.dumps(monthly, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
    if sum(len(rows) for rows in grouped.values()) != len(facts):
        raise ValueError("Monthly fact union does not equal annual facts")
    return {month: len(rows) for month, rows in grouped.items()}


def build_opening(source: Path, target: Path) -> int:
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    fields = [
        "dataset_id", "as_of_date", "account", "account_name", "normal_balance",
        "opening_balance", "source_type", "source_reference",
    ]
    output = [{
        "dataset_id": DATASET_ID,
        "as_of_date": "2021-04-01",
        "account": row["account"],
        "account_name": row["account_name"],
        "normal_balance": row["normal_balance"],
        "opening_balance": row["opening_balance"],
        "source_type": row["source_type"],
        "source_reference": row["source_reference"],
    } for row in rows]
    write_csv(target, fields, output)
    return len(output)


def write_manifest(root: Path, validation_status: str) -> None:
    rows = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        if path.name == "PUBLIC_MANIFEST.csv":
            continue
        rel = path.relative_to(root).as_posix()
        period = next((month for month in MONTHS if month in path.name), "2021-04/2022-03")
        rows.append({
            "relative_path": rel,
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
            "dataset_id": DATASET_ID,
            "period": period,
            "source_authority": "project-authored synthetic data",
            "license": "repository content license",
            "generator": "tools/generate_pca_synthetic_evaluation_dataset.py",
            "validation_status": validation_status,
        })
    write_csv(root / "manifests" / "PUBLIC_MANIFEST.csv", list(rows[0]), rows)


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--annual-pca", type=Path, default=repo / "instances/original/PCA/PCA_synthetic_annual_demo.csv")
    parser.add_argument("--annual-structured", type=Path, default=repo / "instances/derived/PCA/PCA_synthetic_annual_demo_structured.csv")
    parser.add_argument("--annual-metadata", type=Path, default=repo / "instances/derived/PCA/PCA_synthetic_annual_demo_structured.json")
    parser.add_argument("--account-master", type=Path, required=True)
    parser.add_argument("--opening-balances", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=repo / f"instances/evaluation/{DATASET_ID}")
    parser.add_argument(
        "--validation-status",
        choices=("PENDING_DELTA_VALIDATION", "PASS"),
        default="PENDING_DELTA_VALIDATION",
        help="Use PASS only after the generated bytes have passed the delta validation plan.",
    )
    args = parser.parse_args()

    for key, path in (("pca", args.annual_pca), ("structured", args.annual_structured),
                      ("metadata", args.annual_metadata), ("accounts", args.account_master),
                      ("opening", args.opening_balances)):
        require_hash(path, EXPECTED[key])

    root = args.output
    original = root / "original/pca"
    structured = root / "structured"
    original.mkdir(parents=True, exist_ok=True)
    structured.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(args.account_master, original / "PCA_SYNTHETIC_ACCOUNT_MASTER.csv")
    april_rows = split_pca(args.annual_pca, original / "PCA_synthetic_2021-04.csv")
    opening_rows = build_opening(args.opening_balances, original / "PCA_SYNTHETIC_OPENING_BALANCES_2021-04-01.csv")
    monthly = split_structured(args.annual_structured, args.annual_metadata, structured)

    readme = f"""# {DATASET_ID}\n\nPublic synthetic evaluation data for fiscal year 2021-04 through 2022-03.\n\n- April physical PCA source: `original/pca/PCA_synthetic_2021-04.csv` ({april_rows} data rows)\n- Opening balances: `original/pca/PCA_SYNTHETIC_OPENING_BALANCES_2021-04-01.csv` ({opening_rows} accounts, as of 2021-04-01 before April activity)\n- Monthly xBRL-CSV pairs: `structured/YYYY-MM.csv` and `structured/YYYY-MM.json`\n- Annual accepted sources remain in `instances/original/PCA` and `instances/derived/PCA`; they are not duplicated here.\n- EPSON output is intentionally absent until an exact product, edition, version, and import-field contract are resolved.\n\nAll names and transactions are fictional.\n"""
    (root / "README.md").write_text(readme, encoding="utf-8", newline="\n")
    provenance = {
        "dataset_id": DATASET_ID,
        "period": {"start": "2021-04-01", "end": "2022-03-31"},
        "opening_balance_as_of": "2021-04-01 before April activity",
        "annual_input_sha256": EXPECTED,
        "monthly_fact_counts": monthly,
        "epson_status": "HOLD_UNRESOLVED_INTERFACE",
    }
    (root / "manifests").mkdir(parents=True, exist_ok=True)
    (root / "manifests/PROVENANCE.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    write_manifest(root, args.validation_status)
    print(json.dumps({"dataset_id": DATASET_ID, "april_rows": april_rows,
                      "opening_rows": opening_rows, "monthly_fact_counts": monthly},
                     ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
