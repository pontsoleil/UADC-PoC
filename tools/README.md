# Tools Directory

`tools/` has two roles.

1. Initial setup after cloning the GitHub repository.
2. Development environment maintenance for continuing work safely.

The main invoice conversion runtime is not in `tools/`. The Structured CSV and
xBRL-CSV metadata JSON converter remains:

```text
src/syntax_binding_hierarchical.py
```

Use `tools/` for setup, regeneration, test artifact building, taxonomy output,
and specification maintenance.

## 1. Initial Setup After GitHub Clone

These steps bring a fresh clone to a usable local PoC state.

### 1.1 Clone And Enter The Workspace

Use the actual GitHub repository URL for this project:

Windows PowerShell:

```powershell
git clone https://github.com/pontsoleil/UADC-PoC.git
cd .\UADC-PoC
```

macOS / Linux shell:

```sh
git clone https://github.com/pontsoleil/UADC-PoC.git
cd ./UADC-PoC
```

If the repository was cloned as a larger workspace, enter the PoC directory:

```powershell
cd <local-clone-directory>\UADC-PoC
```

Set a Python command variable. Adjust the path if Python is installed
elsewhere:

Windows PowerShell:

```powershell
$python = 'python'
& $python --version
```

`$python = 'python'` is a PowerShell variable assignment used by the examples
below. It means "run the Python executable available on `PATH`." If that command
does not work on your machine, replace `python` with the full path to your local
Python executable, for example:

```powershell
$python = '<path-to-python.exe>'
& $python --version
```

macOS / Linux shell:

```sh
PYTHON=python3
$PYTHON --version
```

In macOS/Linux shells, `PYTHON=python3` assigns a shell variable and `$PYTHON ...`
runs it directly. Do not use PowerShell's `& $python` syntax in `sh`, `bash`, or
`zsh`.

### 1.2 Confirm The Directory Layout

The normal working layout is:

```text
src/      runtime conversion scripts
tools/    setup, generation, and maintenance scripts
tests/    regression checks
specs/    committed LHM and binding definitions
samples/  committed sample XML and expected artifacts
out/      local generated output, ignored by Git
```

### 1.3 Compile The Core Scripts

Compile first. This catches syntax errors before generated output changes:

Windows PowerShell:

```powershell
& $python -m py_compile `
  .\src\ads_invoices_received_xbrl_gl.py `
  .\tools\build_syntax_binding.py `
  .\tools\normalize_lhm_semantic_paths.py `
  .\tools\semantic_binding.py `
  .\tools\syntax_binding.py `
  .\src\syntax_binding_hierarchical.py `
  .\tools\build_roundtrip_test_artifacts.py `
  .\tools\taxonomy\xBRLGL_TaxonomyGenerator.py
```

macOS / Linux shell:

```sh
$PYTHON -m py_compile \
  ./src/ads_invoices_received_xbrl_gl.py \
  ./tools/build_syntax_binding.py \
  ./tools/normalize_lhm_semantic_paths.py \
  ./tools/semantic_binding.py \
  ./tools/syntax_binding.py \
  ./src/syntax_binding_hierarchical.py \
  ./tools/build_roundtrip_test_artifacts.py \
  ./tools/taxonomy/xBRLGL_TaxonomyGenerator.py
```

### 1.4 Generate The Local xBRL-CSV Taxonomy

The Structured CSV metadata JSON points to taxonomy files under
`out/taxonomy/`. Generate them with:

```powershell
& $python .\tests\test_xbrlgl_generator_uadc_lhm.py
```

Expected generated files include:

```text
out/taxonomy/en16931/en16931-2026-07-05.xsd
out/taxonomy/gen/gl-gen-2026-07-05.xsd
out/taxonomy/plt/plt-oim-2026-07-05.xsd
out/taxonomy/plt/plt-def-2026-07-05.xml
```

### 1.5 Build Round-Trip Review Artifacts

This creates the reviewable sample outputs under `tests/roundtrip/`:

```powershell
& $python .\tools\build_roundtrip_test_artifacts.py
```

The tool calls `src/syntax_binding_hierarchical.py` and refreshes:

```text
tests/roundtrip/*/source_xml/
tests/roundtrip/*/structured_csv/
tests/roundtrip/*/metadata_json/
tests/roundtrip/*/roundtrip_xml/
```

### 1.6 Run The Minimum Local Test Set

Run these checks after initial setup:

```powershell
& $python .\tests\test_lhm_semantic_paths.py
& $python .\tests\test_lhm_hierarchical_csv_layout.py
& $python .\tests\test_syntax_binding_hierarchical.py
& $python .\tests\test_syntax_binding_reverse.py
& $python .\tests\test_openpeppol_invoice_conversion.py
& $python .\tests\test_bis_billing3_examples_conversion.py
& $python .\tests\test_roundtrip_artifacts.py
```

This minimum set does not require Arelle or the local UBL schema cache.

## 2. Optional Validation Environment

These checks are stronger but require external tools or local cached schemas.

### 2.1 Arelle For xBRL-CSV Metadata

Install Arelle so `arelleCmdLine.exe` is available on `PATH`, or in the Python
Scripts directory. Then run:

```powershell
& $python .\tests\test_xbrl_csv_metadata_arelle.py
```

This validates generated metadata JSON with the Arelle `loadFromOIM` plugin.

### 2.2 UBL 2.1 Schema Cache

For regenerated XML schema validation, place the official OASIS UBL 2.1 package
under:

```text
out/cache/UBL-2.1/
```

The expected Invoice schema path is:

```text
out/cache/UBL-2.1/xsd/maindoc/UBL-Invoice-2.1.xsd
```

Then run:

```powershell
& $python .\tests\test_roundtrip_xml_ubl_schema.py
```

## 3. Continuing Development Workflow

Use this loop while changing scripts, LHM rows, bindings, or taxonomy behavior.

### 3.1 Before Editing

Check the current Git state:

```powershell
git status --short
```

Keep generated local output under `out/`. Do not commit `out/`, Python caches,
virtual environments, or local downloads unless explicitly requested.

### 3.2 After Editing Runtime Scripts

Compile changed files, then run focused tests:

```powershell
& $python -m py_compile .\src\syntax_binding_hierarchical.py
& $python .\tests\test_syntax_binding_hierarchical.py
& $python .\tests\test_syntax_binding_reverse.py
```

If the change affects metadata JSON or round-trip artifacts:

```powershell
& $python .\tools\build_roundtrip_test_artifacts.py
& $python .\tests\test_roundtrip_artifacts.py
```

### 3.3 After Editing LHM Or Binding CSV Files

Regenerate taxonomy and rebuild artifacts:

```powershell
& $python .\tests\test_xbrlgl_generator_uadc_lhm.py
& $python .\tools\build_roundtrip_test_artifacts.py
```

Then run:

```powershell
& $python .\tests\test_lhm_semantic_paths.py
& $python .\tests\test_lhm_hierarchical_csv_layout.py
& $python .\tests\test_roundtrip_artifacts.py
```

Use Arelle and UBL schema validation when available:

```powershell
& $python .\tests\test_xbrl_csv_metadata_arelle.py
& $python .\tests\test_roundtrip_xml_ubl_schema.py
```

### 3.4 After Editing Taxonomy Generation

Compile and regenerate the taxonomy:

```powershell
& $python -m py_compile .\tools\taxonomy\xBRLGL_TaxonomyGenerator.py
& $python .\tests\test_xbrlgl_generator_uadc_lhm.py
& $python .\tests\validate_taxonomy.py
```

Then rebuild dependent Structured CSV metadata:

```powershell
& $python .\tools\build_roundtrip_test_artifacts.py
& $python .\tests\test_roundtrip_artifacts.py
```

### 3.5 Before Sharing Changes

Run a broad local check:

```powershell
& $python -m py_compile `
  .\src\ads_invoices_received_xbrl_gl.py `
  .\tools\build_syntax_binding.py `
  .\tools\normalize_lhm_semantic_paths.py `
  .\tools\semantic_binding.py `
  .\tools\syntax_binding.py `
  .\src\syntax_binding_hierarchical.py `
  .\tools\build_roundtrip_test_artifacts.py `
  .\tools\taxonomy\xBRLGL_TaxonomyGenerator.py

& $python .\tests\test_lhm_semantic_paths.py
& $python .\tests\test_lhm_hierarchical_csv_layout.py
& $python .\tests\test_xbrlgl_generator_uadc_lhm.py
& $python .\tests\test_syntax_binding_hierarchical.py
& $python .\tests\test_syntax_binding_reverse.py
& $python .\tests\test_openpeppol_invoice_conversion.py
& $python .\tests\test_bis_billing3_examples_conversion.py
& $python .\tests\test_roundtrip_artifacts.py
```

Report clearly if Arelle or the UBL schema cache is not available.

## 4. Tool Overview

### `build_roundtrip_test_artifacts.py`

Builds reviewable round-trip test artifacts under `tests/roundtrip/`.

Position:
Development/test environment support. It is in `tools/` because it prepares
test artifacts; it is not the main converter.

Inputs:
Sample XML files, active syntax binding CSV, active LHM CSV, and generated
taxonomy under `out/taxonomy/`.

Outputs:
Source XML copies, Structured CSV, xBRL-CSV metadata JSON, and regenerated XML
under `tests/roundtrip/`.

### `taxonomy/xBRLGL_TaxonomyGenerator.py`

Generates the local UADC-compatible xBRL-CSV taxonomy from the LHM CSV.

Position:
Initial setup and taxonomy maintenance tool. The generated taxonomy is consumed
by `src/syntax_binding_hierarchical.py` when writing metadata JSON.

### `syntax_binding.py`

Earlier simple XML-to-structured-CSV converter.

Position:
Legacy/reference converter used by compatibility tests and tutorials about the
older flat structured CSV layout. The current operational converter is
`src/syntax_binding_hierarchical.py`.

### `semantic_binding.py`

Projects Structured CSV into a flat CSV view using a semantic binding CSV.

Position:
Phase 2 support and development tool for downstream audit-view projection. It
is not part of the current Phase 1 operational runtime.

### `build_syntax_binding.py`

Builds a syntax binding CSV from a smaller `semantic_path,xpath` source table.

Position:
Binding maintenance tool. Use it when regenerating or experimenting with syntax
binding definitions.

### `normalize_lhm_semantic_paths.py`

Normalizes LHM `semantic_path` values from business terms and row hierarchy.

Position:
LHM maintenance tool. Use it when cleaning or regenerating LHM semantic paths.

### `build_lhm_from_source.py`

Builds the generated/current LHM CSV from an editable source CSV.

### `audit_en16931_coverage.py`

Audits EN 16931 BT/BG coverage in the LHM CSV against the source PDF.

### `check_lhm_class_element.py`

Checks LHM `class_term` and `element` values.

### `extend_en16931_lhm_coverage.py`

Helps extend EN 16931 LHM coverage.

### `normalize_lhm_class_element.py`

Normalizes LHM `class_term` and `element` columns.

### `order_lhm_by_en16931_table2.py`

Orders LHM rows according to EN 16931-1 Table 2.

### `update_lhm_definitions_from_pdf.py`

Updates LHM definitions from extracted EN 16931-1 PDF descriptions.

### `update_lhm_syntax_sequence_from_ubl_xsd.py`

Updates LHM syntax sequence values from extracted UBL 2.1 XSD files.

## 5. Directory Boundary

- `src/`: main conversion runtime.
- `tools/`: initial setup, taxonomy/spec generation, test artifact building,
  and development environment maintenance.
- `tests/`: assertions and regression checks.
- `specs/`: committed source definitions.
- `samples/`: committed sample inputs and expected outputs.
- `out/`: local generated output, caches, and validation artifacts.

