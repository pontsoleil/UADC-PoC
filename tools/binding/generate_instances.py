from pathlib import Path
import json, subprocess, sys, shutil

R = Path(__file__).resolve().parents[2]
T = R/'taxonomy'
# Preserve schema bytes. Its ../../module imports require a plt/<cube> directory.
# Taxonomy is already placed at taxonomy/oim/cor_accountingEntries.
P='PCA_Accounting_81col_AnonymousEvaluation_V17_V14'
B='bindings/flat-csv/'+P+'/'+P
logs=[]
for basis in ['anonymous_v17']:
    folder=f'instances/derived/PCA/xbrl-csv/{basis}'
    (R/folder).mkdir(parents=True,exist_ok=True)
    args=['to-structured',f'instances/original/PCA/{basis}/PCA.csv','-o',folder+'/accounting_entries.csv',
          '-m','models/gl-cor/accounting-entries/hmd/XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv',
          '--profile-dir','bindings/flat-csv/'+P,'--columns-file',B+'_COLUMNS.csv',
          '--standard-tax-mapping',B+'_STANDARD_TAX_MAPPING.csv','--account-tax-mapping',B+'_ACCOUNT_TAX_MAPPING.csv',
          '--data-start-row','2','--tax-trace-output',folder+'/tax_trace.csv',
          '--taxonomy-entrypoint',str((T/'oim/cor_accountingEntries/cor-all-oim-2026-12-31.xsd').relative_to(R)),
          '--metadata-output',folder+'/accounting_entries.json','--entity','scheme:ABC-SHOTEN',
          '--period','2022-04-01T00:00:00']
    p=subprocess.run([sys.executable,'tools/binding/flat_csv.py',*args],cwd=R,capture_output=True,text=True)
    logs.append(dict(basis=basis,args=args,exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr))
    print(basis,p.returncode,p.stderr,flush=True)
(R/'docs/recalculation/INSTANCE_GENERATION.json').write_text(json.dumps(logs,ensure_ascii=False,indent=2))
