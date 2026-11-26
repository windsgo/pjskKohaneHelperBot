import urllib.request,concurrent.futures,json,base64
from pathlib import Path
names=['mysekaiPhenomenas','mysekaiGates','mysekaiGameCharacterUnitGroups','mysekaiCharacterTalks','gameCharacterUnits','gameCharacters','mysekaiRefreshTimePeriods','mysekaiItems','mysekaiFixtures','mysekaiMusicRecords']
def get(n):
 p=Path('masterdata')/(n+'.json');p.parent.mkdir(exist_ok=True)
 try:
  b=urllib.request.urlopen(f'https://metadata.exmeaning.com/cn/master/{n}.json',timeout=12).read();json.loads(b);p.write_bytes(b);return n,len(b)
 except Exception as e:return n,str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as e:
 for f in concurrent.futures.as_completed([e.submit(get,n) for n in names]):print(f.result(),flush=True)
