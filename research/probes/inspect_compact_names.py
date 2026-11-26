import json
for n in ['mysekaiFixtures','mysekaiItems','mysekaiPhenomenas']:
 d=json.load(open('masterdata/'+n+'.json',encoding='utf-8'))
 print(n,json.dumps([x for x in d if x['id'] in ([118,119,120,129,480] if n=='mysekaiFixtures' else [7] if n=='mysekaiItems' else [3,10,14,6])],ensure_ascii=True)[:6000])
