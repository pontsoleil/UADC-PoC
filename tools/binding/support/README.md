**English** | [日本語](ja/README.md)

# tools

## Purpose

Optional user-facing evaluation, synchronization, and tutorial programs.

## Rule

`src/**` contains normative programs and required runtime libraries. `tools/**` contains optional evaluation, tutorial, validation, or synchronization tools. `tests/**` contains verification programs. Code under `src/**` must not import `tools/**`.

## Execution and safety

Run commands from the repository root. Confirm input paths, output paths, and overwrite behavior before execution. Use task-local or explicitly approved output locations for experiments.

## Tests

Run only tests relevant to materially changed code or conditions. Reuse accepted PASS evidence when inputs, code, settings, dependency versions, outputs, and validation scope are materially identical.
