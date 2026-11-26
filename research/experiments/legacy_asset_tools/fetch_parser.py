import json,urllib.request,base64
from pathlib import Path
t=json.load(open('ursekai_tree.json',encoding='utf-8'))['tree'];obj=next(x for x in t if x['path']=='js/dataParser.js')
b=base64.b64decode(json.load(urllib.request.urlopen(obj['url'],timeout=12))['content']);Path('reference/ursekai/js/dataParser.js').write_bytes(b)
