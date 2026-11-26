import urllib.request
from pathlib import Path
u='https://raw.githubusercontent.com/endoretic/ursekai/refs/heads/main/js/masterdata.js'
try:
 b=urllib.request.urlopen(u,timeout=10).read();s=b.decode();Path('reference/ursekai/js/masterdata.js').write_bytes(b);print(s[:1800])
except Exception as e:print(e)
