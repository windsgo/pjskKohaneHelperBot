import urllib.request,json,concurrent.futures,zipfile,io
from pathlib import Path
packages={'aiohttp':'3.11.18','aiohappyeyeballs':'2.6.1','aiosignal':'1.3.2','attrs':'25.3.0','frozenlist':'1.6.0','multidict':'6.4.3','propcache':'0.3.1','yarl':'1.20.0','idna':'3.10','typing_extensions':'4.13.2'}
def get(pair):
 name,version=pair
 try:
  data=json.load(urllib.request.urlopen(f'https://pypi.org/pypi/{name}/{version}/json',timeout=25))
  wheels=[x for x in data['urls'] if x['filename'].endswith('.whl')]
  wheel=next((x for x in wheels if 'cp312-cp312-win_amd64' in x['filename']),None) or next(x for x in wheels if 'none-any.whl' in x['filename'])
  b=urllib.request.urlopen(wheel['url'],timeout=30).read()
  import hashlib
  assert hashlib.sha256(b).hexdigest()==wheel['digests']['sha256']
  zipfile.ZipFile(io.BytesIO(b)).extractall('vendor');return name,'OK'
 except Exception as e:return name,str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
 for r in ex.map(get,packages.items()):print(r,flush=True)


