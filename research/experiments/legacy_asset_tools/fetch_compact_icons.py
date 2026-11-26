import json,urllib.request,base64,concurrent.futures
from pathlib import Path
t=json.load(open('ursekai_tree.json',encoding='utf-8'))['tree']
names=['item_junk_15.png','item_blueprint_fragment.png','item_surplus_music_record.png']
for rid in [118,119,120,129,480]:
 names.extend(x['path'].split('/')[-1] for x in t if x['path'].startswith('icon/Texture2D/') and x['path'].endswith('_'+str(rid)+'.png'))
def get(n):
 p=Path('assets/report_icons')/n;p.parent.mkdir(exist_ok=True)
 try:
  o=next(x for x in t if x['path']=='icon/Texture2D/'+n)
  b=base64.b64decode(json.load(urllib.request.urlopen(o['url'],timeout=15))['content']);p.write_bytes(b);return n,len(b)
 except Exception as e:return n,str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
 for f in concurrent.futures.as_completed([ex.submit(get,n) for n in names]):print(f.result(),flush=True)
