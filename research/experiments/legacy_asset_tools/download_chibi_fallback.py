import urllib.request,concurrent.futures
from pathlib import Path
def get(i):
 for host in ['https://storage.exmeaning.com','https://storage.pjsk.moe']:
  for path in [f'/client/jp/player/loose/Sprite/chr_il_{i}/image.png',f'/sekai-jp-assets/bonds_honor/character/chr_sd_{i:02d}_01/chr_sd_{i:02d}_01.webp']:
   try:
    b=urllib.request.urlopen(host+path,timeout=8).read();from PIL import Image;import io
    im=Image.open(io.BytesIO(b));im.save(f'assets/visitors/chibi_{i}.png');return i,host+path,im.size
   except Exception as e:last=str(e)
 return i,last
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
 for r in ex.map(get,[9,12,29,39,49]):print(r,flush=True)
