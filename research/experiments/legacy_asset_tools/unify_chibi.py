import urllib.request,io
from PIL import Image
for i in [9,12]:
 n=f'chr_sd_{i:02d}_01';u=f'https://storage.exmeaning.com/sekai-jp-assets/bonds_honor/character/{n}/{n}.webp'
 try:
  b=urllib.request.urlopen(u,timeout=10).read();Image.open(io.BytesIO(b)).save(f'assets/visitors/chibi_{i}.png');print(i,'OK')
 except Exception as e:print(e)
