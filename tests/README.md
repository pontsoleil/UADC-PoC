# Tests

Run commands from the `UADC_PoC` directory.

The main syntax binding and round-trip checks are:

```powershell
& 'C:\Users\nobuy\AppData\Local\Programs\Python\Python310\python.exe' tests\test_openpeppol_invoice_conversion.py
& 'C:\Users\nobuy\AppData\Local\Programs\Python\Python310\python.exe' tests\test_lhm_hierarchical_csv_layout.py
& 'C:\Users\nobuy\AppData\Local\Programs\Python\Python310\python.exe' tests\test_syntax_binding_hierarchical.py
& 'C:\Users\nobuy\AppData\Local\Programs\Python\Python310\python.exe' tests\test_syntax_binding_reverse.py
& 'C:\Users\nobuy\AppData\Local\Programs\Python\Python310\python.exe' tests\test_bis_billing3_examples_conversion.py
& 'C:\Users\nobuy\AppData\Local\Programs\Python\Python310\python.exe' tests\test_roundtrip_artifacts.py
```

The LHM and taxonomy checks are:

```powershell
& 'C:\Users\nobuy\AppData\Local\Programs\Python\Python310\python.exe' tests\test_lhm_semantic_paths.py
& 'C:\Users\nobuy\AppData\Local\Programs\Python\Python310\python.exe' tests\test_xbrlgl_generator_uadc_lhm.py
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
