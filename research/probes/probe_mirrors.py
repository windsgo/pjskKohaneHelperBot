import urllib.request,json,zipfile,io,hashlib
from pathlib import Path
for host in ['https://pypi.mirrors.ustc.edu.cn','https://mirrors.aliyun.com/pypi']:
 try:
  u=host+'/simple/aiohttp/'
  b=urllib.request.urlopen(u,timeout=12).read();print(host,len(b));break
 except Exception as e:print(host,e)
