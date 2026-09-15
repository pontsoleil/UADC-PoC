#!/usr/bin/env python3
"""HMD/16-column Binding -> occurrence tree -> sparse wide CSV + xBRL-CSV JSON.

Forward-only replacement for the legacy 13-column csv2tidy interface.
The supplied PCA profile supports keyed_rows/source_rows and equality selectors.
No accounting column, class name, tax code or taxonomy URI is built into the engine.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import os
import re
import sys
import tempfile
import unicodedata
from collections import Counter, OrderedDict
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import quote
import xml.etree.ElementTree as ET

FIELDS = ('sequence','level','type','name','datatype','multiplicity','column',
          'semantic_path','occurrence_mode','group_key','row_role','max_occurs',
          'default_value','transformation','required','note')
YES = {'true','1','yes','y'}
NO = {'','false','0','no','n'}

class ConversionError(Exception):
    """Diagnostics deliberately exclude source values."""

def require(ok, code):
    if not ok:
        raise ConversionError(code)

def read_csv(path, encoding):
    with Path(path).open(encoding=encoding, newline='') as f:
        rows = list(csv.reader(f))
    require(bool(rows), 'EMPTY_DEFINITION')
    require(len(set(rows[0])) == len(rows[0]), 'DUPLICATE_HEADER')
    require(all(len(r) == len(rows[0]) for r in rows[1:]), 'DEFINITION_WIDTH')
    return rows[0], [dict(zip(rows[0], r)) for r in rows[1:]]

def parse_path(path):
    """Split at dots outside quoted selectors; reject unsupported grammar."""
    parts=[]; buf=''; depth=0; quoted=''
    for char in path:
        if quoted:
            buf += char
            if char == quoted: quoted=''
        elif char in "\"'" and depth:
            quoted=char; buf+=char
        elif char=='[':
            require(depth==0,'PATH_SELECTOR_INVALID');depth=1;buf+=char
        elif char==']':
            require(depth==1,'PATH_SELECTOR_INVALID');depth=0;buf+=char
        elif char=='.' and not depth:
            parts.append(buf);buf=''
        else:buf+=char
    require(not depth and not quoted, 'PATH_SELECTOR_INVALID')
    parts.append(buf)
    require(parts[0]=='$' and len(parts)>1,'PATH_INVALID')
    result=[]
    for part in parts[1:]:
        m=re.fullmatch(r'([A-Za-z_][A-Za-z_0-9]*)(.*)',part)
        require(m is not None,'PATH_INVALID')
        tail=m[2]; preds=[]
        while tail:
            s=re.match(r'''\[([A-Za-z_][A-Za-z_0-9]*)=(['"])([^'"\[\]]+)\2\]''',tail)
            require(s is not None,'SELECTOR_GRAMMAR_UNSUPPORTED')
            preds.append((s[1],s[3]));tail=tail[s.end():]
        require(len({p[0] for p in preds})==len(preds),'DUPLICATE_PREDICATE')
        result.append((m[1],tuple(sorted(preds))))
    return tuple(result)

def neutral(parts):return '$.'+'.'.join(p[0] for p in parts)
def column_number(value):
    require(re.fullmatch(r'C[1-9][0-9]*',value) is not None,'PHYSICAL_COLUMN_INVALID')
    return int(value[1:])
def repeat(h):return h['multiplicity'].split('..')[-1] in ('*','n','unbounded') or int(h['multiplicity'].split('..')[-1])>1
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lookup_key(values,spec):
    modes=spec.get('key_normalizers',['']*len(values))
    require(len(modes)==len(values),'LOOKUP_NORMALIZER_INVALID')
    require(all(m in ('','NFKC') for m in modes),'LOOKUP_NORMALIZER_INVALID')
    return tuple(unicodedata.normalize(mode,value) if mode else value for value,mode in zip(values,modes))

def transform(name, value):
    if not value or not name:return value
    if name=='date_midnight':
        require(re.fullmatch(r'\d{8}',value) is not None,'DATE_INVALID')
        try:return datetime.strptime(value,'%Y%m%d').strftime('%Y-%m-%dT00:00:00')
        except ValueError:raise ConversionError('DATE_INVALID') from None
    if name=='iso_date_to_yyyymmdd':
        # Historical forward name means compact date -> ISO date, not the reverse.
        return transform('date_midnight',value).split('T')[0]
    if name=='account_base':return value.rsplit('-',1)[0] if '-' in value else value
    if name=='account_suffix':return value.rsplit('-',1)[1] if '-' in value else ''
    raise ConversionError('TRANSFORMATION_UNSUPPORTED')

def typed(value,h):
    dt=h['datatype'].lower()
    if dt in ('monetary','decimal','pure','integer'):
        try:d=Decimal(value)
        except InvalidOperation:raise ConversionError('DATATYPE_INVALID') from None
        require(d.is_finite(),'DATATYPE_INVALID')
        if dt=='integer':require(d==d.to_integral_value(),'DATATYPE_INVALID')
        return format(d,'f')
    if dt in ('date time','datetime'):
        require('T' in value,'DATETIME_REPRESENTATION_REQUIRED')
        try:datetime.fromisoformat(value.replace('Z','+00:00'))
        except ValueError:raise ConversionError('DATATYPE_INVALID') from None
    if dt=='boolean':require(value in ('true','false','0','1'),'DATATYPE_INVALID')
    return value

@dataclass
class Occurrence:
    path: str
    parent: Occurrence | None
    ordinal: int
    identity: tuple
    facts: dict = field(default_factory=dict)
    children: OrderedDict = field(default_factory=OrderedDict)
    sources: set = field(default_factory=set)

class Converter:
    def __init__(self,hmd_path,binding_path,profile_path,definition_encoding='cp932'):
        self.hmd_path=Path(hmd_path);self.binding_path=Path(binding_path)
        self.profile_path=Path(profile_path)
        self.profile=json.loads(self.profile_path.read_text(encoding='utf-8'))
        _, hs=read_csv(hmd_path,self.profile.get('hmd_encoding','utf-8-sig'))
        require(all(h.get('semantic_path') for h in hs),'HMD_PATH_INVALID')
        self.hmd={h['semantic_path']:h for h in hs}
        require(len(hs)==len(self.hmd),'HMD_DUPLICATE_PATH')
        for p,h in self.hmd.items():
            require(int(h['sequence'])>0,'HMD_SEQUENCE_INVALID')
            require(neutral(parse_path(p))==p and '[' not in p,'HMD_PATH_INVALID')
            if p.count('.')>1:require(p.rsplit('.',1)[0] in self.hmd,'HMD_PARENT_MISSING')
        header,rows=read_csv(binding_path,definition_encoding)
        require(tuple(header)==FIELDS,'BINDING_HEADER_INVALID')
        self.headers={};self.rows=[];columns=set();paths=set()
        for r in rows:
            if r['type']=='P':
                n=column_number(r['column']);require(n not in self.headers,'HEADER_DUPLICATE')
                self.headers[n]=r['name'];continue
            r['parts']=parse_path(r['semantic_path']);r['neutral']=neutral(r['parts'])
            h=self.hmd.get(r['neutral']);require(h is not None,'HMD_PATH_UNRESOLVED')
            require(all(r[k]==h[k] for k in ('sequence','level','type','name','datatype','multiplicity')),'HMD_ATTRIBUTE_MISMATCH')
            require(r['semantic_path'] not in paths,'BINDING_PATH_DUPLICATE');paths.add(r['semantic_path'])
            require(r['required'].lower() in YES|NO,'REQUIRED_FLAG_INVALID')
            require(r['occurrence_mode'] in ('','single','keyed_rows','source_rows'),'OCCURRENCE_MODE_UNSUPPORTED')
            if r['max_occurs']:require(int(r['max_occurs'])>0,'MAX_OCCURS_INVALID')
            if r['column']:
                n=column_number(r['column']);require(n not in columns,'PHYSICAL_COLUMN_DUPLICATE');columns.add(n)
            for i,(_,preds) in enumerate(r['parts']):
                if preds:
                    cp=neutral(r['parts'][:i+1]);require(self.hmd[cp]['type']=='C','SELECTOR_NOT_CLASS')
                    for key,val in preds:require(cp+'.'+key in self.hmd,'SELECTOR_FIELD_UNKNOWN')
            self.rows.append(r)
        self.columns=columns;self.width=int(self.profile['width'])
        require(set(self.headers)==set(range(1,self.width+1)),'PHYSICAL_HEADER_INCOMPLETE')
        require(all(n<=self.width for n in columns),'PROFILE_WIDTH_INVALID')
        groups=[r for r in self.rows if r['occurrence_mode']=='keyed_rows']
        drivers=[r for r in self.rows if r['row_role']=='driver']
        require(len(groups)==len(drivers)==1,'GROUP_DRIVER_INVALID')
        self.group=groups[0];self.driver=drivers[0]
        require(self.driver['occurrence_mode']=='source_rows','DRIVER_INVALID')
        require(self.driver['neutral'].rsplit('.',1)[0]==self.group['neutral'],'DRIVER_PARENT_UNSUPPORTED')
        self.group_columns=json.loads(self.group['group_key'])
        require(isinstance(self.group_columns,list) and bool(self.group_columns),'GROUP_KEY_INVALID')
        for c in self.group_columns:require(column_number(c)<=self.width,'GROUP_KEY_INVALID')
        di=len(self.driver['parts'])-1
        self.variants=list(dict.fromkeys(r['parts'][di][1] for r in self.rows if len(r['parts'])>di and r['parts'][:di]==self.driver['parts'][:di] and r['parts'][di][1]))
        require(bool(self.variants),'VARIANTS_MISSING')
        # Every predicate must have an explicit mapped/default fact in that occurrence.
        for r in self.rows:
            for i,(_,preds) in enumerate(r['parts']):
                for key,val in preds:
                    required=r['parts'][:i+1]+((key,()),)
                    require(any(x['parts']==required and (x['column'] or x['default_value']==val) for x in self.rows),'PATH_SELECTOR_VALUE_MISSING')
        self.lookups=[];self.dependencies=[self.hmd_path,self.binding_path,self.profile_path]
        for spec in self.profile.get('lookups',[]):
            path=self.profile_path.parent/spec['file'];self.dependencies.append(path)
            _, data=read_csv(path,spec.get('encoding','utf-8-sig')); index={}
            for item in data:
                key=lookup_key(tuple(item[f] for f in spec['key_fields']),spec)
                require(key not in index,'LOOKUP_KEY_DUPLICATE');index[key]=item
            for output in spec['outputs']:
                require(output['target'] in self.hmd and self.hmd[output['target']]['type']=='A','LOOKUP_TARGET_INVALID')
            self.lookups.append((spec,index))
        self.root=None;self.ignored=Counter();self.source_count=0

    def node(self,parent,path,key):
        if parent is None:
            if self.root is None:self.root=Occurrence(path,None,1,key)
            require(self.root.path==path,'MULTI_ROOT_UNSUPPORTED');return self.root
        identity=(path,key)
        if identity not in parent.children:
            ordinal=1+sum(n.path==path for n in parent.children.values())
            upper=self.hmd[path]['multiplicity'].split('..')[-1]
            if upper not in ('*','n','unbounded'):require(ordinal<=int(upper),'HMD_MULTIPLICITY_EXCEEDED')
            parent.children[identity]=Occurrence(path,parent,ordinal,key)
        return parent.children[identity]

    def owner(self,parts,group_key,source_index,variant,extra=None):
        parent=None
        for i,(_,preds) in enumerate(parts):
            path=neutral(parts[:i+1]);h=self.hmd[path]
            require(h['type']=='C','FACT_OWNER_NOT_CLASS')
            if path==self.group['neutral']:key=('group',group_key)
            elif path==self.driver['neutral']:key=('row',source_index,variant)
            else:key=('selected',preds)
            if extra and i==len(parts)-1:key=('derived',extra)
            parent=self.node(parent,path,key)
        return parent

    def assign(self,node,path,value,source_index):
        if value=='':return
        value=typed(value,self.hmd[path])
        require(path not in node.facts or node.facts[path]==value,'OCCURRENCE_FACT_CONFLICT')
        node.facts[path]=value;node.sources.add(source_index)

    def value(self,r,source):
        value=source[column_number(r['column'])-1] if r['column'] else r['default_value']
        name=self.profile.get('transformations',{}).get(r['neutral'],r['transformation'])
        return transform(name,value)

    def process_scope(self,selected,source,index,group_key,variant):
        for r in selected:
            if r['type']!='A':continue
            inactive=False
            for n in range(len(r['parts'])-1):
                cp=r['parts'][:n+1];np=neutral(cp)
                if np in (self.group['neutral'],self.driver['neutral']) or len(cp)<len(self.driver['parts']):continue
                descendants=[x for x in selected if x['parts'][:len(cp)]==cp and x['column']]
                if descendants and not any(source[column_number(x['column'])-1]!='' for x in descendants):
                    inactive=True;break
            if inactive:continue
            value=self.value(r,source)
            require(value!='' or r['required'].lower() not in YES,'REQUIRED_VALUE_MISSING')
            if value=='':continue
            node=self.owner(r['parts'][:-1],group_key,index,variant)
            self.assign(node,r['neutral'],value,index)
        # Verify predicate values against the facts actually constructed.
        for r in selected:
            if r['type']!='A' or not self.value(r,source):continue
            for i,(_,preds) in enumerate(r['parts'][:-1]):
                if not preds:continue
                # Missing optional branches are not created merely for predicates.
                parent=self.find_owner(r['parts'][:i+1],group_key,index,variant)
                if parent is not None:
                    for key,val in preds:require(parent.facts.get(parent.path+'.'+key)==val,'PATH_SELECTOR_VALUE_MISMATCH')

    def find_owner(self,parts,group_key,index,variant):
        parent=self.root
        for i,(_,preds) in enumerate(parts):
            path=neutral(parts[:i+1])
            if i==0:continue
            key=('group',group_key) if path==self.group['neutral'] else ('row',index,variant) if path==self.driver['neutral'] else ('selected',preds)
            parent=parent.children.get((path,key)) if parent else None
        return parent

    def lookup(self,source,index,group_key,variant):
        for spec,table in self.lookups:
            if tuple(tuple(x) for x in spec['variant'])!=variant:continue
            key=lookup_key(tuple(source[column_number(k['column'])-1] if 'column' in k else k['literal'] for k in spec['keys']),spec)
            if any(x=='' for x in key):
                require(spec.get('optional',False),'LOOKUP_KEY_MISSING');continue
            record=table.get(key);require(record is not None,'LOOKUP_VALUE_UNRESOLVED')
            for target in spec['outputs']:
                value=target.get('literal',record.get(target.get('field',''),''))
                value=transform(target.get('transform',''),value)
                if target.get('when_field') and not transform(target.get('when_transform',''),record[target['when_field']]):continue
                if not value:continue
                parts=parse_path(target['target'])
                # Bind all derived facts to this source-row/side and its declared child.
                parts=list(parts);di=len(self.driver['parts'])-1
                parts[di]=(parts[di][0],variant)
                owner=self.owner(tuple(parts[:-1]),group_key,index,variant,target.get('occurrence_key'))
                if target.get('replace',False):owner.facts.pop(target['target'],None)
                self.assign(owner,target['target'],value,index)

    def convert(self,input_path,encoding,data_start_row,check_header=False):
        require(data_start_row>=1,'DATA_START_ROW_INVALID')
        with Path(input_path).open(encoding=encoding,newline='') as stream:data=list(csv.reader(stream))
        if check_header:require(data and data[0]==[self.headers[i] for i in range(1,self.width+1)],'INPUT_HEADER_MISMATCH')
        require(len(data)>=data_start_row,'NO_DATA_ROWS')
        groups=OrderedDict()
        for number,source in enumerate(data[data_start_row-1:],data_start_row):
            require(len(source)==self.width,'PROFILE_WIDTH_MISMATCH')
            key=tuple(source[column_number(c)-1] for c in self.group_columns)
            require(all(key),'GROUP_KEY_EMPTY');groups.setdefault(key,[]).append((number,source))
            self.ignored.update(f'C{i}' for i,v in enumerate(source,1) if v and i not in self.columns)
        if self.group['max_occurs']:require(len(groups)<=int(self.group['max_occurs']),'MAX_OCCURS_EXCEEDED')
        di=len(self.driver['parts'])-1
        header_rows=[r for r in self.rows if not r['neutral'].startswith(self.driver['neutral'])]
        for key,records in groups.items():
            if self.driver['max_occurs']:require(len(records)<=int(self.driver['max_occurs']),'MAX_OCCURS_EXCEEDED')
            for index,source in records:
                self.source_count+=1
                self.process_scope(header_rows,source,index,key,())
                for variant in self.variants:
                    selected=[r for r in self.rows if r['neutral'].startswith(self.driver['neutral']) and (not r['parts'][di][1] or r['parts'][di][1]==variant)]
                    presence=[r for r in selected if r['row_role']=='presence']
                    require(bool(presence),'VARIANT_PRESENCE_REQUIRED')
                    if not any(self.value(r,source) for r in presence):
                        side_values=[r for r in selected if r['column'] and r['parts'][di][1]==variant]
                        require(not any(self.value(r,source) not in ('','0','0.0','0.00') for r in side_values),'SIDE_WITHOUT_PRESENCE')
                        continue
                    self.process_scope(selected,source,index,key,variant)
                    self.lookup(source,index,key,variant)
        require(self.root is not None,'NO_OCCURRENCES')
        return self

    def walk(self,node=None):
        node=node or self.root
        yield node
        for child in sorted(node.children.values(),key=lambda n:(int(self.hmd[n.path]['sequence']),n.ordinal)):
            yield from self.walk(child)

def uri(path,base):return quote(Path(os.path.relpath(Path(path).resolve(),Path(base).resolve())).as_posix(),safe='/.:_-')
def escape(value):return '#'+value if value.startswith('#') else value

def export(converter,output,entity,period,currency,overwrite=False):
    output=Path(output);require(output.suffix.lower()=='.csv','OUTPUT_SUFFIX_INVALID')
    p=converter.profile
    taxonomy=(converter.profile_path.parent/p['taxonomy']).resolve()
    require(taxonomy.is_file(),'TAXONOMY_MISSING')
    namespaces=p['namespaces'];require(entity.split(':',1)[0] in namespaces,'ENTITY_NAMESPACE_UNKNOWN')
    require(currency.split(':',1)[0] in namespaces,'UNIT_NAMESPACE_UNKNOWN')
    require(':' in entity and bool(entity.split(':',1)[1]),'ENTITY_REQUIRED')
    try:
        for endpoint in period.split('/'):
            require('T' in endpoint,'PERIOD_INVALID');datetime.fromisoformat(endpoint.replace('Z','+00:00'))
    except ValueError:raise ConversionError('PERIOD_INVALID') from None
    # Check declarations in the local taxonomy schema closure. External standard imports
    # are left to a full XBRL processor; no network access or taxonomy regeneration.
    declarations=set();visited=set();stack=[taxonomy];xs='{http://www.w3.org/2001/XMLSchema}'
    while stack:
        path=stack.pop().resolve()
        if path in visited:continue
        visited.add(path);xml=ET.parse(path).getroot();ns=xml.get('targetNamespace','')
        declarations.update((ns,e.get('name')) for e in xml.findall(xs+'element'))
        for e in list(xml.findall(xs+'import'))+list(xml.findall(xs+'include')):
            location=e.get('schemaLocation','')
            if location and not re.match(r'https?://',location):
                dep=path.parent/location;require(dep.is_file(),'TAXONOMY_DEPENDENCY_MISSING');stack.append(dep)
    tree_nodes=list(converter.walk())
    # A class-only row has no XBRL fact.  Its coordinates are already carried
    # on descendant rows; including it makes the xBRL-CSV table invalid.
    nodes=[n for n in tree_nodes if n.facts]
    used={n.path for n in tree_nodes}|{f for n in tree_nodes for f in n.facts}
    ordered=sorted(used,key=lambda path:(int(converter.hmd[path]['sequence']),path))
    columns={path:f'C{i}' for i,path in enumerate(ordered,1)}
    meta_columns={};column_rows=[]
    for path in ordered:
        h=converter.hmd[path];column=columns[path];qname='';dimension=''
        if h['type']=='C':
            # A singleton structural coordinate is not a dimension parameter.
            # Preserve it in the CSV for traceability as an OIM comment column.
            meta_columns[column]={} if repeat(h) else {'comment':True}
        else:
            prefix=p['module_prefixes'][h['module']];qname=f"{prefix}:{h['local_name']}"
            require((namespaces[prefix],h['local_name']) in declarations,'TAXONOMY_CONCEPT_UNDECLARED')
            dims={'concept':qname}
            if h['datatype'].lower()=='monetary':dims['unit']=currency
            # A pure numeric concept has the implicit pure unit in OIM.  A
            # numerator-only xbrli:pure unit is not a legal explicit unit.
            parent=path.rsplit('.',1)[0]
            while parent in converter.hmd:
                if repeat(converter.hmd[parent]):
                    dimension=p['dimensions'].get(parent);require(dimension is not None,'DIMENSION_MAPPING_MISSING')
                    pre,local=dimension.split(':',1)
                    require((namespaces[pre],local) in declarations,'TAXONOMY_DIMENSION_UNDECLARED')
                    dims[dimension]='$'+columns[parent]
                parent=parent.rsplit('.',1)[0]
            meta_columns[column]={'dimensions':dims}
            # Exact precision must not be represented by the invalid lexical
            # xBRL-CSV decimals value "INF".
        column_rows.append([column,h['sequence'],h['type'],h['name'],path,qname,p['dimensions'].get(path,'')])
    metadata={'documentInfo':{'documentType':'https://xbrl.org/2021/xbrl-csv','namespaces':namespaces,'taxonomy':[uri(taxonomy,output.parent)]},
              'tableTemplates':{'structured':{'dimensions':{'entity':entity,'period':period},'columns':meta_columns}},
              'tables':{'structured':{'template':'structured','url':quote(output.name)}}}
    csv_rows=[];trace=[]
    for node in nodes:
        row={};current=node
        while current:
            row[columns[current.path]]=str(current.ordinal);current=current.parent
        for path,value in node.facts.items():row[columns[path]]=escape(value)
        csv_rows.append(row)
        for number in sorted(node.sources):trace.append([len(csv_rows),number,node.path,json.dumps({k:v for k,v in row.items() if converter.hmd[ordered[int(k[1:])-1]]['type']=='C'},separators=(',',':'))])
    report={'source_rows':converter.source_count,'structured_rows':len(nodes),'tree_rows':len(tree_nodes),'factless_tree_rows':len(tree_nodes)-len(nodes),'facts':sum(len(n.facts) for n in nodes),'columns':len(columns),
            'occurrences':dict(Counter(n.path for n in tree_nodes)),
            'unbound_populated_cells':dict(sorted(converter.ignored.items(),key=lambda x:int(x[0][1:]))),
            'definition_sha256':{str(x.name):sha(x) for x in converter.dependencies},
            'validation_scope':'mapped Binding subset; local taxonomy declarations only; Arelle not run'}
    output.parent.mkdir(parents=True,exist_ok=True)
    names=[output.name,output.with_suffix('.json').name,output.stem+'.columns.csv',output.stem+'.trace.csv',output.stem+'.report.json']
    require(overwrite or not any((output.parent/n).exists() for n in names),'OUTPUT_EXISTS')
    require(not any((output.parent/n).resolve() in {x.resolve() for x in converter.dependencies} for n in names),'OUTPUT_OVERWRITES_DEFINITION')
    with tempfile.TemporaryDirectory(dir=output.parent) as temp:
        stage=Path(temp)
        with (stage/names[0]).open('w',encoding='utf-8',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(columns.values()),lineterminator='\n');writer.writeheader();writer.writerows(csv_rows)
        (stage/names[1]).write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        for filename,header,data in [(names[2],['column','sequence','type','name','semantic_path','concept','dimension'],column_rows),(names[3],['structured_row','source_file_row','owner_semantic_path','coordinates'],trace)]:
            with (stage/filename).open('w',encoding='utf-8',newline='') as f:
                writer=csv.writer(f,lineterminator='\n');writer.writerow(header);writer.writerows(data)
        (stage/names[4]).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        backups={};published=[]
        try:
            for filename in names:
                target=output.parent/filename
                if target.exists():
                    backup=stage/(filename+'.previous');os.replace(target,backup);backups[target]=backup
                os.replace(stage/filename,target);published.append(target)
        except OSError:
            for target in published:target.unlink(missing_ok=True)
            for target,backup in backups.items():os.replace(backup,target)
            raise
    return report

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input',type=Path)
    ap.add_argument('-o','--outfile',required=True,type=Path)
    ap.add_argument('-m','--hmd-file','--lhm_file',dest='hmd',required=True,type=Path)
    ap.add_argument('-b','--binding-file','--binding_file',dest='binding',required=True,type=Path)
    ap.add_argument('--profile',required=True,type=Path)
    ap.add_argument('-e','--encoding',default='cp932')
    ap.add_argument('--definition-encoding',default='cp932')
    ap.add_argument('--data-start-row',type=int,default=3)
    ap.add_argument('--check-header',action='store_true')
    ap.add_argument('--entity',required=True);ap.add_argument('--period',required=True)
    ap.add_argument('--currency',required=True);ap.add_argument('--overwrite',action='store_true')
    args=ap.parse_args(argv)
    try:
        require(args.input.resolve()!=args.outfile.resolve(),'OUTPUT_OVERWRITES_INPUT')
        c=Converter(args.hmd,args.binding,args.profile,args.definition_encoding)
        c.convert(args.input,args.encoding,args.data_start_row,args.check_header)
        report=export(c,args.outfile,args.entity,args.period,args.currency,args.overwrite)
        print(json.dumps({k:report[k] for k in ('source_rows','structured_rows','facts','columns')}));return 0
    except ConversionError as e:print(str(e),file=sys.stderr);return 2
    except (OSError,UnicodeError,csv.Error,ET.ParseError,json.JSONDecodeError):print('FILE_OR_DEFINITION_READ_WRITE_ERROR',file=sys.stderr);return 2
    except (ValueError,KeyError,TypeError):print('DEFINITION_OR_ARGUMENT_INVALID',file=sys.stderr);return 2

if __name__=='__main__':sys.exit(main())
