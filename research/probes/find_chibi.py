import urllib.request,json
from pathlib import Path
u='https://api.github.com/repos/moe-sekai/lunabot/git/trees/main?recursive=1'
try:
 b=urllib.request.urlopen(u,timeout=12).read();Path('moe_tree.json').write_bytes(b); print([x['path'] for x in json.loads(b)['tree'] if 'mysekai' in x['path'].lower()])
except Exception as e:print(e)
