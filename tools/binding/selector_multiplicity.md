**English** | [日本語](ja/selector_multiplicity.md)

# selector_multiplicity

## Purpose

This required semantic-layer library parses the limited selector grammar embedded in Binding `semantic_path` values and computes effective multiplicity after selector variants are considered.

## Semantic Path predicate subset

Supported selector expressions are equality (`property='value'`), presence (`property`), `and`, `or`, `not`, and parentheses. Conditions are scoped to the Class segment on which they are written. Different hierarchy levels may carry independent predicates. Unsupported comparison operators, arithmetic, functions, axes, and cross-occurrence expressions fail closed.

Only a pure conjunction of positive equality predicates implies selector facts that may be materialised. `or`, `not`, and presence predicates are selection-only.

## Rule

Selectors distinguish variants of one canonical occurrence. They do not justify manually rewriting the accepted HMD merely to make a Class plural.

## Execution and safety

Run commands from the repository root. Confirm input paths, output paths, and overwrite behavior before execution. Use task-local or explicitly approved output locations for experiments.

## Tests

Run only tests relevant to materially changed code or conditions. Reuse accepted PASS evidence when inputs, code, settings, dependency versions, outputs, and validation scope are materially identical.
