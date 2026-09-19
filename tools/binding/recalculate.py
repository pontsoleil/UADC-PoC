from pathlib import Path
import csv, json, subprocess, sys
from decimal import Decimal

ROOT = Path(__file__).resolve().parents[2]
PROFILE = 'PCA_Accounting_81col_AnonymousEvaluation_V17_V14'
BASE = 'bindings/flat-csv/' + PROFILE + '/' + PROFILE
HMD = 'models/gl-cor/accounting-entries/hmd/XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv'
results = []

def read(path):
    with (ROOT / path).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.reader(f))

def execute(label, args):
    p = subprocess.run([sys.executable, 'tools/binding/flat_csv.py', *args], cwd=ROOT, capture_output=True, text=True)
    results.append(dict(label=label, command=args, exit_code=p.returncode, stdout=p.stdout, stderr=p.stderr))
    print(label, p.returncode, p.stderr, flush=True)
    return p.returncode == 0

for basis in ['anonymous_v17']:
    out = 'instances/derived/PCA/' + basis
    back = 'instances/roundtrip/PCA/' + basis
    (ROOT/out).mkdir(parents=True, exist_ok=True)
    (ROOT/back).mkdir(parents=True, exist_ok=True)
    shared = ['-m', HMD, '--profile-dir', 'bindings/flat-csv/' + PROFILE,
              '--columns-file', BASE+'_COLUMNS.csv', '--standard-tax-mapping', BASE+'_STANDARD_TAX_MAPPING.csv']
    src = f'instances/original/PCA/{basis}/PCA.csv'
    if not execute(basis+' forward', ['to-structured', src, '-o', out+'/structured.csv', *shared,
               '--data-start-row', '2', '--account-tax-mapping', BASE+'_ACCOUNT_TAX_MAPPING.csv',
               '--tax-trace-output', out+'/tax_trace.csv', '--unbound-report', out+'/unbound.csv']):
        continue
    with (ROOT/out/'structured.csv').open(newline='', encoding='utf-8-sig') as f:
        facts = list(csv.DictReader(f))
    source = read(src)[1:]
    by_key = {}
    for fact in facts:
        if fact['source_row'] and fact['occurrence'] in {'D','C'} and fact['type']=='A':
            by_key.setdefault((int(fact['source_row']),fact['occurrence']),{})[fact['semantic_path']] = fact['value']
    differences = []
    sums = {'D':Decimal(0), 'C':Decimal(0)}
    expected_sums = {'D':Decimal(0), 'C':Decimal(0)}
    count = 0
    for index,row in enumerate(source,1):
        for side,amount,tax in [('D',14,15),('C',25,26)]:
            if not row[amount-1]:
                continue
            expected_sums[side] += Decimal(row[amount-1])
            actual = by_key.get((index,side),{})
            for suffix,expected in [('.cor_MonetaryAmount',row[amount-1]),('.cor_DetailDescription',row[26]),('.cor_DetailTax.cor_AmountofTaxes',row[tax-1])]:
                found = [v for k,v in actual.items() if k.endswith(suffix)]
                value = found[0] if len(found)==1 else ''
                if value != expected:
                    differences.append({'row':index,'side':side,'path':suffix,'expected':expected,'actual':value})
            values = [v for k,v in actual.items() if k.endswith('.cor_MonetaryAmount')]
            if values: sums[side] += Decimal(values[0] or '0')
            count += 1
    nonvat = [f for f in facts if f['value']=='JP_CORPORATE_TAXES_COMBINED']
    results.append(dict(label=basis+' independent values', source_rows=len(source), occurrences=count,
                        source_totals={k:str(v) for k,v in expected_sums.items()},
                        output_totals={k:str(v) for k,v in sums.items()}, differences=differences,
                        nonvat_combined_facts=nonvat))
    if execute(basis+' PCA roundtrip', ['to-flat', out+'/structured.csv', '-o', back+'/PCA.csv', *shared,
               '--tax-trace-input',out+'/tax_trace.csv','--tax-reverse-mode','source_restored']):
        target = read(back+'/PCA.csv')
        delta = [{'row':i,'column':j,'expected':a,'actual':b}
                 for i,(x,y) in enumerate(zip(source,target),1)
                 for j,(a,b) in enumerate(zip(x,y),1) if a!=b]
        with (ROOT/back/'differences.json').open('w',encoding='utf-8') as f:
            json.dump(delta,f,ensure_ascii=False,indent=2)
        results.append(dict(label=basis+' all-cell comparison',source_rows=len(source),output_rows=len(target),
                            differences=len(delta),compared_cells=sum(len(x) for x in source)))

(ROOT/'docs/recalculation/RESULTS.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
for r in results:
    if 'command' not in r:
        print({k:(len(v) if k=='differences' and isinstance(v,list) else v) for k,v in r.items()},flush=True)
