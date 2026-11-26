import urllib.request,csv,base64,json,io
from pathlib import Path
from PIL import Image
p=Path('assets/materials');p.mkdir(parents=True,exist_ok=True)
u='https://raw.githubusercontent.com/mouse233/MySekaiMapper/main/assets/resourceId.csv'
b=Path('assets/resourceId.csv').read_bytes() if Path('assets/resourceId.csv').exists() else urllib.request.urlopen(u,timeout=30).read();Path('assets/resourceId.csv').write_bytes(b)
rows=list(csv.DictReader(io.StringIO(b.decode('utf-8-sig'))));print('columns',list(rows[0]))
needed={r['material_id'] for r in json.load(open('decoded/material_drops.json',encoding='utf-8'))}
found=set()
for r in rows:
 try: mid=int(r['resourceId'])
 except ValueError:continue
 if mid not in needed:continue
 raw=base64.b64decode(r['base64']);im=Image.open(io.BytesIO(raw));im.convert('RGBA').save(p/f'{mid}.png');found.add(mid)
print('found',sorted(found),'missing',sorted(needed-found))

