# AGENTS.md

## Project

This repository is the UADA / UADC Proof of Concept workspace.

The purpose of this repository is to develop and maintain a proof of concept for:

- EN 16931 invoice Logical Hierarchical Model (LHM)
- UBL syntax binding
- XML-to-hierarchical-CSV conversion
- hierarchical structured CSV
- xBRL-CSV metadata
- taxonomy generation
- round-trip XML reconstruction tests

This repository replaces the previous UADA repository contents with the UADC PoC workspace.

## Working directory

Use this directory as the main working repository:

```text
C:\Users\nobuy\GitHub\UADC_GIT
```

Do not use the old development directory as the GitHub synchronization target:

```text
C:\Users\nobuy\GitHub\UADA
```

The old directory may contain unrelated local history, large files, and legacy workspaces.

## Important repository rules

- Do not commit generated local output under `out/` unless explicitly requested.
- Do not commit Python cache files.
- Do not commit virtual environment directories.
- Do not commit files larger than 90 MB.
- Do not commit private keys, credentials, certificates, passwords, or local machine configuration.
- Do not reintroduce old UADA legacy folders unless explicitly requested.
- Keep source files, tests, and specifications in the current UADC PoC structure.

## Ignore these paths

The following paths should normally remain untracked:

```text
out/
__pycache__/
.pytest_cache/
.venv/
venv/
*.pyc
```

## Main source areas

Use these directories according to their purpose:

```text
docs/        Project documentation and design notes
references/ Reference notes and source references
samples/    Input and expected sample files
specs/      LHM and syntax binding specifications
src/        Main conversion programs
tests/      Regression tests and test artifacts
tools/      Utility scripts for LHM, bindings, definitions, and taxonomy support
```

## Development policy

When changing code:

1. Understand the existing design before editing.
2. Prefer small, focused changes.
3. Keep the LHM, binding CSV, converter code, and tests consistent.
4. Update documentation when behavior changes.
5. Preserve UTF-8 text files and LF line endings according to `.gitattributes`.

## Test commands

Run the relevant tests after changes.

For a broad check:

```powershell
python -m pytest
```

For focused checks:

```powershell
python .\tests\test_lhm_semantic_paths.py
python .\tests\test_lhm_hierarchical_csv_layout.py
python .\tests\test_syntax_binding_hierarchical.py
python .\tests\test_openpeppol_invoice_conversion.py
python .\tests\test_syntax_binding_reverse.py
python .\tests\test_roundtrip_artifacts.py
python .\tests\test_xbrlgl_generator_uadc_lhm.py
```

If Arelle or UBL schema validation is not available locally, report that clearly instead of assuming success.

## Before committing

Before every commit, run:

```powershell
git status
git diff --stat
git diff
```

Also check for large files:

```powershell
git ls-files | ForEach-Object {
  $f = $_
  if (Test-Path $f) {
    $item = Get-Item $f
    if ($item.Length -gt 90MB) {
      [PSCustomObject]@{
        File = $f
        MB = [math]::Round($item.Length / 1MB, 2)
      }
    }
  }
}
```

Do not commit if any file larger than 90 MB is listed.

## Commit and push policy

Use concise English commit messages.

Examples:

```text
Update LHM generation rules
Fix UBL syntax binding conversion
Add round-trip XML regression test
Update taxonomy generation documentation
```

After successful tests and review:

```powershell
git add -A
git commit -m "Concise commit message"
git push origin main
```

Do not force push unless explicitly instructed.

## Reporting policy

When finishing a task, report:

- what was changed;
- which files were modified;
- which tests were run;
- whether any tests failed or were skipped;
- whether the changes were committed and pushed.
