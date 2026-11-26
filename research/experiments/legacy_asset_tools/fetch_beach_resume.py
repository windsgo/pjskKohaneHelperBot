import urllib.request,json,http.client
from pathlib import Path
t=json.load(open('ursekai_tree.json',encoding='utf-8'))['tree'];o=next(x for x in t if x['path']=='img/beach.png')
u=o['url']
p=Path('reference/ursekai/img/beach.partial')
for attempt in range(3):
 start=p.stat().st_size if p.exists() else 0
 headers={'Accept':'application/vnd.github.raw+json'}
 if start:headers['Range']=f'bytes={start}-'
 try:
  with urllib.request.urlopen(urllib.request.Request(u,headers=headers),timeout=20) as r:
   append=r.status==206
   mode='ab' if append else 'wb'
   with p.open(mode) as f:
    while True:
     try:b=r.read(65536)
     except http.client.IncompleteRead as e:
      f.write(e.partial);break
     if not b:break
     f.write(b)
  print('attempt',attempt,'bytes',p.stat().st_size,flush=True)
  if p.stat().st_size==o['size']:
   from PIL import Image
   Image.open(p).verify();p.replace(p.with_name('beach.png'));print('verified',flush=True);break
 except Exception as e:print(str(e),flush=True)
