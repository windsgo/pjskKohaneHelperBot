import json
from pathlib import Path
from sync_report_assets import catalog
out=Path('assets/catalog');old=json.loads((out/'manifest.json').read_text(encoding='utf-8'));stats={};missing=[]
for r in catalog():
 key=f'{r["kind"]}:{r["id"]}';p=out/r['kind']/f'{r["id"]}.png';entry=old.get(key,r)
 if p.exists():entry={**entry,'status':'cached','path':str(p)}
 else:entry={**entry,'status':'missing'};missing.append(entry)
 old[key]=entry;v=stats.setdefault(r['kind'],{'available':0,'total':0});v['total']+=1;v['available']+=p.exists()
(out/'manifest.json').write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'coverage.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(stats));print('missing',len(missing))
