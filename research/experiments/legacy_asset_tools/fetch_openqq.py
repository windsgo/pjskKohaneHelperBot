import json,urllib.request
from pathlib import Path
t=json.load(open('openqq_tree.json',encoding='utf-8'))['tree'];print([x['path'] for x in t if x['path'].startswith('src/')])
for n in ['src/onebot.mjs','docs/actions.md']:
 try:
  b=urllib.request.urlopen('https://raw.githubusercontent.com/feijx3/OpenQQ/main/'+n,timeout=15).read();Path('reference/openqq_'+n.split('/')[-1]).write_bytes(b)
 except Exception as e:print(e)
