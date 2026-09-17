"""Dataset-specific EPSON mapping candidate; no Official GIT changes."""
import csv
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = 'EPSON_ZaimuKaikeiR4_43col'
PROFILE = ORIGINAL + '_NTA_Fallback'
PCA = 'PCA_Accounting_81col_AnonymousEvaluation_V17_V14'
HMD = ROOT/'models/xbrl-gl-next/accounting-entries/hmd/XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv'
REPORT = ROOT/'docs/epson_recalculation'
REPORT.mkdir(parents=True, exist_ok=True)

def read(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))

old = ROOT/'bindings/flat-csv'/ORIGINAL
new = ROOT/'bindings/flat-csv'/PROFILE
new.mkdir(parents=True, exist_ok=True)
for suffix in ['BINDING', 'COLUMNS', 'STANDARD_TAX_MAPPING']:
    shutil.copyfile(old/f'{ORIGINAL}_{suffix}.csv', new/f'{PROFILE}_{suffix}.csv')
accounts = read(old/f'{ORIGINAL}_ACCOUNT_MAPPING.csv')
pca = read(ROOT/'bindings/flat-csv'/PCA/f'{PCA}_ACCOUNT_MAPPING.csv')
# Build a profile for the PCA-derived candidate. Independent local suffixes
# do not establish semantic equivalence. Unmatched target accounts require registration.
native = accounts
accounts = []
by_code = {}
used = set()
audit = []
for row in pca:
    code = row['eTax_Account_Code']
    candidates = [x for x in native if x['eTax_Account_Code'] == code
                  and x['eTax_Category'] == row['eTax_Category']
                  and (x['eTax_Account_Name'] == row['eTax_Account_Name']
                       or x['Account_Name'] == row['eTax_Account_Name'])]
    if len(candidates) > 1:
        raise ValueError('Ambiguous semantic account mapping: '+code)
    if candidates:
        item = dict(candidates[0], eTax_Account_Name=row['eTax_Account_Name'])
        action = 'SEMANTIC_MATCH'
    else:
        item = dict(row, Account_Code=code, Account_Name=row['Account_Name'])
        action = 'REGISTRATION_REQUIRED_NTA_WITH_LOCAL_SUFFIX' if '-' in code else 'REGISTRATION_REQUIRED_NTA'
    if item['Account_Code'] in used:
        raise ValueError('Output account code collision: '+item['Account_Code'])
    used.add(item['Account_Code']);accounts.append(item);by_code[code]=item
    audit.append(dict(standard_code=code, source_name=row['eTax_Account_Name'],
                      output_code=item['Account_Code'],output_name=item['Account_Name'],action=action,
                      canonical_name_difference=False))
with (new/f'{PROFILE}_ACCOUNT_MAPPING.csv').open('w', encoding='utf-8-sig', newline='') as stream:
    writer = csv.DictWriter(stream, fieldnames=list(accounts[0]))
    writer.writeheader()
    writer.writerows(accounts)
# The generated profile groups only by the values supplied by PCA.
binding_path = new/f'{PROFILE}_BINDING.csv'
bindings = read(binding_path)
for row in bindings:
    if row['occurrence_mode'] == 'keyed_rows':
        row['group_key'] = '["C6","C7"]'
        row['note'] = 'PCA-derived EPSON candidate: date and voucher number identify the voucher; audit user and input date may be absent.'
with binding_path.open('w',encoding='utf-8-sig',newline='') as stream:
    w=csv.DictWriter(stream,fieldnames=list(bindings[0]));w.writeheader();w.writerows(bindings)
# Explicitly reproduce project non-VAT account classifications after target re-import.
source_policies=read(ROOT/'bindings/flat-csv'/PCA/f'{PCA}_ACCOUNT_TAX_MAPPING.csv')
source_by_code={r['Account_Code']:r for r in pca}
policies=[]
for policy in source_policies:
    standard=source_by_code[policy['source_account_code']]['eTax_Account_Code']
    target=by_code[standard]
    policies.append(dict(policy,source_account_code=target['Account_Code'],source_account_name=target['Account_Name']))
with (new/f'{PROFILE}_ACCOUNT_TAX_MAPPING.csv').open('w',encoding='utf-8-sig',newline='') as stream:
    w=csv.DictWriter(stream,fieldnames=list(source_policies[0]));w.writeheader();w.writerows(policies)

(REPORT/'ACCOUNT_RESOLUTION.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')

results = []
def execute(label, command):
    p = subprocess.run([sys.executable, str(ROOT/'tools/uadc/flat_csv.py'), *map(str, command)], capture_output=True, text=True)
    results.append(dict(label=label, exit_code=p.returncode, stdout=p.stdout, stderr=p.stderr))
    (REPORT/'RESULTS.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    print(label, p.returncode, p.stderr.strip(), flush=True)
    return p.returncode == 0

common = ['-m', HMD, '--profile-dir', new, '--columns-file', new/f'{PROFILE}_COLUMNS.csv', '--standard-tax-mapping', new/f'{PROFILE}_STANDARD_TAX_MAPPING.csv', '--account-tax-mapping', new/f'{PROFILE}_ACCOUNT_TAX_MAPPING.csv']
for basis in ['anonymous_v17']:
    folder = ROOT/'instances/derived/EPSON'/basis
    folder.mkdir(parents=True, exist_ok=True)
    source = ROOT/f'instances/derived/PCA/{basis}/structured.csv'
    target = folder/'EPSON.csv'
    if not execute(basis+' PCA structured to EPSON', ['to-flat', source, '-o', target, *common, '--materialization-mode', 'ordered_cumulative_pairing']):
        continue
    back = ROOT/'instances/roundtrip/EPSON'/basis
    back.mkdir(parents=True, exist_ok=True)
    structured = back/'structured.csv'
    trace = back/'tax_trace.csv'
    if not execute(basis+' EPSON to structured', ['to-structured', target, '-o', structured, *common, '--data-start-row', '1', '--tax-trace-output', trace]):
        continue
    if execute(basis+' EPSON roundtrip', ['to-flat', structured, '-o', back/'EPSON.csv', *common, '--tax-trace-input', trace, '--tax-reverse-mode', 'source_restored']):
        with target.open(encoding='utf-8-sig', newline='') as stream: before = list(csv.reader(stream))
        with (back/'EPSON.csv').open(encoding='utf-8-sig', newline='') as stream: after = list(csv.reader(stream))
        assert len(before) == len(after)
        assert all(len(a) == len(b) for a,b in zip(before, after))
        delta = sum(x != y for a,b in zip(before, after) for x,y in zip(a,b))
        results.append(dict(label=basis+' EPSON all cell comparison', rows=len(before), differences=delta))
    oim_folder = folder/'xbrl-csv'
    oim_folder.mkdir(parents=True, exist_ok=True)
    execute(basis+' EPSON xBRL-CSV generation', ['to-structured', target, '-o', oim_folder/'accounting_entries.csv', *common,
        '--data-start-row','1','--tax-trace-output',oim_folder/'tax_trace.csv',
        '--taxonomy-entrypoint',ROOT/'taxonomy/oim/cor_accountingEntries/cor-all-oim-2026-12-31.xsd',
        '--metadata-output',oim_folder/'accounting_entries.json','--entity','scheme:ABC-SHOTEN','--period','2022-04-01T00:00:00'])
    pdir = ROOT/'bindings/flat-csv'/PCA
    execute(basis+' EPSON structured to PCA', ['to-flat', structured, '-o', back/'PCA.csv', '-m', HMD, '--profile-dir', pdir, '--columns-file', pdir/f'{PCA}_COLUMNS.csv', '--standard-tax-mapping', pdir/f'{PCA}_STANDARD_TAX_MAPPING.csv', '--account-tax-mapping',pdir/f'{PCA}_ACCOUNT_TAX_MAPPING.csv'])
(REPORT/'RESULTS.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
