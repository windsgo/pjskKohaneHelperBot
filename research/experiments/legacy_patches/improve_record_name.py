from pathlib import Path
p=Path('render_compact_report.py');s=p.read_text(encoding='utf-8')
s=s.replace("if k[0]=='mysekai_music_record':return f'唱片 #{k[1]}'", "if k[0]=='mysekai_music_record':\n  rec=next((r for r in load('mysekaiMusicRecords') if r['id']==k[1]),None)\n  musics=json.loads((B/'masterdata/musics.json').read_text(encoding='utf-8')) if (B/'masterdata/musics.json').exists() else []\n  music=next((m for m in musics if rec and m['id']==rec.get('externalId')),None)\n  return '唱片·'+(music.get('infos',[{}])[0].get('title',music['title']) if music else str(k[1]))")
p.write_text(s,encoding='utf-8')
