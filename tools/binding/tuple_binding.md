**English** | [日本語](ja/tuple_binding.md)

# tuple_binding

## Purpose

`src/tuple_binding.py` converts Tuple XBRL ⇄ Structured CSV for the same HMD semantic model. It is not a semantic-model mapper.

## Preservation requirements

- selector and ordinal stability
- EE1 QName values
- nil state
- occurrence identity

## CLI

```text
py src/tuple_binding.py <input> --metadata <metadata.json> --hmd <hmd.csv> --qname-map <qname-map.csv> --taxonomy <entrypoint.xsd> --output <output> [--overlay <overlay.csv>] [--nil-manifest <file>]
```

## Execution and safety

Run commands from the repository root. Confirm input paths, output paths, and overwrite behavior before execution. Use task-local or explicitly approved output locations for experiments.

## Tests

Run only tests relevant to materially changed code or conditions. Reuse accepted PASS evidence when inputs, code, settings, dependency versions, outputs, and validation scope are materially identical.
