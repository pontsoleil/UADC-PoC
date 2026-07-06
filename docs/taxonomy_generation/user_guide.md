# User Guide: Taxonomy Generation

## 1. Working Directory

Run commands from the `UADC_PoC` directory:

```powershell
cd UADC_PoC
```

All paths below are relative to this directory. The taxonomy generator is included in `tools/taxonomy/`, so no external `XBRL-GL-2026` checkout is required.

Set the Python command for the local Windows environment:

```powershell
$python = 'C:\Users\nobuy\AppData\Local\Programs\Python\Python310\python.exe'
```

## 2. Input

The taxonomy generator uses:

```text
specs/lhm/EN16931_CIUS_Invoice_LHM.csv
```

Regenerate and check the LHM before generating taxonomy when the source model has changed.

## 3. Generate the Taxonomy

Run the taxonomy regression script:

```powershell
& $python .\tests\test_xbrlgl_generator_uadc_lhm.py
```

This regenerates files under:

```text
out/taxonomy/
```

## 4. Direct Generator Command

To run the taxonomy generator directly:

```powershell
& $python .\tools\taxonomy\xBRLGL_TaxonomyGenerator.py `
  .\specs\lhm\EN16931_CIUS_Invoice_LHM.csv `
  -b .\out\taxonomy `
  -p en16931 `
  -n https://example.com/uada/en16931/invoice/2026-07-05 `
  -l ja `
  -c JPY
```

Useful options:

- `-b`, `--base_dir`: output directory.
- `-p`, `--palette`: palette/module prefix used for generated files.
- `-r`, `--root`: root element name for JSON metadata and CSV skeleton generation.
- `-l`, `--lang`: local label language.
- `-c`, `--currency`: ISO currency for amount facts.
- `-n`, `--namespace`: namespace. The final 10 characters are used as the version date.
- `-e`, `--encoding`: input/output encoding. Default is `utf-8-sig`.
- `-t`, `--trace`: print trace messages.
- `-d`, `--debug`: print debug messages.

## 5. Output Files

Key files:

```text
out/taxonomy/en16931/en16931-2026-07-05.xsd
out/taxonomy/en16931/en16931-2026-07-05-presentation.xml
out/taxonomy/en16931/lang/en16931-2026-07-05-label.xml
out/taxonomy/en16931/lang/en16931-2026-07-05-label-ja.xml
out/taxonomy/gen/gl-gen-2026-07-05.xsd
out/taxonomy/plt/plt-def-2026-07-05.xml
out/taxonomy/plt/plt-oim-2026-07-05.xsd
```

Meaning:

- `en16931/en16931-2026-07-05.xsd`: module item concepts.
- `gen/gl-gen-2026-07-05.xsd`: GL generic item type schema referenced as `../gen/gl-gen-<version>.xsd`.
- `plt/plt-oim-2026-07-05.xsd`: xBRL-CSV taxonomy schema with hypercubes, dimensions, and primary items.
- `plt/plt-def-2026-07-05.xml`: xBRL-CSV dimensional definition linkbase.

## 6. Verify the Taxonomy Separation

Check that the local taxonomy structure is consistent:

```powershell
& $python .\tests\validate_taxonomy.py
```

Expected output:

```text
ok: local taxonomy checks passed
```

Check that `plt-oim` does not contain tuple or content schema definitions:

```powershell
Select-String -Path .\out\taxonomy\plt\plt-oim-2026-07-05.xsd `
  -Pattern 'en16931-content','complexType','xbrli:tuple'
```

Expected result: no matches.

Check that `plt-oim` contains hypercube, dimension, and primary item concepts:

```powershell
Select-String -Path .\out\taxonomy\plt\plt-oim-2026-07-05.xsd `
  -Pattern 'xbrldt:hypercubeItem','xbrldt:dimensionItem','substitutionGroup="xbrli:item"'
```

Check that the module schema imports the GL generic schema:

```powershell
Select-String -Path .\out\taxonomy\en16931\en16931-2026-07-05.xsd `
  -Pattern '../gen/gl-gen-2026-07-05.xsd'
```

Check that `plt-all` and `en16931-content` are not generated:

```powershell
Test-Path .\out\taxonomy\plt\plt-all-2026-07-05.xsd
Test-Path .\out\taxonomy\plt\en16931-content-2026-07-05.xsd
```

Expected result: `False`.

## 7. Run Arelle Taxonomy Validation

If Arelle is installed, run:

```powershell
& 'C:\Users\nobuy\AppData\Local\Programs\Python\Python310\Scripts\arelleCmdLine.exe' `
  --file .\out\taxonomy\plt\plt-oim-2026-07-05.xsd `
  --validate
```

Expected output includes:

```text
[info] validated
```

## 8. Run the Regression Check

Run:

```powershell
& $python .\tests\test_xbrlgl_generator_uadc_lhm.py
```

Expected output includes:

```text
ok: XBRL-GL generator accepted UADC LHM CSV
```

## 9. Troubleshooting

### Python is not found

Use the full Python path:

```powershell
& 'C:\Users\nobuy\AppData\Local\Programs\Python\Python310\python.exe' --version
```

### `plt-oim` contains tuple or content definitions

Regenerate with the current generator:

```powershell
& $python .\tests\test_xbrlgl_generator_uadc_lhm.py
```

The current design is xBRL-CSV only. It keeps hypercube, dimension, and primary item definitions in `plt-oim`; it does not generate XBRL 2.1 tuple concepts.

### The taxonomy uses an unexpected date

Check the `-n` namespace option. The generator uses the final 10 characters of the namespace as the version date.
