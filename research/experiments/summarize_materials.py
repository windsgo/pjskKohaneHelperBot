"""Summarize before_drop materials using CN master names and explicit quantity."""
import collections,csv,json
from pathlib import Path
BASE=Path(__file__).resolve().parent
materials=json.loads((BASE/'materials_cn.json').read_text(encoding='utf-8'))
lookup={x['id']:x for x in materials}
maps=json.loads((BASE/'decoded/harvest_maps.json').read_text(encoding='utf-8'))
counts=collections.defaultdict(collections.Counter)
other=collections.Counter()
details=[]
for site in maps:
 for drop in site[2]:
  resource_type,rid,x,z,hp,seq,status,quantity=drop[:8]
  if status != 'before_drop': continue
  if not isinstance(quantity,int) or quantity<=0: raise ValueError('Invalid quantity')
  if resource_type!='mysekai_material':
   other[resource_type]+=quantity
   continue
  if rid not in lookup: raise ValueError(f'Unmapped material {rid}')
  counts[rid][site[0]]+=quantity
  details.append({'site_id':site[0],'material_id':rid,'name':lookup[rid]['name'],'x':x,'z':z,'quantity':quantity,'status':status,'seq':seq})
rows=[]
for rid in sorted(counts):
 row={'material_id':rid,'name':lookup[rid]['name'],**{f'site_{s}':counts[rid][s] for s in (5,6,7,8)},'total':sum(counts[rid].values())}
 rows.append(row)
assert sum(r['total'] for r in rows)==sum(d['quantity'] for d in details)
out=BASE/'decoded'
for name,data in [('material_totals',rows),('material_drops',details)]:
 (out/f'{name}.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
 with (out/f'{name}.csv').open('w',encoding='utf-8-sig',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(data[0]));writer.writeheader();writer.writerows(data)
print(json.dumps({'materials':rows,'material_total':sum(r['total'] for r in rows),'other_quantities':dict(other)},ensure_ascii=True,indent=2))
