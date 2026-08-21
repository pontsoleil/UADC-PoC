#!/usr/bin/env python3
"""Deterministic semantic-datatype to XBRL item-type binding."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path


MAPPING_HEADER = [
    "hmd_datatype",
    "xsd_base_type",
    "xbrl_item_type",
    "unit_semantics",
    "status",
    "source",
    "notes",
]

OVERRIDE_HEADER = [
    "semantic_path",
    "module",
    "local_name",
    "hmd_datatype",
    "xbrl_item_type",
    "status",
    "reason",
    "source",
    "notes",
]

ALLOWED_STATUSES = {
    "confirmed",
    "candidate",
    "legacy-observed",
    "review-required",
}

QNAME_RE = re.compile(
    r"^[A-Za-z_][A-Za-z0-9._-]*:[A-Za-z_][A-Za-z0-9._-]*$"
)


class DatatypeBindingError(ValueError):
    """Raised when binding resources or an HMD row are not conforming."""


def default_mapping_path() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / "definitions"
        / "taxonomy"
        / "datatype_mapping.csv"
    )


def default_override_path() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / "definitions"
        / "taxonomy"
        / "datatype_override.csv"
    )


def normalize_datatype_key(value: str) -> str:
    """Preserve the former case/space-insensitive datatype lookup contract."""
    return re.sub(r"\s+", "", (value or "").strip()).casefold()


def _required(row: dict[str, str], field: str, source: Path, line: int) -> str:
    value = (row.get(field) or "").strip()
    if not value:
        raise DatatypeBindingError(
            f"{source}:{line}: {field} must not be blank."
        )
    return value


def _qname(value: str, field: str, source: Path, line: int) -> str:
    if not QNAME_RE.fullmatch(value):
        raise DatatypeBindingError(
            f"{source}:{line}: {field} must be a lexical QName; got {value!r}."
        )
    return value


def _read_rows(path: Path, expected_header: list[str]) -> list[tuple[int, dict[str, str]]]:
    path = Path(path).resolve()
    try:
        handle = path.open("r", encoding="utf-8-sig", newline="")
    except OSError as exc:
        raise DatatypeBindingError(
            f"Cannot read datatype binding resource {path}: {exc}"
        ) from exc
    with handle:
        reader = csv.DictReader(handle)
        actual = [name.lstrip("\ufeff") for name in (reader.fieldnames or [])]
        if actual != expected_header:
            raise DatatypeBindingError(
                f"{path}: header mismatch; expected {expected_header!r}, "
                f"got {actual!r}."
            )
        return [
            (line, {key: (value or "").strip() for key, value in row.items()})
            for line, row in enumerate(reader, start=2)
            if any((value or "").strip() for value in row.values())
        ]


@dataclass(frozen=True)
class MappingRecord:
    hmd_datatype: str
    xsd_base_type: str
    xbrl_item_type: str
    unit_semantics: str
    status: str
    source: str
    notes: str


@dataclass(frozen=True)
class OverrideRecord:
    semantic_path: str
    module: str
    local_name: str
    hmd_datatype: str
    xbrl_item_type: str
    status: str
    reason: str
    source: str
    notes: str


@dataclass(frozen=True)
class BindingResult:
    hmd_datatype: str
    xbrl_item_type: str
    status: str
    origin: str
    source: str
    unit_semantics: str
    overridden: bool


class DatatypeBinding:
    """Load, validate, and apply default mappings and explicit overrides."""

    def __init__(self, mapping_path=None, override_path=None):
        self.mapping_path = Path(mapping_path or default_mapping_path()).resolve()
        self.override_path = Path(override_path or default_override_path()).resolve()
        self.mappings = self._load_mappings(self.mapping_path)
        self.overrides = self._load_overrides(self.override_path)

    @staticmethod
    def _validate_status(value: str, source: Path, line: int) -> str:
        if value not in ALLOWED_STATUSES:
            raise DatatypeBindingError(
                f"{source}:{line}: unsupported status {value!r}; expected one of "
                f"{sorted(ALLOWED_STATUSES)!r}."
            )
        return value

    def _load_mappings(self, path: Path) -> dict[str, MappingRecord]:
        mappings: dict[str, MappingRecord] = {}
        for line, row in _read_rows(path, MAPPING_HEADER):
            datatype = _required(row, "hmd_datatype", path, line)
            key = normalize_datatype_key(datatype)
            if not key:
                raise DatatypeBindingError(
                    f"{path}:{line}: hmd_datatype must not normalize to blank."
                )
            if key in mappings:
                raise DatatypeBindingError(
                    f"{path}:{line}: duplicate default mapping for "
                    f"{datatype!r}."
                )
            xsd_base = _qname(
                _required(row, "xsd_base_type", path, line),
                "xsd_base_type",
                path,
                line,
            )
            item_type = _qname(
                _required(row, "xbrl_item_type", path, line),
                "xbrl_item_type",
                path,
                line,
            )
            status = self._validate_status(
                _required(row, "status", path, line), path, line
            )
            mappings[key] = MappingRecord(
                hmd_datatype=datatype,
                xsd_base_type=xsd_base,
                xbrl_item_type=item_type,
                unit_semantics=_required(row, "unit_semantics", path, line),
                status=status,
                source=_required(row, "source", path, line),
                notes=row["notes"],
            )
        if not mappings:
            raise DatatypeBindingError(f"{path}: no datatype mappings found.")
        return mappings

    def _load_overrides(self, path: Path) -> dict[str, OverrideRecord]:
        overrides: dict[str, OverrideRecord] = {}
        for line, row in _read_rows(path, OVERRIDE_HEADER):
            semantic_path = _required(row, "semantic_path", path, line)
            if semantic_path in overrides:
                raise DatatypeBindingError(
                    f"{path}:{line}: duplicate semantic_path override "
                    f"{semantic_path!r}."
                )
            datatype = _required(row, "hmd_datatype", path, line)
            if normalize_datatype_key(datatype) not in self.mappings:
                raise DatatypeBindingError(
                    f"{path}:{line}: override hmd_datatype {datatype!r} has no "
                    "default mapping record."
                )
            item_type = _qname(
                _required(row, "xbrl_item_type", path, line),
                "xbrl_item_type",
                path,
                line,
            )
            status = self._validate_status(
                _required(row, "status", path, line), path, line
            )
            overrides[semantic_path] = OverrideRecord(
                semantic_path=semantic_path,
                module=_required(row, "module", path, line),
                local_name=_required(row, "local_name", path, line),
                hmd_datatype=datatype,
                xbrl_item_type=item_type,
                status=status,
                reason=_required(row, "reason", path, line),
                source=_required(row, "source", path, line),
                notes=row["notes"],
            )
        return overrides

    def resolve(
        self,
        hmd_datatype: str,
        semantic_path: str,
        module: str,
        local_name: str,
    ) -> BindingResult:
        datatype = (hmd_datatype or "").strip()
        if not datatype:
            raise DatatypeBindingError(
                f"Blank HMD datatype at semantic_path {semantic_path!r}."
            )

        override = self.overrides.get((semantic_path or "").strip())
        if override is not None:
            mismatches = []
            if normalize_datatype_key(override.hmd_datatype) != normalize_datatype_key(datatype):
                mismatches.append(
                    f"datatype {datatype!r} != {override.hmd_datatype!r}"
                )
            if (module or "").strip() != override.module:
                mismatches.append(f"module {module!r} != {override.module!r}")
            if (local_name or "").strip() != override.local_name:
                mismatches.append(
                    f"local_name {local_name!r} != {override.local_name!r}"
                )
            if mismatches:
                raise DatatypeBindingError(
                    f"Explicit datatype override mismatch for {semantic_path!r}: "
                    + "; ".join(mismatches)
                )
            if override.status == "review-required":
                raise DatatypeBindingError(
                    f"Datatype override for {semantic_path!r} is review-required."
                )
            mapping = self.mappings[normalize_datatype_key(datatype)]
            return BindingResult(
                hmd_datatype=datatype,
                xbrl_item_type=override.xbrl_item_type,
                status=override.status,
                origin="override",
                source=override.source,
                unit_semantics=mapping.unit_semantics,
                overridden=True,
            )

        mapping = self.mappings.get(normalize_datatype_key(datatype))
        if mapping is None:
            raise DatatypeBindingError(
                f"Unknown HMD datatype {datatype!r} at semantic_path "
                f"{semantic_path!r}; no string fallback is permitted."
            )
        if mapping.status == "review-required":
            raise DatatypeBindingError(
                f"HMD datatype {datatype!r} at semantic_path {semantic_path!r} "
                f"is review-required ({mapping.source})."
            )
        return BindingResult(
            hmd_datatype=datatype,
            xbrl_item_type=mapping.xbrl_item_type,
            status=mapping.status,
            origin="default",
            source=mapping.source,
            unit_semantics=mapping.unit_semantics,
            overridden=False,
        )
