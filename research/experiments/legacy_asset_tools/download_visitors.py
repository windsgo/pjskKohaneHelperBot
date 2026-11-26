import urllib.request,concurrent.futures
from pathlib import Path
try:print(urllib.request.urlopen('https://raw.githubusercontent.com/StarMoe-org/Moesekai/main/web/src/lib/assetDomains.ts',timeout=10).read().decode(),flush=True)
except Exception as e:print(e)
def get(i):
 u=f'https://moe.exmeaning.com/assets/chr_ts_{i}.png'
 try:
  b=urllib.request.urlopen(u,timeout=12).read();p=Path('assets/visitors');p.mkdir(exist_ok=True);(p/f'{i}.png').write_bytes(b);return i,len(b)
 except Exception as e:return i,str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
 for r in ex.map(get,[9,12,29,39,49]):print(r,flush=True)
