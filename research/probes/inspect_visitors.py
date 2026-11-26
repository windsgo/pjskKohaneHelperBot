import json
r=json.load(open('decoded/response.json',encoding='utf-8'))
v=r['userMysekaiGateCharacterVisit'];print('visit fields',v.keys())
for k,val in v.items():
 if k not in ['userMysekaiGateCharacters','mysekaiCharacterTalkWithReadHistories']:print(k,json.dumps(val,ensure_ascii=True)[:4000])
print('gamedata',json.dumps(r['updatedResources'].get('userMysekaiGateSkin'),ensure_ascii=True))
print('icons',[(x['path'],x.get('size')) for x in json.load(open('ursekai_tree.json',encoding='utf-8'))['tree'] if 'junk_15' in x['path']])
