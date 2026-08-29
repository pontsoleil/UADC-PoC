**English** | [日本語](ja/semantic_binding.md)

# semantic_binding

## Purpose

`src/semantic_binding.py` is the normative reversible Semantic Binding runtime. It performs Structured CSV ⇄ Structured CSV mapping using an explicit Semantic Binding Table.

The absent `semantic_table.py` contract is not the normative program.

## Inputs

- source Structured CSV;
- source and target HMDs;
- Semantic Binding CSV;
- taxonomy extension overlay and QName map;
- target OIM taxonomy entry point.

## CLI

```text
py src/semantic_binding.py <input.csv> --binding <binding.csv> --source-hmd <source.csv> --target-hmd <target.csv> --overlay <overlay.csv> --qname-map <qname-map.csv> --output <output.csv> --taxonomy <entrypoint.xsd>
```

## Rules

Mappings are explicit by `semantic_path`; do not infer mappings from local-name or QName similarity. Selector conditions are expressed in `semantic_path`, not in a separate selector column. Equality, presence, and `not(presence)` predicates are supported where defined by the binding.

Variant selection is based on supplementary semantic facts within the same canonical Class occurrence. It must not be selected directly from the source or target syntax name. The current Formal GIT does not contain a standalone `oim_metadata.py`. OIM metadata generation remains within the existing runtime implementation; this document does not claim that metadata processing has been extracted to a separate common module.

## Execution and safety

Run commands from the repository root. Confirm input paths, output paths, and overwrite behavior before execution. Use task-local or explicitly approved output locations for experiments.

## Tests

Run only tests relevant to materially changed code or conditions. Reuse accepted PASS evidence when inputs, code, settings, dependency versions, outputs, and validation scope are materially identical.
