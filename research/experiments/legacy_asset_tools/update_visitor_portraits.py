from pathlib import Path
p=Path('render_compact_report.py');s=p.read_text(encoding='utf-8')
s=s.replace("text(dr,(60,190),'本次到访角色 · '+str(len(visitors))+' 位',17,'#edf3ff')", "text(dr,(620,157),'到访 '+str(len(visitors))+' 位',16,'#edf3ff')")
old="x=60+i*139;dr.rounded_rectangle((x,222,x+130,259),9,fill='#f3f6ff');dr.rectangle((x,231,x+4,250),fill=v['color']);text(dr,(x+10,229),shorten(v['name'],8),16)"
new="""x=60+i*139
  portrait=B/'assets/visitors'/f'chibi_{v["unit_id"]}.png'
  if portrait.exists():
   avatar=Image.open(portrait).convert('RGBA');avatar.thumbnail((96,78),Image.Resampling.LANCZOS);im.paste(avatar,(x+(130-avatar.width)//2,183+(78-avatar.height)),avatar)
  text(dr,(x+max(0,(130-dr.textbbox((0,0),v['name'],font=f(15))[2])//2),261),v['name'],15,'white')"""
assert old in s;s=s.replace(old,new).replace('(60,277)','(60,290)');p.write_text(s,encoding='utf-8')
