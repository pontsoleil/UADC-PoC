# Tests

Run commands from the `UADC_PoC` directory.

## Subdirectories and Supporting Files

- `roundtrip/` - Reviewable round-trip artifacts. Each case keeps source XML,
  structured CSV, xBRL-CSV metadata JSON, and regenerated XML together.
- `roundtrip_test_guide.md` - Explains the round-trip artifact layout, test
  commands, and review points.
- `test_execution_report.md` - Current test execution report for the PoC.
- `../tools/build_roundtrip_test_artifacts.py` - Rebuilds the round-trip
  artifact sets from sample XML inputs.

The main syntax binding and round-trip checks are:

```powershell
& $python .\tests\test_openpeppol_invoice_conversion.py
& $python .\tests\test_lhm_hierarchical_csv_layout.py
& $python .\tests\test_syntax_binding_hierarchical.py
& $python .\tests\test_syntax_binding_reverse.py
& $python .\tests\test_bis_billing3_examples_conversion.py
& $python .\tests\test_roundtrip_artifacts.py
```

The LHM and taxonomy checks are:

```powershell
& $python .\tests\test_lhm_semantic_paths.py
& $python .\tests\test_xbrlgl_generator_uadc_lhm.py
```

Round-trip test artifacts are documented in:

```text
tests/roundtrip_test_guide.md
```

Current test execution report:

```text
tests/test_execution_report.md
```

Some tests write generated files under `out/`, which is ignored by Git. The round-trip artifact test also refreshes files under `tests/roundtrip/` so source XML, structured CSV, metadata JSON, and regenerated XML can be reviewed together.
