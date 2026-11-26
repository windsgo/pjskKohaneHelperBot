import urllib.request,json
from pathlib import Path
urls={'lunabot_asset.py':'https://raw.githubusercontent.com/StarMoe-org/lunabot/master/src/plugins/sekai/asset.py','lunabot_profile.py':'https://raw.githubusercontent.com/StarMoe-org/lunabot/master/src/plugins/sekai/modules/profile.py','mapper_tree.json':'https://api.github.com/repos/mouse233/MySekaiMapper/git/trees/main?recursive=1','materials_cn.json':'https://metadata.pjsk.moe/cn/master/mysekaiMaterials.json'}
for name,url in urls.items():
 try:
  data=urllib.request.urlopen(url,timeout=15).read(); Path(name).write_bytes(data); print(name,len(data))
 except Exception as e: print(name,str(e))
