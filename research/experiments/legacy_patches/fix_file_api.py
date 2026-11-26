from pathlib import Path
p=Path('qqbot_server.py');s=p.read_text(encoding='utf-8')
s=s.replace("if reply.get('status')=='failed' or reply.get('retcode',0)!=0:raise RuntimeError(f'OneBot API failed: {action}')", "if reply.get('status')=='failed' or reply.get('retcode',0)!=0:\n    detail=reply.get('wording') or reply.get('message') or reply.get('msg') or 'no details'\n    raise RuntimeError(f'OneBot API failed: {action}; retcode={reply.get(\"retcode\")}; {detail}')")
a=s.index("  if event.get('group_id'):\n   data=await self.call('get_group_file_url'");b=s.index('  url=data.get',a)
s=s[:a]+'''  attempts=[]
  if event.get('group_id'):
   params={'group_id':int(event['group_id']),'file_id':fid}
   attempts.append(('get_group_file_url',params))
   if file.get('busid') is not None:attempts.append(('get_group_file_url',{**params,'busid':file['busid']}))
  else:attempts.append(('get_private_file_url',{'file_id':fid}))
  attempts.append(('get_file',{'file_id':fid}))
  errors=[];data={}
  for action,params in attempts:
   try:
    candidate=await self.call(action,params)
    candidate_url=candidate.get('url') or candidate.get('file_url')
    if isinstance(candidate_url,str) and urlsplit(candidate_url).scheme in ('http','https'):
     data=candidate;break
    errors.append(f'{action}: no HTTP URL returned')
   except (RuntimeError,asyncio.TimeoutError) as exc:
    errors.append(str(exc) or f'{action}: timed out')
  else:raise RuntimeError('Could not obtain file download URL. '+' | '.join(errors))
''' +s[b:]
s=s.replace("LOG.warning('Job %s failed: %s',job.name,type(exc).__name__)","LOG.warning('Job %s failed: %s: %s',job.name,type(exc).__name__,exc)")
p.write_text(s,encoding='utf-8')
p=Path('test_qqbot_flow.py');s=p.read_text(encoding='utf-8-sig');s=s.replace("if message['action']=='get_group_file_url':data={'url':f'http://127.0.0.1:{fp}/sample'}", "if message['action']=='get_group_file_url':\n      await ws.send_json({'status':'failed','retcode':1200,'wording':'mock incompatible group-file API','echo':message['echo']});continue\n     elif message['action']=='get_file':data={'url':f'http://127.0.0.1:{fp}/sample'}")
s=s.replace("assert actions.count('get_group_file_url')==1","assert actions.count('get_group_file_url')==2\n    assert actions.count('get_file')==1")
Path('test_qqbot_file_fallback.py').write_text(s,encoding='utf-8')
