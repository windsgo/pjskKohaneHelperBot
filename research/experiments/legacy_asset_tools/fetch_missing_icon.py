import urllib.request,concurrent.futures
from pathlib import Path
paths=['mysekai/material/item_junk_15_rip/item_junk_15.png','mysekai/thumbnail/material/item_junk_15_rip/item_junk_15.png','mysekai/thumbnail/material_rip/item_junk_15.png','mysekai/material_rip/item_junk_15.png']
urls=['https://storage.sekai.best/sekai-jp-assets/'+p for p in paths]+['https://storage2.pjsk.moe/sekai-jp-assets/'+p for p in paths]
def get(u):
 try:
  b=urllib.request.urlopen(u,timeout=8).read()
  if b[:4]==b'\x89PNG':Path('assets/materials/94.png').write_bytes(b);return 'OK '+u
  return str(len(b))+' '+u
 except Exception as e:return str(e)+' '+u
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as e:
 for result in e.map(get,urls):print(result,flush=True)
