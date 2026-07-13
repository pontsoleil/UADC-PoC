# User Guide: Taxonomy Generation

## 1. Working Directory

Run commands from the **UADC_PoC** directory:

```
cd UADC_PoC
```

All paths below are relative to this directory. The taxonomy generator is included in **tools/taxonomy/**.

Set the Python command for the local Windows environment:

```
$python = 'python'
```

## 2. Input

The taxonomy generator uses:

```
specs/lhm/EN16931_CIUS_Invoice_LHM.csv
```

Regenerate and check the LHM before generating taxonomy when the source model has changed.

## 3. Generate the Taxonomy

Run the taxonomy regression script:

```
& $python .\tests\test_xbrlgl_generator_uadc_lhm.py
```

This regenerates files under:

```
out/taxonomy/
```

## 4. Direct Generator Command

To run the taxonomy generator directly:

```
& $python .\tools\taxonomy\xBRLGL_TaxonomyGenerator.py `
  .\specs\lhm\EN16931_CIUS_Invoice_LHM.csv `
  -b .\out\taxonomy `
  -p en16931 `
  -n https://example.com/uada/en16931/invoice/2026-07-05 `
  -l ja `
  -c JPY
```

Useful options:

- **-b**, **--base_dir**: output directory.
- **-p**, **--palette**: palette/module prefix used for generated files.
- **-r**, **--root**: root element name for JSON metadata and CSV skeleton generation.
- **-l**, **--lang**: local label language.
- **-c**, **--currency**: ISO currency for amount facts.
- **-n**, **--namespace**: namespace. The final 10 characters are used as the version date.
- **-e**, **--encoding**: input/output encoding. Default is **utf-8-sig**.
- **-t**, **--trace**: print trace messages.
- **-d**, **--debug**: print debug messages.

## 5. Output Files

Key files:

```
out/taxonomy/en16931/en16931-2026-07-05.xsd
out/taxonomy/en16931/en16931-2026-07-05-presentation.xml
out/taxonomy/en16931/lang/en16931-2026-07-05-label.xml
out/taxonomy/en16931/lang/en16931-2026-07-05-label-ja.xml
out/taxonomy/gen/gl-gen-2026-07-05.xsd
out/taxonomy/plt/en16931-def-2026-07-05.xml
out/taxonomy/plt/en16931-oim-2026-07-05.xsd
```

Meaning:

- **en16931/en16931-2026-07-05.xsd**: module item concepts.
- **gen/gl-gen-2026-07-05.xsd**: GL generic item type schema referenced as **../gen/gl-gen-<version>.xsd**.
- **plt/en16931-oim-2026-07-05.xsd**: xBRL-CSV taxonomy entry point with hypercubes, dimensions, primary items, and references to labels, presentation, and definition relationships.
- **plt/en16931-def-2026-07-05.xml**: xBRL-CSV dimensional definition linkbase.
- **en16931/en16931-2026-07-05-presentation.xml**: LHM parent-child hierarchy; BG/Class nodes point to OIM primary items and BT nodes point to module facts.

## 6. Verify the Taxonomy Separation

Check that the local taxonomy structure is consistent:

```
& $python .\tests\validate_taxonomy.py
```

Expected output:

```
ok: local taxonomy checks passed
```

Check that **en16931-oim** does not contain tuple or content schema definitions:

```
Select-String -Path .\out\taxonomy\plt\en16931-oim-2026-07-05.xsd `
  -Pattern 'en16931-content','complexType','xbrli:tuple'
```

Expected result: no matches.

Check that **en16931-oim** contains hypercube, dimension, and primary item concepts:

```
Select-String -Path .\out\taxonomy\plt\en16931-oim-2026-07-05.xsd `
  -Pattern 'xbrldt:hypercubeItem','xbrldt:dimensionItem','substitutionGroup="xbrli:item"'
```

Check that the module schema imports the GL generic schema:

```
Select-String -Path .\out\taxonomy\en16931\en16931-2026-07-05.xsd `
  -Pattern '../gen/gl-gen-2026-07-05.xsd'
```

Check that **plt-all** and **en16931-content** are not generated:

```
Test-Path .\out\taxonomy\plt\plt-all-2026-07-05.xsd
Test-Path .\out\taxonomy\plt\en16931-content-2026-07-05.xsd
```

Expected result: **False**.

## 7. Run Arelle Taxonomy Validation

If Arelle is installed, run:

```
& arelleCmdLine.exe `
  --file .\out\taxonomy\plt\en16931-oim-2026-07-05.xsd `
  --validate
```

Expected output includes:

```
[info] validated
```

## 8. Run the Regression Check

Run:

```
& $python .\tests\test_xbrlgl_generator_uadc_lhm.py
```

Expected output includes:

```
ok: XBRL-GL generator accepted UADC LHM CSV
```

## 9. Troubleshooting

### Python is not found

Use the full Python path:

```
& $python --version
```

### **en16931-oim** contains tuple or content definitions

Regenerate with the current generator:

```
& $python .\tests\test_xbrlgl_generator_uadc_lhm.py
```

The current design is xBRL-CSV only. It keeps hypercube, dimension, and primary item definitions in **en16931-oim**; it does not generate XBRL 2.1 tuple concepts.

### The taxonomy uses an unexpected date

Check the **-n** namespace option. The generator uses the final 10 characters of the namespace as the version date.
