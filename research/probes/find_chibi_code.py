import urllib.request,concurrent.futures
from pathlib import Path
urls=['https://raw.githubusercontent.com/moe-sekai/lunabot/master/src/plugins/sekai/modules/mysekai.py','https://raw.githubusercontent.com/moe-sekai/lunabot/main/src/plugins/sekai/modules/mysekai.py','https://raw.githubusercontent.com/StarMoe-org/lunabot/master/src/plugins/sekai/common.py']
def get(u):
 try:
  b=urllib.request.urlopen(u,timeout=12).read();p=Path('reference')/('chibi_'+str(urls.index(u))+'.py');p.write_bytes(b);return str(p),len(b)
 except Exception as e:return str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
 for r in ex.map(get,urls):print(r)
