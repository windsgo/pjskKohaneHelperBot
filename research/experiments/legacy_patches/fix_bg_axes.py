import json
from pathlib import Path
p=Path('assets/map_transforms.json');c=json.loads(p.read_text(encoding='utf-8'))
for k,v in c.items():v['swap_axes']=k in ['5','7']
p.write_text(json.dumps(c,ensure_ascii=False,indent=2),encoding='utf-8')
p=Path('plot_background_maps.py');s=p.read_text(encoding='utf-8').replace(' def xy(x,z):\n  return',' def xy(x,z):\n  if c["swap_axes"]: x,z=z,x\n  return');p.write_text(s,encoding='utf-8')
