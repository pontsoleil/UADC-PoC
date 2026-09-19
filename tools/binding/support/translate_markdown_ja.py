#!/usr/bin/env python3
# coding: utf-8
"""
Generate Japanese Markdown documents with a controlled terminology table.

Purpose:
    Translate first-party UADC Markdown documents from English to Japanese
    while preserving code blocks, commands, paths, URLs, identifiers, and
    Markdown structure. Apply project terminology consistently from a CSV file.

Processing overview:
    The script discovers supported Markdown sources, maps every source to a
    ja/ subdirectory below its current directory, protects technical tokens and
    glossary terms, translates natural-language segments with an installed
    local Argos Translate English-to-Japanese model, restores protected values,
    and writes UTF-8 Japanese Markdown. Re-running the script after changing
    the terminology CSV applies corrected Japanese terms to every output.

Command-line arguments:
    --root: UADC_PoC repository root. Defaults to the parent of tools/.
    --terminology: Terminology CSV. Defaults to docs/ja/TERMINOLOGY.csv.
    --runtime: Directory containing the local argostranslate Python package.
    --check: Validate source/output coverage without writing files.

Results:
    Writes Japanese Markdown files below ja/ directories and prints the source
    and output counts. Returns exit code 0 on success.

Creation Date: 2026-07-14
Last Modified: 2026-07-14

Copyright 2026 Sambuichi Professional Engineers Office
Designed by SAMBUICHI, Nobuyuki
Produced by ChatGPT and Codex, edited by SAMBUICHI, Nobuyuki

License:
    This software source code is licensed under the MIT License.

    Non-code materials in the UADC-PoC project, including original mapping
    tables, syntax binding definitions, semantic binding definitions,
    transformation rules, explanatory notes, and documentation, may be licensed
    separately under Creative Commons Attribution-NonCommercial 4.0
    International License (CC BY-NC 4.0), where so indicated.

    Third-party standards, schemas, taxonomies, code lists, field names,
    descriptions, and excerpts remain subject to their original copyright
    notices and licenses. This license notice does not relicense third-party
    materials.

MIT License

Copyright (c) 2026 Sambuichi Professional Engineers Office

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
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable


EXCLUDED_DIRECTORY_NAMES = {
    ".git",
    ".translation_runtime",
    ".translation_data",
    ".translation_cache",
    "docs_a",
    "docs_codex",
    "ja",
    "out",
}
EXCLUDED_FILES = {"AGENTS.md"}
TECHNICAL_TOKEN_RE = re.compile(
    r"https?://[^\s)]+"
    r"|(?<![\w])--[a-zA-Z0-9][a-zA-Z0-9-]*"
    r"|(?:0|1)\.\.\*"
    r"|d_?\*"
    r"|(?:[A-Za-z0-9_.-]+[\\/])+(?:[A-Za-z0-9_.${}-]+)"
    r"|\$\.[A-Za-z0-9_.\[\]?@='\"-]+"
    r"|/[A-Za-z0-9_:.\-\[\]?@='\"/]+"
    r"|[A-Za-z0-9_.*-]+\.(?:py|csv|json|xml|xsd|xlsx|xbrl|md|pdf|psv|html)"
    r"|\b(?:d[A-Z][A-Za-z0-9]*|BT-[0-9]+|BG-[0-9]+|C[0-9]{4}|A[0-9]{4})\b"
)
LINK_TARGET_RE = re.compile(r"(?P<prefix>\]\()(?P<target>[^)]+)(?P<suffix>\))")
TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?(?:\s*:?-+:?\s*\|)+\s*$")


@dataclass(frozen=True)
class Term:
    source: str
    japanese: str
    match_mode: str


class Protector:
    def __init__(self) -> None:
        self.values: list[str] = []

    def token(self, value: str) -> str:
        index = len(self.values)
        self.values.append(value)
        return f"[{90000 + index}]"

    def restore(self, text: str) -> str:
        for index in range(len(self.values) - 1, -1, -1):
            value = self.values[index]
            number = 90000 + index
            token = f"[{number}]"
            text = re.sub(
                rf"(?:\[\s*{number}\s*\]|【\s*{number}\s*】|「\s*{number}\s*」)",
                lambda _match, v=value: v,
                text,
            )
            text = text.replace(token, value)
        return text


@dataclass(frozen=True)
class ProtectedRange:
    start: int
    end: int
    replacement: str
    priority: int


def parse_args() -> argparse.Namespace:
    default_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Generate Japanese Markdown under ja/ directories.")
    parser.add_argument("--root", type=Path, default=default_root)
    parser.add_argument("--terminology", type=Path)
    parser.add_argument("--runtime", type=Path)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def read_terms(path: Path) -> list[Term]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    terms = [
        Term((row.get("source_term") or "").strip(), (row.get("ja_term") or "").strip(), (row.get("match_mode") or "phrase").strip())
        for row in rows
        if (row.get("source_term") or "").strip() and (row.get("ja_term") or "").strip()
    ]
    return sorted(terms, key=lambda term: len(term.source), reverse=True)


def source_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.md"):
        relative = path.relative_to(root)
        if path.name in EXCLUDED_FILES:
            continue
        if any(part in EXCLUDED_DIRECTORY_NAMES for part in relative.parts[:-1]):
            continue
        files.append(path)
    return sorted(files)


def output_path(source: Path) -> Path:
    return source.parent / "ja" / source.name


def rewrite_relative_links(text: str, source: Path, target: Path) -> str:
    def replace(match: re.Match[str]) -> str:
        link = match.group("target")
        if re.match(r"^(?:https?://|mailto:|#)", link):
            return match.group(0)
        path_text, separator, fragment = link.partition("#")
        if not path_text:
            return match.group(0)
        resolved = (source.parent / path_text).resolve()
        destination = output_path(resolved) if resolved.suffix.lower() == ".md" and resolved.is_file() else resolved
        relative = os.path.relpath(destination, target.parent).replace("\\", "/")
        rewritten = relative + (separator + fragment if separator else "")
        return match.group("prefix") + rewritten + match.group("suffix")

    return LINK_TARGET_RE.sub(replace, text)


def protect_link_targets(text: str, protector: Protector) -> str:
    return LINK_TARGET_RE.sub(
        lambda match: match.group("prefix") + protector.token(match.group("target")) + match.group("suffix"),
        text,
    )


def protect_terms(text: str, terms: Iterable[Term], protector: Protector) -> str:
    for term in terms:
        flags = 0 if term.match_mode == "literal" else re.IGNORECASE
        pattern = re.compile(re.escape(term.source), flags)
        text = pattern.sub(lambda _match, value=term.japanese: protector.token(value), text)
    return text


def protect_technical_tokens(text: str, protector: Protector) -> str:
    text = protect_link_targets(text, protector)
    return TECHNICAL_TOKEN_RE.sub(lambda match: protector.token(match.group(0)), text)


def term_pattern(term: Term) -> re.Pattern[str]:
    escaped = re.escape(term.source)
    if term.source[:1].isalnum():
        escaped = r"(?<![A-Za-z0-9_])" + escaped
    if term.source[-1:].isalnum():
        escaped += r"(?![A-Za-z0-9_])"
    flags = 0 if term.match_mode == "literal" else re.IGNORECASE
    return re.compile(escaped, flags)


def protected_ranges(text: str, terms: Iterable[Term]) -> list[ProtectedRange]:
    candidates: list[ProtectedRange] = []
    for term in terms:
        for match in term_pattern(term).finditer(text):
            candidates.append(ProtectedRange(match.start(), match.end(), term.japanese, 0))
    for match in LINK_TARGET_RE.finditer(text):
        candidates.append(
            ProtectedRange(match.start("target"), match.end("target"), match.group("target"), 1)
        )
    for match in TECHNICAL_TOKEN_RE.finditer(text):
        candidates.append(ProtectedRange(match.start(), match.end(), match.group(0), 2))

    selected: list[ProtectedRange] = []
    occupied: list[tuple[int, int]] = []
    for candidate in sorted(candidates, key=lambda item: (item.priority, item.start, -(item.end - item.start))):
        if any(candidate.start < end and start < candidate.end for start, end in occupied):
            continue
        selected.append(candidate)
        occupied.append((candidate.start, candidate.end))
    return sorted(selected, key=lambda item: item.start)


def translate_plain_segment(text: str, translator: Callable[[str], str], terms: list[Term]) -> str:
    if not text or not re.search(r"[A-Za-z]", text):
        return text
    protector = Protector()
    protected = protect_technical_tokens(text, protector)
    protected = protect_terms(protected, terms, protector)
    translated = translator(protected)
    translated = protector.restore(translated)
    return translated.replace("**", "")


def bold_spans(text: str) -> list[tuple[int, int, str]]:
    spans: list[tuple[int, int, str]] = []
    cursor = 0
    while True:
        start = text.find("**", cursor)
        if start < 0:
            break
        search = start + 2
        while True:
            end = text.find("**", search)
            if end < 0:
                return spans
            if end + 2 < len(text) and text[end + 2] == "*":
                search = end + 1
                continue
            spans.append((start, end + 2, text[start + 2:end]))
            cursor = end + 2
            break
    return spans


def translate_segment(text: str, translator: Callable[[str], str], terms: list[Term]) -> str:
    if not text.strip() or TABLE_SEPARATOR_RE.match(text):
        return text
    pieces: list[str] = []
    cursor = 0
    for start, end, content in bold_spans(text):
        pieces.append(translate_plain_segment(text[cursor:start], translator, terms))
        inner = translate_plain_segment(content, translator, terms)
        pieces.append("**" + inner + "**")
        cursor = end
    pieces.append(translate_plain_segment(text[cursor:], translator, terms))
    return "".join(pieces)


def translate_markdown(text: str, translator: Callable[[str], str], terms: list[Term]) -> str:
    output: list[str] = []
    paragraph: list[str] = []
    in_fence = False

    def flush_paragraph() -> None:
        if not paragraph:
            return
        joined = " ".join(line.strip() for line in paragraph)
        output.append(translate_segment(joined, translator, terms))
        paragraph.clear()

    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            flush_paragraph()
            in_fence = not in_fence
            output.append(line)
            continue
        if in_fence:
            output.append(line)
            continue
        if not line.strip():
            flush_paragraph()
            output.append("")
            continue
        structural = re.match(r"^(#{1,6}\s+|\s*[-*+]\s+|\s*\d+\.\s+|>\s*|\|)", line)
        if structural or TABLE_SEPARATOR_RE.match(line):
            flush_paragraph()
            prefix = structural.group(1) if structural else ""
            body = line[len(prefix):] if prefix else line
            output.append(prefix + translate_segment(body, translator, terms))
            continue
        paragraph.append(line)
    flush_paragraph()
    return "\n".join(output).rstrip() + "\n"


def load_translator(runtime: Path, root: Path) -> Callable[[str], str]:
    if str(runtime) not in sys.path:
        sys.path.insert(0, str(runtime))
    os.environ.setdefault("ARGOS_PACKAGES_DIR", str(root / ".translation_data" / "packages"))
    os.environ.setdefault("XDG_DATA_HOME", str(root / ".translation_data"))
    os.environ.setdefault("XDG_CACHE_HOME", str(root / ".translation_cache"))
    os.environ.setdefault("XDG_CONFIG_HOME", str(root / ".translation_data" / "config"))
    os.environ.setdefault("ARGOS_CHUNK_TYPE", "MINISBD")
    from argostranslate import translate  # type: ignore

    installed = translate.get_installed_languages()
    source_language = next((language for language in installed if language.code == "en"), None)
    target_language = next((language for language in installed if language.code == "ja"), None)
    if source_language is None or target_language is None:
        raise RuntimeError("Argos English-to-Japanese model is not installed in .translation_data.")
    translation = source_language.get_translation(target_language)
    cache: dict[str, str] = {}

    def cached_translate(text: str) -> str:
        if text not in cache:
            cache[text] = translation.translate(text)
        return cache[text]

    return cached_translate


def validate_outputs(root: Path, sources: list[Path]) -> list[str]:
    errors: list[str] = []
    for source in sources:
        target = output_path(source)
        if not target.is_file():
            errors.append(f"missing output: {target.relative_to(root)}")
            continue
        source_fences = source.read_text(encoding="utf-8-sig").count("```")
        source_bold = source.read_text(encoding="utf-8-sig").count("**")
        target_text = target.read_text(encoding="utf-8-sig")
        if target_text.count("```") != source_fences:
            errors.append(f"code fence mismatch: {target.relative_to(root)}")
        if target_text.count("**") != source_bold:
            errors.append(f"bold marker mismatch: {target.relative_to(root)}")
        if not re.search(r"[ぁ-んァ-ヶ一-龠]", target_text):
            errors.append(f"no Japanese text: {target.relative_to(root)}")
    return errors


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    terminology = (args.terminology or root / "docs" / "ja" / "TERMINOLOGY.csv").resolve()
    runtime = (args.runtime or root / ".translation_runtime").resolve()
    sources = source_files(root)
    if args.check:
        errors = validate_outputs(root, sources)
        for error in errors:
            print(error, file=sys.stderr)
        print(f"checked {len(sources)} source Markdown file(s); errors={len(errors)}")
        return 1 if errors else 0

    terms = read_terms(terminology)
    translator = load_translator(runtime, root)
    for index, source in enumerate(sources, start=1):
        target = output_path(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        source_text = source.read_text(encoding="utf-8-sig")
        translated = translate_markdown(source_text, translator, terms)
        translated = rewrite_relative_links(translated, source, target)
        target.write_text(translated, encoding="utf-8", newline="\n")
        print(f"[{index}/{len(sources)}] {source.relative_to(root)} -> {target.relative_to(root)}")

    errors = validate_outputs(root, sources)
    for error in errors:
        print(error, file=sys.stderr)
    print(f"generated {len(sources)} Japanese Markdown file(s); errors={len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
