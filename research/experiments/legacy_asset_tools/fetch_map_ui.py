import urllib.request,json,base64
from pathlib import Path
t=json.load(open('ursekai_tree.json',encoding='utf-8'))['tree']
for name in ['js/ui.js','js/state.js']:
 obj=next(x for x in t if x['path']==name)
 try:
  b=base64.b64decode(json.load(urllib.request.urlopen(obj['url'],timeout=15))['content']);Path('reference/ursekai',name).write_bytes(b);print(name,len(b),flush=True)
 except Exception as e:print(e,flush=True)
