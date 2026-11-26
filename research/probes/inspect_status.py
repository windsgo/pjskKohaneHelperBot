import json
r=json.load(open('decoded/response.json',encoding='utf-8'))
for k,v in r.items():
 if k!='updatedResources':print(k,json.dumps(v,ensure_ascii=True)[:4000])
u=r['updatedResources']
for k in ['now','userMysekaiGamedata','userMysekaiGates','userMysekaiGateCommonInfo','userMysekaiGateCharacters','userMysekaiPhenomenas']:
 print(k,json.dumps(u.get(k),ensure_ascii=True)[:7000])
