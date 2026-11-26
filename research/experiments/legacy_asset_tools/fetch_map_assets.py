import urllib.request,concurrent.futures
from pathlib import Path
names=['js/config.js','js/canvas.js','img/beach.png','img/flowergarden.png','img/grassland.png','img/memorialplace.png']
def get(n):
 try:
  b=urllib.request.urlopen('https://raw.githubusercontent.com/endoretic/ursekai/main/'+n,timeout=25).read();p=Path('reference/ursekai')/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);return n,len(b)
 except Exception as e:return n,str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
 for r in ex.map(get,names):print(r,flush=True)
