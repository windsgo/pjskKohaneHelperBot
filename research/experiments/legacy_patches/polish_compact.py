from pathlib import Path
p=Path('render_compact_report.py');s=p.read_text(encoding='utf-8-sig')
s=s.replace('(1400,1660)','(1400,1720)').replace('(18,18,1382,1642)','(18,18,1382,1702)')
s=s.replace('(34,y,1366,y+293)','(34,y,1366,y+(350 if s==8 else 293))').replace('(48,1592)','(48,1660)')
s=s.replace("'特殊关注：电池、钻石、四叶草、夕桐以红框与 ★ 标记'", "'★ 特殊掉落：'+ '  ·  '.join(f'{M[i][\"name\"]} ×{TOTAL[(\"mysekai_material\",i)]}' for i in [17,12,20,5])")
p.write_text(s,encoding='utf-8')
