import urllib.request,concurrent.futures
from pathlib import Path
urls={'mapper_render.go':'https://raw.githubusercontent.com/mouse233/MySekaiMapper/main/internal/mapper/render.go','mapper_layout.go':'https://raw.githubusercontent.com/mouse233/MySekaiMapper/main/internal/mapper/layout.go','asset_config.yaml':'https://raw.githubusercontent.com/StarMoe-org/lunabot/master/example_config/sekai/asset.yaml'}
def get(p):
 n,u=p
 try:b=urllib.request.urlopen(u,timeout=20).read();Path(n).write_bytes(b);return n,len(b)
 except Exception as e:return n,str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as e:
 for r in e.map(get,urls.items()):print(r,flush=True)
