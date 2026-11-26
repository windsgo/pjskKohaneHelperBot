from pathlib import Path
p=Path('download_assets.py');s=p.read_text(encoding='utf-8-sig');s=s.replace("except Exception as e:return {'path':x['path'],'status':'failed','error':str(e)}", "except Exception as e:\n  try:\n   b=urllib.request.urlopen('https://raw.githubusercontent.com/endoretic/ursekai/refs/heads/main/'+x['path'],timeout=a.timeout).read()\n   if len(b)!=x['size']:raise ValueError('size mismatch')\n   path.write_bytes(b);return {'path':x['path'],'status':'downloaded'}\n  except Exception as last:return {'path':x['path'],'status':'failed','error':str(last)}")
p.write_text(s,encoding='utf-8')
import shutil
for directory,prefix in [('assets/report_icons','icon/Texture2D'),('reference/ursekai/img','img')]:
 for q in Path(directory).glob('*.png'):
  dest=Path('assets/library')/prefix/q.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,dest)
