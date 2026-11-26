import urllib.request,json,concurrent.futures
from pathlib import Path
urls={
'mapper_archive.go':'https://raw.githubusercontent.com/mouse233/MySekaiMapper/main/internal/mapper/archive.go',
'mapper_resources.go':'https://raw.githubusercontent.com/mouse233/MySekaiMapper/main/internal/mapper/resources.go',
'asset_config.yaml':'https://raw.githubusercontent.com/StarMoe-org/lunabot/master/example_config/sekai/asset.yaml',
'materials_cn.json':'https://metadata.exmeaning.com/cn/master/mysekaiMaterials.json',
'lunabot_resbox.py':'https://raw.githubusercontent.com/StarMoe-org/lunabot/master/src/plugins/sekai/modules/resbox.py'}
def fetch(pair):
 n,u=pair
 try:
  b=urllib.request.urlopen(u,timeout=15).read(); Path(n).write_bytes(b); return n,len(b)
 except Exception as e:return n,str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
 for result in ex.map(fetch,urls.items()): print(result)
