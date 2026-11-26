import urllib.request,concurrent.futures
from pathlib import Path
urls=['https://raw.githubusercontent.com/StarMoe-org/Moesekai/main/web/src/lib/assets.ts','https://raw.githubusercontent.com/moe-sekai/lunabot/master/src/plugins/sekai/modules/mysekai/__init__.py','https://raw.githubusercontent.com/moe-sekai/lunabot/master/src/plugins/sekai/modules/mysekai/draw.py']
def get(u):
 try:
  b=urllib.request.urlopen(u,timeout=12).read();p=Path('reference')/('avatar_source_'+str(urls.index(u))+'.txt');p.write_bytes(b);return str(p),len(b)
 except Exception as e:return str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as e:
 for r in e.map(get,urls):print(r)
