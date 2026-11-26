import csv,base64,io,json
from pathlib import Path
from PIL import Image
m={x['id']:x for x in json.load(open('materials_cn.json',encoding='utf-8'))}
p=Path('assets/library/icon/Texture2D')
for r in csv.DictReader(open('assets/resourceId.csv',encoding='utf-8-sig')):
 if not r['resourceId'] or int(r['resourceId']) not in m or not r['base64']:continue
 name=m[int(r['resourceId'])]['iconAssetbundleName']+'.png'
 if not (p/name).exists():Image.open(io.BytesIO(base64.b64decode(r['base64']))).save(p/name)
print('local PNG assets',len(list(Path('assets').rglob('*.png'))))
