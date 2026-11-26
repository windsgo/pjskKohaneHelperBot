from pathlib import Path
p=Path('qqbot_server.py');s=p.read_text(encoding='utf-8');s=s.replace('import argparse,asyncio,base64,collections','import argparse,asyncio,base64,collections,shutil')
s=s.replace("    errors.append(str(exc) or f'{action}: timed out')", "    errors.append(str(exc) or f'{action}: timed out')\n    if isinstance(exc,asyncio.TimeoutError) or 'retcode=1501' in str(exc) or '超时' in str(exc):break")
s=s.replace("  url=data.get('url') or data.get('file_url')", "  if not data:raise RuntimeError('Could not obtain file download URL. '+' | '.join(errors))\n  url=data.get('url') or data.get('file_url')")
s=s.replace("   await self.download(await self.url(event,file),job/'input.bin')", """   local=None
   cache=getattr(self.config,'file_cache',None)
   if cache:
    name=str(file.get('name') or file.get('file_name') or '')
    if name and '/' not in name and '\\\\' not in name:
     candidate=(cache/name).resolve()
     if candidate.parent==cache and candidate.is_file():
      actual=candidate.stat().st_size
      if 0<actual<=self.config.max_mb*1024*1024 and (not size or actual==int(size)):local=candidate
   (job/'source.json').write_text(json.dumps({'name':file.get('name') or file.get('file_name'),'id':file.get('id') or file.get('file_id'),'size':size,'source':'configured local cache' if local else 'QQBot download'},ensure_ascii=False,indent=2),encoding='utf-8')
   if local:
    await asyncio.to_thread(shutil.copyfile,local,job/'input.bin');LOG.info('Using configured local cache for job %s',job.name)
   else:await self.download(await self.url(event,file),job/'input.bin')""")
s=s.replace(" p.add_argument('--no-token'", " p.add_argument('--file-cache',type=Path,help='Optional directory containing already downloaded upload files')\n p.add_argument('--no-token'")
s=s.replace(' a.output=a.output.resolve();'," if a.file_cache:\n  a.file_cache=a.file_cache.resolve()\n  if not a.file_cache.is_dir():p.error('--file-cache must be an existing directory')\n a.output=a.output.resolve();")
p.write_text(s,encoding='utf-8')
