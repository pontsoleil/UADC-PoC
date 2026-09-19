"""Reproduce the package. Successful execution is not full route acceptance."""
from pathlib import Path
import subprocess, sys, json
R = Path(__file__).resolve().parents[2]
D = R / 'docs/retest'
D.mkdir(parents=True, exist_ok=True)
results = []
commands = [('regression_tests', [sys.executable, '-m', 'unittest', 'discover', '-s', str(R/'tests'), '-p', 'test_*.py', '-v'])]
commands += [(name, [sys.executable, str(R/'tools/uadc'/name)]) for name in [
    'recalculate.py', 'verify_mapping.py', 'generate_instances.py',
    'regenerate_opening.py', 'generate_opening_accounting_entries.py',
    'verify_opening_accounting_entries.py', 'recalculate_epson.py',
    'check_account_fallback.py', 'audit_materialization.py', 'verify_retest_semantics.py']]
for name, cmd in commands:
    p = subprocess.run(cmd, cwd=R, capture_output=True, text=True)
    log = name + '.log'
    (D/log).write_text(p.stdout+'\n'+p.stderr, encoding='utf-8')
    results.append(dict(script=name, exit_code=p.returncode, log=log))
    (D/'EXECUTIONS.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    print(name, p.returncode, flush=True)
    if p.returncode:
        raise SystemExit(p.returncode)
print('Execution complete. Inspect SEMANTIC_COMPARISON.json and docs/epson_recalculation/RESULTS.json: child route HOLD and missing tax facts are not PASS.', flush=True)
