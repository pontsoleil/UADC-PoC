#!/usr/bin/env python3
"""Prepare and validate Canonical 18-column HMD files for taxonomy tooling.

The preprocessor keeps family-specific legacy column layouts outside the
Taxonomy Generator.  Namespace behaviour is selected explicitly as either
``single-namespace`` or ``module-based``; it is never inferred from a family
name.  A taxonomy module identity and the lexical namespace prefix used in an
XPath are separate inputs.  The first legacy mapping profile is the EN CIUS
20-column LHM.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Iterable


CANONICAL_HEADER = [
    "sequence",
    "module",
    "level",
    "type",
    "identifier",
    "name",
    "datatype",
    "multiplicity",
    "association_role",
    "definition",
    "label_local",
    "definition_local",
    "source_bsm_id",
    "semantic_path",
    "associated_module",
    "class_term",
    "local_name",
    "xpath",
]

EN_CIUS_LEGACY_HEADER = [
    "sequence",
    "syntax_sequence",
    "level",
    "lhm_level",
    "type",
    "identifier",
    "name",
    "datatype",
    "multiplicity",
    "domain_name",
    "definition",
    "module",
    "class_term",
    "id",
    "path",
    "semantic_path",
    "label_local",
    "definition_local",
    "element",
    "xpath",
]

NCNAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9._-]*$")
MULTIPLICITY_RE = re.compile(r"^(?:0|1|[01]\.\.(?:0|1|\*|n))$")


class HmdError(ValueError):
    """Raised when conversion or validation cannot proceed safely."""


def read_csv(path: Path, encoding: str) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding=encoding, newline="") as handle:
        reader = csv.DictReader(handle)
        header = [(name or "").lstrip("\ufeff") for name in (reader.fieldnames or [])]
        rows = []
        for raw in reader:
            row = {
                (key or "").lstrip("\ufeff"): (value or "").strip()
                for key, value in raw.items()
                if key is not None
            }
            if any(row.values()):
                rows.append(row)
    return header, rows


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def qname_step(
    row: dict[str, str],
    mode: str,
    module_prefix_template: str,
    namespace_prefix: str | None,
) -> str:
    local_name = row["local_name"]
    if namespace_prefix is not None:
        return f"{namespace_prefix}:{local_name}"
    if mode == "single-namespace":
        return local_name
    return f"{module_prefix_template.format(module=row['module'])}:{local_name}"


def derive_xpaths(
    rows: Iterable[dict[str, str]],
    mode: str,
    xpath_root: str,
    module_prefix_template: str,
    namespace_prefix: str | None,
) -> list[str]:
    ancestors: list[tuple[int, str]] = []
    result = []
    root = xpath_root.rstrip("/")
    for row in rows:
        try:
            level = int(row["level"])
        except (KeyError, ValueError) as exc:
            raise HmdError(f"Invalid level {row.get('level')!r}.") from exc
        while ancestors and ancestors[-1][0] >= level:
            ancestors.pop()
        step = qname_step(row, mode, module_prefix_template, namespace_prefix)
        path_steps = [ancestor_step for _, ancestor_step in ancestors] + [step]
        result.append(root + "/" + "/".join(path_steps))
        if row.get("type") in {"C", "R"}:
            ancestors.append((level, step))
    return result


def convert_en_cius(
    rows: list[dict[str, str]],
    module: str,
    namespace_prefix: str,
    xpath_root: str,
) -> list[dict[str, str]]:
    converted = []
    for row in rows:
        try:
            source_level = int(row["level"])
        except (KeyError, ValueError) as exc:
            raise HmdError(
                f"EN CIUS row sequence {row.get('sequence')!r} has invalid level."
            ) from exc
        converted.append(
            {
                "sequence": row.get("sequence", ""),
                "module": module,
                "level": str(source_level + 1),
                "type": row.get("type", ""),
                "identifier": row.get("identifier", ""),
                "name": row.get("name", ""),
                "datatype": row.get("datatype", ""),
                "multiplicity": row.get("multiplicity", ""),
                "association_role": "",
                "definition": row.get("definition", ""),
                "label_local": row.get("label_local", ""),
                "definition_local": row.get("definition_local", ""),
                "source_bsm_id": row.get("id", ""),
                "semantic_path": row.get("semantic_path", ""),
                "associated_module": "",
                "class_term": row.get("class_term", ""),
                "local_name": row.get("element", ""),
                "xpath": "",
            }
        )
    xpaths = derive_xpaths(
        converted, "module-based", xpath_root, "{module}", namespace_prefix
    )
    for row, xpath in zip(converted, xpaths):
        row["xpath"] = xpath
    return converted


def validate(
    header: list[str],
    rows: list[dict[str, str]],
    mode: str,
    xpath_root: str,
    module_prefix_template: str,
    namespace_prefix: str | None,
) -> dict[str, object]:
    errors: list[str] = []
    if header != CANONICAL_HEADER:
        errors.append(f"header must equal the fixed Canonical 18-column header: {header!r}")
    if not rows:
        errors.append("HMD has no data rows")

    sequences: list[int] = []
    levels: list[int] = []
    seen_semantic: set[str] = set()
    seen_qname: set[tuple[str, str] | str] = set()
    seen_xpath: set[str] = set()
    structural_levels: set[int] = set()
    roots = 0

    for index, row in enumerate(rows, start=2):
        try:
            sequence = int(row.get("sequence", ""))
            if sequence <= 0:
                raise ValueError
            sequences.append(sequence)
        except ValueError:
            errors.append(f"row {index}: sequence must be a positive integer")

        try:
            level = int(row.get("level", ""))
            if level < 1:
                raise ValueError
            levels.append(level)
        except ValueError:
            errors.append(f"row {index}: level must be an integer >= 1")
            level = -1

        row_type = row.get("type", "")
        if row_type not in {"A", "C", "R"}:
            errors.append(f"row {index}: unsupported type {row_type!r}")
        if level == 1:
            roots += 1
            if row_type != "C":
                errors.append(f"row {index}: level-1 root must be type C")
        elif level > 1 and (level - 1) not in structural_levels:
            errors.append(f"row {index}: no structural parent exists at level {level - 1}")
        structural_levels = {value for value in structural_levels if value < level}
        if row_type in {"C", "R"} and level >= 1:
            structural_levels.add(level)

        multiplicity = row.get("multiplicity", "")
        if not MULTIPLICITY_RE.fullmatch(multiplicity):
            errors.append(f"row {index}: invalid multiplicity {multiplicity!r}")

        semantic_path = row.get("semantic_path", "")
        if not semantic_path:
            errors.append(f"row {index}: semantic_path is empty")
        elif semantic_path in seen_semantic:
            errors.append(f"row {index}: duplicate semantic_path {semantic_path!r}")
        seen_semantic.add(semantic_path)

        local_name = row.get("local_name", "")
        if not local_name or not NCNAME_RE.fullmatch(local_name) or ":" in local_name:
            errors.append(f"row {index}: local_name is not a valid unprefixed NCName: {local_name!r}")

        module = row.get("module", "")
        if mode == "single-namespace":
            if module:
                errors.append(f"row {index}: module must be empty in single-namespace mode")
            qname_key: tuple[str, str] | str = local_name
        else:
            if not module or not NCNAME_RE.fullmatch(module) or ":" in module:
                errors.append(f"row {index}: module is required and must be an NCName")
            qname_key = (module, local_name)
        if qname_key in seen_qname:
            errors.append(f"row {index}: duplicate QName key {qname_key!r}")
        seen_qname.add(qname_key)

        xpath = row.get("xpath", "")
        if not xpath:
            errors.append(f"row {index}: xpath is empty")
        elif xpath in seen_xpath:
            errors.append(f"row {index}: duplicate xpath {xpath!r}")
        seen_xpath.add(xpath)

    if roots != 1:
        errors.append(f"HMD must have exactly one level-1 root; found {roots}")
    if sequences and (len(sequences) != len(set(sequences)) or sequences != sorted(sequences)):
        errors.append("sequence values must be unique and ascending")
    if levels:
        for previous, current in zip(levels, levels[1:]):
            if current > previous + 1:
                errors.append(f"level hierarchy jumps from {previous} to {current}")

    if not errors:
        expected_xpaths = derive_xpaths(
            rows, mode, xpath_root, module_prefix_template, namespace_prefix
        )
        for index, (row, expected) in enumerate(zip(rows, expected_xpaths), start=2):
            if row.get("xpath", "") != expected:
                errors.append(
                    f"row {index}: xpath is not deterministic; expected {expected!r}, "
                    f"got {row.get('xpath', '')!r}"
                )

    return {
        "status": "PASS" if not errors else "FAIL",
        "row_count": len(rows),
        "column_count": len(header),
        "namespace_mode": mode,
        "root_count": roots,
        "error_count": len(errors),
        "errors": errors,
    }


def write_csv(path: Path, rows: list[dict[str, str]], encoding: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding=encoding, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CANONICAL_HEADER, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--profile", choices=("canonical", "en-cius-legacy"), required=True,
        help="Explicit input column-mapping profile; it does not select namespace mode.",
    )
    parser.add_argument(
        "--namespace-mode", choices=("single-namespace", "module-based"), required=True
    )
    parser.add_argument("--validation-only", action="store_true")
    parser.add_argument("--input-encoding", default="utf-8-sig")
    parser.add_argument("--output-encoding", default="utf-8")
    parser.add_argument(
        "--xpath-root",
        default=None,
        help="Taxonomy XPath root. Defaults to empty for single namespace and /xbrli:xbrl for module based.",
    )
    parser.add_argument(
        "--module-prefix-template",
        default="gl-{module}",
        help="Format string used to resolve module names to XPath prefixes.",
    )
    parser.add_argument(
        "--module",
        help="Taxonomy module identity assigned by a legacy conversion profile.",
    )
    parser.add_argument(
        "--namespace-prefix",
        help="Explicit lexical namespace prefix used in generated or validated XPath steps.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        input_path = args.input.resolve()
        header, source_rows = read_csv(input_path, args.input_encoding)
        input_hash = sha256(input_path)
        xpath_root = args.xpath_root
        if xpath_root is None:
            xpath_root = "" if args.namespace_mode == "single-namespace" else "/xbrli:xbrl"
        if args.module is not None and (
            not NCNAME_RE.fullmatch(args.module) or ":" in args.module
        ):
            raise HmdError("--module must be an unprefixed NCName.")
        if args.namespace_prefix is not None and (
            not NCNAME_RE.fullmatch(args.namespace_prefix)
            or ":" in args.namespace_prefix
        ):
            raise HmdError("--namespace-prefix must be an unprefixed NCName.")

        if args.profile == "en-cius-legacy":
            if header != EN_CIUS_LEGACY_HEADER:
                raise HmdError(
                    f"EN CIUS legacy header mismatch. Expected {EN_CIUS_LEGACY_HEADER!r}, got {header!r}."
                )
            if args.namespace_mode != "module-based":
                raise HmdError(
                    "EN CIUS legacy profile with a module requires module-based mode."
                )
            if args.module is None:
                raise HmdError("--module is required for EN CIUS legacy conversion.")
            if args.namespace_prefix is None:
                raise HmdError(
                    "--namespace-prefix is required for EN CIUS legacy conversion."
                )
            if args.validation_only:
                raise HmdError("Legacy input must be converted before Canonical validation.")
            if args.output is None:
                raise HmdError("--output is required for legacy conversion.")
            output_path = args.output.resolve()
            if output_path.exists():
                raise HmdError(
                    f"Output already exists and will not be overwritten: {output_path}"
                )
            rows = convert_en_cius(
                source_rows, args.module, args.namespace_prefix, xpath_root
            )
            validation = validate(
                CANONICAL_HEADER, rows, args.namespace_mode, xpath_root,
                args.module_prefix_template, args.namespace_prefix,
            )
            if validation["status"] != "PASS":
                raise HmdError(json.dumps(validation, ensure_ascii=False))
            write_csv(output_path, rows, args.output_encoding)
            result = {
                **validation,
                "profile": args.profile,
                "input": str(input_path),
                "input_sha256": input_hash,
                "output": str(output_path),
                "output_sha256": sha256(output_path),
            }
        else:
            if header != CANONICAL_HEADER:
                raise HmdError(
                    f"Canonical header mismatch. Expected {CANONICAL_HEADER!r}, got {header!r}."
                )
            if not args.validation_only:
                raise HmdError("Canonical profile is validation-only in this implementation.")
            if args.output is not None:
                raise HmdError("--output is not allowed with --validation-only.")
            validation = validate(
                header, source_rows, args.namespace_mode, xpath_root,
                args.module_prefix_template, args.namespace_prefix,
            )
            result = {
                **validation,
                "profile": args.profile,
                "input": str(input_path),
                "input_sha256": input_hash,
                "content_unchanged": True,
            }

        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "PASS" else 1
    except (OSError, HmdError, KeyError, ValueError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
