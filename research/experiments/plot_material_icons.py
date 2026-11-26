"""Draw material drop coordinates with Pillow; no background or coordinate rotation."""
import json,math,collections
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
BASE=Path(__file__).resolve().parent
OUT=BASE/'decoded'/'icon_maps'; OUT.mkdir(exist_ok=True)
DATA=json.loads((BASE/'decoded/material_drops.json').read_text(encoding='utf-8'))
FONT='C:/Windows/Fonts/msyh.ttc'
def font(n): return ImageFont.truetype(FONT,n)
F=font(24); SMALL=font(22); TITLE=font(48); SUB=font(25)
SIZE=2400
HEIGHT=2760
ICONS={int(p.stem):Image.open(p).convert("RGBA") for p in (BASE/"assets/materials").glob("*.png")}
NAMES={r["material_id"]:r["name"] for r in DATA}
def paste_icon(im,mid,x,y,size=52):
 if mid not in ICONS:
  draw=ImageDraw.Draw(im);draw.rounded_rectangle((x,y,x+size,y+size),radius=6,fill="#e2e8f0",outline="#94a3b8")
  draw.text((x+4,y+size/2-14),"太空" if mid==94 else str(mid),font=font(20),fill="#475569")
  return
 icon=ICONS[mid].copy();icon.thumbnail((size,size),Image.Resampling.LANCZOS)
 im.paste(icon,(int(x+(size-icon.width)/2),int(y+(size-icon.height)/2)),icon)
COLORS=['#2563eb','#0f766e','#9333ea','#c2410c']
def intersect(a,b):
 return max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
def make(site,color):
 rows=[r for r in DATA if r['site_id']==site]
 groups=collections.defaultdict(collections.Counter)
 for r in rows: groups[(r['x'],r['z'])][(r['material_id'],r['name'])]+=r['quantity']
 im=Image.new('RGB',(SIZE,HEIGHT),'#f8fafc'); dr=ImageDraw.Draw(im)
 dr.text((80,48),f'场地 {site} · 材料掉落位置',font=TITLE,fill='#0f172a')
 dr.text((80,117),f'{len(groups)} 个材料点位 · {sum(r["quantity"] for r in rows)} 个材料 | 同坐标合并，标签为材料图标 × 数量',font=SUB,fill='#475569')
 dr.text((80,160),'原始坐标：X 向右，Z 向上；未旋转、未镜像。仅统计 before_drop 材料。太空零件图标缺失，使用文字方块。',font=SUB,fill='#475569')
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
  lines=[(mid,count) for (mid,name),count in sorted(materials.items())]
  w=min(2,len(lines))*120+16;h=math.ceil(len(lines)/2)*62+12
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
  for i,(mid,count) in enumerate(lines):
   ix=box[0]+8+(i%2)*120;iy=box[1]+6+(i//2)*62
   paste_icon(im,mid,ix,iy)
   dr.text((ix+54,iy+12),f'×{count}',font=font(28),fill='#1e293b')
 for pos in groups:
  px,py=xy(*pos);dr.ellipse((px-7,py-7,px+7,py+7),fill=color,outline='white',width=2)
 dr.text((80,2340),'点的位置为真实坐标；标签经避让排布，用引线对应点位。',font=SMALL,fill='#64748b')
 for i,mid in enumerate(sorted(NAMES)):
  lx=65+(i%6)*390;ly=2410+(i//6)*78
  paste_icon(im,mid,lx,ly,60)
  dr.text((lx+68,ly+17),NAMES[mid],font=SMALL,fill='#334155')
 im.save(OUT/f'site_{site}.png')
 return im
images=[make(s,c) for s,c in zip([5,6,7,8],COLORS)]
overview=Image.new('RGB',(SIZE*2,HEIGHT*2),'white')
for i,im in enumerate(images):overview.paste(im,((i%2)*SIZE,(i//2)*HEIGHT))
overview.save(OUT/'all_sites.png')
preview=overview.copy();preview.thumbnail((2000,2000));preview.save(OUT/'preview.png')
print(OUT/'all_sites.png')
