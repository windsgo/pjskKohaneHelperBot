import urllib.request,json
from pathlib import Path
u='https://api.github.com/repos/endoretic/ursekai/git/trees/main?recursive=1'
try:
 b=urllib.request.urlopen(u,timeout=15).read();Path('ursekai_tree.json').write_bytes(b)
 print('\n'.join(x['path'] for x in json.loads(b)['tree'] if any(k in x['path'] for k in ['img/','.js','.py'])))
except Exception as e:print(e)
