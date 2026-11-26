import json
r=json.load(open('decoded/response.json',encoding='utf-8'))
def walk(x,path=''):
 if isinstance(x,dict):
  for k,v in x.items():
   if any(s in k.lower() for s in ['visit','appearing','staying','characterunit']):print(path+'/'+k,str(v)[:800])
   walk(v,path+'/'+k)
 elif isinstance(x,list):
  for i,v in enumerate(x[:5]):walk(v,path+f'/{i}')
walk(r['updatedResources'])
