# Runtime test execution manifests

`tests/runtime/` contains reproducibility manifests for accepted or explicitly
held conversion test cases. It does not contain duplicate input or output data.
Inputs and accepted outputs remain under `instances/original/`,
`instances/derived/`, and `instances/roundtrip/`.

Each case is stored in its own directory as `RUN_PARAMETERS.json`. Paths are
repository-root-relative and use `/` as the separator. A manifest records an
existing runtime invocation; it does not add runtime options or provide a
`--config` interface.

## Schema version 1.0

The following members are required unless marked optional:

| Member | Type | Meaning |
|---|---|---|
| `schema_version` | string | Must be `1.0`. |
| `case_id` | string | Stable, unique test-case identifier. |
| `status` | string | `PASS` or `HOLD`; registration must not upgrade a prior result. |
| `runtime.program` | string | Repository-relative executable project program. |
| `runtime.sha256` | string | SHA-256 of `runtime.program` used by the accepted run. |
| `direction` | string | Conversion direction represented by the invocation. |
| `source_format` | string | Source syntax or profile name. |
| `target_format` | string | Target syntax or profile name. |
| `profile` | string or null | Existing runtime profile identifier; `null` when not applicable. |
| `hmd` | string or null | Repository-relative HMD used by the runtime. |
| `binding` | string or null | Repository-relative Binding used by the runtime. |
| `input` | string | Repository-relative input file. |
| `outputs` | object | Named repository-relative accepted output files. |
| `runtime_arguments` | array of strings | Exact arguments passed to `runtime.program`, excluding the interpreter and program path. |
| `working_directory` | string | Repository-relative working directory; normally `.`. |
| `encoding` | string | Encoding explicitly selected by the invocation, or the runtime default when the accepted command omitted an encoding option. |
| `options` | object | Only existing runtime options or execution conditions that materially affect the result. |
| `checksums` | object | SHA-256 values for the HMD, Binding, input, additional material dependencies, and accepted outputs. |
| `evidence.source` | string | Repository-relative evidence directory when available; an absolute path is reference-only and must not be required for execution. |
| `evidence.accepted_result` | string | Exact accepted result or HOLD classification. |
| `evidence.accepted_date` | string | Acceptance date in `YYYY-MM-DD` form. |
| `evidence.execution_script` | string | Optional repository-relative wrapper or runner that recorded the invocation. |

SHA-256 values use 64 uppercase hexadecimal characters. A `PASS` manifest is
valid only when the recorded runtime, HMD, Binding, input, other material
dependencies, and accepted outputs match those used by its cited evidence.
Relocation alone does not permit changing their bytes. If any material premise
differs, keep the case at `HOLD` and record that a retest is required.

## Required shape

```json
{
  "schema_version": "1.0",
  "case_id": "example-case",
  "status": "HOLD",
  "runtime": {
    "program": "src/example.py",
    "sha256": "0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF"
  },
  "direction": "source-to-target",
  "source_format": "source",
  "target_format": "target",
  "profile": null,
  "hmd": "models/example/HMD.csv",
  "binding": "bindings/example/BINDING.csv",
  "input": "instances/original/example/input.xml",
  "outputs": {
    "expected": "instances/derived/source_to_target/output.csv"
  },
  "runtime_arguments": [],
  "working_directory": ".",
  "encoding": "utf-8-sig",
  "options": {},
  "checksums": {
    "hmd": "...",
    "binding": "...",
    "input": "...",
    "dependencies": {},
    "outputs": {
      "expected": "..."
    }
  },
  "evidence": {
    "source": "docs/Codex/YYYY/YYYYMM/YYYYMMDD/run-id/outputs",
    "accepted_result": "HOLD",
    "accepted_date": "YYYY-MM-DD",
    "execution_script": "tools/example_runner.py"
  }
}
```

Do not store credentials, personal information, machine-local settings, or
private accounting values in a manifest. Do not use a Windows absolute path as
an executable input. An absolute evidence path may appear only as non-executable
reference information.
