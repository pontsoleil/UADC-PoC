**English** | [日本語](ja/syntax_binding.md)

# syntax_binding

## Purpose

`src/syntax_binding.py` applies a Syntax Binding CSV to XML ⇄ Structured CSV conversion for one semantic model.

## Inputs

- input XML or Structured CSV with `--reverse`
- Syntax Binding CSV
- Canonical HMD where required

## Output

- Structured CSV plus OIM metadata JSON, or reconstructed XML

## CLI

```text
py src/syntax_binding.py <input> -b <binding.csv> -o <output> [--hmd-file <hmd.csv>] [--metadata-output <metadata.json>] [--taxonomy-base <dir>] [--reverse]
```

## OIM metadata

The current Formal GIT does not contain a standalone `oim_metadata.py`. OIM metadata generation remains within the existing runtime implementation; this document does not claim that metadata processing has been extracted to a separate common module.

## Execution and safety

Run commands from the repository root. Confirm input paths, output paths, and overwrite behavior before execution. Use task-local or explicitly approved output locations for experiments.

## Tests

Run only tests relevant to materially changed code or conditions. Reuse accepted PASS evidence when inputs, code, settings, dependency versions, outputs, and validation scope are materially identical.
