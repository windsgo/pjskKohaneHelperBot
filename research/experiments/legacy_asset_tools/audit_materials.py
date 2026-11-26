import json
from pathlib import Path
M=json.load(open('materials_cn.json',encoding='utf-8'));lib=Path('assets/library/icon/Texture2D');missing=[]
for r in M:
 p=lib/(r['iconAssetbundleName']+'.png');p2=lib/f'material{r["id"]}.png'
 if not p.exists() and not p2.exists():missing.append((r['id'],r['iconAssetbundleName']))
print('missing',missing)
