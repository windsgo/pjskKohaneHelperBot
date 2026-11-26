import json,collections
r=json.load(open('decoded/harvest_maps.json',encoding='utf-8'));print(collections.Counter((d[0],d[1]) for s in r for d in s[2] if d[0]!='mysekai_material'))
for name in ['mysekaiItems','mysekaiFixtures','mysekaiMusicRecords','gameCharacters']:
 try:
  t=json.load(open('masterdata/'+name+'.json',encoding='utf-8'));print(name,json.dumps(t[:2],ensure_ascii=True)[:1300])
 except:pass
paths=[x['path'] for x in json.load(open('ursekai_tree.json',encoding='utf-8'))['tree'] if x['path'].startswith('icon/Texture2D/')];print(paths[:35])
