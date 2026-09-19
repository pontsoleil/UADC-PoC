from pathlib import Path
from collections import defaultdict,Counter
from decimal import Decimal
import csv,json,hashlib
R=Path(__file__).resolve().parents[2];D=R/'docs/retest';D.mkdir(exist_ok=True)
def load(path):
 with path.open(encoding='utf-8-sig',newline='') as s:return list(csv.DictReader(s))
def aggregate(path):
 groups=defaultdict(list)
 for r in load(path):
  if r['occurrence']in ('D','C') and r['source_row']:groups[(r['entry_key'],r['source_row'],r['occurrence'])].append(r)
 sums=defaultdict(Decimal);tax=Decimal(0);nonzero=0;nonvat=0
 for (entry,source,side),rows in groups.items():
  def value(suffix):
   vs=[r['value']for r in rows if r['semantic_path'].endswith(suffix) and r['value']]
   if len(vs)>1:raise ValueError('Ambiguous fact '+suffix)
   return vs[0]if vs else ''
  amount=value('.cor_MonetaryAmount')
  if not amount:continue
  account=value('.cor_AccountNumber')
  suffix=next((r['value']for r in rows if r['semantic_path'].endswith('.cor_SubaccountID')and 'account-subaccount'in r['binding_path']),'')
  typ,cat,rate=(value(x)for x in ['.cor_TaxType','.cor_TaxCategory','.cor_TaxPercentageRate'])
  sums[(entry,side,account,suffix,typ,cat,rate,value('.cor_TaxTransactionClassification'))]+=Decimal(amount)
  tx=Decimal(value('.cor_AmountofTaxes')or'0');tax+=tx;nonzero+=tx!=0;nonvat+=cat=='JP_CORPORATE_TAXES_COMBINED'
 return sums,dict(tax_amount_total=str(tax),nonzero_tax_occurrences=nonzero,nonvat_combined_occurrences=nonvat)
results=[]
P='PCA_Accounting_81col_AnonymousEvaluation_V17_V14'
bound={int(r['column'][1:])for r in load(R/f'bindings/flat-csv/{P}/{P}_BINDING.csv')if r['column']}
for basis in ['original_basis','evaluation_v17_basis']:
 before,bt=aggregate(R/f'instances/derived/PCA/{basis}/structured.csv')
 after,at=aggregate(R/f'instances/roundtrip/EPSON/{basis}/structured.csv')
 delta=[dict(key=list(k),before=str(before[k]),after=str(after[k]))for k in before.keys()|after.keys()if before[k]!=after[k]]
 diffs=json.loads((R/f'instances/roundtrip/PCA/{basis}/differences.json').read_text())
 results.append(dict(basis=basis,account_tax_amount_aggregate_differences=len(delta),differences=delta,source_tax=bt,epson_tax=at,
   tax_amount_preservation='PASS'if bt['tax_amount_total']==at['tax_amount_total']else'FAIL_UNREPRESENTED_IN_TARGET_BINDING',
   pca_roundtrip_bound_cell_differences=sum(x['column']in bound for x in diffs),pca_roundtrip_unbound_cell_differences=sum(x['column']not in bound for x in diffs)))
 print({k:v for k,v in results[-1].items()if k!='differences'},flush=True)
(D/'SEMANTIC_COMPARISON.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
