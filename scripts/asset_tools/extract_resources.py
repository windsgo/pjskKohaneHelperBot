import csv
import json
from pathlib import Path
p = Path(__file__).resolve().parents[2] / 'runtime' / 'decoded'
d = json.loads((p/'response.json').read_text(encoding='utf-8'))
r = d['updatedResources']
(p/'updatedResources.json').write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding='utf-8')
maps = r['userMysekaiHarvestMaps']
(p/'harvest_maps.json').write_text(json.dumps(maps, ensure_ascii=False, indent=2), encoding='utf-8')
summary=[]
for site in maps:
    site_id=site[0]
    summary.append({'site_id': site_id, 'array_lengths': [len(x) if isinstance(x,list) else None for x in site[1:]]})
    for j, rows in enumerate(site[1:],1):
        if not isinstance(rows,list) or not rows or not all(isinstance(x,list) for x in rows): continue
        width=max(map(len,rows))
        with (p/f'site_{site_id}_array_{j}.csv').open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.writer(f); w.writerow([f'column_{i}' for i in range(width)])
            w.writerows(rows)
(p/'harvest_summary.json').write_text(json.dumps(summary, indent=2),encoding='utf-8')
print(summary)
