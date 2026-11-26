import urllib.request,concurrent.futures,time
from pathlib import Path
names=['beach','flowergarden','grassland','memorialplace']
def get(n):
 u=f'https://cdn.jsdelivr.net/gh/endoretic/ursekai@main/img/{n}.png'
 try:
  with urllib.request.urlopen(u,timeout=15) as r:
   chunks=[];size=0;start=time.monotonic()
   while True:
    b=r.read(65536)
    if not b:break
    chunks.append(b);size+=len(b)
    if time.monotonic()-start>60:raise TimeoutError(f'total timeout {size} bytes')
   p=Path('reference/ursekai/img')/f'{n}.png';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b''.join(chunks));return n,size
 except Exception as e:return n,str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as e:
 for f in concurrent.futures.as_completed([e.submit(get,n) for n in names]):print(f.result(),flush=True)
