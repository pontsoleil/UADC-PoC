**English** | [日本語](ja/README.md)

# tests

## Purpose

Tests verify normative src programs and approved public tools.

## Execution

```text
py -m pytest tests
```

Do not rerun a test when input, code, configuration, dependency versions, output artefacts, and validation scope are materially identical to an already accepted PASS.

## Tests

Run only tests relevant to materially changed code or conditions. Reuse accepted PASS evidence when inputs, code, settings, dependency versions, outputs, and validation scope are materially identical.
