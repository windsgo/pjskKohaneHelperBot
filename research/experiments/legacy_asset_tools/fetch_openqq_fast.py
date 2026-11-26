import urllib.request,concurrent.futures
from pathlib import Path
names=['src/onebot.mjs','src/actions.mjs','src/media.mjs','docs/actions.md']
def get(n):
 try:
  b=urllib.request.urlopen('https://raw.githubusercontent.com/feijx3/OpenQQ/refs/heads/main/'+n,timeout=12).read();Path('reference/openqq_'+n.split('/')[-1]).write_bytes(b);return n,len(b)
 except Exception as e:return n,str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 for r in ex.map(get,names):print(r,flush=True)
