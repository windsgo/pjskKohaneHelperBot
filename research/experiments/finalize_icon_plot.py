from pathlib import Path
p=Path('plot_material_icons.py');s=p.read_text(encoding='utf-8')
s=s.replace('icon=ICONS[mid].copy();icon.thumbnail', 'if mid not in ICONS:\n  draw=ImageDraw.Draw(im);draw.rounded_rectangle((x,y,x+size,y+size),radius=6,fill="#e2e8f0",outline="#94a3b8")\n  draw.text((x+4,y+size/2-14),"太空" if mid==94 else str(mid),font=font(20),fill="#475569")\n  return\n icon=ICONS[mid].copy();icon.thumbnail')
s=s.replace('仅统计 before_drop 材料。','仅统计 before_drop 材料。太空零件图标缺失，使用文字方块。')
p.write_text(s,encoding='utf-8')
