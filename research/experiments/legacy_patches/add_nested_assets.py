from pathlib import Path
p=Path('sync_report_assets.py');s=p.read_text(encoding='utf-8');s=s.replace("if kind in ('mysekai_material','mysekai_item','mysekai_fixture','weather'):paths=", "if kind in ('mysekai_material','mysekai_item','weather'):\n   paths=[p.rsplit('/',1)[0]+'/'+p.rsplit('/',1)[1].rsplit('.',1)[0]+'/'+p.rsplit('/',1)[1] for p in paths]+paths\n  if kind in ('mysekai_material','mysekai_item','mysekai_fixture','weather'):paths=")
p.write_text(s,encoding='utf-8')
