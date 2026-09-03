#!/usr/bin/env python3
"""Canonical 16-column Flat CSV converter.

The Binding Table and HMD are the only structural definitions used by this
module.  Physical accounting values are never included in diagnostics or
summary output.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, Mapping, Sequence


CANONICAL_FIELDS = (
    "sequence",
    "level",
    "type",
    "name",
    "datatype",
    "multiplicity",
    "column",
    "semantic_path",
    "occurrence_mode",
    "group_key",
    "row_role",
    "max_occurs",
    "default_value",
    "transformation",
    "required",
    "note",
)
LEGACY_17_FIELDS = (
    "sequence", "level", "type", "id", "name", "datatype", "multiplicity",
    "column", "semantic_path", "occurrence_mode", "group_key", "row_role",
    "max_occurs", "default_value", "transformation", "required", "note",
)
STRUCTURED_FIELDS = (
    "entry_key",
    "source_row",
    "occurrence",
    "sequence",
    "level",
    "type",
    "id",
    "name",
    "semantic_path",
    "binding_path",
    "value",
)
OIM_CONTROL_FIELDS = ("concept", "unit", "decimals")
COLUMN_RE = re.compile(r"^C([1-9][0-9]*)$")
LEGACY_COLUMN_RE = re.compile(r"^Column([1-9][0-9]*)$")
SELECTOR_RE = re.compile(r"\[[^\]]+\]")
SUPPORTED_MODES = {"", "single", "source_rows", "keyed_rows", "marker_rows"}
SUPPORTED_ROLES = {"", "group", "driver", "header", "presence"}
TRUE_VALUES = {"1", "true", "yes", "y"}
FALSE_VALUES = {"", "0", "false", "no", "n"}
TRANSFORMATION_NAMES = {"", "jp_era_date_to_iso", "iso_date_to_yyyymmdd"}
MATERIALIZATION_MODES = {
    "source_rows",
    "balanced_single_counterpart",
    "exact_unique_amount_pairing",
}
PHYSICAL_HEADER_TYPE = "P"
CODE_MAP_FIELDS = ("map_name", "semantic_value", "physical_value")
ERA_START = {"M": 1868, "T": 1912, "S": 1926, "H": 1989, "R": 2019}


class ConversionError(Exception):
    """A classified error whose text is safe for stderr."""

    def __init__(self, kind: str, message: str):
        super().__init__(message)
        self.kind = kind
        self.message = message

    def __str__(self) -> str:
        return f"{self.kind}: {self.message}"


@dataclass(frozen=True)
class BindingRow:
    order: int
    values: Mapping[str, str]

    @property
    def sequence(self) -> int:
        return int(self.values["sequence"])

    @property
    def level(self) -> int:
        return int(self.values["level"])

    @property
    def path(self) -> str:
        return self.values["semantic_path"]

    @property
    def neutral_path(self) -> str:
        return SELECTOR_RE.sub("", self.path)

    @property
    def max_occurs(self) -> int | None:
        raw = self.values["max_occurs"]
        return int(raw) if raw else None

    @property
    def is_required(self) -> bool:
        return self.values["required"].lower() in TRUE_VALUES


@dataclass(frozen=True)
class GroupSpec:
    mode: str
    columns: tuple[str, ...] = ()
    marker_column: str = ""
    single: str = ""
    start: str = ""
    continuation: str = ""
    end: str = ""


@dataclass(frozen=True)
class ConversionOptions:
    input_path: Path
    output_path: Path
    hmd_path: Path
    binding_path: Path
    definition_encoding: str = "utf-8-sig"
    input_encoding: str = "utf-8-sig"
    output_encoding: str = "utf-8"
    profile_width: int | None = None
    summary_log: Path | None = None
    metadata_output: Path | None = None
    taxonomy_entrypoint: Path | None = None
    entity: str = "scheme:UADC-PoC"
    period: str = "2026-12-31T00:00:00"
    currency: str = "iso4217:JPY"
    data_start_row: int = 1
    input_header_rows: int = 0
    output_header: bool = False
    materialization_mode: str = "source_rows"
    code_map_paths: tuple[Path, ...] = ()
    debug: bool = False
    trace: bool = False


@dataclass(frozen=True)
class ConversionSummary:
    source_rows: int
    profile_width: int
    structured_rows: int = 0
    shared_column_overwrite_total: int = 0
    shared_column_overwrites: Mapping[str, int] | None = None
    materialization_mode: str = "source_rows"
    materialized_1_1: int = 0
    materialized_n_1: int = 0
    materialized_1_n: int = 0
    materialized_exact_unique_n_m: int = 0

    def as_dict(self) -> dict[str, object]:
        return {
            "source_rows": self.source_rows,
            "profile_width": self.profile_width,
            "structured_rows": self.structured_rows,
            "shared_column_overwrite_total": self.shared_column_overwrite_total,
            "shared_column_overwrites": dict(self.shared_column_overwrites or {}),
            "materialization_mode": self.materialization_mode,
            "materialized_1_1": self.materialized_1_1,
            "materialized_n_1": self.materialized_n_1,
            "materialized_1_n": self.materialized_1_n,
            "materialized_exact_unique_n_m": self.materialized_exact_unique_n_m,
        }


@dataclass(frozen=True)
class Definition:
    rows: tuple[BindingRow, ...]
    hmd_sequences: Mapping[str, int]
    hmd_rows: Mapping[str, Mapping[str, str]]
    header_group: BindingRow
    group_spec: GroupSpec
    driver: BindingRow
    variants: tuple[str, ...]
    max_bound_column: int
    physical_headers: Mapping[int, str]
    code_maps: Mapping[str, tuple[Mapping[str, str], Mapping[str, str]]]


def _upper_camel(value: str) -> str:
    value = (value or "").strip()
    return f"{value[:1].upper()}{value[1:]}" if value else ""


def _repeats(multiplicity: str) -> bool:
    upper = (multiplicity or "").strip().rsplit("..", 1)[-1].lower()
    if upper in {"*", "n", "unbounded"}:
        return True
    try:
        return int(upper) > 1
    except ValueError:
        return False


def _column_number(column: str) -> int | None:
    match = COLUMN_RE.fullmatch(column)
    return int(match.group(1)) if match else None


def _legacy_column_to_cn(value: str) -> str:
    return LEGACY_COLUMN_RE.sub(lambda match: f"C{match.group(1)}", value)


def _parse_positive_int(raw: str, field: str) -> int:
    try:
        value = int(raw)
    except ValueError as exc:
        raise ConversionError("DEFINITION_INVALID", f"{field} must be a positive integer") from exc
    if value <= 0:
        raise ConversionError("DEFINITION_INVALID", f"{field} must be a positive integer")
    return value


def _variant_for(row: BindingRow, driver_path: str) -> str:
    prefix = driver_path + "["
    if not row.path.startswith(prefix):
        return ""
    end = row.path.find("]", len(prefix))
    if end < 0:
        raise ConversionError("DEFINITION_INVALID", "a driver selector is not closed")
    predicate = row.path[len(prefix) : end].strip()
    match = re.fullmatch(r"[^=]+=['\"]([^'\"]+)['\"]", predicate)
    if not match:
        raise ConversionError("DEFINITION_INVALID", "a driver selector is invalid")
    return match.group(1)


def _parse_group_spec(row: BindingRow) -> GroupSpec:
    raw = row.values["group_key"]
    try:
        config = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ConversionError("GROUP_KEY_INVALID", "group_key must be valid JSON") from exc

    if row.values["occurrence_mode"] == "keyed_rows":
        if not isinstance(config, list) or not config:
            raise ConversionError(
                "GROUP_KEY_INVALID", "keyed_rows group_key must be a non-empty Cn array"
            )
        columns = tuple(str(item) for item in config)
        if any(_column_number(column) is None for column in columns):
            raise ConversionError(
                "GROUP_KEY_INVALID", "keyed_rows group_key must contain only Cn names"
            )
        if len(set(columns)) != len(columns):
            raise ConversionError("GROUP_KEY_INVALID", "keyed_rows group columns must be unique")
        return GroupSpec(mode="keyed_rows", columns=columns)

    required_keys = {"marker_column", "single", "start", "continue", "end"}
    if not isinstance(config, dict) or set(config) != required_keys:
        raise ConversionError(
            "GROUP_KEY_INVALID",
            "marker_rows group_key must contain marker_column, single, start, continue, end",
        )
    marker_column = str(config["marker_column"])
    if _column_number(marker_column) is None:
        raise ConversionError("GROUP_KEY_INVALID", "marker_column must be a Cn name")
    codes = tuple(str(config[key]) for key in ("single", "start", "continue", "end"))
    if any(not code for code in codes) or len(set(codes)) != 4:
        raise ConversionError(
            "GROUP_KEY_INVALID", "marker control codes must be distinct and non-empty"
        )
    return GroupSpec(
        mode="marker_rows",
        marker_column=marker_column,
        single=codes[0],
        start=codes[1],
        continuation=codes[2],
        end=codes[3],
    )


def load_binding(path: Path, encoding: str = "utf-8-sig") -> list[BindingRow]:
    try:
        with path.open(newline="", encoding=encoding) as stream:
            reader = csv.reader(stream)
            header = tuple(next(reader, ()))
            if header == CANONICAL_FIELDS:
                source_fields = CANONICAL_FIELDS
                legacy_17 = False
            elif header == LEGACY_17_FIELDS:
                source_fields = LEGACY_17_FIELDS
                legacy_17 = True
            else:
                raise ConversionError(
                    "BINDING_HEADER_INVALID", "Binding header must exactly match the canonical 16 columns"
                )
            rows: list[BindingRow] = []
            for order, values in enumerate(reader):
                if len(values) != len(source_fields):
                    raise ConversionError(
                        "BINDING_ROW_INVALID", "a Binding row does not match its declared contract"
                    )
                normalized = {
                    name: value.strip()
                    for name, value in zip(source_fields, values)
                    if name != "id"
                }
                if legacy_17:
                    normalized["column"] = _legacy_column_to_cn(normalized["column"])
                    normalized["group_key"] = _legacy_column_to_cn(normalized["group_key"])
                rows.append(
                    BindingRow(
                        order=order,
                        values=normalized,
                    )
                )
    except ConversionError:
        raise
    except (OSError, UnicodeError, csv.Error) as exc:
        raise ConversionError("DEFINITION_IO_ERROR", "Binding could not be read") from exc
    if not rows:
        raise ConversionError("DEFINITION_INVALID", "Binding must contain at least one row")
    return rows


def load_hmd_rows(path: Path, encoding: str = "utf-8-sig") -> dict[str, dict[str, str]]:
    try:
        with path.open(newline="", encoding=encoding) as stream:
            reader = csv.DictReader(stream)
            fields = tuple(reader.fieldnames or ())
            if "semantic_path" not in fields or "sequence" not in fields:
                raise ConversionError(
                    "HMD_HEADER_INVALID", "HMD must contain semantic_path and sequence columns"
                )
            definitions: dict[str, dict[str, str]] = {}
            for source in reader:
                path_value = (source.get("semantic_path") or "").strip()
                if not path_value:
                    continue
                sequence_raw = (source.get("sequence") or "").strip()
                try:
                    sequence = int(sequence_raw)
                except ValueError as exc:
                    raise ConversionError("HMD_ROW_INVALID", "an HMD sequence is not an integer") from exc
                if path_value in definitions:
                    raise ConversionError("HMD_ROW_INVALID", "HMD semantic_path values must be unique")
                definitions[path_value] = {
                    key: (value or "").strip() for key, value in source.items() if key is not None
                }
    except ConversionError:
        raise
    except (OSError, UnicodeError, csv.Error) as exc:
        raise ConversionError("DEFINITION_IO_ERROR", "HMD could not be read") from exc
    if not definitions:
        raise ConversionError("HMD_ROW_INVALID", "HMD contains no usable semantic paths")
    return definitions


def load_hmd(path: Path, encoding: str = "utf-8-sig") -> dict[str, int]:
    return {
        semantic_path: int(row["sequence"])
        for semantic_path, row in load_hmd_rows(path, encoding).items()
    }


def validate_definition(
    rows: Sequence[BindingRow],
    hmd_sequences: Mapping[str, int],
    hmd_rows: Mapping[str, Mapping[str, str]] | None = None,
    code_maps: Mapping[str, tuple[Mapping[str, str], Mapping[str, str]]] | None = None,
) -> Definition:
    physical_columns: list[str] = []
    semantic_rows: list[BindingRow] = []
    physical_headers: dict[int, str] = {}
    for row in rows:
        for field in ("sequence", "level"):
            _parse_positive_int(row.values[field], field)
        if row.values["type"] == PHYSICAL_HEADER_TYPE:
            column = row.values["column"]
            number = _column_number(column)
            if (
                row.values["row_role"] != "header"
                or number is None
                or not row.values["name"]
                or row.path
                or row.values["transformation"]
                or row.values["default_value"]
                or row.values["required"].lower() not in FALSE_VALUES
            ):
                raise ConversionError(
                    "PHYSICAL_HEADER_INVALID",
                    "physical header rows require type P, row_role header, Cn, name, and no semantic value contract",
                )
            if number in physical_headers:
                raise ConversionError(
                    "PHYSICAL_HEADER_DUPLICATE", "a physical header column is declared more than once"
                )
            physical_headers[number] = row.values["name"]
            continue
        semantic_rows.append(row)
        if not row.path:
            raise ConversionError("DEFINITION_INVALID", "semantic_path must not be empty")
        if row.values["occurrence_mode"] not in SUPPORTED_MODES:
            raise ConversionError("DEFINITION_INVALID", "occurrence_mode is unsupported")
        if row.values["row_role"] not in SUPPORTED_ROLES:
            raise ConversionError("DEFINITION_INVALID", "row_role is unsupported")
        required = row.values["required"].lower()
        if required not in TRUE_VALUES | FALSE_VALUES:
            raise ConversionError("DEFINITION_INVALID", "required must be a recognized boolean")
        if row.values["max_occurs"]:
            _parse_positive_int(row.values["max_occurs"], "max_occurs")
        transformation = row.values["transformation"]
        if transformation not in TRANSFORMATION_NAMES and not transformation.startswith("code_map:"):
            raise ConversionError(
                "TRANSFORMATION_UNSUPPORTED", "Binding contains an unsupported transformation"
            )
        column = row.values["column"]
        if column:
            if _column_number(column) is None:
                raise ConversionError(
                    "PHYSICAL_COLUMN_INVALID", "physical columns must use positive Cn names"
                )
            physical_columns.append(column)
        hmd_sequence = hmd_sequences.get(row.neutral_path)
        if hmd_sequence is None:
            raise ConversionError("HMD_PATH_UNRESOLVED", "a Binding semantic_path is absent from HMD")
        if hmd_sequence != row.sequence:
            raise ConversionError(
                "SEQUENCE_MISMATCH", "Binding and HMD sequence values do not match"
            )

    duplicates = sorted(
        column for column, count in Counter(physical_columns).items() if count > 1
    )
    if duplicates:
        raise ConversionError(
            "PHYSICAL_COLUMN_DUPLICATE", "a physical column is assigned more than once"
        )

    referenced_maps = {
        row.values["transformation"].split(":", 1)[1]
        for row in semantic_rows
        if row.values["transformation"].startswith("code_map:")
    }
    if "" in referenced_maps or not referenced_maps.issubset(set(code_maps or {})):
        raise ConversionError("CODE_MAP_UNRESOLVED", "a Binding code-map reference is unavailable")

    drivers = [row for row in semantic_rows if row.values["row_role"] == "driver"]
    if len(drivers) != 1:
        raise ConversionError("DRIVER_INVALID", "exactly one driver row is required")
    driver = drivers[0]
    if driver.values["occurrence_mode"] != "source_rows":
        raise ConversionError("DRIVER_INVALID", "the driver must use source_rows")

    header_groups = [
        row for row in semantic_rows if row.values["occurrence_mode"] in {"keyed_rows", "marker_rows"}
    ]
    if len(header_groups) != 1:
        raise ConversionError(
            "HEADER_GROUP_INVALID", "exactly one keyed_rows or marker_rows header group is required"
        )
    header_group = header_groups[0]
    if header_group.values["row_role"] != "group":
        raise ConversionError("HEADER_GROUP_INVALID", "the header group must have row_role group")
    group_spec = _parse_group_spec(header_group)
    if group_spec.marker_column and group_spec.marker_column in physical_columns:
        raise ConversionError(
            "PHYSICAL_COLUMN_DUPLICATE", "marker control column cannot also hold a semantic value"
        )

    variants: list[str] = []
    for row in semantic_rows:
        variant = _variant_for(row, driver.path)
        if variant and variant not in variants:
            variants.append(variant)
    if not variants:
        raise ConversionError("DRIVER_INVALID", "driver has no selector variants")

    max_bound = max((_column_number(column) or 0 for column in physical_columns), default=0)
    max_bound = max([max_bound, *physical_headers.keys()], default=max_bound)
    marker_number = _column_number(group_spec.marker_column) if group_spec.marker_column else 0
    key_numbers = [_column_number(column) or 0 for column in group_spec.columns]
    max_bound = max([max_bound, marker_number or 0, *key_numbers])
    return Definition(
        rows=tuple(semantic_rows),
        hmd_sequences=dict(hmd_sequences),
        hmd_rows=dict(hmd_rows or {}),
        header_group=header_group,
        group_spec=group_spec,
        driver=driver,
        variants=tuple(variants),
        max_bound_column=max_bound,
        physical_headers=dict(sorted(physical_headers.items())),
        code_maps=dict(code_maps or {}),
    )


def _definition(options: ConversionOptions) -> Definition:
    rows = load_binding(options.binding_path, options.definition_encoding)
    hmd_rows = load_hmd_rows(options.hmd_path, options.definition_encoding)
    hmd_sequences = {path: int(row["sequence"]) for path, row in hmd_rows.items()}
    code_maps = load_code_maps(options.code_map_paths, options.definition_encoding)
    return validate_definition(rows, hmd_sequences, hmd_rows, code_maps)


def load_code_maps(
    paths: Sequence[Path], encoding: str = "utf-8-sig"
) -> dict[str, tuple[dict[str, str], dict[str, str]]]:
    semantic_to_physical: dict[str, dict[str, str]] = defaultdict(dict)
    physical_to_semantic: dict[str, dict[str, str]] = defaultdict(dict)
    for path in paths:
        try:
            with path.open(newline="", encoding=encoding) as stream:
                reader = csv.DictReader(stream)
                if tuple(reader.fieldnames or ()) != CODE_MAP_FIELDS:
                    raise ConversionError(
                        "CODE_MAP_HEADER_INVALID",
                        "code-map header must exactly match the canonical three columns",
                    )
                for source in reader:
                    map_name = (source.get("map_name") or "").strip()
                    semantic = (source.get("semantic_value") or "").strip()
                    physical = (source.get("physical_value") or "").strip()
                    if not map_name or not semantic or not physical:
                        raise ConversionError("CODE_MAP_ROW_INVALID", "code-map values must not be empty")
                    if semantic in semantic_to_physical[map_name] or physical in physical_to_semantic[map_name]:
                        raise ConversionError("CODE_MAP_DUPLICATE", "code-map values must be one-to-one")
                    semantic_to_physical[map_name][semantic] = physical
                    physical_to_semantic[map_name][physical] = semantic
        except ConversionError:
            raise
        except (OSError, UnicodeError, csv.Error) as exc:
            raise ConversionError("DEFINITION_IO_ERROR", "code-map could not be read") from exc
    return {
        name: (semantic_to_physical[name], physical_to_semantic[name])
        for name in sorted(semantic_to_physical)
    }


def _resolved_width(definition: Definition, requested: int | None) -> int:
    if requested is not None and requested <= 0:
        raise ConversionError("PROFILE_WIDTH_INVALID", "profile-width must be a positive integer")
    width = requested or definition.max_bound_column
    if width < definition.max_bound_column:
        raise ConversionError(
            "PROFILE_WIDTH_INVALID", "profile-width is smaller than a referenced physical column"
        )
    return width


def _physical_header(definition: Definition, width: int) -> list[str]:
    missing = [number for number in range(1, width + 1) if number not in definition.physical_headers]
    if missing:
        raise ConversionError(
            "PHYSICAL_HEADER_INCOMPLETE",
            "physical header declarations do not cover the configured profile width",
        )
    return [definition.physical_headers[number] for number in range(1, width + 1)]


def _read_flat_rows(
    path: Path,
    encoding: str,
    width: int,
    expected_header: Sequence[str] | None = None,
    header_rows: int = 0,
) -> list[list[str]]:
    try:
        with path.open(newline="", encoding=encoding) as stream:
            rows = [list(row) for row in csv.reader(stream)]
    except (OSError, UnicodeError, csv.Error) as exc:
        raise ConversionError("INPUT_IO_ERROR", "Flat CSV input could not be read") from exc
    for index, row in enumerate(rows, 1):
        if len(row) != width:
            raise ConversionError(
                "PROFILE_WIDTH_MISMATCH",
                f"source row {index} does not contain the configured number of columns",
            )
    if header_rows:
        if len(rows) < header_rows:
            raise ConversionError("INPUT_HEADER_MISSING", "Flat CSV input does not contain a header row")
        if expected_header is not None and rows[0] != list(expected_header):
            raise ConversionError(
                "INPUT_HEADER_MISMATCH", "Flat CSV input header does not match Binding declarations"
            )
        rows = rows[header_rows:]
    return rows


def _transform_forward(
    name: str,
    value: str,
    code_maps: Mapping[str, tuple[Mapping[str, str], Mapping[str, str]]],
) -> str:
    if not value or not name:
        return value
    if name == "jp_era_date_to_iso":
        match = re.fullmatch(r"([MTSHR])\.(\d{1,2})/(\d{1,2})/(\d{1,2})", value)
        if not match:
            raise ConversionError(
                "TRANSFORMATION_VALUE_INVALID", "a value does not match the configured date format"
            )
        era, year, month, day = match.groups()
        try:
            western_year = ERA_START[era] + int(year) - 1
            return date(western_year, int(month), int(day)).isoformat()
        except ValueError as exc:
            raise ConversionError(
                "TRANSFORMATION_VALUE_INVALID", "a transformed date is invalid"
            ) from exc
    if name == "iso_date_to_yyyymmdd":
        if not re.fullmatch(r"\d{8}", value):
            raise ConversionError(
                "TRANSFORMATION_VALUE_INVALID", "a value does not match the configured compact date format"
            )
        try:
            return date(int(value[:4]), int(value[4:6]), int(value[6:8])).isoformat()
        except ValueError as exc:
            raise ConversionError("TRANSFORMATION_VALUE_INVALID", "a transformed date is invalid") from exc
    if name.startswith("code_map:"):
        map_name = name.split(":", 1)[1]
        mapped = code_maps[map_name][1].get(value)
        if mapped is None:
            raise ConversionError("CODE_MAP_VALUE_UNRESOLVED", "a physical value is absent from its code-map")
        return mapped
    raise ConversionError("TRANSFORMATION_UNSUPPORTED", "transformation is unsupported")


def _transform_reverse(
    name: str,
    value: str,
    code_maps: Mapping[str, tuple[Mapping[str, str], Mapping[str, str]]],
) -> str:
    if not value or not name:
        return value
    if name == "jp_era_date_to_iso":
        try:
            parsed = date.fromisoformat(value)
        except ValueError as exc:
            raise ConversionError(
                "TRANSFORMATION_VALUE_INVALID", "a reverse date value is invalid"
            ) from exc
        eras = sorted(ERA_START.items(), key=lambda item: item[1], reverse=True)
        selected = next((item for item in eras if parsed.year >= item[1]), None)
        if selected is None:
            raise ConversionError(
                "TRANSFORMATION_VALUE_INVALID", "a reverse date predates supported eras"
            )
        era, start = selected
        return f"{era}.{parsed.year - start + 1:02d}/{parsed.month:02d}/{parsed.day:02d}"
    if name == "iso_date_to_yyyymmdd":
        try:
            return date.fromisoformat(value).strftime("%Y%m%d")
        except ValueError as exc:
            raise ConversionError("TRANSFORMATION_VALUE_INVALID", "a reverse date value is invalid") from exc
    if name.startswith("code_map:"):
        map_name = name.split(":", 1)[1]
        mapped = code_maps[map_name][0].get(value)
        if mapped is None:
            raise ConversionError("CODE_MAP_VALUE_UNRESOLVED", "a semantic value is absent from its code-map")
        return mapped
    raise ConversionError("TRANSFORMATION_UNSUPPORTED", "transformation is unsupported")


def _value_for(
    row: BindingRow,
    source: Sequence[str],
    code_maps: Mapping[str, tuple[Mapping[str, str], Mapping[str, str]]],
) -> str:
    column = row.values["column"]
    if column:
        number = _column_number(column)
        assert number is not None
        value = source[number - 1]
    else:
        value = row.values["default_value"]
    return _transform_forward(row.values["transformation"], value, code_maps)


def group_source_rows(
    source_rows: Sequence[list[str]], spec: GroupSpec
) -> list[tuple[str, list[tuple[int, list[str]]]]]:
    if spec.mode == "keyed_rows":
        grouped: dict[str, list[tuple[int, list[str]]]] = {}
        for source_index, source in enumerate(source_rows, 1):
            key_values: list[str] = []
            for column in spec.columns:
                number = _column_number(column)
                assert number is not None
                value = source[number - 1]
                if not value:
                    raise ConversionError(
                        "GROUP_KEY_EMPTY", f"group key {column} is empty at source row {source_index}"
                    )
                key_values.append(value)
            key = json.dumps(key_values, ensure_ascii=False, separators=(",", ":"))
            grouped.setdefault(key, []).append((source_index, source))
        return list(grouped.items())

    marker_number = _column_number(spec.marker_column)
    assert marker_number is not None
    groups: list[tuple[str, list[tuple[int, list[str]]]]] = []
    current: list[tuple[int, list[str]]] | None = None
    for source_index, source in enumerate(source_rows, 1):
        marker = source[marker_number - 1]
        if marker == spec.single:
            if current is not None:
                raise ConversionError("MARKER_NESTED", "a single marker occurred inside an open group")
            groups.append((json.dumps(["marker", len(groups) + 1]), [(source_index, source)]))
        elif marker == spec.start:
            if current is not None:
                raise ConversionError("MARKER_NESTED", "a marker group is nested")
            current = [(source_index, source)]
        elif marker == spec.continuation:
            if current is None:
                raise ConversionError("MARKER_SEQUENCE", "a continuation marker has no start")
            current.append((source_index, source))
        elif marker == spec.end:
            if current is None:
                raise ConversionError("MARKER_SEQUENCE", "an end marker has no start")
            current.append((source_index, source))
            groups.append((json.dumps(["marker", len(groups) + 1]), current))
            current = None
        else:
            raise ConversionError("MARKER_UNKNOWN", "an unknown marker was found")
    if current is not None:
        raise ConversionError("MARKER_UNCLOSED", "a marker group is not closed")
    return groups


def _header_source(
    grouped_rows: Sequence[tuple[int, list[str]]],
    header_rows: Sequence[BindingRow],
    width: int,
) -> list[str]:
    selected = grouped_rows[0][1].copy() if grouped_rows else [""] * width
    for row in header_rows:
        number = _column_number(row.values["column"])
        if number is None:
            continue
        nonempty = {source[number - 1] for _, source in grouped_rows if source[number - 1]}
        if len(nonempty) > 1:
            raise ConversionError(
                "SHARED_COLUMN_CONFLICT", "a header column changes within one group"
            )
        if nonempty:
            selected[number - 1] = next(iter(nonempty))
    return selected


def _active_rows(
    rows: Sequence[BindingRow],
    source: Sequence[str],
    driver: BindingRow,
    code_maps: Mapping[str, tuple[Mapping[str, str], Mapping[str, str]]],
) -> list[BindingRow]:
    suppressed: list[str] = []
    for row in rows:
        if row.values["type"] != "C" or row.path == driver.path:
            continue
        descendants = [candidate for candidate in rows if candidate.path.startswith(row.path + ".")]
        physical = [candidate for candidate in descendants if candidate.values["column"]]
        if physical and not any(_value_for(candidate, source, code_maps) for candidate in physical):
            suppressed.append(row.path)
    return [
        row
        for row in rows
        if not any(row.path == prefix or row.path.startswith(prefix + ".") for prefix in suppressed)
    ]


def _require_value(row: BindingRow, value: str) -> None:
    if row.is_required and row.values["type"] == "A" and not value:
        raise ConversionError("REQUIRED_VALUE_MISSING", "a required Binding value is empty")


def _structured_record(
    row: BindingRow, entry_key: str, source_row: str, occurrence: str, value: str
) -> dict[str, str]:
    return {
        "entry_key": entry_key,
        "source_row": source_row,
        "occurrence": occurrence,
        "sequence": f"{row.sequence:04d}",
        "level": row.values["level"],
        "type": row.values["type"],
        "id": row.values.get("id", ""),
        "name": row.values["name"],
        "semantic_path": row.neutral_path,
        "binding_path": row.path,
        "value": value,
    }


def _write_structured(path: Path, rows: Iterable[Mapping[str, str]], encoding: str) -> None:
    row_list = list(rows)
    keys = {key for row in row_list for key in row}
    if set(STRUCTURED_FIELDS).issubset(keys):
        fieldnames = list(STRUCTURED_FIELDS)
        fieldnames.extend(sorted(keys - set(STRUCTURED_FIELDS)))
    else:
        fieldnames = [field for field in ("concept", "unit", "value") if field in keys]
        fieldnames.extend(sorted(keys - set(fieldnames)))
    try:
        with path.open("w", newline="", encoding=encoding) as stream:
            writer = csv.DictWriter(stream, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(row_list)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise ConversionError("OUTPUT_IO_ERROR", "Structured CSV output could not be written") from exc


def _relative_uri(target: Path, metadata: Path) -> str:
    import os

    return Path(os.path.relpath(target.resolve(), metadata.resolve().parent)).as_posix()


def _selector_value(binding_path: str, class_path: str) -> str:
    binding_parts = binding_path.split(".")
    class_parts = class_path.split(".")
    if len(binding_parts) < len(class_parts):
        return ""
    for binding_part, class_part in zip(binding_parts, class_parts):
        if binding_part.split("[", 1)[0] != class_part:
            return ""
    target_part = binding_parts[len(class_parts) - 1]
    tail = target_part[len(class_parts[-1]) :]
    match = re.match(r"\[[^=\]]+=(?:\"([^\"]*)\"|'([^']*)')\]", tail)
    return (match.group(1) or match.group(2) or "") if match else ""


def _occurrence_value(record: Mapping[str, str], class_path: str) -> str:
    local = class_path.rsplit(".", 1)[-1].split("_", 1)[-1].lower()
    if local == "accountingentries":
        return "1"
    if local == "entryheader":
        return (record.get("entry_key") or "1").strip()
    if local == "entrydetail":
        source_row = (record.get("source_row") or "1").strip()
        occurrence = (record.get("occurrence") or "1").strip()
        return f"{source_row}-{occurrence}"
    selector = _selector_value(record.get("binding_path") or "", class_path)
    return selector or "1"


def _oim_records(
    records: Sequence[Mapping[str, str]], definition: Definition, currency: str
) -> tuple[list[dict[str, str]], list[str], dict[str, str]]:
    repeated_classes = [
        (path, row)
        for path, row in definition.hmd_rows.items()
        if (row.get("type") or "").upper() == "C" and _repeats(row.get("multiplicity") or "")
    ]
    repeated_classes.sort(key=lambda item: (item[0].count("."), item[0]))
    output: list[dict[str, str]] = []
    namespaces: dict[str, str] = {}
    dimension_columns: set[str] = set()
    for source in records:
        if (source.get("type") or "").upper() != "A":
            continue
        if not (source.get("value") or ""):
            continue
        semantic_path = (source.get("semantic_path") or "").strip()
        hmd = definition.hmd_rows.get(semantic_path)
        if hmd is None:
            raise ConversionError("HMD_PATH_UNRESOLVED", "Structured semantic_path is absent from HMD")
        module = hmd.get("module") or hmd.get("associated_module") or ""
        local_name = hmd.get("local_name") or ""
        if not module or not local_name:
            raise ConversionError("HMD_ROW_INVALID", "HMD module/local_name is required for OIM output")
        target = {
            "concept": f"{module}:{local_name}",
            "unit": currency if (hmd.get("datatype") or "").lower() == "monetary" else "",
            "value": source.get("value") or "",
        }
        namespaces[module] = (
            f"https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/"
            f"experimental/{module}/2026-12-31"
        )
        for class_path, class_row in repeated_classes:
            if semantic_path == class_path or not semantic_path.startswith(class_path + "."):
                continue
            class_module = class_row.get("module") or class_row.get("associated_module") or ""
            class_local = class_row.get("local_name") or ""
            if not class_module or not class_local:
                raise ConversionError("HMD_ROW_INVALID", "repeated HMD Class lacks module/local_name")
            column = f"d_{class_module}_{class_local}"
            target[column] = _occurrence_value(source, class_path)
            dimension_columns.add(column)
        output.append(target)
    return output, sorted(dimension_columns), namespaces


def _write_oim_metadata(
    metadata_path: Path,
    csv_path: Path,
    taxonomy_entrypoint: Path,
    dimension_columns: Sequence[str],
    namespaces: Mapping[str, str],
    entity: str,
    period: str,
) -> None:
    version_match = re.search(r"(\d{4}-\d{2}-\d{2})", taxonomy_entrypoint.name)
    version = version_match.group(1) if version_match else "2026-12-31"
    namespace_map = {
        **dict(sorted(namespaces.items())),
        "plt": (
            f"https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/"
            f"experimental/plt/{version}"
        ),
        "iso4217": "http://www.xbrl.org/2003/iso4217",
        "scheme": "http://www.example.com",
        "xbrl": "https://xbrl.org/2021",
    }
    dimensions = {
        "period": period,
        "entity": entity,
        **{f"plt:{column}": f"${column}" for column in dimension_columns},
    }
    columns: dict[str, object] = {
        "concept": {},
        "unit": {},
        "value": {"dimensions": {"concept": "$concept", "unit": "$unit"}},
    }
    columns.update({column: {} for column in dimension_columns})
    metadata = {
        "documentInfo": {
            "documentType": "https://xbrl.org/2021/xbrl-csv",
            "namespaces": namespace_map,
            "taxonomy": [_relative_uri(taxonomy_entrypoint, metadata_path)],
        },
        "tables": {"structured": {"template": "structured", "url": _relative_uri(csv_path, metadata_path)}},
        "tableTemplates": {"structured": {"dimensions": dimensions, "columns": columns}},
    }
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def convert_to_structured(options: ConversionOptions) -> ConversionSummary:
    definition = _definition(options)
    width = _resolved_width(definition, options.profile_width)
    expected_header = _physical_header(definition, width) if options.input_header_rows else None
    source_rows = _read_flat_rows(
        options.input_path,
        options.input_encoding,
        width,
        expected_header,
        (options.data_start_row - 1) if options.data_start_row != 1 else options.input_header_rows,
    )
    groups = group_source_rows(source_rows, definition.group_spec)
    if definition.header_group.max_occurs is not None and len(groups) > definition.header_group.max_occurs:
        raise ConversionError("MAX_OCCURS_EXCEEDED", "header group max_occurs was exceeded")

    root_rows = [row for row in definition.rows if row.level == 1]
    header_rows = [
        row
        for row in definition.rows
        if row.level in {2, 3} and row.values["row_role"] != "driver"
    ]
    detail_rows = [row for row in definition.rows if row.level >= 4]
    shared_rows = [
        row for row in detail_rows if not _variant_for(row, definition.driver.path)
    ]
    variant_rows = {
        variant: [
            row
            for row in detail_rows
            if _variant_for(row, definition.driver.path) == variant
        ]
        for variant in definition.variants
    }

    records: list[dict[str, str]] = []
    empty_source = [""] * width
    for row in sorted(root_rows, key=lambda item: (item.sequence, item.order)):
        value = _value_for(row, empty_source, definition.code_maps)
        _require_value(row, value)
        records.append(_structured_record(row, "", "", "ROOT", value))

    for entry_key, grouped_rows in groups:
        if definition.driver.max_occurs is not None and len(grouped_rows) > definition.driver.max_occurs:
            raise ConversionError("MAX_OCCURS_EXCEEDED", "driver max_occurs was exceeded")
        selected_header_source = _header_source(grouped_rows, header_rows, width)
        for row in sorted(header_rows, key=lambda item: (item.sequence, item.order)):
            value = _value_for(row, selected_header_source, definition.code_maps)
            _require_value(row, value)
            records.append(_structured_record(row, entry_key, "", "HEADER", value))

        for source_index, source in grouped_rows:
            for variant in definition.variants:
                selected = variant_rows[variant]
                presence = [row for row in selected if row.values["row_role"] == "presence"]
                if presence and not any(
                    _value_for(row, source, definition.code_maps) for row in presence
                ):
                    continue
                active = _active_rows(
                    [definition.driver, *selected, *shared_rows],
                    source,
                    definition.driver,
                    definition.code_maps,
                )
                for row in sorted(active, key=lambda item: (item.sequence, item.order)):
                    value = _value_for(row, source, definition.code_maps)
                    _require_value(row, value)
                    records.append(
                        _structured_record(row, entry_key, str(source_index), variant, value)
                    )

    if options.taxonomy_entrypoint is not None:
        metadata_output = options.metadata_output or options.output_path.with_suffix(".json")
        if metadata_output.stem != options.output_path.stem or metadata_output.parent.resolve() != options.output_path.parent.resolve():
            raise ConversionError(
                "OIM_PAIR_INVALID", "Structured CSV and JSON metadata must share directory and basename"
            )
        records, dimension_columns, namespaces = _oim_records(records, definition, options.currency)
        _write_oim_metadata(
            metadata_output,
            options.output_path,
            options.taxonomy_entrypoint,
            dimension_columns,
            namespaces,
            options.entity,
            options.period,
        )
    elif options.metadata_output is not None:
        raise ConversionError("OIM_TAXONOMY_REQUIRED", "--metadata-output requires --taxonomy-entrypoint")
    _write_structured(options.output_path, records, options.output_encoding)
    summary = ConversionSummary(
        source_rows=len(source_rows), profile_width=width, structured_rows=len(records)
    )
    if options.summary_log is not None:
        write_summary(options.summary_log, summary)
    return summary


def _records_from_oim(
    rows: Sequence[dict[str, str]], definition: Definition
) -> list[dict[str, str]]:
    concept_paths: dict[str, str] = {}
    for semantic_path, hmd in definition.hmd_rows.items():
        if (hmd.get("type") or "").upper() != "A":
            continue
        module = hmd.get("module") or hmd.get("associated_module") or ""
        local_name = hmd.get("local_name") or ""
        concept = f"{module}:{local_name}"
        if concept in concept_paths and concept_paths[concept] != semantic_path:
            raise ConversionError("HMD_ROW_INVALID", "HMD concept QNames must be unique for OIM reverse")
        concept_paths[concept] = semantic_path

    repeated_classes = [
        (path, row)
        for path, row in definition.hmd_rows.items()
        if (row.get("type") or "").upper() == "C" and _repeats(row.get("multiplicity") or "")
    ]
    reconstructed: list[dict[str, str]] = []
    for source in rows:
        semantic_path = concept_paths.get((source.get("concept") or "").strip())
        if not semantic_path:
            raise ConversionError("STRUCTURED_BINDING_MISMATCH", "OIM concept is absent from HMD")
        detail_value = ""
        entry_value = ""
        for class_path, class_row in repeated_classes:
            module = class_row.get("module") or class_row.get("associated_module") or ""
            local_name = class_row.get("local_name") or ""
            dimension = f"d_{module}_{local_name}"
            if local_name == "entryHeader":
                entry_value = (source.get(dimension) or "").strip()
            elif local_name == "entryDetail":
                detail_value = (source.get(dimension) or "").strip()
        source_row, occurrence = (detail_value.rsplit("-", 1) + [""])[:2] if "-" in detail_value else ("", "")

        candidates = [row for row in definition.rows if row.neutral_path == semantic_path and row.values["type"].upper() == "A"]
        selected: list[BindingRow] = []
        for candidate in candidates:
            variant = _variant_for(candidate, definition.driver.path)
            if variant and variant != occurrence:
                continue
            matches = True
            for class_path, class_row in repeated_classes:
                selector = _selector_value(candidate.path, class_path)
                if not selector:
                    continue
                module = class_row.get("module") or class_row.get("associated_module") or ""
                local_name = class_row.get("local_name") or ""
                dimension_value = (source.get(f"d_{module}_{local_name}") or "").strip()
                # The Entry Detail occurrence is encoded as ``<source-row>-<variant>``
                # so that facts from different Flat CSV rows remain distinct.  The
                # Binding selector identifies only the variant (for example D or C),
                # while other repeated-class selectors are compared to their complete
                # occurrence-key dimension value.
                comparable_value = occurrence if class_path == definition.driver.path else dimension_value
                if comparable_value != selector:
                    matches = False
                    break
            if matches:
                selected.append(candidate)
        if len(selected) != 1:
            raise ConversionError(
                "STRUCTURED_BINDING_MISMATCH",
                f"OIM concept {(source.get('concept') or '').strip()} resolves to {len(selected)} Binding rows",
            )
        binding = selected[0]
        reconstructed.append(
            {
                "entry_key": entry_value,
                "source_row": source_row,
                "occurrence": occurrence or "HEADER",
                "sequence": f"{binding.sequence:04d}",
                "level": binding.values["level"],
                "type": binding.values["type"],
                "id": binding.values.get("id", ""),
                "name": binding.values["name"],
                "semantic_path": binding.neutral_path,
                "binding_path": binding.path,
                "value": source.get("value") or "",
            }
        )
    return reconstructed


def _read_structured(path: Path, encoding: str, definition: Definition) -> list[dict[str, str]]:
    try:
        with path.open(newline="", encoding=encoding) as stream:
            reader = csv.DictReader(stream)
            fields = tuple(reader.fieldnames or ())
            if set(STRUCTURED_FIELDS).issubset(fields):
                rows = [dict(row) for row in reader]
            elif {"concept", "value"}.issubset(fields):
                rows = _records_from_oim([dict(row) for row in reader], definition)
            else:
                raise ConversionError(
                    "STRUCTURED_HEADER_INVALID", "Structured CSV header lacks a required field"
                )
    except ConversionError:
        raise
    except (OSError, UnicodeError, csv.Error) as exc:
        raise ConversionError("INPUT_IO_ERROR", "Structured CSV input could not be read") from exc
    return rows


def _validated_structured_rows(
    rows: Sequence[dict[str, str]], definition: Definition
) -> tuple[dict[str, list[dict[str, str]]], dict[tuple[str, int], list[dict[str, str]]]]:
    by_path = {row.path: row for row in definition.rows}
    variant_set = set(definition.variants)
    headers: dict[str, list[dict[str, str]]] = defaultdict(list)
    details: dict[tuple[str, int], list[dict[str, str]]] = defaultdict(list)
    for source_row in rows:
        binding_row = by_path.get(source_row["binding_path"])
        if binding_row is None:
            candidates = [
                candidate
                for candidate in definition.rows
                if candidate.neutral_path == source_row["semantic_path"]
                and (
                    not _variant_for(candidate, definition.driver.path)
                    or _variant_for(candidate, definition.driver.path) == source_row["occurrence"]
                )
            ]
            source_selectors = set(SELECTOR_RE.findall(source_row["binding_path"]))
            selector_matches = [
                candidate
                for candidate in candidates
                if set(SELECTOR_RE.findall(candidate.path)).issubset(source_selectors)
            ]
            if len(selector_matches) == 1:
                binding_row = selector_matches[0]
            elif len(candidates) == 1:
                binding_row = candidates[0]
            elif not candidates:
                continue
            else:
                raise ConversionError(
                    "STRUCTURED_BINDING_AMBIGUOUS",
                    "Structured semantic_path resolves to more than one target Binding row",
                )
        if source_row["semantic_path"] != binding_row.neutral_path:
            raise ConversionError(
                "STRUCTURED_BINDING_MISMATCH", "Structured semantic_path does not match Binding"
            )
        row = dict(source_row)
        row.update(
            {
                "binding_path": binding_row.path,
                "sequence": f"{binding_row.sequence:04d}",
                "level": binding_row.values["level"],
                "type": binding_row.values["type"],
                "id": binding_row.values.get("id", ""),
                "name": binding_row.values["name"],
            }
        )
        try:
            sequence = int(row["sequence"])
        except ValueError as exc:
            raise ConversionError(
                "STRUCTURED_ROW_INVALID", "Structured sequence is not an integer"
            ) from exc
        if sequence != binding_row.sequence:
            raise ConversionError(
                "STRUCTURED_BINDING_MISMATCH", "Structured sequence does not match Binding"
            )
        occurrence = row["occurrence"]
        if occurrence == "HEADER":
            headers[row["entry_key"]].append(row)
        elif occurrence in variant_set:
            try:
                source_row = int(row["source_row"])
            except ValueError as exc:
                raise ConversionError(
                    "STRUCTURED_ROW_INVALID", "Structured source_row is not a positive integer"
                ) from exc
            if source_row <= 0:
                raise ConversionError(
                    "STRUCTURED_ROW_INVALID", "Structured source_row is not a positive integer"
                )
            details[(row["entry_key"], source_row)].append(row)
        elif occurrence != "ROOT":
            raise ConversionError("STRUCTURED_ROW_INVALID", "Structured occurrence is unknown")
    if rows and not details:
        raise ConversionError("STRUCTURED_ROW_INVALID", "Structured input contains no detail rows")
    return headers, details


def _write_flat(
    path: Path,
    rows: Iterable[Sequence[str]],
    encoding: str,
    header: Sequence[str] | None = None,
) -> None:
    try:
        with path.open("w", newline="", encoding=encoding) as stream:
            writer = csv.writer(stream)
            if header is not None:
                writer.writerow(header)
            writer.writerows(rows)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise ConversionError("OUTPUT_IO_ERROR", "Flat CSV output could not be written") from exc


def _compound_semantics(definition: Definition) -> tuple[str, str, str, str]:
    indicator_variants: dict[str, str] = {}
    amount_paths: dict[str, str] = {}
    for row in definition.rows:
        variant = _variant_for(row, definition.driver.path)
        if not variant or row.values["type"] != "A":
            continue
        hmd = definition.hmd_rows.get(row.neutral_path, {})
        local_name = (hmd.get("local_name") or "").lower()
        if local_name == "debitcreditindicator":
            indicator = row.values["default_value"].strip().upper()
            if indicator in {"D", "C"}:
                indicator_variants[indicator] = variant
        elif local_name == "monetaryamount":
            if variant in amount_paths and amount_paths[variant] != row.path:
                raise ConversionError(
                    "DEFINITION_INVALID",
                    "a debit or credit occurrence has more than one target MonetaryAmount",
                )
            amount_paths[variant] = row.path
    if set(indicator_variants) != {"D", "C"}:
        raise ConversionError(
            "DEFINITION_INVALID",
            "balanced materialization requires HMD-defined debit and credit indicators",
        )
    debit_variant = indicator_variants["D"]
    credit_variant = indicator_variants["C"]
    if debit_variant not in amount_paths or credit_variant not in amount_paths:
        raise ConversionError(
            "DEFINITION_INVALID",
            "balanced materialization requires one target MonetaryAmount per debit and credit occurrence",
        )
    return debit_variant, credit_variant, amount_paths[debit_variant], amount_paths[credit_variant]


def _decimal_amount(rows: Sequence[dict[str, str]], binding_path: str) -> tuple[Decimal, str]:
    values = [row["value"].strip() for row in rows if row["binding_path"] == binding_path]
    if len(values) != 1 or not values[0]:
        raise ConversionError(
            "COMPOUND_AMOUNT_INVALID",
            "each materialized occurrence must contain exactly one non-empty MonetaryAmount",
        )
    try:
        return Decimal(values[0]), values[0]
    except InvalidOperation as exc:
        raise ConversionError(
            "COMPOUND_AMOUNT_INVALID", "a materialized MonetaryAmount is not a decimal"
        ) from exc


def _copy_with_amount(
    rows: Sequence[dict[str, str]], binding_path: str, amount: str
) -> list[dict[str, str]]:
    copied = [dict(row) for row in rows]
    replaced = 0
    for row in copied:
        if row["binding_path"] == binding_path:
            row["value"] = amount
            replaced += 1
    if replaced != 1:
        raise ConversionError(
            "COMPOUND_AMOUNT_INVALID",
            "a singleton counterpart does not contain exactly one target MonetaryAmount",
        )
    return copied


def _materialized_detail_groups(
    details: Mapping[tuple[str, int], list[dict[str, str]]],
    definition: Definition,
    mode: str,
) -> tuple[list[tuple[tuple[str, int], list[dict[str, str]]]], Counter[str]]:
    if mode == "source_rows":
        return sorted(details.items(), key=lambda item: item[0][1]), Counter()
    if mode not in MATERIALIZATION_MODES:
        raise ConversionError("MATERIALIZATION_MODE_INVALID", "materialization mode is unknown")

    debit_variant, credit_variant, debit_amount_path, credit_amount_path = _compound_semantics(
        definition
    )
    by_entry: dict[str, list[tuple[int, list[dict[str, str]]]]] = defaultdict(list)
    for (entry_key, source_row), rows in details.items():
        by_entry[entry_key].append((source_row, rows))

    materialized: list[tuple[tuple[str, int], list[dict[str, str]]]] = []
    counts: Counter[str] = Counter()
    ordered_entries = sorted(by_entry.items(), key=lambda item: min(row[0] for row in item[1]))
    for entry_key, source_groups in ordered_entries:
        occurrences: dict[str, list[tuple[int, list[dict[str, str]]]]] = {
            debit_variant: [],
            credit_variant: [],
        }
        for source_row, rows in sorted(source_groups, key=lambda item: item[0]):
            for variant, amount_path in (
                (debit_variant, debit_amount_path),
                (credit_variant, credit_amount_path),
            ):
                variant_rows = [row for row in rows if row["occurrence"] == variant]
                amount_is_present = any(
                    row["binding_path"] == amount_path and row["value"].strip()
                    for row in variant_rows
                )
                if amount_is_present:
                    occurrences[variant].append((source_row, variant_rows))

        debit = occurrences[debit_variant]
        credit = occurrences[credit_variant]
        debit_count = len(debit)
        credit_count = len(credit)
        if mode == "exact_unique_amount_pairing":
            if debit_count <= 1 or credit_count <= 1:
                raise ConversionError(
                    "COMPOUND_PAIRING_UNRESOLVED",
                    "exact unique amount pairing requires multiple debit and credit occurrences",
                )
            debit_amounts = [_decimal_amount(rows, debit_amount_path) for _, rows in debit]
            credit_amounts = [_decimal_amount(rows, credit_amount_path) for _, rows in credit]
            debit_total = sum((value for value, _ in debit_amounts), Decimal("0"))
            credit_total = sum((value for value, _ in credit_amounts), Decimal("0"))
            if debit_total != credit_total:
                raise ConversionError(
                    "COMPOUND_AMOUNT_MISMATCH",
                    "debit and credit occurrence totals do not match",
                )
            if debit_count != credit_count:
                raise ConversionError(
                    "COMPOUND_PAIRING_UNRESOLVED",
                    "debit and credit occurrence counts do not match",
                )
            debit_counter = Counter(value for value, _ in debit_amounts)
            credit_counter = Counter(value for value, _ in credit_amounts)
            if debit_counter != credit_counter:
                raise ConversionError(
                    "COMPOUND_PAIRING_UNRESOLVED",
                    "debit and credit MonetaryAmount multisets do not match",
                )
            if any(count != 1 for count in debit_counter.values()) or any(
                count != 1 for count in credit_counter.values()
            ):
                raise ConversionError(
                    "COMPOUND_PAIRING_AMBIGUOUS",
                    "a repeated MonetaryAmount prevents unique debit-credit pairing",
                )
            credit_by_amount = {
                value: (source_row, rows)
                for (source_row, rows), (value, _) in zip(credit, credit_amounts)
            }
            for (source_row, debit_rows), (value, _) in zip(debit, debit_amounts):
                _, credit_rows = credit_by_amount[value]
                materialized.append(
                    (
                        (entry_key, source_row),
                        [
                            *(dict(row) for row in debit_rows),
                            *(dict(row) for row in credit_rows),
                        ],
                    )
                )
            counts["N:M-exact"] += 1
            continue
        if debit_count == 1 and credit_count == 1:
            source_row = min(debit[0][0], credit[0][0])
            materialized.append(((entry_key, source_row), [*debit[0][1], *credit[0][1]]))
            counts["1:1"] += 1
            continue
        if debit_count > 1 and credit_count > 1:
            raise ConversionError(
                "COMPOUND_PAIRING_UNRESOLVED",
                "an entry has multiple debit and multiple credit occurrences",
            )
        if debit_count > 1 and credit_count == 1:
            debit_amounts = [_decimal_amount(rows, debit_amount_path) for _, rows in debit]
            credit_total, _ = _decimal_amount(credit[0][1], credit_amount_path)
            if sum((value for value, _ in debit_amounts), Decimal("0")) != credit_total:
                raise ConversionError(
                    "COMPOUND_AMOUNT_MISMATCH",
                    "debit occurrence total does not equal the singleton credit MonetaryAmount",
                )
            for (source_row, debit_rows), (_, lexical_amount) in zip(debit, debit_amounts):
                materialized.append(
                    (
                        (entry_key, source_row),
                        [
                            *debit_rows,
                            *_copy_with_amount(credit[0][1], credit_amount_path, lexical_amount),
                        ],
                    )
                )
            counts["N:1"] += 1
            continue
        if debit_count == 1 and credit_count > 1:
            debit_total, _ = _decimal_amount(debit[0][1], debit_amount_path)
            credit_amounts = [_decimal_amount(rows, credit_amount_path) for _, rows in credit]
            if debit_total != sum((value for value, _ in credit_amounts), Decimal("0")):
                raise ConversionError(
                    "COMPOUND_AMOUNT_MISMATCH",
                    "singleton debit MonetaryAmount does not equal the credit occurrence total",
                )
            for (source_row, credit_rows), (_, lexical_amount) in zip(credit, credit_amounts):
                materialized.append(
                    (
                        (entry_key, source_row),
                        [
                            *_copy_with_amount(debit[0][1], debit_amount_path, lexical_amount),
                            *credit_rows,
                        ],
                    )
                )
            counts["1:N"] += 1
            continue
        raise ConversionError(
            "COMPOUND_PAIRING_UNRESOLVED",
            "an entry lacks a debit or credit occurrence required for materialization",
        )
    return materialized, counts


def convert_to_flat(options: ConversionOptions) -> ConversionSummary:
    definition = _definition(options)
    width = _resolved_width(definition, options.profile_width)
    structured_rows = _read_structured(options.input_path, options.input_encoding, definition)
    headers, details = _validated_structured_rows(structured_rows, definition)
    by_path = {row.path: row for row in definition.rows}
    variant_rank = {variant: index for index, variant in enumerate(definition.variants)}

    overwrite_counts: Counter[str] = Counter()
    output_records: list[tuple[str, int, list[str]]] = []
    ordered_detail_groups, materialization_counts = _materialized_detail_groups(
        details, definition, options.materialization_mode
    )
    for (entry_key, source_row), rows in ordered_detail_groups:
        target = [""] * width
        ordered = [*headers.get(entry_key, [])]
        ordered.extend(
            sorted(
                rows,
                key=lambda row: (
                    variant_rank[row["occurrence"]],
                    int(row["sequence"]),
                    row["binding_path"],
                ),
            )
        )
        for structured in ordered:
            binding_row = by_path[structured["binding_path"]]
            column = binding_row.values["column"]
            value = _transform_reverse(
                binding_row.values["transformation"], structured["value"], definition.code_maps
            )
            if not column or not value:
                continue
            number = _column_number(column)
            assert number is not None
            previous = target[number - 1]
            if previous and previous != value:
                overwrite_counts[column] += 1
            target[number - 1] = value
        output_records.append((entry_key, source_row, target))

    required_columns = {
        _column_number(row.values["column"])
        for row in definition.rows
        if row.is_required and row.values["type"] == "A" and row.values["column"]
    }
    for _, _, target in output_records:
        if any(number is not None and not target[number - 1] for number in required_columns):
            raise ConversionError("REQUIRED_VALUE_MISSING", "a required target Binding value is empty")

    if definition.group_spec.mode == "marker_rows":
        marker_number = _column_number(definition.group_spec.marker_column)
        assert marker_number is not None
        header_columns = {
            _column_number(row.values["column"])
            for row in definition.rows
            if row.level in {2, 3}
            and row.values["row_role"] != "driver"
            and row.values["column"]
        }
        by_entry: dict[str, list[list[str]]] = defaultdict(list)
        for entry_key, _, target in output_records:
            by_entry[entry_key].append(target)
        for targets in by_entry.values():
            for target in targets[1:]:
                for number in header_columns:
                    assert number is not None
                    target[number - 1] = ""
            if len(targets) == 1:
                targets[0][marker_number - 1] = definition.group_spec.single
            else:
                targets[0][marker_number - 1] = definition.group_spec.start
                for target in targets[1:-1]:
                    target[marker_number - 1] = definition.group_spec.continuation
                targets[-1][marker_number - 1] = definition.group_spec.end

    output_rows = [target for _, _, target in output_records]
    output_header = _physical_header(definition, width) if options.output_header else None
    _write_flat(options.output_path, output_rows, options.output_encoding, output_header)
    summary = ConversionSummary(
        source_rows=len(output_rows),
        profile_width=width,
        structured_rows=len(structured_rows),
        shared_column_overwrite_total=sum(overwrite_counts.values()),
        shared_column_overwrites=dict(sorted(overwrite_counts.items())),
        materialization_mode=options.materialization_mode,
        materialized_1_1=materialization_counts["1:1"],
        materialized_n_1=materialization_counts["N:1"],
        materialized_1_n=materialization_counts["1:N"],
        materialized_exact_unique_n_m=materialization_counts["N:M-exact"],
    )
    if options.summary_log is not None:
        write_summary(options.summary_log, summary)
    return summary


def write_summary(path: Path, summary: ConversionSummary) -> None:
    try:
        with path.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(summary.as_dict(), stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
    except (OSError, UnicodeError) as exc:
        raise ConversionError("SUMMARY_IO_ERROR", "summary output could not be written") from exc


def _positive_width(raw: str) -> int:
    try:
        value = int(raw)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a positive integer") from exc
    if value <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return value


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Canonical 16-column Flat CSV converter")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("input", type=Path)
        subparser.add_argument("-o", "--output", required=True, type=Path)
        subparser.add_argument("-m", "--hmd-file", required=True, type=Path)
        subparser.add_argument("-b", "--binding-file", required=True, type=Path)
        subparser.add_argument("-e", "--definition-encoding", default="utf-8-sig")
        subparser.add_argument("--profile-width", type=_positive_width)
        subparser.add_argument("--summary-log", type=Path)
        subparser.add_argument("--code-map-file", action="append", type=Path, default=[])
        subparser.add_argument("--debug", action="store_true")
        subparser.add_argument("--trace", action="store_true")

    forward = subparsers.add_parser("to-structured", help="convert Flat CSV to Structured CSV")
    add_common(forward)
    forward.add_argument("--input-encoding", default="utf-8-sig")
    header_group = forward.add_mutually_exclusive_group()
    header_group.add_argument("--data-start-row", type=_positive_width)
    header_group.add_argument("--input-header", dest="input_header_rows", action="store_const", const=1)
    header_group.add_argument("--input-header-rows", type=_positive_width)
    forward.add_argument("--metadata-output", type=Path)
    forward.add_argument("--taxonomy-entrypoint", type=Path)
    forward.add_argument("--entity", default="scheme:UADC-PoC")
    forward.add_argument("--period", default="2026-12-31T00:00:00")
    forward.add_argument("--currency", default="iso4217:JPY")

    reverse = subparsers.add_parser("to-flat", help="convert Structured CSV to Flat CSV")
    add_common(reverse)
    reverse.add_argument("--output-encoding", default="utf-8")
    reverse.add_argument("--output-header", action="store_true")
    reverse.add_argument(
        "--materialization-mode",
        choices=sorted(MATERIALIZATION_MODES),
        default="source_rows",
        help="materialize balanced debit/credit occurrences when explicitly requested",
    )
    return parser.parse_args(argv)


def _options_from_args(args: argparse.Namespace) -> ConversionOptions:
    if args.command == "to-structured":
        input_encoding = args.input_encoding
        output_encoding = "utf-8"
    else:
        input_encoding = "utf-8-sig"
        output_encoding = args.output_encoding
    legacy_header_rows = getattr(args, "input_header_rows", None) or 0
    data_start_row = getattr(args, "data_start_row", None) or legacy_header_rows + 1
    return ConversionOptions(
        input_path=args.input,
        output_path=args.output,
        hmd_path=args.hmd_file,
        binding_path=args.binding_file,
        definition_encoding=args.definition_encoding,
        input_encoding=input_encoding,
        output_encoding=output_encoding,
        profile_width=args.profile_width,
        summary_log=args.summary_log,
        metadata_output=getattr(args, "metadata_output", None),
        taxonomy_entrypoint=getattr(args, "taxonomy_entrypoint", None),
        entity=getattr(args, "entity", "scheme:UADC-PoC"),
        period=getattr(args, "period", "2026-12-31T00:00:00"),
        currency=getattr(args, "currency", "iso4217:JPY"),
        data_start_row=data_start_row,
        input_header_rows=legacy_header_rows,
        output_header=getattr(args, "output_header", False),
        materialization_mode=getattr(args, "materialization_mode", "source_rows"),
        code_map_paths=tuple(args.code_map_file),
        debug=args.debug,
        trace=args.trace,
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    options = _options_from_args(args)
    try:
        if args.command == "to-structured":
            convert_to_structured(options)
        else:
            convert_to_flat(options)
    except ConversionError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except Exception:
        print("INTERNAL_ERROR: conversion failed without value disclosure", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
