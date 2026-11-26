from pathlib import Path
p=Path('sync_report_assets.py');s=p.read_text(encoding='utf-8');s=s.replace("def add(kind,rid,name,paths):entries.append(dict(kind=kind,id=rid,name=name,urls=[HOST+p for p in paths]))", "def add(kind,rid,name,paths):\n  if kind in ('mysekai_material','mysekai_item','mysekai_fixture','weather'):paths=[p.replace('.webp','.png') for p in paths]+paths\n  entries.append(dict(kind=kind,id=rid,name=name,urls=[HOST+p for p in paths]))")
p.write_text(s,encoding='utf-8')
