#!/usr/bin/env python3
# coding: utf-8
"""
Generate target delimited files from UADC Structured CSV by semantic binding.

Purpose:
    Convert UADC Phase 1 Structured CSV into Phase 2 target flat files, such
    as ADS pipe-separated value (PSV) files or ISO 21378 ADC CSV files, by
    applying a semantic binding table that maps each target field_name to a
    UADC semantic_path.

Processing overview:
    The script reads one Structured CSV file, or all CSV files in a directory.
    It reads a semantic binding CSV, derives the Structured CSV source column
    and repeated row scope from semantic_path and class multiplicity rows in
    the binding table, merges hierarchical child rows into their current
    invoice record, copies values into the target columns in binding order,
    and writes one delimited output file.

Command-line arguments:
    input: Structured CSV file, or directory containing Structured CSV files.
    -b, --binding-csv: Semantic binding CSV with ADS field_name and semantic_path.
    -o, --output-dir: Directory for generated delimited target files.
    --format: Output preset: psv or csv.
    --delimiter: Output delimiter. Overrides --format when supplied.
    --extension: Output file extension. Overrides --format when supplied.
    --output-filename: Explicit output file name when the input is one CSV file.

Results:
    Writes one target delimited file per input CSV and prints the generated
    file count. Returns exit code 0 on success.

Creation Date: 2026-07-11
Last Modified: 2026-07-13

Copyright 2026 Sambuichi Professional Engineers Office
Designed by SAMBUICHI, Nobuyuki
Produced by ChatGPT & Codex, edited by  SAMBUICHI, Nobuyuki
MIT License

(c) 2026 Sambuichi Professional Engineers Office

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
CC-BY-NC
"""

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
INDEXED_PATH_RE = re.compile(r"^(?P<group>.+?)\[(?P<index>\d+)\](?P<tail>(?:\..*)?)$")
TARGET_BINDING_RE = re.compile(
    r"^(?:(?:ADS|ISO21378|ISO_21378)_)?(?P<target>.+?)_(?:PSV|CSV)_Binding\.csv$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class SemanticBinding:
    """One target-column binding resolved from semantic_path to source column."""

    sequence: int
    target_column: str
    semantic_path: str = ""
    normalized_semantic_path: str = ""
    source_column: str = ""
    repeat_group_path: str = ""
    repeat_group_column: str = ""
    repeat_index: int | None = None
    default_value: str = ""
    required: bool = False


@dataclass(frozen=True)
class SemanticClass:
    """One semantic class row that can define a repeated row scope."""

    semantic_path: str
    multiplicity: str


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Generate target delimited files from UADC Structured CSV by semantic binding."
    )
    parser.add_argument("input", type=Path, help="Structured CSV file or directory.")
    parser.add_argument("-b", "--binding-csv", type=Path, required=True, help="Semantic binding CSV.")
    parser.add_argument("-o", "--output-dir", type=Path, required=True, help="Output directory.")
    parser.add_argument(
        "--format",
        choices=("psv", "csv"),
        default="psv",
        help="Output format preset. Default: psv.",
    )
    parser.add_argument("--delimiter", help="Output delimiter. Overrides --format.")
    parser.add_argument("--extension", help="Output extension. Overrides --format.")
    parser.add_argument(
        "--taxonomy-base",
        type=Path,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--output-filename",
        help="Explicit output file name. Allowed only when input is one CSV file.",
    )
    return parser.parse_args()


def sequence_number(value: str) -> int:
    """Return an integer sort key for a binding sequence value."""

    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 999999


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read CSV rows encoded as UTF-8, accepting an optional BOM."""

    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def multiplicity_repeats(multiplicity: str) -> bool:
    """Return whether a multiplicity upper bound allows repeated rows."""

    multiplicity = (multiplicity or "").strip().lower()
    if ".." not in multiplicity:
        return False
    upper = multiplicity.rsplit("..", 1)[1]
    if upper in {"*", "n", "unbounded"}:
        return True
    try:
        return int(upper) > 1
    except ValueError:
        return False


def parse_optional_int(value: str) -> int | None:
    """Parse an optional integer value."""

    value = (value or "").strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def indexed_semantic_path(semantic_path: str) -> tuple[str, str, int | None]:
    """Return normalized path, indexed group path, and occurrence number."""

    match = INDEXED_PATH_RE.match(semantic_path)
    if not match:
        return semantic_path, "", None

    group_path = match.group("group")
    tail = match.group("tail")
    normalized_path = f"{group_path}{tail}"
    return normalized_path, group_path, int(match.group("index"))


def semantic_segment_to_column(segment: str) -> str:
    """Return the Structured CSV column name implied by a semantic path segment."""

    segment = re.sub(r"\[\d+\]", "", (segment or "").strip())
    if not segment:
        return ""
    return f"{segment[:1].upper()}{segment[1:]}"


def source_column_for_path(semantic_path: str) -> str:
    """Return the Structured CSV value column implied by a semantic path."""

    if not semantic_path:
        return ""
    return semantic_segment_to_column(semantic_path.rsplit(".", 1)[-1])


def dimension_column_for_path(semantic_path: str) -> str:
    """Return the Structured CSV dimension column implied by a semantic class path."""

    source_column = source_column_for_path(semantic_path)
    return f"d{source_column}" if source_column else ""


def deepest_repeated_class_ancestor(
    semantic_path: str,
    repeated_classes: dict[str, SemanticClass],
) -> tuple[str, str]:
    """Return the deepest repeated class ancestor defined by the binding table."""

    best_path = ""
    for candidate_path in repeated_classes:
        if semantic_path == candidate_path or semantic_path.startswith(f"{candidate_path}."):
            best_path = candidate_path
    return best_path, dimension_column_for_path(best_path)


def resolve_bindings_for_classes(
    bindings: list[SemanticBinding],
    repeated_classes: dict[str, SemanticClass],
) -> list[SemanticBinding]:
    """Resolve source columns and repeated row scopes from binding class rows."""

    resolved: list[SemanticBinding] = []
    for binding in bindings:
        source_column = binding.source_column or source_column_for_path(binding.normalized_semantic_path)
        repeat_group_path = binding.repeat_group_path
        repeat_group_column = binding.repeat_group_column
        if repeat_group_path and not repeat_group_column:
            repeat_group_column = dimension_column_for_path(repeat_group_path)
        if not repeat_group_path:
            repeat_group_path, repeat_group_column = deepest_repeated_class_ancestor(
                binding.normalized_semantic_path,
                repeated_classes,
            )
        resolved.append(
            replace(
                binding,
                source_column=source_column,
                repeat_group_path=repeat_group_path,
                repeat_group_column=repeat_group_column,
            )
        )
    return resolved


def load_bindings(binding_csv: Path) -> list[SemanticBinding]:
    """Load target-column bindings from a semantic binding CSV.

    The preferred binding layout starts with the target definition table columns
    and adds semantic_path. In that layout, field_name is the emitted output column.
    """

    rows = read_csv_rows(binding_csv)
    repeated_classes: dict[str, SemanticClass] = {}
    for row in rows:
        row_type = (row.get("type") or "").strip().upper()
        semantic_path = (row.get("semantic_path") or "").strip()
        multiplicity = (row.get("multiplicity") or "").strip()
        if row_type == "C" and semantic_path and multiplicity_repeats(multiplicity):
            repeated_classes[semantic_path] = SemanticClass(
                semantic_path=semantic_path,
                multiplicity=multiplicity,
            )

    bindings: list[SemanticBinding] = []
    for row in rows:
        row_type = (row.get("type") or "").strip()
        if row_type and row_type.upper() != "A":
            continue
        semantic_path = (row.get("semantic_path") or "").strip()
        target_column = (
            row.get("target_column") or row.get("field_name") or row.get("target_name") or ""
        ).strip()
        normalized_path, repeat_group_path, repeat_index = indexed_semantic_path(semantic_path)
        if not target_column:
            continue
        bindings.append(
            SemanticBinding(
                sequence=sequence_number(row.get("sequence") or row.get("field_no") or ""),
                target_column=target_column,
                semantic_path=semantic_path,
                normalized_semantic_path=normalized_path,
                source_column=source_column_for_path(normalized_path),
                repeat_group_path=repeat_group_path,
                repeat_group_column=dimension_column_for_path(repeat_group_path),
                repeat_index=repeat_index,
                default_value=(row.get("default_value") or "").strip(),
                required=(row.get("required") or "").strip().lower() in {"yes", "true", "1"},
            )
        )
    bindings = sorted(bindings, key=lambda item: (item.sequence, item.target_column))
    return resolve_bindings_for_classes(bindings, repeated_classes)


def input_files(path: Path) -> list[Path]:
    """Return Structured CSV input files from a file or directory argument."""

    if path.is_file():
        return [path]
    if path.is_dir():
        return sorted(item for item in path.glob("*.csv") if item.is_file())
    raise FileNotFoundError(f"Input path does not exist: {path}")


def binding_target_stem(binding_csv: Path, fallback_stem: str) -> str:
    """Return the target file stem implied by a semantic binding file name."""

    match = TARGET_BINDING_RE.match(binding_csv.name)
    if match:
        return match.group("target")
    stem = binding_csv.stem
    for suffix in ("_Binding", "-Binding"):
        if stem.endswith(suffix):
            return stem[: -len(suffix)]
    return fallback_stem


def output_format_options(format_name: str, delimiter: str | None, extension: str | None) -> tuple[str, str]:
    """Return delimiter and extension after applying format presets and overrides."""

    presets = {
        "psv": ("|", ".psv"),
        "csv": (",", ".csv"),
    }
    preset_delimiter, preset_extension = presets[format_name]
    return delimiter if delimiter is not None else preset_delimiter, extension if extension is not None else preset_extension


def output_path(
    input_csv: Path,
    output_dir: Path,
    extension: str,
    output_filename: str | None,
    binding_csv: Path,
) -> Path:
    """Return the target output path for one input CSV."""

    if output_filename:
        return output_dir / output_filename
    suffix = extension if extension.startswith(".") else f".{extension}"
    target_stem = binding_target_stem(binding_csv, input_csv.stem)
    return output_dir / input_csv.stem / f"{target_stem}{suffix}"


def row_has_bound_data(row: dict[str, str], bindings: Iterable[SemanticBinding]) -> bool:
    """Return true when a Structured CSV row has data for the bound target view."""

    for binding in bindings:
        if not binding.source_column:
            continue
        if (row.get(binding.source_column) or binding.default_value or "").strip():
            return True
    return False


def empty_target_row(bindings: list[SemanticBinding]) -> dict[str, str]:
    """Create an empty target row with all bound target columns."""

    return {binding.target_column: "" for binding in bindings}


def row_scope_group(bindings: list[SemanticBinding]) -> tuple[str, str]:
    """Return the repeated group used to emit one target row per occurrence."""

    candidates: list[tuple[str, str]] = []
    for binding in bindings:
        if binding.repeat_index is not None:
            continue
        if not binding.repeat_group_path or not binding.repeat_group_column:
            continue
        candidates.append((binding.repeat_group_path, binding.repeat_group_column))
    if not candidates:
        return "", ""
    candidates.sort(key=lambda item: (-len(item[0]), item[0]))
    return candidates[0]


def repeated_group_present(source_row: dict[str, str], binding: SemanticBinding) -> bool:
    """Return true when a source row represents the binding's repeated group."""

    group_column = binding.repeat_group_column
    if group_column and (source_row.get(group_column) or "").strip():
        return True
    if group_column.startswith("d"):
        fallback_column = group_column[1:]
        if (source_row.get(fallback_column) or "").strip():
            return True
    return bool(binding.source_column and (source_row.get(binding.source_column) or "").strip())


def row_repeat_indices(
    source_row: dict[str, str],
    bindings: list[SemanticBinding],
    repeat_counts: dict[str, int],
) -> dict[str, int]:
    """Assign zero-based occurrence numbers to repeated groups in one source row."""

    indices: dict[str, int] = {}
    for binding in bindings:
        if binding.repeat_index is None or not binding.repeat_group_path:
            continue
        if binding.repeat_group_path in indices:
            continue
        if not repeated_group_present(source_row, binding):
            continue
        index = repeat_counts.get(binding.repeat_group_path, 0)
        indices[binding.repeat_group_path] = index
        repeat_counts[binding.repeat_group_path] = index + 1
    return indices


def merge_values(
    target_row: dict[str, str],
    source_row: dict[str, str],
    bindings: list[SemanticBinding],
    repeat_indices: dict[str, int],
) -> None:
    """Merge non-empty Structured CSV values into one target row."""

    for binding in bindings:
        if not binding.source_column:
            continue
        if binding.repeat_index is not None:
            if repeat_indices.get(binding.repeat_group_path) != binding.repeat_index:
                continue
        value = (source_row.get(binding.source_column) or "").strip()
        if not value:
            value = binding.default_value
        if value and not target_row.get(binding.target_column):
            target_row[binding.target_column] = value


def transform_rows(rows: list[dict[str, str]], bindings: list[SemanticBinding]) -> list[dict[str, str]]:
    """Apply semantic bindings and merge hierarchical child rows by invoice."""

    scope_path, scope_column = row_scope_group(bindings)
    if scope_path:
        return transform_repeated_group_rows(rows, bindings, scope_path, scope_column)

    output_rows: list[dict[str, str]] = []
    current_row: dict[str, str] | None = None
    repeat_counts: dict[str, int] = {}
    key_binding = next((binding for binding in bindings if binding.source_column), bindings[0])
    for row in rows:
        if not row_has_bound_data(row, bindings):
            continue
        starts_record = bool((row.get(key_binding.source_column) or "").strip())
        if starts_record or current_row is None:
            if current_row and any(value for value in current_row.values()):
                output_rows.append(current_row)
            current_row = empty_target_row(bindings)
            repeat_counts = {}
        repeat_indices = row_repeat_indices(row, bindings, repeat_counts)
        merge_values(current_row, row, bindings, repeat_indices)
    if current_row and any(value for value in current_row.values()):
        output_rows.append(current_row)
    return output_rows


def transform_repeated_group_rows(
    rows: list[dict[str, str]],
    bindings: list[SemanticBinding],
    scope_path: str,
    scope_column: str,
) -> list[dict[str, str]]:
    """Apply semantic bindings and emit one target row per repeated group row."""

    output_rows: list[dict[str, str]] = []
    parent_context = empty_target_row(bindings)
    current_group_row: dict[str, str] | None = None
    current_scope_value = ""
    repeat_counts: dict[str, int] = {}
    parent_bindings = [
        binding
        for binding in bindings
        if binding.repeat_group_path != scope_path or binding.repeat_index is not None
    ]
    scoped_bindings = [
        binding
        for binding in bindings
        if binding.repeat_group_path == scope_path and binding.repeat_index is None
    ]

    for row in rows:
        if not row_has_bound_data(row, bindings):
            continue
        if (row.get("dInvoice") or "").strip() and not (row.get(scope_column) or "").strip():
            merge_values(parent_context, row, parent_bindings, {})
            continue
        if not (row.get(scope_column) or "").strip():
            continue
        scope_value = (row.get(scope_column) or "").strip()
        starts_group = scope_value != current_scope_value
        if starts_group or current_group_row is None:
            if current_group_row and any(value for value in current_group_row.values()):
                output_rows.append(current_group_row)
            current_group_row = dict(parent_context)
            current_scope_value = scope_value
            repeat_counts = {}
        repeat_indices = row_repeat_indices(row, scoped_bindings, repeat_counts)
        merge_values(current_group_row, row, scoped_bindings, repeat_indices)

    if current_group_row and any(value for value in current_group_row.values()):
        output_rows.append(current_group_row)
    return output_rows


def write_target_file(path: Path, rows: list[dict[str, str]], fieldnames: list[str], delimiter: str) -> None:
    """Write target rows as a delimited text file."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            delimiter=delimiter,
            lineterminator="\n",
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def convert_file(
    input_csv: Path,
    output_dir: Path,
    bindings: list[SemanticBinding],
    delimiter: str,
    extension: str,
    output_filename: str | None,
    binding_csv: Path,
) -> Path:
    """Convert one Structured CSV file to one target delimited file."""

    rows = read_csv_rows(input_csv)
    target_rows = transform_rows(rows, bindings)
    fieldnames = [binding.target_column for binding in bindings]
    target_path = output_path(input_csv, output_dir, extension, output_filename, binding_csv)
    write_target_file(target_path, target_rows, fieldnames, delimiter)
    return target_path


def main() -> int:
    """Run the semantic binding conversion."""

    args = parse_args()
    files = input_files(args.input)
    if args.output_filename and len(files) != 1:
        raise ValueError("--output-filename can be used only with one input CSV file.")

    delimiter, extension = output_format_options(args.format, args.delimiter, args.extension)
    bindings = load_bindings(args.binding_csv)
    if not bindings:
        raise ValueError(f"No target fact bindings found in {args.binding_csv}")

    generated: list[Path] = []
    for input_csv in files:
        generated.append(
            convert_file(
                input_csv=input_csv,
                output_dir=args.output_dir,
                bindings=bindings,
                delimiter=delimiter,
                extension=extension,
                output_filename=args.output_filename,
                binding_csv=args.binding_csv,
            )
        )
    for path in generated:
        print(f"Wrote {path}")
    print(f"ok: generated {len(generated)} semantic binding output file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
