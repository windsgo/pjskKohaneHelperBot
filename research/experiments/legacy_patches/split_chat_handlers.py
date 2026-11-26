from pathlib import Path
p=Path('qqbot_server.py');s=p.read_text(encoding='utf-8')
a=s.index('def attachments(');b=s.index('\nclass Connection:',a)
s=s[:a]+'''def chat_kind(event):
 if event.get('message_type')=='private' or event.get('notice_type') in ('offline_file','friend_upload','private_upload'):return 'private'
 if event.get('message_type')=='group' or event.get('notice_type')=='group_upload' or event.get('group_id'):return 'group'
 return 'private' if event.get('user_id') else None

def attachments(event):
 if event.get('post_type')=='notice' and event.get('notice_type') in ('group_upload','offline_file','friend_upload','private_upload'):
  yield event.get('file',{})
 elif event.get('post_type')=='message':
  message=event.get('message',event.get('raw_message',[]))
  if isinstance(message,str):
   def unescape(x):return x.replace('&#44;',',').replace('&#91;','[').replace('&#93;',']').replace('&amp;','&')
   for match in re.finditer(r'\\[CQ:file,([^\\]]*)\\]',message):
    yield {k:unescape(v) for part in match[1].split(',') if '=' in part for k,v in [part.split('=',1)]}
  elif isinstance(message,list):
   for segment in message:
    if isinstance(segment,dict) and segment.get('type')=='file':yield segment.get('data',{})
''' +s[b:]
s=s.replace("  if event.get('group_id'):\n   return await self.call('send_group_msg'", "  if chat_kind(event)=='group':\n   return await self.call('send_group_msg'")
s=s.replace("  fid=file.get('id') or file.get('file_id')", "  fid=file.get('id') or file.get('file_id') or file.get('file')")
s=s.replace("  if event.get('group_id'):\n   params=", "  if chat_kind(event)=='group':\n   params=")
s=s.replace("  else:attempts.append(('get_private_file_url',{'file_id':fid}))", "  elif getattr(self.config,'adapter','onebot')!='openqq':attempts.append(('get_private_file_url',{'file_id':fid}))")
s=s.replace("    if self.config.groups and str(event.get('group_id','')) not in self.config.groups:continue", "    kind=chat_kind(event)\n    if event.get('post_type') in ('message','notice') and kind:\n     LOG.info('Received %s event: post=%s message=%s notice=%s message_format=%s',kind,event.get('post_type'),event.get('message_type'),event.get('notice_type'),type(event.get('message')).__name__)\n    if kind=='group' and self.config.groups and str(event.get('group_id','')) not in self.config.groups:continue")
s=s.replace("     name=str(file.get('name') or file.get('file_name') or '')\n     if not PATTERN.match(name):continue", "     file=dict(file)\n     name=str(file.get('name') or file.get('file_name') or file.get('filename') or file.get('file') or '')\n     if not PATTERN.match(name):\n      LOG.info('Ignored %s attachment: name=%r keys=%s',kind,name[:140],','.join(file));continue\n     file['name']=name\n     if not (file.get('id') or file.get('file_id') or file.get('file')):file['id']=name\n     LOG.info('Queueing %s file: %s',kind,name)")
p.write_text(s,encoding='utf-8')
