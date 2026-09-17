from pathlib import Path
from collections import Counter,defaultdict
from decimal import Decimal
import csv,json,hashlib
R=Path(__file__).resolve().parents[2]
def read(p):return list(csv.reader((R/p).open(encoding='utf-8-sig',newline='')))
src=read('instances/original/PCA/anonymous_v17/PCA.csv')[1:]
back=read('instances/roundtrip/PCA/anonymous_v17/PCA.csv')
eps=read('instances/derived/EPSON/anonymous_v17/EPSON.csv')
facts=list(csv.DictReader((R/'instances/derived/PCA/anonymous_v17/structured.csv').open(encoding='utf-8-sig')))
by={}
for f in facts:
 if f['source_row'] and f['type']=='A':by.setdefault((int(f['source_row']),f['occurrence']),[]).append(f)
diff=[];checks=0
for i,row in enumerate(src,1):
 for side,base in [('D',0),('C',11)]:
  if not row[7+base]:continue
  fs=by.get((i,side),[])
  for kind,idx,suffix,role in [('department_code',5+base,'.cor_SubaccountID','department'),('department_name',6+base,'.cor_SubaccountDescription','department'),('aux_code',9+base,'.cor_SubaccountID','source-subaccount'),('aux_name',10+base,'.cor_SubaccountDescription','source-subaccount')]:
   expected=row[idx]
   if not expected:continue
   vals=[f['value'] for f in fs if f['semantic_path'].endswith(suffix) and (role=='source-subaccount' and 'department' not in f['binding_path'] and 'account-subaccount' not in f['binding_path'] or role=='department' and "cor_Type='department'" in f['binding_path'])]
   checks+=1
   if expected not in vals:diff.append([i,side,kind,expected,vals])
# Independent name+department monetary grouping across the split into EPSON 1:1 rows.
a=defaultdict(Decimal);b=defaultdict(Decimal)
for row in src:
 for side,base in [('D',0),('C',11)]:
  if row[7+base]:a[(row[0],row[1],side,row[5+base],row[6+base],row[9+base],row[10+base])]+=Decimal(row[13+base] or '0')
for row in eps:
 for side,base in [('D',0),('C',13)]:
  if row[11+base]:b[(row[5].replace('-',''),row[6],side,row[9+base],row[10+base],row[13+base],row[14+base])]+=Decimal(row[15+base] or '0')
nd=[{'key':k,'source':str(a[k]),'epson':str(b[k])} for k in a.keys()|b.keys() if a[k]!=b[k]]
raw=R/'instances/original/PCA/anonymous_v17/PCA_original_format.csv'
orig=list(csv.reader(raw.open(encoding='utf8')))[2:]
source_diff=sum(x!=y for r,s in zip(orig,src) for x,y in zip(r,s))
companies=sorted({r[j+3] for r in src for j in [7,18] if r[j] in ['152','312'] and r[j+3]})
banks=sorted({r[j+3] for r in src for j in [7,18] if r[j] in ['121','131'] and r[j+3]})
report={'source_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'source_data_cell_changes':source_diff,'source_rows':len(src),'epson_rows':len(eps),'vouchers':len({tuple(r[:2]) for r in src}),'source_to_structured_name_checks':checks,'source_to_structured_name_differences':diff,'source_to_epson_name_amount_group_differences':nd,'company_names':companies,'bank_names':banks,'departments':sorted({r[j] for r in src for j in [6,17] if r[j]}),'returns_by_side':dict(Counter(s+' '+r[t] for r in src for s,t in [('D',11),('C',22)] if r[t] in ['C5','R5']))}
(R/'docs/name_revision/NAME_VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print({k:v for k,v in report.items() if k not in ['company_names','source_to_structured_name_differences','source_to_epson_name_amount_group_differences']});print('DIFF',len(diff),len(nd),nd[:2],diff[:2]);assert source_diff==0 and not diff and not nd
