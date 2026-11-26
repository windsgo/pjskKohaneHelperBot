import urllib.request,json,base64
from pathlib import Path
r=next(x for x in json.load(open('mapper_tree.json',encoding='utf-8'))['tree'] if x['path']=='assets/resourceId.csv');print(r,flush=True)
u='https://raw.githubusercontent.com/mouse233/MySekaiMapper/refs/heads/main/assets/resourceId.csv'
with urllib.request.urlopen(u,timeout=45) as resp:
 b=resp.read();Path('assets/resourceId.csv').write_bytes(b);print(len(b),flush=True)
