import urllib.request
from pathlib import Path
u='https://raw.githubusercontent.com/mouse233/MySekaiMapper/refs/heads/main/internal/mapper/card.go'
try:
 b=urllib.request.urlopen(u,timeout=15).read();Path('mapper_card.go').write_bytes(b);print(b.decode()[:9000])
except Exception as e:print(e)
