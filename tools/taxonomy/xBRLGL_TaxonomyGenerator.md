**English** | [日本語](ja/xBRLGL_TaxonomyGenerator.md)

# xBRLGL_TaxonomyGenerator

## Purpose

This is the synchronized UADC copy of the XBRL GL Next taxonomy Generator.

## Do not fork

Do not edit this copy independently. Validate byte identity with the XBRL GL Next authority before use.

## CLI

```text
py tools/taxonomy/xBRLGL_TaxonomyGenerator.py --hmd-dir <hmd-dir> --output-dir <empty-output-dir> -n <namespace> --value-domain <domains.csv> --value <values.csv> --taxonomy-extension-overlay <overlay.csv> [options]
```

## Execution and safety

Run commands from the repository root. Confirm input paths, output paths, and overwrite behavior before execution. Use task-local or explicitly approved output locations for experiments.

## Tests

Run only tests relevant to materially changed code or conditions. Reuse accepted PASS evidence when inputs, code, settings, dependency versions, outputs, and validation scope are materially identical.
