# Tutorial Scripts

This directory contains small beginner-friendly scripts for learning the UADC
PoC flow. They are wrappers around the operational scripts in `src/`.

Run them from the UADC PoC root:

Windows PowerShell:

```powershell
cd <local-clone-directory>\UADC-PoC
$python = 'python'
```

`$python` is a PowerShell shortcut for the Python command. Use a full local
Python executable path if `python` is not available on your `PATH`.

macOS / Linux shell:

```sh
cd <local-clone-directory>/UADC-PoC
PYTHON=python3
```

For macOS/Linux, run tutorial scripts as `$PYTHON ./src/tutorial/<script>.py`.

## Recommended Order

1. Check the local environment:

   ```powershell
   & $python .\src\tutorial\00_check_environment.py
   ```

2. Convert the minimal sample UBL Invoice XML to Structured CSV and metadata:

   ```powershell
   & $python .\src\tutorial\01_convert_sample_to_structured_csv.py
   ```

3. Convert the Structured CSV back to UBL Invoice XML:

   ```powershell
   & $python .\src\tutorial\02_roundtrip_structured_csv_to_xml.py
   ```

4. Generate a sample ADS Invoices Received XBRL GL instance:

   ```powershell
   & $python .\src\tutorial\03_generate_ads_xbrl_gl.py
   ```

## Output

Tutorial output is written under:

```text
out/tutorial/
```

The tutorial scripts are not the system of record. Use the operational scripts
directly for production-like PoC runs:

```text
src/syntax_binding_hierarchical.py
src/ads_invoices_received_xbrl_gl.py
```

