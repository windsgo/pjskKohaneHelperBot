import argparse,base64,concurrent.futures,json,urllib.request
from pathlib import Path
B=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description='Cache every available ursekai icon and map; resume existing files')
p.add_argument('--workers',type=int,default=6);p.add_argument('--timeout',type=int,default=20);a=p.parse_args()
t=json.loads((B/'ursekai_tree.json').read_text(encoding='utf-8'))['tree']
entries=[x for x in t if x['path'].startswith(('icon/Texture2D/','img/')) and x['path'].endswith('.png')]
def fetch(x):
 path=B/'assets/library'/x['path'];path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists() and path.stat().st_size==x['size']:return {'path':x['path'],'status':'cached'}
 try:
  r=json.load(urllib.request.urlopen(x['url'],timeout=a.timeout));b=base64.b64decode(r['content'])
  if len(b)!=x['size']:raise ValueError('size mismatch')
  path.write_bytes(b);return {'path':x['path'],'status':'downloaded'}
 except Exception as e:
  try:
   b=urllib.request.urlopen('https://raw.githubusercontent.com/endoretic/ursekai/refs/heads/main/'+x['path'],timeout=a.timeout).read()
   if len(b)!=x['size']:raise ValueError('size mismatch')
   path.write_bytes(b);return {'path':x['path'],'status':'downloaded'}
  except Exception as last:return {'path':x['path'],'status':'failed','error':str(last)}
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as ex:
 for r in ex.map(fetch,entries):results.append(r);print(r['status'],r['path'],flush=True)
(B/'assets/download_manifest.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
