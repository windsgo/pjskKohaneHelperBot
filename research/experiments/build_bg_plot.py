from pathlib import Path
import json
cfg={5:dict(name='草地',image='grassland',scale=33.333,offset_x=0,offset_y=-40,x_sign=-1,z_sign=-1),6:dict(name='沙滩',image='beach',scale=20.513,offset_x=0,offset_y=80,x_sign=1,z_sign=-1),7:dict(name='花田',image='flowergarden',scale=24.806,offset_x=-62.015,offset_y=20.672,x_sign=-1,z_sign=-1),8:dict(name='遗忘之地',image='memorialplace',scale=21.333,offset_x=0,offset_y=-106.667,x_sign=1,z_sign=-1)}
Path('assets/map_transforms.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf-8')
s=Path('plot_material_icons.py').read_text(encoding='utf-8').replace("OUT=BASE/'decoded'/'icon_maps'","OUT=BASE/'decoded'/'background_maps'")
s=s.replace("COLORS=['#2563eb'", "CONFIG=json.loads((BASE/'assets/map_transforms.json').read_text(encoding='utf-8'))\nCOLORS=['#2563eb'")
s=s.replace("f'场地 {site} · 材料掉落位置'", "f'{CONFIG[str(site)][\"name\"]} · 场地 {site} · 材料掉落位置'")
s=s.replace("'原始坐标：X 向右，Z 向上；未旋转、未镜像。仅统计 before_drop 材料。太空零件图标缺失，使用文字方块。'", "'背景与坐标按地图配置对齐；点为掉落坐标，引线对应图标。太空零件暂用文字方块。'")
a=s.index(' left,top,right,bottom=');b=s.index(' points=[xy(*p)',a)
s=s[:a]+''' c=CONFIG[str(site)]
 bg=Image.open(BASE/'reference/ursekai/img'/f'{c["image"]}.png').convert('RGBA')
 bw,bh=bg.size
 fit=min(2060/bw,1960/bh)
 dw,dh=round(bw*fit),round(bh*fit)
 left=round((SIZE-dw)/2);top=300+round((1960-dh)/2)
 bg=bg.resize((dw,dh),Image.Resampling.LANCZOS)
 im.paste(bg,(left,top),bg)
 def xy(x,z):
  return (left+(bw/2+c['offset_x']+c['x_sign']*x*c['scale'])*fit,
          top+(bh/2+c['offset_y']+c['z_sign']*z*c['scale'])*fit)
 for pos in groups:
  px,py=xy(*pos)
  if not (left<=px<=left+dw and top<=py<=top+dh):
   raise ValueError(f'Point outside background: site {site} {pos}')
''' +s[b:]
Path('plot_background_maps.py').write_text(s,encoding='utf-8')
