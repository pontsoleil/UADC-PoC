from pathlib import Path
import csv,json,hashlib
from decimal import Decimal

R=Path(__file__).resolve().parents[2]
def read(path):
    with (R/path).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

source=read('instances/original/PCA/opening_v14/V14.csv')
inputs=read('bindings/flat-csv/PCA_OpeningBalance_7col/PCA_OpeningBalance_7col_BINDING.csv')
outputs=read('bindings/structured-csv/XBRL_GL_Next_AccountsPeriodBalances_C13/XBRL_GL_Next_AccountsPeriodBalances_C13_BINDING.csv')
hmd={r['semantic_path']:r for r in read('models/xbrl-gl-next/accounts-period-balances/hmd/ISO21378_GL_ACCOUNTS_PERIOD_BALANCE_HMD.csv')}
for row in inputs+outputs:
    path=row['semantic_path']
    if path and path not in hmd:raise ValueError('Undefined HMD path: '+path)
mapping={(r['Account_Code'],r['Account_Name']):r for r in read('bindings/flat-csv/PCA_OpeningBalance_7col/PCA_OpeningBalance_7col_ACCOUNT_MAPPING.csv')}
fields=[r['structured_column'] for r in sorted(outputs,key=lambda r:int(r['ordinal']))]
by_path={r['semantic_path']:r['structured_column'] for r in outputs if r['semantic_path']}
root='$.adc_GLAccountsPeriodBalances';account=root+'.adc_AccountBalance';period=account+'.adc_PeriodBalance'
class_col=next(r['structured_column'] for r in outputs if r['role']=='row-class')
date_col=next(r['structured_column'] for r in outputs if r['binding_path']=='profile:openingBalanceEffectiveDate')
result=[];trace=[]
def emit(cls,values,effective_date=None):
    row={c:'' for c in fields};row[class_col]=cls
    for path,value in values.items():row[by_path[path]]=str(value)
    if effective_date:row[date_col]=effective_date
    result.append(row)
emit('GLAccountsPeriodBalances',{root:1})
seen=set()
for i,s in enumerate(source,1):
    if s['code'] in seen:raise ValueError('Duplicate source account')
    seen.add(s['code'])
    m=mapping[(s['code'],s['name'])]
    debit,credit=Decimal(s['debit'] or '0'),Decimal(s['credit'] or '0')
    if min(debit,credit)<0 or (debit and credit):raise ValueError('Ambiguous balance sides')
    side='D' if debit else 'C' if credit else ''
    emit('AccountBalance',{root:1,account:i,account+'.adc_GLAccountNumber':m['eTax_Account_Code'],account+'.uadc_AccountName':m['eTax_Account_Name'],account+'.uadc_NormalBalanceIndicator':side})
    emit('PeriodBalance',{root:1,account:i,period:1,period+'.adc_FiscalYear':'2021',period+'.adc_AccountingPeriod':'M01',period+'.adc_BEGBalanceIndicator':side,period+'.adc_BeginningBalance':debit+credit,period+'.adc_CurrencyCode':'JPY'},'2021-04-01')
    trace.append({'input_row':i,'source_code':s['code'],'target_code':m['eTax_Account_Code'],'debit':str(debit),'credit':str(credit)})
out=R/'instances/derived/PCA/opening_v14/opening.csv'
with out.open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(result)
metadata={'metadataType':'UADC Structured Tidy contract metadata','notFormalXbrlCsvMetadata':True,'table':'opening.csv','source':'../../../original/PCA/opening_v14/V14.csv','effectiveDate':'2021-04-01','fiscalYear':2021,'accountingPeriod':'M01','columns':{r['structured_column']:r['binding_path'] for r in outputs}}
(out.with_suffix('.contract.json')).write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

# Independent readback against the source and the previously generated candidate.
actual=read('instances/derived/PCA/opening_v14/opening.csv');previous=read('docs/recalculation/opening_v14/previous.csv')
assert len(actual)==1+2*len(source)
errors=[]
for i,s in enumerate(source):
    a,b=actual[1+2*i:3+2*i]
    m=mapping[(s['code'],s['name'])]
    expected_side='D' if Decimal(s['debit']) else 'C' if Decimal(s['credit']) else ''
    checks=[a['C5']==m['eTax_Account_Code'],a['C6']==m['eTax_Account_Name'],b['C10']==expected_side,
            Decimal(b['C11'])==Decimal(s['debit'])+Decimal(s['credit']),b['C8']=='2021',b['C9']=='M01',b['C13']=='2021-04-01']
    if not all(checks):errors.append(i+1)
report={'source':'pca.zip / pca_regenerated/private/ADOPTED_V14.csv','source_sha256':hashlib.sha256((R/'instances/original/PCA/opening_v14/V14.csv').read_bytes()).hexdigest(),'accounts':len(source),'structured_rows':len(actual),'columns':len(fields),'debit_total':str(sum(Decimal(s['debit']) for s in source)),'credit_total':str(sum(Decimal(s['credit']) for s in source)),'source_comparison_differences':errors,'previous_cell_differences':sum(a[c]!=b[c] for a,b in zip(actual,previous) for c in fields),'previous_row_count_matches':len(actual)==len(previous),'arelle':'NOT_RUN; contract JSON is not xBRL-CSV metadata','ledgerexplorer':'NOT_RUN'}
(R/'docs/recalculation/opening_v14/VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));(R/'docs/recalculation/opening_v14/SOURCE_TRACE.json').write_text(json.dumps(trace,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
assert not errors and report['previous_cell_differences']==0 and report['previous_row_count_matches']
