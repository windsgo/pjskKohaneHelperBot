import urllib.request,json,concurrent.futures,base64,http.client
from pathlib import Path
t=json.load(open('ursekai_tree.json',encoding='utf-8'))['tree']
def get(name):
 obj=next(x for x in t if x['path']=='img/'+name+'.png')
 try:
  req=urllib.request.Request(obj['url'],headers={'Accept':'application/vnd.github.raw+json'})
  with urllib.request.urlopen(req,timeout=20) as r:
   b=r.read()
  if b[:1]==b'{':b=base64.b64decode(json.loads(b)['content'])
  from PIL import Image
  import io
  Image.open(io.BytesIO(b)).verify()
  Path('reference/ursekai/img/'+name+'.png').write_bytes(b)
  return name,len(b)
 except Exception as e:return name,str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as e:
 for r in e.map(get,['beach','memorialplace']):print(r,flush=True)
