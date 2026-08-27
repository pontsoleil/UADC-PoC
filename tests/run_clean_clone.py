#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Execute the public Candidate without project/task-history dependencies."""

from __future__ import annotations

import argparse, csv, hashlib, json, subprocess
from pathlib import Path

def resolve(base: Path, value: str) -> Path:
    p = Path(value)
    return p if p.is_absolute() else (base / p).resolve()

def run(cmd, log=None):
    result = subprocess.run([str(x) for x in cmd], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, encoding="utf-8", errors="replace")
    if log: log.write_text(result.stdout, encoding="utf-8")
    if result.returncode: raise RuntimeError(result.stdout)

def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as h: return list(csv.DictReader(h))

def facts(path, dimensions):
    return {tuple(sorted((k,v) for k,v in row.items() if v and k not in dimensions)) for row in rows(path)}

def semantic_facts(csv_path, metadata):
    meta=json.loads(metadata.read_text(encoding="utf-8")); tmpl=meta["tableTemplates"]["structured"]
    dims={v[1:] for k,v in tmpl["dimensions"].items() if ":" in k and isinstance(v,str) and v.startswith("$")}
    result=set()
    for row in rows(csv_path):
        identity=tuple(sorted((d,row[d]) for d in dims if row.get(d)))
        for k,v in row.items():
            if v and k not in dims: result.add((identity,k,v))
    return result

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--config",type=Path,required=True); ap.add_argument("--output-dir",type=Path,required=True)
    a=ap.parse_args(); raw=json.loads(a.config.read_text(encoding="utf-8")); base=a.config.parent
    scalar={"entity","period"}; c={k:(v if k in scalar else resolve(base,v)) for k,v in raw.items()}
    out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    en=out/"en.csv"
    run([c["python"],c["syntax_binding"],c["ubl_fixture"],"-b",c["ubl_binding"],"-o",en,"--hmd-file",c["source_hmd"],"--taxonomy-base",c["en_taxonomy_support"],"--drop-empty-columns"])
    if hashlib.sha256(en.read_bytes()).digest() != hashlib.sha256(c["expected_en_csv"].read_bytes()).digest():
        raise AssertionError("UBL to EN output differs from public expected fixture")
    gl=out/"gl.csv"
    sem=[c["python"],c["semantic_binding"],"forward",en,"--binding",c["semantic_binding_table"],"--source-hmd",c["source_hmd"],"--target-hmd",c["target_hmd"],"--overlay",c["overlay"],"--qname-map",c["qname_map"],"--taxonomy",c["oim_entry"],"--output",gl,"--entity",c["entity"],"--period",c["period"]]
    run(sem); meta=gl.with_suffix(".json")
    tup=out/"invoice_tuple.xml"
    run([c["python"],c["tuple_binding"],"serialize",gl,"--metadata",meta,"--hmd",c["target_hmd"],"--overlay",c["overlay"],"--qname-map",c["qname_map"],"--taxonomy",c["tuple_entry"],"--output",tup])
    recovered=out/"gl_recovered.csv"
    run([c["python"],c["tuple_binding"],"deserialize",tup,"--metadata",meta,"--hmd",c["target_hmd"],"--overlay",c["overlay"],"--qname-map",c["qname_map"],"--taxonomy",c["tuple_entry"],"--output",recovered])
    en2=out/"en_recovered.csv"
    run([c["python"],c["semantic_binding"],"reverse",recovered,"--binding",c["semantic_binding_table"],"--source-hmd",c["source_hmd"],"--target-hmd",c["target_hmd"],"--overlay",c["overlay"],"--qname-map",c["qname_map"],"--output",en2])
    gl2=out/"gl_reforward.csv"; sem2=list(sem); sem2[3]=en2; sem2[sem2.index(gl)+0]=gl2 if False else gl
    sem2=[gl2 if x==gl else x for x in sem2]; run(sem2)
    if semantic_facts(gl,meta)!=semantic_facts(recovered,meta): raise AssertionError("Tuple GL diff")
    if semantic_facts(gl,meta)!=semantic_facts(gl2,gl2.with_suffix('.json')): raise AssertionError("re-forward GL diff")
    rr=rows(gl)
    if not any(r.get("headerInvoiceType")=="gen:vdN1001InvoiceCreditNoteTypeN380" for r in rr): raise AssertionError("380 QName")
    parties=[(r.get("dEntityParty"),r.get("entityPartyType")) for r in rr if r.get("entityPartyType")]
    if parties != [("1","gen:vdPartyTypeSeller"),("2","gen:vdPartyTypeBuyer")]: raise AssertionError(str(parties))
    results=[]
    for name,path in (("oim",meta),("tuple",tup)):
        log=out/f"arelle_{name}.log"; run([c["arelle"],"--file",path,"--validate","--logFile",log])
        text=log.read_text(encoding="utf-8-sig",errors="replace").lower(); e=text.count("[error]"); w=text.count("[warning]")
        if e or w: raise AssertionError(f"Arelle {name}: {e}/{w}")
        results.append({"test":f"arelle_{name}","status":"PASS","details":f"error {e} / warning {w}"})
    results += [{"test":"clean_clone_full_route","status":"PASS","details":"semantic/value/ordinal diff 0"},{"test":"invoice_type_380","status":"PASS","details":"EE1 QName retained"},{"test":"entity_party","status":"PASS","details":"seller 1 / buyer 2 ordinal retained"}]
    with (out/"CLEAN_CLONE_RESULTS.csv").open("w",encoding="utf-8-sig",newline="") as h:
        w=csv.DictWriter(h,fieldnames=["test","status","details"],lineterminator="\n"); w.writeheader(); w.writerows(results)
    print(json.dumps({"status":"PASS","tests":len(results)}))
if __name__=="__main__": main()
