import urllib.request,concurrent.futures,json,base64
from pathlib import Path
tree=json.load(open('ursekai_tree.json',encoding='utf-8'))['tree']
paths=['js/config.js','js/canvas.js','img/beach.png','img/flowergarden.png','img/grassland.png','img/memorialplace.png']
def get(n):
 try:
  obj=next(x for x in tree if x['path']==n)
  req=urllib.request.Request(obj['url'],headers={'User-Agent':'local-map-renderer'})
  b=base64.b64decode(json.load(urllib.request.urlopen(req,timeout=12))['content']);p=Path('reference/ursekai')/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);return n,len(b)
 except Exception as e:return n,str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
 for r in ex.map(get,paths):print(r,flush=True)
