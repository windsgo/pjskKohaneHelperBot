from pathlib import Path
p=Path('render_compact_report.py');s=p.read_text(encoding='utf-8');s=s.replace('ICONS={}',"NEEDED={(d[0],d[1]) for site in U['userMysekaiHarvestMaps'] for d in site[2]}\nICONS={}",1)
s=s.replace('  if key in ICONS:continue','  if key in ICONS or key not in NEEDED:continue')
s=s.replace("  ICONS[(typ,int(path.stem))]=Image.open(path).convert('RGBA')", "  key=(typ,int(path.stem))\n  if key in NEEDED:ICONS[key]=Image.open(path).convert('RGBA')")
s=s.replace("for rid,record in RECORDS.items():\n cover=", "for rid,record in RECORDS.items():\n if ('mysekai_music_record',rid) not in NEEDED:continue\n cover=")
p.write_text(s,encoding='utf-8')
