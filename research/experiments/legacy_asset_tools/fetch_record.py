import json,urllib.request
from pathlib import Path
r=next(x for x in json.load(open('masterdata/mysekaiMusicRecords.json',encoding='utf-8')) if x['id']==182);print(r,flush=True)
b=urllib.request.urlopen('https://metadata.exmeaning.com/cn/master/musics.json',timeout=15).read();Path('masterdata/musics.json').write_bytes(b)
m=next(x for x in json.loads(b) if x['id']==r['externalId']);Path('assets/record_182.json').write_text(json.dumps(m,ensure_ascii=False),encoding='utf-8');print(m,flush=True)
for host in ['https://storage.sekai.best/sekai-jp-assets','https://assets.unipjsk.com/ondemand']:
 try:
  u=host+f'/music/jacket/jacket_s_{m["id"]:03d}/jacket_s_{m["id"]:03d}.png';d=urllib.request.urlopen(u,timeout=10).read();Path('assets/record_182.png').write_bytes(d);print('cover',len(d));break
 except Exception as e:print(e,flush=True)
