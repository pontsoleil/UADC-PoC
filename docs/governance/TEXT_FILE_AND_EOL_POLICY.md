# Text File and EOL Policy

## Purpose

This policy makes project text byte-stable from identical inputs on Windows, macOS, and Linux. Project processing must not depend on a user's global `core.autocrlf` setting. The policy prevents unnecessary SHA-256 changes and large diffs caused only by EOL conversion. It applies to CSV, XML, JSON, Markdown, programs, logs, and generated taxonomy text.

## File classifications

### 1. `PROJECT_TEXT`

Project-authored text other than CSV must use UTF-8 without BOM, LF line endings, exactly one final LF, and no space or tab at a logical line end. Project-authored CSV is governed by the `CSV_TEXT` rules below.

### 2. `GENERATED_TEXT`

Non-CSV text emitted by a Generator or materializer must use the same canonical form as `PROJECT_TEXT`. Generated CSV must use the `CSV_TEXT` canonical form. The responsible Generator or materializer must guarantee the applicable form. Do not hand-edit only the final generated artifact.

### 3. `EXTERNAL_VERBATIM`

Third-party originals must retain their exact bytes, BOM, and EOL. They are outside automatic normalization and their provenance must be controlled by SHA-256.

### 4. `BINARY`

DOCX, XLSX, PDF, ZIP, images, and other binary files are outside EOL processing.

### 5. `CSV_TEXT`

Canonical CSV files shall be encoded as UTF-8 without BOM. CRLF and LF record delimiters and embedded line breaks in quoted fields are permitted. Line-ending style and the presence of a final line break are informational properties and shall not, by themselves, cause validation failure. Conformance shall be determined by successful strict UTF-8 decoding, successful CSV parsing, structural integrity, and preservation of cell values and business semantics. Use the approved CSV/XLSX bridge for Excel review rather than adding a BOM to Canonical CSV.

- CSV readers may use `utf-8-sig` or equivalent for input tolerance so a BOM is not treated as part of the first header.
- Project-controlled CSV writers must emit UTF-8 without BOM; they must not preserve or add an input BOM accidentally.
- The rule applies to Structured CSV, FSM, BSM, LHM, HMD, Binding, Value Domain, manifest, diagnostic, test fixture, and evidence CSV where present.
- An approved `EXTERNAL_VERBATIM` CSV retains its original bytes.
- A CSV required by an external specification to use a different encoding or BOM rule needs an explicit exception approval identifying the path and specification basis.
- Git EOL processing and CSV BOM control are separate controls. A future Formal GIT governance change may use `*.csv -text` to preserve approved Candidate CSV bytes, but an actual `.gitattributes` change requires separate impact analysis and approval.

Test logs are an evidence subclass of `PROJECT_TEXT` when included in a public package. Convert CRLF and CR to LF, remove only space or tab at each logical line end, preserve messages, line order, exit status, and diagnostics, and retain exactly one final LF. If a raw log is necessary, store it separately as non-public evidence and record its SHA-256.

## Multiline values

Whitespace can be data inside an HMD `definition`, a quoted CSV field, XML label text, or a JSON string. For governed non-CSV multiline values, normalize in this order:

1. Convert CRLF and CR to LF.
2. Remove space and tab only at each logical line end.
3. Preserve leading indentation and spaces between words.
4. Preserve meaningful internal blank lines.
5. Remove unnecessary blank lines at the end of the value.
6. Regenerate dependent artifacts from the normalized authoritative input.

CSV is excluded from the forced multiline-newline conversion above: preserve CSV cell values and use a CSV parser to assess structure and semantics. Do not apply an unconditional `rstrip()` to a completed CSV or XML file. Use a format-aware parser and normalize only a governed value for which normalization is required, not arbitrary physical lines.

## Responsibility boundaries

- The author of an authoritative non-CSV input normalizes governed logical line endings of multiline strings; CSV preserves approved parsed cell values.
- A materializer carries normalized model values into the HMD.
- The Taxonomy Generator emits XML and XSD from the normalized HMD in the required text form.
- The log-capture process normalizes evidence selected for public inclusion.
- The manifest generator records SHA-256 for the normalized bytes.
- Do not repair only a downstream artifact while leaving its upstream input inconsistent.

## Candidate gate

Before Candidate approval, place the complete Payload in an isolated temporary Git repository or independent index and virtually stage every file. Explicitly include evidence that would normally be ignored, then run:

```text
git diff --cached --check
```

A tracked-only `git diff --check` is not a substitute for this full-Payload gate. Confirm all of the following:

- invalid UTF-8: 0;
- unexpected BOM in project-authored or generated CSV: 0;
- unexpected BOM in non-CSV project text: 0;
- CRLF or CR in non-CSV governed text: 0, excluding `EXTERNAL_VERBATIM`; CSV EOL findings are informational unless parsing, structure, values, or business semantics are affected;
- trailing space or tab: 0;
- missing final LF in non-CSV governed text: 0;
- multiple final LF in non-CSV governed text: 0;
- manifest SHA-256 mismatch: 0;
- external-original SHA-256 change: 0.

## Formal GIT gate

Before commit:

- compare the staged path set with the approved plan;
- confirm that every approved target, including ignored evidence, is staged;
- run `git diff --cached --check`;
- confirm that every staged blob matches its Candidate SHA-256;
- do not bypass a failure with `--no-verify`, whitespace-setting changes, or an unapproved `.gitattributes` exception.

## Protection of existing files

This policy does not authorize bulk EOL conversion of an existing repository. A nonconforming existing file may be normalized only in a limited change set that records explicit paths, a pre-replacement backup, before and after SHA-256, semantic-difference classification, regeneration of dependent artifacts, a successor Candidate, and explicit placement and Git-operation approval.

## Recommended `.gitattributes` and `.editorconfig`

The following examples are guidance. They are not authorization to create or change these files in an existing repository.

```gitattributes
* text=auto
*.md   text eol=lf
*.csv  -text
*.json text eol=lf
*.xml  text eol=lf
*.xsd  text eol=lf
*.py   text eol=lf
*.log  text eol=lf
*.pdf  binary
*.zip  binary
*.png  binary
path/to/external-verbatim/** -text
```

```editorconfig
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.csv]
charset = utf-8
end_of_line = unset
insert_final_newline = unset
trim_trailing_whitespace = unset

[*.{pdf,zip,png,jpg,jpeg,gif,docx,xlsx}]
insert_final_newline = unset
trim_trailing_whitespace = unset
```

Editor trimming must still be disabled or applied through a format-aware process where whitespace is data in multiline CSV, XML, or JSON values. Explicitly classify external-verbatim paths before applying editor automation.

Adding `.gitattributes` alone is not permission to renormalize existing files. Do not run `git add --renormalize .` without separate explicit approval.
