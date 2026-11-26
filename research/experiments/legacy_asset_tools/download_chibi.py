import urllib.request,concurrent.futures
from pathlib import Path
def get(i):
 n=f'chr_sd_{i:02d}_01';u=f'https://storage.pjsk.moe/sekai-jp-assets/bonds_honor/character/{n}/{n}.png'
 try:
  b=urllib.request.urlopen(u,timeout=12).read();Path(f'assets/visitors/chibi_{i}.png').write_bytes(b);return i,len(b)
 except Exception as e:return i,str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
 for r in ex.map(get,[9,12,29,39,49]):print(r,flush=True)
