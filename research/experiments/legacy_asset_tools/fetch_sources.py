import urllib.request,json
from pathlib import Path
urls={'lunabot_tree.json':'https://api.github.com/repos/StarMoe-org/lunabot/git/trees/master?recursive=1','materials_jp.json':'https://raw.githubusercontent.com/Sekai-World/sekai-master-db-diff/main/mysekaiMaterials.json','materials_cn.json':'https://raw.githubusercontent.com/Sekai-World/sekai-master-db-cn/main/mysekaiMaterials.json'}
for name,url in urls.items():
 try:
  data=urllib.request.urlopen(url,timeout=15).read(); Path(name).write_bytes(data); print(name,len(data))
 except Exception as e: print(name,str(e))
