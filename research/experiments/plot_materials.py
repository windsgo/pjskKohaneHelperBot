"""Draw material drop coordinates with Pillow; no background or coordinate rotation."""
import json,math,collections
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
BASE=Path(__file__).resolve().parent
OUT=BASE/'decoded'/'maps'; OUT.mkdir(exist_ok=True)
DATA=json.loads((BASE/'decoded/material_drops.json').read_text(encoding='utf-8'))
FONT='C:/Windows/Fonts/msyh.ttc'
def font(n): return ImageFont.truetype(FONT,n)
F=font(24); SMALL=font(22); TITLE=font(48); SUB=font(25)
SIZE=2400
COLORS=['#2563eb','#0f766e','#9333ea','#c2410c']
def intersect(a,b):
 return max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
def make(site,color):
 rows=[r for r in DATA if r['site_id']==site]
 groups=collections.defaultdict(collections.Counter)
 for r in rows: groups[(r['x'],r['z'])][(r['material_id'],r['name'])]+=r['quantity']
 im=Image.new('RGB',(SIZE,SIZE),'#f8fafc'); dr=ImageDraw.Draw(im)
 dr.text((80,48),f'场地 {site} · 材料掉落位置',font=TITLE,fill='#0f172a')
 dr.text((80,117),f'{len(groups)} 个材料点位 · {sum(r["quantity"] for r in rows)} 个材料 | 同坐标合并，标签为名称 × 数量',font=SUB,fill='#475569')
 dr.text((80,160),'原始坐标：X 向右，Z 向上；未旋转、未镜像。仅统计 before_drop 材料。',font=SUB,fill='#475569')
 left,top,right,bottom=220,300,2180,2260
 # Same scale and coordinate range for all four maps.
 lo,hi=-35,30
 def xy(x,z):return left+(x-lo)/(hi-lo)*(right-left), bottom-(z-lo)/(hi-lo)*(bottom-top)
 for v in range(-35,31,5):
  px,_=xy(v,0);_,py=xy(0,v)
  dr.line((px,top,px,bottom),fill='#dce4ed',width=2)
  dr.line((left,py,right,py),fill='#dce4ed',width=2)
  dr.text((px-18,bottom+16),str(v),font=SMALL,fill='#64748b')
  dr.text((left-62,py-15),str(v),font=SMALL,fill='#64748b')
 x0,z0=xy(0,0)
 dr.line((x0,top,x0,bottom),fill='#94a3b8',width=3)
 dr.line((left,z0,right,z0),fill='#94a3b8',width=3)
 dr.text((right+30,z0-15),'X',font=SUB,fill='#334155');dr.text((x0-10,top-48),'Z',font=SUB,fill='#334155')
 points=[xy(*p) for p in groups]
 labels=[]
 for pos,materials in groups.items():
  lines=[f'{name} × {count}' for (mid,name),count in sorted(materials.items())]
  w=max(dr.textbbox((0,0),t,font=F)[2] for t in lines)+24;h=len(lines)*34+12
  labels.append((pos,lines,w,h))
 # Large callouts are placed first; choose a nearby free rectangle.
 occupied=[]; placements=[]
 for pos,lines,w,h in sorted(labels,key=lambda t:-t[2]*t[3]):
  px,py=xy(*pos);best=None
  for radius in [18,45,80,120,170,230,300,390,490]:
   for angle in range(0,360,20):
    a=math.radians(angle);cx=px+math.cos(a)*(radius+w/2);cy=py+math.sin(a)*(radius+h/2)
    box=(cx-w/2,cy-h/2,cx+w/2,cy+h/2)
    if box[0]<70 or box[2]>2330 or box[1]<230 or box[3]>2270:continue
    overlap=sum(intersect(box,b) for b in occupied)
    covered=sum(box[0]-9<x<box[2]+9 and box[1]-9<y<box[3]+9 for x,y in points)
    dist=math.hypot(max(box[0]-px,0,px-box[2]),max(box[1]-py,0,py-box[3]))
    score=overlap*1000+covered*100000+dist
    if best is None or score<best[0]:best=(score,box)
   if best and best[0]<100000:break
  if best is None:raise RuntimeError('No label placement')
  box=best[1];occupied.append((box[0]-5,box[1]-5,box[2]+5,box[3]+5));placements.append((pos,lines,box))
 for pos,lines,box in placements:
  px,py=xy(*pos);ax=min(max(px,box[0]),box[2]);ay=min(max(py,box[1]),box[3])
  dr.line((px,py,ax,ay),fill='#94a3b8',width=2)
 for pos,lines,box in placements:
  dr.rounded_rectangle(box,radius=7,fill='white',outline='#cbd5e1',width=2)
  for i,line in enumerate(lines): dr.text((box[0]+12,box[1]+4+34*i),line,font=F,fill='#1e293b')
 for pos in groups:
  px,py=xy(*pos);dr.ellipse((px-7,py-7,px+7,py+7),fill=color,outline='white',width=2)
 dr.text((80,2340),'点的位置为真实坐标；标签经避让排布，用引线对应点位。',font=SMALL,fill='#64748b')
 im.save(OUT/f'site_{site}.png')
 return im
images=[make(s,c) for s,c in zip([5,6,7,8],COLORS)]
overview=Image.new('RGB',(SIZE*2,SIZE*2),'white')
for i,im in enumerate(images):overview.paste(im,((i%2)*SIZE,(i//2)*SIZE))
overview.save(OUT/'all_sites.png')
preview=overview.copy();preview.thumbnail((2000,2000));preview.save(OUT/'preview.png')
print(OUT/'all_sites.png')
