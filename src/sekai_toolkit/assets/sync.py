"""Cache report assets declared by local master data, with resumable manifests."""
import argparse,concurrent.futures,io,json,urllib.request,time
from pathlib import Path
from PIL import Image
from sekai_toolkit.common.paths import ROOT as B
HOST='https://storage.exmeaning.com/sekai-jp-assets/'
def load(n):return json.loads((B/'masterdata'/f'{n}.json').read_text(encoding='utf-8'))
def catalog():
 entries=[]
 def add(kind,rid,name,paths):
  if kind in ('mysekai_material','mysekai_item','weather'):
   paths=[p.rsplit('/',1)[0]+'/'+p.rsplit('/',1)[1].rsplit('.',1)[0]+'/'+p.rsplit('/',1)[1] for p in paths]+paths
  if kind in ('mysekai_material','mysekai_item','mysekai_fixture','weather'):paths=[p.replace('.webp','.png') for p in paths]+paths
  entries.append(dict(kind=kind,id=rid,name=name,urls=[HOST+p for p in paths]))
 for r in load('gameCharacterUnits'):
  n=f'chr_sd_{r["id"]:02d}_01';add('visitors',r['id'],str(r['id']),[f'bonds_honor/character/{n}/{n}.webp'])
 for r in json.loads((B/'masterdata/materials_cn.json').read_text(encoding='utf-8')):
  add('mysekai_material',r['id'],r['name'],[f'mysekai/thumbnail/material/{r["iconAssetbundleName"]}.webp'])
 for r in load('mysekaiItems'):add('mysekai_item',r['id'],r['name'],[f'mysekai/thumbnail/item/{r["iconAssetbundleName"]}.webp'])
 for r in load('mysekaiFixtures'):
  n=r['assetbundleName']+'_1';genre=r.get('mysekaiFixtureMainGenreId');surface={7:'wall',8:'floor'}.get(genre)
  if surface:
   folder='mysekai/thumbnail/surface_appearance';bundle=r['assetbundleName'];n=f'tex_{bundle}_{surface}_appearance_1'
  else:folder='mysekai/thumbnail/fixture';bundle=n
  add('mysekai_fixture',r['id'],r['name'],[f'{folder}/{bundle}/{n}.webp',f'{folder}/{n}.webp'])
 for r in load('musics'):
  n=r.get('assetbundleName',f'jacket_s_{r["id"]:03d}');add('music',r['id'],r['title'],[f'music/jacket/{n}/{n}.webp'])
 for r in load('mysekaiPhenomenas'):add('weather',r['id'],r['name'],[f'mysekai/thumbnail/phenomena/{r["iconAssetbundleName"]}.webp'])
 return entries

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--workers',type=int,default=12);p.add_argument('--timeout',type=int,default=8);p.add_argument('--kinds',nargs='*');a=p.parse_args()
 entries=[r for r in catalog() if not a.kinds or r['kind'] in a.kinds];out=B/'assets/catalog';out.mkdir(exist_ok=True)
 manifest=out/'manifest.json';results={}
 if manifest.exists():results=json.loads(manifest.read_text(encoding='utf-8'))
 def fetch(r):
  path=out/r['kind']/f'{r["id"]}.png';path.parent.mkdir(exist_ok=True)
  if path.exists():
   try:Image.open(path).verify();return {**r,'status':'cached','path':str(path.relative_to(B))}
   except Exception:pass
  errors=[]
  for url in r['urls']:
   try:
    with urllib.request.urlopen(url,timeout=a.timeout) as response:b=response.read()
    image=Image.open(io.BytesIO(b)).convert('RGBA');temp=path.with_suffix('.part');image.save(temp,format='PNG');temp.replace(path)
    return {**r,'status':'ok','source':url,'path':str(path.relative_to(B))}
   except Exception as e:errors.append(str(e))
  return {**r,'status':'missing','errors':errors}
 with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as ex:
  for n,r in enumerate(ex.map(fetch,entries),1):
   results[f'{r["kind"]}:{r["id"]}']=r
   if n%40==0 or n==len(entries):
    manifest.write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8');print(f'素材进度 {n}/{len(entries)}；本轮成功 '+str(sum(v['status']!='missing' for v in results.values())),flush=True)
 print('Manifest:',manifest)
if __name__=='__main__':main()
