# Canonical normal-route negative report integration.
#!/usr/bin/env python3
"""UADC CSV physical-format adapter.

Converts application-specific CSV serialization to/from the normalized CSV
serialization consumed/produced around flat_csv.py. The adapter is deliberately
syntax/transport-only: it does not map accounts, tax semantics, HMD paths, or
business meaning.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation
import csv
import hashlib
import io
import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Sequence

SCHEMA_VERSION = 1
KNOWN_BOMS = {
    "utf-8": b"\xef\xbb\xbf",
    "utf-16-le": b"\xff\xfe",
    "utf-16-be": b"\xfe\xff",
}
NEWLINE_BYTES = {"LF": b"\n", "CRLF": b"\r\n", "CR": b"\r"}
QUOTE_POLICIES = {"none", "minimal", "all"}
BOM_POLICIES = {"forbidden", "optional", "required"}
DATE_FORMATS = {"YYYY/M/D", "YYYY/MM/DD", "YYYY-MM-DD", "YYYYMMDD"}


class AdapterError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclass(frozen=True)
class SideSpec:
    encoding: str
    bom: str
    newline: str
    final_newline: bool
    delimiter: str
    quote_policy: str


@dataclass(frozen=True)
class DateTransform:
    column: int
    application_format: str
    uadc_format: str


@dataclass(frozen=True)
class NumericTransform:
    column: int
    application_input_grouping: str
    uadc_grouping: str
    application_output_grouping: str


@dataclass(frozen=True)
class Profile:
    profile_name: str
    width: int
    header_rows: int
    expected_header_rows: tuple[tuple[str, ...], ...]
    reject_blank_records: bool
    application_input: SideSpec
    application_output: SideSpec
    uadc: SideSpec
    date_transforms: tuple[DateTransform, ...]
    numeric_transforms: tuple[NumericTransform, ...]


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as stream:
            obj = json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AdapterError("PROFILE_IO_ERROR", "profile JSON could not be read") from exc
    if not isinstance(obj, dict):
        raise AdapterError("PROFILE_INVALID", "profile root must be an object")
    return obj


def _required(obj: dict[str, Any], key: str, expected_type: type) -> Any:
    value = obj.get(key)
    if not isinstance(value, expected_type):
        raise AdapterError("PROFILE_INVALID", f"{key} has an invalid type")
    return value


def _parse_side(obj: dict[str, Any], key: str) -> SideSpec:
    raw = obj.get(key)
    if not isinstance(raw, dict):
        raise AdapterError("PROFILE_INVALID", f"{key} must be an object")
    encoding = _required(raw, "encoding", str).lower()
    bom = _required(raw, "bom", str).lower()
    newline = _required(raw, "newline", str).upper()
    final_newline = raw.get("final_newline")
    delimiter = _required(raw, "delimiter", str)
    quote_policy = _required(raw, "quote_policy", str).lower()
    if bom not in BOM_POLICIES:
        raise AdapterError("PROFILE_INVALID", f"{key}.bom is unsupported")
    if newline not in NEWLINE_BYTES:
        raise AdapterError("PROFILE_INVALID", f"{key}.newline is unsupported")
    if not isinstance(final_newline, bool):
        raise AdapterError("PROFILE_INVALID", f"{key}.final_newline must be boolean")
    if len(delimiter) != 1 or delimiter in {"\r", "\n", '"'}:
        raise AdapterError("PROFILE_INVALID", f"{key}.delimiter must be one safe character")
    if quote_policy not in QUOTE_POLICIES:
        raise AdapterError("PROFILE_INVALID", f"{key}.quote_policy is unsupported")
    return SideSpec(encoding, bom, newline, final_newline, delimiter, quote_policy)


def load_profile(path: Path) -> Profile:
    obj = _load_json(path)
    if obj.get("schema_version") != SCHEMA_VERSION:
        raise AdapterError("PROFILE_INVALID", "unsupported schema_version")
    profile_name = _required(obj, "profile_name", str).strip()
    width = obj.get("width")
    header_rows = obj.get("header_rows")
    reject_blank_records = obj.get("reject_blank_records", True)
    if not profile_name:
        raise AdapterError("PROFILE_INVALID", "profile_name must not be blank")
    if not isinstance(width, int) or width <= 0:
        raise AdapterError("PROFILE_INVALID", "width must be a positive integer")
    if not isinstance(header_rows, int) or header_rows < 0:
        raise AdapterError("PROFILE_INVALID", "header_rows must be a non-negative integer")
    if not isinstance(reject_blank_records, bool):
        raise AdapterError("PROFILE_INVALID", "reject_blank_records must be boolean")

    expected_raw = obj.get("expected_header_rows", [])
    if not isinstance(expected_raw, list):
        raise AdapterError("PROFILE_INVALID", "expected_header_rows must be an array")
    expected: list[tuple[str, ...]] = []
    for row in expected_raw:
        if not isinstance(row, list) or not all(isinstance(v, str) for v in row):
            raise AdapterError("PROFILE_INVALID", "expected_header_rows contains an invalid row")
        if len(row) != width:
            raise AdapterError("PROFILE_INVALID", "expected header width differs from profile width")
        expected.append(tuple(row))
    if len(expected) > header_rows:
        raise AdapterError("PROFILE_INVALID", "more expected header rows than header_rows")

    transforms_raw = obj.get("date_transforms", [])
    if not isinstance(transforms_raw, list):
        raise AdapterError("PROFILE_INVALID", "date_transforms must be an array")
    transforms: list[DateTransform] = []
    used: set[int] = set()
    for item in transforms_raw:
        if not isinstance(item, dict):
            raise AdapterError("PROFILE_INVALID", "date_transforms contains an invalid object")
        col_raw = item.get("column")
        if not isinstance(col_raw, str) or not re.fullmatch(r"C[1-9][0-9]*", col_raw):
            raise AdapterError("PROFILE_INVALID", "date transform column must use C<n>")
        col = int(col_raw[1:])
        if col > width or col in used:
            raise AdapterError("PROFILE_INVALID", "date transform column is invalid or duplicated")
        app_fmt = item.get("application_format")
        uadc_fmt = item.get("uadc_format")
        if app_fmt not in DATE_FORMATS or uadc_fmt not in DATE_FORMATS:
            raise AdapterError("PROFILE_INVALID", "date transform format is unsupported")
        if uadc_fmt != "YYYY-MM-DD":
            raise AdapterError(
                "PROFILE_INVALID",
                "uadc_format for date transforms must be YYYY-MM-DD for flat_csv.py",
            )
        transforms.append(DateTransform(col, app_fmt, uadc_fmt))
        used.add(col)

    numeric_raw = obj.get("numeric_transforms", [])
    if not isinstance(numeric_raw, list):
        raise AdapterError("PROFILE_INVALID", "numeric_transforms must be an array")
    numeric: list[NumericTransform] = []
    numeric_used: set[int] = set()
    for item in numeric_raw:
        if not isinstance(item, dict):
            raise AdapterError("PROFILE_INVALID", "numeric_transforms contains an invalid object")
        col_raw = item.get("column")
        if not isinstance(col_raw, str) or not re.fullmatch(r"C[1-9][0-9]*", col_raw):
            raise AdapterError("PROFILE_INVALID", "numeric transform column must use C<n>")
        col = int(col_raw[1:])
        if col > width or col in numeric_used:
            raise AdapterError("PROFILE_INVALID", "numeric transform column is invalid or duplicated")
        values = [
            item.get("application_input_grouping", ""),
            item.get("uadc_grouping", ""),
            item.get("application_output_grouping", ""),
        ]
        if any(v not in {"", ","} for v in values):
            raise AdapterError("PROFILE_INVALID", "numeric grouping supports only blank or comma")
        numeric.append(NumericTransform(col, values[0], values[1], values[2]))
        numeric_used.add(col)

    return Profile(
        profile_name=profile_name,
        width=width,
        header_rows=header_rows,
        expected_header_rows=tuple(expected),
        reject_blank_records=reject_blank_records,
        application_input=_parse_side(obj, "application_input"),
        application_output=_parse_side(obj, "application_output"),
        uadc=_parse_side(obj, "uadc"),
        date_transforms=tuple(transforms),
        numeric_transforms=tuple(numeric),
    )


def _known_bom(data: bytes) -> tuple[str | None, bytes]:
    for name, marker in KNOWN_BOMS.items():
        if data.startswith(marker):
            return name, marker
    return None, b""


def _validate_bom(data: bytes, spec: SideSpec) -> tuple[bytes, bool]:
    name, marker = _known_bom(data)
    has_bom = bool(marker)
    if spec.bom == "forbidden" and has_bom:
        raise AdapterError("BOM_FORBIDDEN", "input has a BOM but the profile forbids it")
    if spec.bom == "required" and not has_bom:
        raise AdapterError("BOM_REQUIRED", "input has no BOM but the profile requires one")
    if has_bom:
        if spec.encoding == "utf-8" and name != "utf-8":
            raise AdapterError("BOM_ENCODING_MISMATCH", "BOM does not match the declared encoding")
        if spec.encoding == "utf-16-le" and name != "utf-16-le":
            raise AdapterError("BOM_ENCODING_MISMATCH", "BOM does not match the declared encoding")
        if spec.encoding == "utf-16-be" and name != "utf-16-be":
            raise AdapterError("BOM_ENCODING_MISMATCH", "BOM does not match the declared encoding")
        data = data[len(marker):]
    return data, has_bom


def _record_newline_counts(text: str) -> tuple[int, int, int]:
    """Count record terminators outside quoted CSV fields.

    CR/LF characters inside quoted fields are data and must not be confused
    with physical record terminators. Escaped double quotes ("") remain inside
    the quoted field.
    """
    crlf = bare_lf = bare_cr = 0
    in_quotes = False
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == '"':
            if in_quotes and i + 1 < len(text) and text[i + 1] == '"':
                i += 2
                continue
            in_quotes = not in_quotes
            i += 1
            continue
        if not in_quotes:
            if ch == "\r":
                if i + 1 < len(text) and text[i + 1] == "\n":
                    crlf += 1
                    i += 2
                    continue
                bare_cr += 1
            elif ch == "\n":
                bare_lf += 1
        i += 1
    return crlf, bare_lf, bare_cr


def _validate_newlines(text: str, spec: SideSpec) -> dict[str, Any]:
    crlf, bare_lf, bare_cr = _record_newline_counts(text)
    if spec.newline == "CRLF" and (bare_lf or bare_cr):
        raise AdapterError("NEWLINE_MISMATCH", "input contains a non-CRLF record terminator")
    if spec.newline == "LF" and (crlf or bare_cr):
        raise AdapterError("NEWLINE_MISMATCH", "input contains a non-LF record terminator")
    if spec.newline == "CR" and (crlf or bare_lf):
        raise AdapterError("NEWLINE_MISMATCH", "input contains a non-CR record terminator")
    marker = {"LF": "\n", "CRLF": "\r\n", "CR": "\r"}[spec.newline]
    ends = text.endswith(marker)
    if spec.final_newline != ends:
        raise AdapterError("FINAL_NEWLINE_MISMATCH", "input final record terminator differs from the profile")
    return {"crlf": crlf, "bare_lf": bare_lf, "bare_cr": bare_cr, "final_newline": ends}


def _decode(data: bytes, spec: SideSpec) -> tuple[str, bool, dict[str, Any]]:
    stripped, has_bom = _validate_bom(data, spec)
    try:
        text = stripped.decode(spec.encoding, errors="strict")
    except (LookupError, UnicodeError) as exc:
        raise AdapterError("ENCODING_ERROR", "input cannot be decoded using the declared encoding") from exc
    newline_info = _validate_newlines(text, spec)
    if spec.quote_policy == "none" and '"' in text:
        raise AdapterError("QUOTE_FORBIDDEN", "input contains a quote character but quote_policy is none")
    return text, has_bom, newline_info


def _reader(text: str, spec: SideSpec) -> csv.reader:
    quoting = csv.QUOTE_NONE if spec.quote_policy == "none" else csv.QUOTE_MINIMAL
    return csv.reader(
        io.StringIO(text, newline=""),
        delimiter=spec.delimiter,
        quotechar='"',
        quoting=quoting,
        strict=True,
    )


def _quote_stats(text: str, spec: SideSpec, header_rows: int) -> dict[str, int]:
    """Return value-free counts of CSV fields that are physically quoted."""
    quoted_fields = 0
    quoted_data_fields = 0
    row_index = 0
    at_field_start = True
    in_quotes = False
    i = 0
    while i < len(text):
        ch = text[i]
        if in_quotes:
            if ch == '"':
                if i + 1 < len(text) and text[i + 1] == '"':
                    i += 2
                    continue
                in_quotes = False
            i += 1
            continue
        if at_field_start and ch == '"':
            quoted_fields += 1
            if row_index >= header_rows:
                quoted_data_fields += 1
            in_quotes = True
            at_field_start = False
            i += 1
            continue
        if ch == spec.delimiter:
            at_field_start = True
            i += 1
            continue
        if ch == "\r":
            if i + 1 < len(text) and text[i + 1] == "\n":
                i += 2
            else:
                i += 1
            row_index += 1
            at_field_start = True
            continue
        if ch == "\n":
            row_index += 1
            at_field_start = True
            i += 1
            continue
        at_field_start = False
        i += 1
    return {"quoted_fields": quoted_fields, "quoted_data_fields": quoted_data_fields}


def _parse_rows(text: str, spec: SideSpec, profile: Profile) -> list[list[str]]:
    try:
        rows = [list(row) for row in _reader(text, spec)]
    except csv.Error as exc:
        raise AdapterError("CSV_PARSE_ERROR", "CSV records could not be parsed") from exc
    for index, row in enumerate(rows, start=1):
        if profile.reject_blank_records and len(row) == 0:
            raise AdapterError("BLANK_RECORD", f"blank record at row {index}")
        if len(row) != profile.width:
            raise AdapterError("PROFILE_WIDTH_MISMATCH", f"row {index} does not have {profile.width} columns")
    if len(rows) < profile.header_rows:
        raise AdapterError("HEADER_MISSING", "input has fewer rows than header_rows")
    for i, expected in enumerate(profile.expected_header_rows):
        if tuple(rows[i]) != expected:
            raise AdapterError("HEADER_MISMATCH", f"header row {i + 1} does not match the profile")
    return rows


def _parse_date(value: str, fmt: str) -> date:
    patterns = {
        "YYYY/M/D": r"^(\d{4})/(\d{1,2})/(\d{1,2})$",
        "YYYY/MM/DD": r"^(\d{4})/(\d{2})/(\d{2})$",
        "YYYY-MM-DD": r"^(\d{4})-(\d{2})-(\d{2})$",
        "YYYYMMDD": r"^(\d{4})(\d{2})(\d{2})$",
    }
    m = re.fullmatch(patterns[fmt], value)
    if not m:
        raise ValueError("lexical mismatch")
    y, mo, d = map(int, m.groups())
    return date(y, mo, d)


def _format_date(value: date, fmt: str) -> str:
    if fmt == "YYYY/M/D":
        return f"{value.year}/{value.month}/{value.day}"
    if fmt == "YYYY/MM/DD":
        return f"{value.year:04d}/{value.month:02d}/{value.day:02d}"
    if fmt == "YYYY-MM-DD":
        return f"{value.year:04d}-{value.month:02d}-{value.day:02d}"
    if fmt == "YYYYMMDD":
        return f"{value.year:04d}{value.month:02d}{value.day:02d}"
    raise AssertionError(fmt)


def _transform_dates(rows: list[list[str]], profile: Profile, direction: str) -> int:
    count = 0
    for row_number, row in enumerate(rows[profile.header_rows:], start=profile.header_rows + 1):
        for transform in profile.date_transforms:
            idx = transform.column - 1
            raw = row[idx]
            if raw == "":
                continue
            src = transform.application_format if direction == "to-uadc" else transform.uadc_format
            dst = transform.uadc_format if direction == "to-uadc" else transform.application_format
            try:
                parsed = _parse_date(raw, src)
            except (ValueError, OverflowError) as exc:
                raise AdapterError(
                    "DATE_FORMAT_INVALID",
                    f"row {row_number} column C{transform.column} is not in {src} format",
                ) from exc
            row[idx] = _format_date(parsed, dst)
            count += 1
    return count



def _ungroup_number(value: str, grouping: str) -> str:
    if value == "":
        return value
    sign = ""
    body = value
    if body[0:1] in {"+", "-"}:
        sign, body = body[0], body[1:]
    if grouping == ",":
        if "," in body:
            integer, dot, fraction = body.partition(".")
            if not re.fullmatch(r"\d{1,3}(?:,\d{3})+", integer):
                raise ValueError("invalid grouping")
            body = integer.replace(",", "") + (dot + fraction if dot else "")
    elif "," in body:
        raise ValueError("grouping not allowed")
    if not re.fullmatch(r"\d+(?:\.\d+)?", body):
        raise ValueError("invalid numeric lexical form")
    return sign + body


def _apply_grouping(value: str, grouping: str) -> str:
    if value == "" or grouping == "":
        return value
    sign = ""
    body = value
    if body[0:1] in {"+", "-"}:
        sign, body = body[0], body[1:]
    integer, dot, fraction = body.partition(".")
    grouped = f"{int(integer):,}"
    return sign + grouped + (dot + fraction if dot else "")


def _transform_numbers(rows: list[list[str]], profile: Profile, direction: str) -> int:
    count = 0
    for row_number, row in enumerate(rows[profile.header_rows:], start=profile.header_rows + 1):
        for transform in profile.numeric_transforms:
            idx = transform.column - 1
            raw = row[idx]
            if raw == "":
                continue
            if direction == "to-uadc":
                source_grouping = transform.application_input_grouping
                target_grouping = transform.uadc_grouping
            else:
                source_grouping = transform.uadc_grouping
                target_grouping = transform.application_output_grouping
            try:
                canonical = _ungroup_number(raw, source_grouping)
                row[idx] = _apply_grouping(canonical, target_grouping)
            except (ValueError, OverflowError) as exc:
                raise AdapterError(
                    "NUMERIC_FORMAT_INVALID",
                    f"row {row_number} column C{transform.column} has an invalid numeric lexical form",
                ) from exc
            if row[idx] != raw:
                count += 1
    return count

def _render_rows(rows: Iterable[Sequence[str]], spec: SideSpec) -> str:
    rows = list(rows)
    newline = {"LF": "\n", "CRLF": "\r\n", "CR": "\r"}[spec.newline]
    if spec.quote_policy == "none":
        rendered: list[str] = []
        for row_no, row in enumerate(rows, start=1):
            for col_no, value in enumerate(row, start=1):
                if spec.delimiter in value or "\r" in value or "\n" in value or '"' in value:
                    raise AdapterError(
                        "UNQUOTED_CSV_UNSAFE_VALUE",
                        f"row {row_no} column C{col_no} cannot be emitted without quoting",
                    )
            rendered.append(spec.delimiter.join(row))
        text = newline.join(rendered)
        if spec.final_newline and rows:
            text += newline
        return text

    quoting = csv.QUOTE_MINIMAL if spec.quote_policy == "minimal" else csv.QUOTE_ALL
    buffer = io.StringIO(newline="")
    writer = csv.writer(
        buffer,
        delimiter=spec.delimiter,
        quotechar='"',
        quoting=quoting,
        lineterminator=newline,
        doublequote=True,
    )
    writer.writerows(rows)
    text = buffer.getvalue()
    if not spec.final_newline and text.endswith(newline):
        text = text[: -len(newline)]
    return text


def _encode(text: str, spec: SideSpec) -> tuple[bytes, bool]:
    try:
        raw = text.encode(spec.encoding, errors="strict")
    except (LookupError, UnicodeError) as exc:
        raise AdapterError("ENCODING_ERROR", "output cannot be encoded using the declared encoding") from exc
    bom_added = False
    if spec.bom == "required":
        marker = KNOWN_BOMS.get(spec.encoding)
        if marker is None:
            raise AdapterError("PROFILE_INVALID", "required BOM is unsupported for the declared encoding")
        raw = marker + raw
        bom_added = True
    return raw, bom_added


def _read_bytes(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        raise AdapterError("INPUT_IO_ERROR", "input file could not be read") from exc


def _write_bytes(path: Path, data: bytes) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    except OSError as exc:
        raise AdapterError("OUTPUT_IO_ERROR", "output file could not be written") from exc


def _write_report(path: Path | None, report: dict[str, Any]) -> None:
    if path is None:
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
    except (OSError, UnicodeError) as exc:
        raise AdapterError("REPORT_IO_ERROR", "report could not be written") from exc


def _spec_for(profile: Profile, side: str) -> SideSpec:
    if side == "application-input":
        return profile.application_input
    if side == "application-output":
        return profile.application_output
    if side == "uadc":
        return profile.uadc
    raise AdapterError("ARGUMENT_ERROR", "side must be application-input, application-output, or uadc")


def inspect_file(input_path: Path, profile: Profile, side: str) -> dict[str, Any]:
    spec = _spec_for(profile, side)
    raw = _read_bytes(input_path)
    text, has_bom, newline_info = _decode(raw, spec)
    rows = _parse_rows(text, spec, profile)
    quote_stats = _quote_stats(text, spec, profile.header_rows)
    return {
        "profile": profile.profile_name,
        "side": side,
        "input_sha256": _sha256(raw),
        "bytes": len(raw),
        "rows": len(rows),
        "header_rows": profile.header_rows,
        "data_rows": max(0, len(rows) - profile.header_rows),
        "width": profile.width,
        "encoding": spec.encoding,
        "bom_present": has_bom,
        "newline": spec.newline,
        "final_newline": newline_info["final_newline"],
        "quote_policy": spec.quote_policy,
        "quoted_fields": quote_stats["quoted_fields"],
        "quoted_data_fields": quote_stats["quoted_data_fields"],
        "status": "PASS",
    }


def _convert(input_path: Path, output_path: Path, profile: Profile, direction: str) -> dict[str, Any]:
    if direction == "to-uadc":
        source, target = profile.application_input, profile.uadc
    elif direction == "from-uadc":
        source, target = profile.uadc, profile.application_output
    else:
        raise AdapterError("ARGUMENT_ERROR", "direction is invalid")

    raw = _read_bytes(input_path)
    text, source_bom, source_newline_info = _decode(raw, source)
    source_quote_stats = _quote_stats(text, source, profile.header_rows)
    rows = _parse_rows(text, source, profile)
    transformed_dates = _transform_dates(rows, profile, direction)
    transformed_numbers = _transform_numbers(rows, profile, direction)
    rendered = _render_rows(rows, target)
    output_bytes, output_bom = _encode(rendered, target)
    _write_bytes(output_path, output_bytes)

    # Re-read our own output with the target contract. This is the publication gate.
    out_text, out_has_bom, out_newline_info = _decode(output_bytes, target)
    target_quote_stats = _quote_stats(out_text, target, profile.header_rows)
    out_rows = _parse_rows(out_text, target, profile)
    if out_rows != rows:
        raise AdapterError("SELF_CHECK_FAILED", "written output does not reproduce the transformed records")

    return {
        "profile": profile.profile_name,
        "direction": direction,
        "input_sha256": _sha256(raw),
        "output_sha256": _sha256(output_bytes),
        "input_bytes": len(raw),
        "output_bytes": len(output_bytes),
        "rows": len(rows),
        "header_rows": profile.header_rows,
        "data_rows": max(0, len(rows) - profile.header_rows),
        "width": profile.width,
        "date_values_transformed": transformed_dates,
        "numeric_values_transformed": transformed_numbers,
        "source_encoding": source.encoding,
        "target_encoding": target.encoding,
        "source_bom_present": source_bom,
        "target_bom_present": output_bom or out_has_bom,
        "source_newline": source.newline,
        "target_newline": target.newline,
        "source_final_newline": source_newline_info["final_newline"],
        "target_final_newline": out_newline_info["final_newline"],
        "source_quote_policy": source.quote_policy,
        "target_quote_policy": target.quote_policy,
        "source_quoted_fields": source_quote_stats["quoted_fields"],
        "source_quoted_data_fields": source_quote_stats["quoted_data_fields"],
        "target_quoted_fields": target_quote_stats["quoted_fields"],
        "target_quoted_data_fields": target_quote_stats["quoted_data_fields"],
        "status": "PASS",
    }



def convert(input_path, output_path, profile, direction):
    result = _convert(input_path, output_path, profile, direction)
    sidecar = Path(str(input_path) + ".conversion-report.json")
    if direction != "from-uadc" or not sidecar.exists():
        return result
    payload = json.loads(sidecar.read_text(encoding="utf-8"))
    if payload["normalized_sha256"].lower() != result["input_sha256"].lower():
        raise AdapterError("REPORT_INPUT_MISMATCH", "conversion report does not identify this normalized CSV")
    report = payload["summary"]["negative_amount_report"]
    original = {(d["output_record_number"], d["output_column_position"]): d
                for d in report["output_detections"]}
    detections = []
    with output_path.open(encoding=profile.application_output.encoding, newline="") as stream:
        reader = csv.reader(stream)
        previous = 0
        for record_number, row in enumerate(reader, 1):
            start = previous + 1
            previous = reader.line_num
            if record_number <= profile.header_rows:
                continue
            for column, info in report["amount_columns"].items():
                number = int(column)
                lexical = row[number - 1]
                try:
                    value = Decimal(lexical.strip())
                except (InvalidOperation, ValueError):
                    continue
                if not value.is_finite() or value >= 0:
                    continue
                source = original.get((record_number, number))
                if source is None:
                    raise AdapterError("REPORT_OUTPUT_MISMATCH", "negative final cell has no conversion provenance")
                detection = dict(source)
                detection.update({"output_file": str(output_path.resolve()), "amount": lexical,
                    "physical_line_start": start, "physical_line_end": previous,
                    "physical_line_number": start if start == previous else None,
                    "action": "ORIGINAL_NEGATIVE_AMOUNT_PRESERVED_IN_OUTPUT"})
                for name in ("account_code", "account_name"):
                    position = info.get(name + "_column")
                    detection[name] = row[position - 1] if position else None
                detections.append(detection)
    if len(detections) != len(original):
        raise AdapterError("REPORT_OUTPUT_MISMATCH", "reported and final negative cell sets differ")
    report.update({"output_representation": "APPLICATION_CSV", "output_file": str(output_path.resolve()),
                   "conversion_status": "APPLICATION_OUTPUT_GENERATED", "output_generated": True,
                   "output_negative_cell_count": len(detections), "output_detections": detections})
    result["negative_amount_report"] = report
    final_summary = dict(payload["summary"])
    final_summary["negative_amount_report"] = report
    final_payload = {"application_sha256": result["output_sha256"], "summary": final_summary}
    _write_report(Path(str(output_path) + ".conversion-report.json"), final_payload)
    return result


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert application CSV physical serialization to/from UADC normalized CSV"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    inspect_p = sub.add_parser("inspect", help="validate a CSV against one side of a profile")
    inspect_p.add_argument("input", type=Path)
    inspect_p.add_argument("--profile", required=True, type=Path)
    inspect_p.add_argument("--side", required=True, choices=["application-input", "application-output", "uadc"])
    inspect_p.add_argument("--report", type=Path)

    for command, help_text in [
        ("to-uadc", "convert application CSV to normalized UADC CSV"),
        ("from-uadc", "convert normalized UADC CSV to application CSV"),
    ]:
        p = sub.add_parser(command, help=help_text)
        p.add_argument("input", type=Path)
        p.add_argument("-o", "--output", required=True, type=Path)
        p.add_argument("--profile", required=True, type=Path)
        p.add_argument("--report", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        profile = load_profile(args.profile)
        if args.command == "inspect":
            report = inspect_file(args.input, profile, args.side)
        else:
            report = convert(args.input, args.output, profile, args.command)
        _write_report(args.report, report)
        if args.report is None:
            print(json.dumps(report, ensure_ascii=False, sort_keys=True))
        return 0
    except AdapterError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except Exception:
        print("INTERNAL_ERROR: CSV physical adaptation failed", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
