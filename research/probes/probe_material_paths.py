import urllib.request,concurrent.futures
paths=['mysekai/thumbnail/material/item_wood_1/item_wood_1.png','mysekai/thumbnail/material/material1.png','mysekai/thumbnail/material/item_memoria_1/item_memoria_1.png','mysekai/thumbnail/material/material35.png','mysekai/thumbnail/item/item_blueprint_fragment/item_blueprint_fragment.png','mysekai/thumbnail/material/item_wood_1_rip/item_wood_1.png']
def get(p):
 try:
  r=urllib.request.urlopen('https://storage.exmeaning.com/sekai-jp-assets/'+p,timeout=6);b=r.read();return p,len(b)
 except Exception as e:return p,str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
 for x in ex.map(get,paths):print(x,flush=True)
