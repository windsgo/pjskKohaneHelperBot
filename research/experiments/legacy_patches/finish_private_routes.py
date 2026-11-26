from pathlib import Path
p=Path('qqbot_server.py');s=p.read_text(encoding='utf-8')
a=s.index('  attempts=[]\n',s.index(' async def url'));b=s.index('  errors=[];data={}',a)
s=s[:a]+"  attempts=self.group_file_actions(event,file,fid) if chat_kind(event)=='group' else self.private_file_actions(file,fid)\n"+s[b:]
a=s.index(' async def url(')
methods=''' def private_file_actions(self,file,fid):
  if getattr(self.config,'adapter','onebot')=='openqq':
   key=str(file.get('name') or file.get('file_name') or fid)
   return [('get_file',{'file':key,'file_id':key})]
  return [('get_private_file_url',{'file_id':fid}),('get_file',{'file_id':fid})]
 def group_file_actions(self,event,file,fid):
  actions=[]
  if getattr(self.config,'adapter','onebot')=='openqq':
   key=str(file.get('name') or file.get('file_name') or fid)
   actions.append(('get_file',{'file':key,'file_id':key}))
  params={'group_id':int(event['group_id']),'file_id':fid}
  actions.append(('get_group_file_url',params))
  if file.get('busid') is not None:actions.append(('get_group_file_url',{**params,'busid':file['busid']}))
  if getattr(self.config,'adapter','onebot')!='openqq':actions.append(('get_file',{'file_id':fid}))
  return actions
'''
s=s[:a]+methods+s[a:];p.write_text(s,encoding='utf-8')
s=Path('test_openqq_private.py').read_text(encoding='utf-8').replace("event['message']=[{'type':'file','data':event['file']}]", "event['message']='[CQ:file,file=&#91;428&#93; response_mkcn_test.bin]'")
Path('test_openqq_private_cq.py').write_text(s,encoding='utf-8')
