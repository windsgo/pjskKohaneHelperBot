import json
for name,ids in [('mysekaiGameCharacterUnitGroups',[9,12,29,39,49,1313,1782]),('gameCharacterUnits',[9,12,29,39,49])]:
 data=json.load(open('masterdata/'+name+'.json',encoding='utf-8'));print(name)
 for r in data:
  if r['id'] in ids: print(json.dumps(r,ensure_ascii=True))
r=json.load(open('decoded/response.json',encoding='utf-8'))
print('talk len',len(r['userMysekaiGateCharacterVisit']['mysekaiCharacterTalkWithReadHistories']))
