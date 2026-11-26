import urllib.request,json
from pathlib import Path
u='https://api.github.com/repos/feijx3/OpenQQ/git/trees/main?recursive=1'
try:
 b=urllib.request.urlopen(u,timeout=15).read();Path('openqq_tree.json').write_bytes(b);print('\n'.join(x['path'] for x in json.loads(b)['tree'] if any(s in x['path'].lower() for s in ['file','onebot','upload'])))
except Exception as e:print(e)
