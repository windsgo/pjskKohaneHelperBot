"""Create a compact MySekai overview and four annotated maps from decoded response."""
from functools import lru_cache
import os,json,csv,base64,io,math,collections
from pathlib import Path
from datetime import datetime,timedelta,timezone
from PIL import Image,ImageDraw,ImageFont
from sekai_toolkit.common.paths import ROOT as B
O=Path(os.environ.get('SEKAI_RENDER_OUT',str(B/'runtime'/'decoded'/'compact_report')));O.mkdir(parents=True,exist_ok=True)
R=json.loads(Path(os.environ.get('SEKAI_RESPONSE',str(B/'runtime/decoded/response.json'))).read_text(encoding='utf-8'));U=R['updatedResources']
C=json.loads((B/'assets/map_transforms.json').read_text(encoding='utf-8'))
def load(n):return json.loads((B/'masterdata'/f'{n}.json').read_text(encoding='utf-8'))
M={x['id']:x for x in json.loads((B/'masterdata/materials_cn.json').read_text(encoding='utf-8'))}
TABLES={'mysekai_material':M,'mysekai_item':{x['id']:x for x in load('mysekaiItems')},'mysekai_fixture':{x['id']:x for x in load('mysekaiFixtures')}}
NEEDED={(d[0],d[1]) for site in U['userMysekaiHarvestMaps'] for d in site[2]}
ICONS={}
for r in csv.DictReader((B/'assets/resourceId.csv').open(encoding='utf-8-sig')):
 if r['resourceId'] and r['base64']:
  ICONS[('mysekai_material',int(r['resourceId']))]=Image.open(io.BytesIO(base64.b64decode(r['base64']))).convert('RGBA')
for t,i,n in [('mysekai_material',94,'item_junk_15'),('mysekai_item',7,'item_blueprint_fragment'),('mysekai_music_record',182,'item_surplus_music_record')]:
 ICONS[(t,i)]=Image.open(B/'assets/report_icons'/f'{n}.png').convert('RGBA')
for i in [118,119,120,129,480]:
 p=next((B/'assets/report_icons').glob(f'*_{i}.png'));ICONS[('mysekai_fixture',i)]=Image.open(p).convert('RGBA')
# Resolve all cached resources, not only the first captured sample.
for typ,table in TABLES.items():
 for rid,record in table.items():
  key=(typ,rid)
  if key in ICONS or key not in NEEDED:continue
  base=record.get('iconAssetbundleName')
  candidates=list((B/'assets/library/icon/Texture2D').glob(f'*_{rid}.png')) if typ=='mysekai_fixture' else []
  if base:candidates.insert(0,B/'assets/library/icon/Texture2D'/f'{base}.png')
  for candidate in candidates:
   if candidate.is_file():ICONS[key]=Image.open(candidate).convert('RGBA');break
# Catalog downloads take precedence; the old library remains a fallback.
for typ in TABLES:
 for path in (B/'assets/catalog'/typ).glob('*.png'):
  key=(typ,int(path.stem))
  if key in NEEDED and key not in ICONS:ICONS[key]=Image.open(path).convert('RGBA')
RECORDS={r['id']:r for r in load('mysekaiMusicRecords')}
for rid,record in RECORDS.items():
 if ('mysekai_music_record',rid) not in NEEDED:continue
 cover=B/'assets/catalog/music'/f'{record.get("externalId",0)}.png'
 if record.get('mysekaiMusicTrackType')=='music' and cover.exists():ICONS[('mysekai_music_record',rid)]=Image.open(cover).convert('RGBA')
SPECIAL={5,12,17,20}; PALETTE={'wood':('#158158','#e6f6ec'),'mineral':('#7b56b6','#f0eafa'),'junk':('#267db1','#e7f1fb'),'plant':('#b28720','#fff6d9'),'other':('#69758a','#edf0f5'),'extra':('#4a69ad','#e9edff')}
def style(k):
 t,i=k
 typ=M.get(i,{}).get('mysekaiMaterialType','other') if t=='mysekai_material' else 'extra'
 return PALETTE.get(typ,PALETTE['other'])
def special(k):return k[0]=='mysekai_material' and k[1] in SPECIAL
def abundant_point(k,q):
 if k[0]!='mysekai_material' or q<2:return False
 material=M.get(k[1],{})
 return material.get('mysekaiMaterialType') in ('wood','mineral') or any(word in material.get('name','') for word in ('亚麻','棉花'))
def name(k):
 if k[0]=='mysekai_music_record':
  rec=next((r for r in load('mysekaiMusicRecords') if r['id']==k[1]),None)
  musics=json.loads((B/'masterdata/musics.json').read_text(encoding='utf-8')) if (B/'masterdata/musics.json').exists() else []
  music=next((m for m in musics if rec and m['id']==rec.get('externalId')),None)
  return '唱片·'+(music.get('infos',[{}])[0].get('title',music['title']) if music else str(k[1]))
 return TABLES.get(k[0],{}).get(k[1],{}).get('name',f'{k[0]} #{k[1]}')
def item_size(k):
 if k[0]=='mysekai_music_record':return 48
 if k[0]=='mysekai_fixture' and '唱片' in name(k):return 40
 return 36 if k[0]=='mysekai_material' else 24
@lru_cache(maxsize=32)
def f(n,bold=False):return ImageFont.truetype('C:/Windows/Fonts/msyh'+('bd' if bold else '')+'.ttc',n)
def text(dr,xy,s,n=20,fill='#334155',bold=False):dr.text(xy,str(s),font=f(n,bold),fill=fill)
def icon(im,k,x,y,size):
 ic=ICONS[k].copy();ic.thumbnail((size,size),Image.Resampling.LANCZOS);im.paste(ic,(round(x+(size-ic.width)/2),round(y+(size-ic.height)/2)),ic)
def missing_icon(k):
 typ,rid=k
 colors={'mysekai_material':('#d8eee4','#28785a'),'mysekai_item':('#deebfa','#396b9f'),'mysekai_fixture':('#eee6f8','#7559a1'),'mysekai_music_record':('#f7e7ed','#a45173')}
 fill,ink=colors.get(typ,('#e2e8f0','#475569'))
 tile=Image.new('RGBA',(64,64),fill);draw=ImageDraw.Draw(tile)
 label=str(rid);box=draw.textbbox((0,0),label,font=f(18,True))
 draw.text(((64-(box[2]-box[0]))/2,(64-(box[3]-box[1]))/2-3),label,font=f(18,True),fill=ink)
 return tile
def shorten(s,n):return s if len(s)<=n else s[:n-1]+'…'
SITES={};TOTAL=collections.Counter()
for site,fixtures,drops in U['userMysekaiHarvestMaps']:
 groups=collections.defaultdict(collections.Counter);counts=collections.Counter()
 for d in drops:
  t,i,x,z,hp,seq,status,q=d[:8]
  if status!='before_drop':continue
  k=(t,i)
  if k not in ICONS:
   ICONS[k]=missing_icon(k)
   print(f'缺少素材 {t} #{i}，使用纯色占位图',flush=True)
  groups[(x,z)][k]+=q;counts[k]+=q;TOTAL[k]+=q
 SITES[site]={'groups':groups,'counts':counts,'total':sum(counts.values())}
assert all(q>=0 for q in TOTAL.values())
# Current response visit groups describe single visitors and their talk combinations.
groups={x['id']:x for x in load('mysekaiGameCharacterUnitGroups')};units={x['id']:x for x in load('gameCharacterUnits')};chars={x['id']:x for x in load('gameCharacters')}
visitor_ids=set()
for rec in R['userMysekaiGateCharacterVisit']['userMysekaiGateCharacters']:
 for k,v in groups[rec['mysekaiGameCharacterUnitGroupId']].items():
  if k.startswith('gameCharacterUnitId'):visitor_ids.add(v)
visitors=[]
for uid in sorted(visitor_ids):
 ch=chars[units[uid]['gameCharacterId']];visitors.append({'unit_id':uid,'name':ch.get('firstName','')+ch.get('givenName',''),'color':units[uid]['colorCode']})
gate=next((g for g in U.get('userMysekaiGates',[]) if g.get('isSettingAtHomeSite')),None)
if gate is None:
 gate=R.get('userMysekaiGateCharacterVisit',{}).get('userMysekaiGate')
if gate is None:
 gate=next((g for g in U.get('userMysekaiGates',[]) if g.get('mysekaiGateId')),None)
gate=gate or {}
gate_master=next((g for g in load('mysekaiGates') if g['id']==gate.get('mysekaiGateId')),None) or {}
phen={x['id']:x for x in load('mysekaiPhenomenas')};period={x['id']:x for x in load('mysekaiRefreshTimePeriods')};tz=timezone(timedelta(hours=8))
weather=[]
for w in R['mysekaiPhenomenaSchedules']:
 dt=datetime.fromtimestamp(w['scheduleDate']/1000,tz).replace(hour=0,minute=0,second=0,microsecond=0)+timedelta(hours=period[w['mysekaiRefreshTimePeriodId']]['startHour'])
 weather.append({'time':dt.strftime('%m/%d %H:%M'),'name':phen[w['mysekaiPhenomenaId']]['name'],'id':w['mysekaiPhenomenaId']})
status={'snapshot_time':datetime.fromtimestamp(U['now']/1000,tz).strftime('%Y-%m-%d %H:%M:%S'),'rank':U['userMysekaiGamedata']['mysekaiRank'],'gate_name':gate_master.get('name','大门信息未知'),'gate_id':gate.get('mysekaiGateId'),'gate_level':gate.get('mysekaiGateLevel','?'),'visitors':visitors,'weather':weather}
(O/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8')
NAMES={5:'初始空地',6:'心愿沙滩',7:'烂漫花田',8:'忘却之所'}
def chip(im,dr,k,q,x,y,w=182,h=58):
 border,fill=style(k)
 if special(k):border,fill='#e04c56','#fff0ef'
 dr.rounded_rectangle((x,y,x+w,y+h),12,fill=fill,outline=border,width=4 if special(k) else 1)
 icon(im,k,x+7,y+8,40);text(dr,(x+54,y+6),shorten(name(k),9),15)
 text(dr,(x+54,y+27),f'×{q}'+(' ★' if special(k) else ''),21,'#c43648' if special(k) else border,True)
def overview():
 heights=[max(286,108+math.ceil(len(SITES[s]['counts'])/5)*63) for s in [5,6,7,8]]
 total_height=339+sum(heights)+18*3+90
 im=Image.new('RGB',(1400,total_height),'#edf2fc');dr=ImageDraw.Draw(im)
 dr.rounded_rectangle((18,18,1382,total_height-18),28,outline='#b8c6de',width=2)
 dr.rounded_rectangle((34,38,1366,324),24,fill='#ccd5e8')
 dr.rounded_rectangle((34,34,1366,320),24,fill='#7186b1')
 text(dr,(60,53),'MySekai · 今日采集总览',32,'white',True)
 text(dr,(60,106),f'Lv.{status["rank"]}  ·  数据时间 {status["snapshot_time"]}（北京时间）',18,'#edf3ff')
 text(dr,(60,147),f'{status["gate_name"]}  Lv.{status["gate_level"]}',24,'white',True)
 text(dr,(620,157),'到访 '+str(len(visitors))+' 位',16,'#edf3ff')
 for i,v in enumerate(visitors):
  step=min(139,720/max(1,len(visitors)));x=60+int(i*step);cell=int(step)-8
  portrait=B/'assets/catalog/visitors'/f'{v["unit_id"]}.png'
  if not portrait.exists():portrait=B/'assets/visitors'/f'chibi_{v["unit_id"]}.png'
  if portrait.exists():
   avatar=Image.open(portrait).convert('RGBA');avatar.thumbnail((min(96,cell),78),Image.Resampling.LANCZOS);im.paste(avatar,(x+(cell-avatar.width)//2,183+(78-avatar.height)),avatar)
  text(dr,(x+max(0,(cell-dr.textbbox((0,0),v['name'],font=f(15))[2])//2),261),v['name'],15,'white')
 for i,w in enumerate(weather):
  x=800+(i%2)*268;y=58+(i//2)*91
  dr.rounded_rectangle((x,y,x+250,y+77),15,fill='#e4ecff',outline='white',width=2)
  text(dr,(x+16,y+9),w['time'],18,bold=True);text(dr,(x+16,y+38),w['name'],20)
 text(dr,(60,290),'★ 特殊掉落：'+ '  ·  '.join(f'{M[i]["name"]} ×{TOTAL[("mysekai_material",i)]}' for i in [17,12,20,5]),17,'white')
 y=339
 for j,s in enumerate([5,6,7,8]):
  info=SITES[s];card_height=heights[j]
  dr.rounded_rectangle((34,y,1366,y+card_height),22,fill='#f9fbff',outline='#b8c6de',width=2)
  bg=Image.open(B/'assets/maps'/f'{C[str(s)]["image"]}.png').convert('RGB');bg=bg.crop(map_crop_box(bg,s));bg.thumbnail((240,140),Image.Resampling.LANCZOS);mask=Image.new('L',bg.size,0);ImageDraw.Draw(mask).rounded_rectangle((0,0,bg.width-1,bg.height-1),12,fill=255);im.paste(bg,(57,y+38),mask)
  text(dr,(57,y+188),f'{len(info["groups"])} 个掉落点位',16)
  text(dr,(327,y+17),f'{NAMES[s]}  #{s}',25,bold=True)
  text(dr,(327,y+54),f'总量 {info["total"]} · 种类 {len(info["counts"])}',17,'#64748b')
  for idx,(k,q) in enumerate(sorted(info['counts'].items(),key=lambda x:(-x[1],x[0]))):chip(im,dr,k,q,327+(idx%5)*199,y+88+(idx//5)*63,188,57)
  y+=card_height+18
 text(dr,(48,total_height-58),'总览含全部掉落；地图省略心愿木材/石块。天气来自本次响应，非实时预报。',16,'#64748b')
 im.save(O/'overview.png')
def map_crop_box(image,site=None):
 # Fixed 32:27 map crop (1280x1080 from the 1920x1080 source).
 width,height=image.size
 crop_width=min(width,round(height*32/27))
 crop_height=min(height,round(crop_width*27/32))
 left=max(0,(width-crop_width)//2)
 # 忘却之所的左下角偶尔有掉落紧贴裁切边，整体向左留出 48 px。
 if site is not None and int(site)==8:left=max(0,left-48)
 top=max(0,(height-crop_height)//2)
 return (left,top,left+crop_width,top+crop_height)

def map_image(s):
 c=C[str(s)];source=Image.open(B/'assets/maps'/f'{c["image"]}.png').convert('RGB')
 box=map_crop_box(source,s);crop_left,crop_top=box[0],box[1]
 bg=source.crop(box);bw,bh=bg.size;ow,oh=source.size
 im=bg.copy();dr=ImageDraw.Draw(im)
 info=SITES[s]
 def xy(x,z):
  if c['swap_axes']:x,z=z,x
  return (ow/2+c['offset_x']+c['x_sign']*x*c['scale']-crop_left,
          oh/2+c['offset_y']+c['z_sign']*z*c['scale']-crop_top)
 records=[]
 for pos,items in info['groups'].items():
  filtered=[(k,q) for k,q in items.items() if k not in [('mysekai_material',1),('mysekai_material',6)]]
  if filtered:records.append((pos,sorted(filtered,key=lambda x:(not special(x[0]),x[0][0]!='mysekai_material',x[0][1]))))
 placements=[]
 for pos,items in records:
  px,py=xy(*pos)
  if px < -20 or px > bw+20 or py < -20 or py > bh+20:continue
  sizes=[item_size(k) for k,q in items];width=sum(z+5 for z in sizes)+6;height=max(48,max(sizes)+8)
  # Clamp the icon stack inside the image so a drop near the crop edge does
  # not lose its leftmost/rightmost icon. The anchor remains at the real point.
  left=min(max(4,px-width/2),max(4,bw-width-4))
  top=min(max(20,py-49),max(20,bh-height-4))
  box=(left,top,left+width,top+height)
  placements.append((pos,items,sizes,box))
 for pos,items,sizes,box in placements:
  cx=box[0]+3
  for (k,q),sz in zip(items,sizes):
   border,fill=style(k);sp=special(k)
   if sp:border,fill='#e22e47','#fff0f0'
   cy=box[1]+height-sz-3
   if sp:dr.rounded_rectangle((cx-3,cy-3,cx+sz+3,cy+sz+3),4,fill='#fff0ee',outline=border,width=3)
   else:dr.rounded_rectangle((cx-1,cy-1,cx+sz+1,cy+sz+1),3,fill=fill,outline=border,width=1)
   icon(im,k,cx,cy,sz)
   label=str(q)+('★' if sp else '')
   tw=dr.textbbox((0,0),label,font=f(14,True))[2]
   highlighted=abundant_point(k,q)
   dr.rounded_rectangle((cx-2,cy-11,cx+tw+4,cy+6),3,fill='#fff2f2' if sp or highlighted else 'white')
   text(dr,(cx,cy-12),label,14,'#d3263d' if highlighted else border,True);cx+=sz+5
 # Draw anchors last so dense icon groups cannot cover the actual locations.
 for pos,items,sizes,box in placements:
  px,py=xy(*pos)
  dr.ellipse((px-3.5,py-3.5,px+3.5,py+3.5),fill='white',outline='#334155',width=2)
 im.save(O/f'site_{s}.png')
 # Full data remains available for validation and alternative display choices.
 return im
if __name__=='__main__':
 overview()
 images=[map_image(s) for s in [5,6,7,8]]
 cw,ch=images[0].size
 contact=Image.new('RGB',(cw*2,ch*2),'white')
 for j,im in enumerate(images):contact.paste(im,((j%2)*cw,(j//2)*ch))
 contact.save(O/'maps_preview.png')
 (O/'report_data.json').write_text(json.dumps({'status':status,'site_totals':{s:{'total':i['total'],'types':len(i['counts'])} for s,i in SITES.items()},'special_totals':{M[i]['name']:TOTAL[('mysekai_material',i)] for i in sorted(SPECIAL)}},ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(status,ensure_ascii=True));print('Report generated:',O)
