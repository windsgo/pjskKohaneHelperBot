"""OneBot v11 reverse-WebSocket receiver for local MySekai rendering."""
import argparse,asyncio,base64,collections,shutil,hmac,json,logging,os,re,sys,time,uuid,platform
from pathlib import Path
from urllib.parse import urlsplit
from sekai_toolkit.common.paths import ROOT, JOBS, STATE
from sekai_toolkit.bot.stamina import StaminaStore
from sekai_toolkit.bot.converter import ConverterStore
from sekai_toolkit.bot.group_settings import GroupSettings
from aiohttp import web,ClientSession,ClientTimeout,WSMsgType
PATTERN=re.compile(r'^\[\d+\]\s*response_mkcn',re.I)
LOG=logging.getLogger('sekai-bot')
GROUP_DECODE_OWNER='1245784195'
COMMAND_PREFIXES=('/', '\\')
COMMAND_ALIASES={
 'help':'help','帮助':'help','-help':'help',
 'status':'status','状态':'status',
 'group_decode':'group_decode','烤森群抓包解析':'group_decode','群聊烤森解码':'group_decode',
 'reply':'reply','烤森解析回复模式':'reply','烤森回复':'reply','sekai_reply':'reply',
 'recall':'recall','自动撤回用户烤森抓包消息':'recall','自动撤回烤森抓包':'recall',
 'stamina':'stamina','火':'stamina',
 'converter':'converter','转换器':'converter',
}
COMMAND_NAMES=tuple(sorted(COMMAND_ALIASES,key=len,reverse=True))

def strip_command_prefix(text):
 value=str(text).strip()
 while value and value[0] in COMMAND_PREFIXES:
  value=value[1:].lstrip()
 return value

def split_command(text):
 value=str(text).strip()
 for name in COMMAND_NAMES:
  if value==name:return COMMAND_ALIASES[name],''
  if value.startswith(name) and len(value)>len(name) and value[len(name)].isspace():
   return COMMAND_ALIASES[name],value[len(name):].strip()
 return None,value

def help_requested(value):
 return str(value).strip().lower() in ('help','-help','帮助')

def command_help_footer():
 return '提示：指令可以带 /、\\ 或不带前缀；群聊里 @机器人 也可以触发。'

def help_text(mode,auto_recall=True,group_decode=True):
 mode_text='私聊上传者' if mode=='private' else '群组'
 return ('【烤森工具箱帮助】\n'
         '地图报告：在群里上传名称以 [数字] response_mkcn 开头的 MySekai 文件，自动返回总览和四张地图。\n'
         '抓包教程：https://upload.sakura-bot.cn/about\n\n'
         '1. 总体状态\n'
         '  状态\n'
         '  状态 help\n\n'
         '2. 全局群抓包解析（仅指定管理 QQ 可修改）\n'
         f'  烤森群抓包解析 开启/关闭/查询（当前：{"开启" if group_decode else "关闭"}）\n'
         '  示例：烤森群抓包解析 查询\n\n'
         '3. 本群烤森回复模式\n'
         f'  烤森解析回复模式 群组/私聊/查询（当前：{mode_text}）\n'
         '  示例：烤森解析回复模式 私聊\n\n'
         '4. 本群自动撤回抓包消息\n'
         f'  自动撤回用户烤森抓包消息 开启/关闭/查询（当前：{"开启" if auto_recall else "关闭"}）\n'
         '  示例：自动撤回用户烤森抓包消息 关闭\n\n'
         '5. 体力提醒\n'
         '  火 最大值 50\n'
         '  火 记录 -cur 23 -min 12\n'
         '  火 查询\n'
         '  火 help\n\n'
         '6. 转换器计时\n'
         '  转换器 -time 22\n'
         '  转换器 查询\n'
         '  转换器 help\n\n'
         '7. 帮助\n'
         '  help\n'
         '  /help\n'
         '  各指令后加 help 或 -help 查看单独帮助。\n\n'
         '命令前缀 /、\\ 可以省略；群聊 @机器人 也可以触发。')

def stamina_help_text():
 return ('【体力提醒帮助】\n'
         '1. 设置体力上限\n'
         '  火 最大值 50\n'
         '  火 最大值 -v 50\n\n'
         '2. 记录当前体力\n'
         '  火 记录 -cur 23 -min 12\n'
         '  火 记录 23 12\n'
         '  -min 表示距下一点体力恢复的分钟数（1–30）。\n\n'
         '3. 查询\n'
         '  火 查询\n\n'
         '4. 提醒规则\n'
         '  每 30 分钟恢复 1 点；满体力前半小时和满时各提醒一次；Bot 关闭期间时间照常流逝。\n\n'
         '5. 发送方式\n'
         '  优先私聊；群聊记录若私聊失败，会在原群 @ 你。\n\n'
         +command_help_footer())

def converter_help_text():
 return ('【转换器计时帮助】\n'
         '1. 设置完成时间\n'
         '  转换器 -time 22\n'
         '  转换器 -计时 22\n'
         '  转换器 22\n'
         '  表示从发送命令起 22 小时后完成；再次设置会覆盖上次时间。\n\n'
         '2. 查询\n'
         '  转换器 查询\n\n'
         '3. 提醒规则\n'
         '  完成前半小时和完成时各提醒一次；Bot 关闭期间时间照常流逝。\n\n'
         '4. 发送方式\n'
         '  优先私聊；群聊记录若私聊失败，会在原群 @ 你。\n\n'
         +command_help_footer())

def status_help_text():
 return ('【状态帮助】\n'
         '  状态        查询协议端名称、版本、在线状态和连接时长\n'
         '  状态 help   显示本帮助\n\n'
         +command_help_footer())

def group_decode_help_text():
 return ('【烤森群抓包解析帮助】\n'
         '  烤森群抓包解析 开启|关闭|查询\n'
         '  只有指定管理 QQ 可以修改全局开关；所有人可查询。\n'
         '  关闭后不再接收群聊抓包文件，已排队但尚未开始的任务会跳过。\n\n'
         +command_help_footer())

def reply_help_text(mode='group'):
 return ('【烤森解析回复模式帮助】\n'
         f'  烤森解析回复模式 群组|私聊|查询（当前：{"私聊上传者" if mode=="private" else "群组"}）\n'
         '  群组：五张图发到群里\n'
         '  私聊：五张图私聊发给上传者\n\n'
         +command_help_footer())

def recall_help_text(auto_recall=True):
 return ('【自动撤回用户烤森抓包消息帮助】\n'
         f'  自动撤回用户烤森抓包消息 开启|关闭|查询（当前：{"开启" if auto_recall else "关闭"}）\n'
         '  仅在机器人有群管理权限时生效。\n\n'
         +command_help_footer())

def parse_toggle(value):
 value=re.sub(r'^(?:-v|--verbose)\s+','',str(value).strip(),flags=re.I).strip().lower()
 if value in ('开启','开','on','true','1'):return True
 if value in ('关闭','关','off','false','0'):return False
 if value in ('查询','query','status'):return 'query'
 return None

def parse_reply_mode(value):
 value=re.sub(r'^(?:-type|--type)\s+','',str(value).strip(),flags=re.I).strip().lower()
 if value in ('群组','群聊','group'):return 'group'
 if value in ('私聊','private'):return 'private'
 if value in ('查询','query','status'):return 'query'
 return None

def command_body(event):
 text=plain_text(event).strip()
 if not text:return None
 explicit=text[0] in COMMAND_PREFIXES
 text=strip_command_prefix(text)
 if not text:return None
 name,_=split_command(text)
 message=event.get('message',event.get('raw_message',''))
 self_id=str(event.get('self_id',''))
 at=False
 if self_id:
  if isinstance(message,list):
   at=any(isinstance(s,dict) and s.get('type')=='at' and str((s.get('data') or {}).get('qq'))==self_id for s in message)
  else:
   at=bool(re.search(r'\[CQ:at,qq='+re.escape(self_id)+r'(?:,|\])',str(message)))
 return text if (explicit or at or name) else None

def duration_text(seconds):
 seconds=max(0,int(seconds))
 days,seconds=divmod(seconds,86400);hours,seconds=divmod(seconds,3600);minutes=seconds//60
 return (f'{days}天 ' if days else '')+f'{hours}小时 {minutes}分钟'

# Known OneBot v11 implementations: probe key -> display name. Only used to label
# status output, never to switch API flows, so an unknown implementation still works.
PROTOCOLS=(('napcat','NapCat'),('openqq','OpenQQ'),('lagrange','Lagrange.Core'),('llonebot','LLOneBot'),('shamrock','Shamrock'),('go-cqhttp','go-cqhttp'))

def detect_protocol(version,status=None,user_agent=''):
 '''Label the OneBot v11 implementation from version info or the WS User-Agent.'''
 def text(value):return str(value).strip() if value not in (None,'') else ''
 if not isinstance(version,dict):version={}
 if not isinstance(status,dict):status={}
 hints=[text(version.get(key)) for key in ('app_name','app','impl','implementation','name')]
 hints.append(text(status.get('app_name')))
 hints.append(text(user_agent))
 blob=' '.join(hints).lower()
 for key,label in PROTOCOLS:
  if key in blob:return label
 app=text(version.get('app_name')) or text(version.get('app')) or text(version.get('impl'))
 if app:return app
 token=re.split(r'[/\s]',text(user_agent))[0] if text(user_agent) else ''
 # Generic HTTP/library user agents say nothing about the implementation.
 if token.lower() in ('aiohttp','python-requests','go-http-client','okhttp','mozilla','curl','node'):return 'OneBot v11'
 return token or 'OneBot v11'

def status_text(status,version,connected_at,protocol_name=''):
 def flag(value):return '是' if value is True else '否' if value is False else '未知'
 if not isinstance(status,dict):status={}
 if not isinstance(version,dict):version={}
 name=protocol_name or detect_protocol(version,status)
 ver=version.get(name.lower()+'_version') or version.get('app_version') or version.get('napcat_version') or version.get('version') or '未知'
 remote_platform=version.get('platform') or status.get('platform')
 remote_arch=version.get('arch') or version.get('architecture') or status.get('arch')
 protocol_version=version.get('protocol_version') or status.get('protocol_version')
 if remote_platform:
  platform_line=f'平台：{remote_platform}'+(f' ({remote_arch})' if remote_arch else '')
 else:
  platform_line=f'Bot 平台：{platform.system().lower()} ({platform.architecture()[0]})'
 uptime=status.get('uptime') or status.get('run_time')
 if isinstance(uptime,(int,float)) and uptime>=0:
  uptime_line=f'{name} 运行时间：'+duration_text(uptime)
 else:
  uptime_line=f'Bot 与 {name} 连续连接：'+duration_text(time.monotonic()-connected_at)
 header=name+' 信息'+(f'（协议 {protocol_version}）' if protocol_version else '')
 return '\n'.join((header,f'版本：{ver}',platform_line,uptime_line,f'在线：{flag(status.get("online"))}｜运行正常：{flag(status.get("good"))}'))

def plain_text(event):
 message=event.get('message',event.get('raw_message',''))
 if isinstance(message,str):return re.sub(r'\[CQ:[^\]]*\]','',message).strip()
 if isinstance(message,list):return ''.join(str(s.get('data',{}).get('text','')) for s in message if isinstance(s,dict) and s.get('type')=='text').strip()
 return ''

def chat_kind(event):
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
   for match in re.finditer(r'\[CQ:file,([^\]]*)\]',message):
    yield {k:unescape(v) for part in match[1].split(',') if '=' in part for k,v in [part.split('=',1)]}
  elif isinstance(message,list):
   for segment in message:
    if isinstance(segment,dict) and segment.get('type')=='file':yield segment.get('data',{})

def message_summary(event,limit=500):
 message=event.get('message',event.get('raw_message',''))
 if isinstance(message,str):
  if '[CQ:' in message:
   # CQ media can contain URLs/Base64; log only their type and actual text.
   message=re.sub(r'\[CQ:([^,\]]+)[^\]]*\]',lambda m:'['+m[1]+']',message)
  result=message
 elif isinstance(message,list):
  parts=[]
  for segment in message:
   if not isinstance(segment,dict):continue
   data=segment.get('data') or {};typ=segment.get('type','未知')
   if typ=='text':parts.append(str(data.get('text','')))
   elif typ=='file':parts.append('[文件：'+str(data.get('name') or data.get('file_name') or data.get('filename') or data.get('file') or '未提供文件名')+']')
   elif typ=='at':parts.append('@'+str(data.get('qq','')))
   else:parts.append('['+str(typ)+']')
  result=''.join(parts)
 else:result=''
 if not result and event.get('file'):result='[文件：'+str(event['file'].get('name','未知'))+']'
 result=result.replace('\r','\\r').replace('\n','\\n')
 return result[:limit]+('…' if len(result)>limit else '')

class Connection:
 def __init__(self,ws,config,semaphore,request=None):
  self.ws=ws;self.config=config;self.semaphore=semaphore;self.pending={};self.queue=asyncio.Queue(maxsize=10);self.seen=collections.OrderedDict();self.uploads={};self.connected_at=time.monotonic()
  self.user_agent=request.headers.get('User-Agent','') if request is not None else ''
  self.protocol_name=None
 def protocol_label(self):return self.protocol_name or detect_protocol({},None,self.user_agent)
 async def refresh_protocol(self):
  '''Query the generic OneBot v11 version API once and remember the implementation name.'''
  if self.protocol_name:return self.protocol_name
  version={}
  try:
   version=await self.call('get_version_info',{})
  except Exception as exc:
   LOG.info('协议端版本查询失败，按连接信息判断协议端：%s',exc)
  self.protocol_name=detect_protocol(version if isinstance(version,dict) else {},None,self.user_agent)
  LOG.info('协议端：%s | 版本信息=%s',self.protocol_name,version if isinstance(version,dict) else '—')
  return self.protocol_name
 def group_preferences(self,event):
  return self.config.group_settings.get(event.get('group_id'))
 async def heartbeat_once(self):
  group_id=int(self.config.heartbeat_group)
  try:
   name=await self.refresh_protocol()
   status=await self.call('get_status',{})
   if not isinstance(status,dict):status={}
   def flag(value):return '是' if value is True else '否' if value is False else '未知'
   message=(f'{name} 在线报告｜在线：{flag(status.get("online"))}｜运行正常：{flag(status.get("good"))}'
            f'｜Bot 连续连接：{duration_text(time.monotonic()-self.connected_at)}')
   await self.call('send_group_msg',{'group_id':group_id,'message':message})
   LOG.info('定期在线报告已发送 | 群=%s | 协议端=%s | 在线=%s | 运行正常=%s',group_id,name,status.get('online'),status.get('good'))
  except Exception as exc:
   LOG.warning('定期在线报告失败 | 群=%s | %s: %s',group_id,type(exc).__name__,exc)
 async def heartbeat_reports(self):
  while True:
   await asyncio.sleep(self.config.heartbeat_minutes*60)
   await self.heartbeat_once()
 async def send_status(self,event):
  name=self.protocol_label()
  try:
   status=await self.call('get_status',{})
   if not isinstance(status,dict):status={}
   try:version=await self.call('get_version_info',{})
   except Exception as exc:
    LOG.warning('版本查询失败 | QQ=%s | %s',event.get('user_id'),exc)
    version={}
   if not isinstance(version,dict):version={}
   name=detect_protocol(version,status,self.user_agent)
   self.protocol_name=name
   message=status_text(status,version,self.connected_at,name)
   LOG.info('状态查询 | QQ=%s | 协议端=%s | online=%s | good=%s | version=%s',event.get('user_id'),name,status.get('online'),status.get('good'),version.get('app_version') or version.get('napcat_version') or version.get('version'))
  except Exception as exc:
   LOG.warning('状态查询失败 | QQ=%s | 协议端=%s | %s',event.get('user_id'),name,exc)
   message=f'{name} 状态查询失败，请查看 Bot 与 {name} 的连接日志。'
  try:await self.send(event,message)
  except Exception as exc:LOG.warning('状态回复失败 | QQ=%s | %s',event.get('user_id'),exc)
 async def stamina_reminders(self):
  while True:
   for qq,cap,group_id,phase in self.config.stamina.due():
    message=f'体力提醒：你的体力将在约半小时后达到 {cap}，记得使用。' if phase=='half' else f'体力提醒：你的体力已达到上限 {cap}，记得使用。'
    try:
     await self.call('send_private_msg',{'user_id':qq,'message':message})
    except Exception as exc:
     if group_id:
      try:await self.call('send_group_msg',{'group_id':group_id,'message':f'[CQ:at,qq={qq}] {message}'})
      except Exception as group_exc:
       LOG.warning('体力提醒发送失败 | QQ=%s | 私聊=%s | 群聊=%s',qq,exc,group_exc)
       continue
     else:
      LOG.warning('体力提醒私聊失败 | QQ=%s | %s',qq,exc)
      continue
    self.config.stamina.mark(qq,phase)
    LOG.info('体力提醒已发送 | QQ=%s | 阶段=%s',qq,phase)
   for qq,group_id,phase in self.config.converter.due():
    message='转换器提醒：约半小时后完成，记得处理。' if phase=='half' else '转换器提醒：转换器已到时间，记得处理。'
    try:
     await self.call('send_private_msg',{'user_id':qq,'message':message})
    except Exception as exc:
     if group_id:
      try:await self.call('send_group_msg',{'group_id':group_id,'message':f'[CQ:at,qq={qq}] {message}'})
      except Exception as group_exc:
       LOG.warning('转换器提醒发送失败 | QQ=%s | 私聊=%s | 群聊=%s',qq,exc,group_exc)
       continue
     else:
      LOG.warning('转换器提醒私聊失败 | QQ=%s | %s',qq,exc)
      continue
    self.config.converter.mark(qq,phase)
    LOG.info('转换器提醒已发送 | QQ=%s | 阶段=%s',qq,phase)
   await asyncio.sleep(30)
 async def call(self,action,params):
  LOG.debug('API request: %s',action)
  echo=uuid.uuid4().hex;future=asyncio.get_running_loop().create_future();self.pending[echo]=future
  try:
   await self.ws.send_json({'action':action,'params':params,'echo':echo})
   reply=await asyncio.wait_for(future,30)
   LOG.debug('API response: %s status=%s retcode=%s',action,reply.get('status'),reply.get('retcode'))
   if reply.get('status')=='failed' or reply.get('retcode',0)!=0:
    detail=reply.get('wording') or reply.get('message') or reply.get('msg') or 'no details'
    raise RuntimeError(f'OneBot API failed: {action}; retcode={reply.get("retcode")}; {detail}')
   return reply.get('data') or {}
  finally:self.pending.pop(echo,None)
 async def send(self,event,message):
  if chat_kind(event)=='group':
   return await self.call('send_group_msg',{'group_id':int(event['group_id']),'message':message})
  return await self.call('send_private_msg',{'user_id':int(event['user_id']),'message':message})
 async def acknowledge_upload(self,event):
  try:
   await self.send(event,'已收到烤森抓包文件，正在解析，请稍候。')
   LOG.info('已发送接收确认 | 发送者=%s | 群=%s',event.get('user_id'),event.get('group_id','—'))
  except Exception as exc:LOG.warning('发送接收确认失败 | 发送者=%s | %s',event.get('user_id'),exc)
 async def notify_private_group(self,event,success):
  if chat_kind(event)!='private':return
  target=getattr(self.config,'notify_group',None)
  if target is None:target=getattr(self.config,'heartbeat_group',0)
  if not target:return
  user=event.get('user_id');prefix=f'[CQ:at,qq={user}] ' if user else ''
  status='私聊烤森抓包已解析完成，五张图已私聊发送。' if success else '私聊烤森抓包解析失败，已私聊告知上传者。'
  try:
   await self.call('send_group_msg',{'group_id':int(target),'message':prefix+status})
   LOG.info('已发送私聊完成群提醒 | 群=%s | 上传者=%s | 成功=%s',target,user,success)
  except Exception as exc:LOG.warning('发送私聊完成群提醒失败 | 群=%s | 上传者=%s | %s',target,user,exc)
 async def send_result(self,event,message,sent_count=0):
  if chat_kind(event)=='group' and self.group_preferences(event)[0]=='private':
   try:
    await self.call('send_private_msg',{'user_id':int(event['user_id']),'message':message})
    return True
   except Exception as exc:
    LOG.warning('无法私聊群文件上传者 %s：%s',event.get('user_id'),exc)
    reason='图片上传失败' if 'rich media transfer failed' in str(exc) else '私聊发送失败'
    await self.send(event,[{'type':'text','data':{'text':f'图片已生成，已向上传者私聊发送 {sent_count}/5 张；第 {sent_count+1} 张{reason}。请检查 {self.protocol_label()} 日志，或在群里发送 烤森解析回复模式 群组。'}}])
    return False
  await self.send(event,message)
  return True
 async def recall_group_upload(self,event,file):
  if chat_kind(event)!='group' or not getattr(self.config,'cleanup_group_files',True) or not self.group_preferences(event)[1]:return
  group_id=int(event['group_id']);self_id=event.get('self_id')
  try:
   if not self_id:raise ValueError('缺少机器人账号 ID')
   member=await self.call('get_group_member_info',{'group_id':group_id,'user_id':int(self_id),'no_cache':True})
   role=member.get('role')
  except Exception as exc:
   LOG.warning('撤回权限查询失败 | 群=%s | %s',group_id,exc)
   role=None
  if role not in ('admin','owner'):
   notice='机器人没有群管理权限，请自行撤回这条抓包文件消息。' if role=='member' else '无法确认机器人群管理权限，请自行撤回这条抓包文件消息。'
   try:await self.call('send_group_msg',{'group_id':group_id,'message':notice})
   except Exception as exc:LOG.warning('撤回提示发送失败 | 群=%s | %s',group_id,exc)
   return
  message_id=file.get('_message_id') or event.get('message_id')
  if not message_id:
   LOG.warning('无法撤回群文件消息 | 群=%s | 文件=%s | 缺少消息ID',group_id,file.get('name'))
   try:await self.call('send_group_msg',{'group_id':group_id,'message':'已收到并解析抓包文件，但未取得消息 ID；请自行撤回文件消息。'})
   except Exception:pass
   return
  try:
   await self.call('delete_msg',{'message_id':message_id})
   LOG.info('已撤回群文件消息 | 群=%s | 消息=%s | 文件=%s',group_id,message_id,file.get('name'))
  except Exception as exc:
   LOG.warning('群文件消息撤回失败 | 群=%s | 消息=%s | %s',group_id,message_id,exc)
   try:await self.call('send_group_msg',{'group_id':group_id,'message':'已收到并解析抓包文件，但自动撤回失败；请自行撤回原文件消息。'})
   except Exception:pass
   return
  try:await self.call('send_group_msg',{'group_id':group_id,'message':'已收到并解析抓包文件，为避免群文件堆积，已自动撤回原文件消息。'})
  except Exception as exc:LOG.warning('撤回成功提示发送失败 | 群=%s | %s',group_id,exc)
 def file_actions(self,file,fid,group_id=None):
  # get_file is the OneBot v11 standard API shared by NapCat and OpenQQ.
  # Both read `file` before `file_id`, but each protocol端 puts a different
  # identifier there (NapCat: encoded id, OpenQQ: file name), so try the value
  # the protocol actually sent first, then the plain file_id, then the name.
  raw=file.get('file');name=str(file.get('name') or file.get('file_name') or '')
  base={'file_id':fid}
  if group_id is not None:base['group_id']=int(group_id)
  candidates=[dict(base)]
  if isinstance(raw,str) and raw and raw!=str(fid):candidates.insert(0,{'file':raw,**base})
  if name and name not in (str(fid),raw if isinstance(raw,str) else None):candidates.append({'file':name,**base})
  # If the event gave no separate id, still try the filename as `file`.
  if isinstance(raw,str) and raw and raw==str(fid):candidates.append({'file':raw,**base})
  unique=[]
  for params in candidates:
   if params not in unique:unique.append(params)
  return [('get_file',params) for params in unique]
 def private_file_actions(self,file,fid):
  return self.file_actions(file,fid)+[('get_private_file_url',{'file_id':fid})]
 def group_file_actions(self,event,file,fid):
  base={'group_id':int(event['group_id']),'file_id':fid,'busid':file.get('busid',102)}
  raw=file.get('file');name=str(file.get('name') or file.get('file_name') or '')
  url_candidates=[dict(base)]
  for value in (raw,name):
   if isinstance(value,str) and value and value!=fid:
    params=dict(base);params['file']=value
    if params not in url_candidates:url_candidates.append(params)
  return ([('get_group_file_url',params) for params in url_candidates]
          +self.file_actions(file,fid,event.get('group_id')))
 async def url(self,event,file):
  direct=file.get('url')
  if isinstance(direct,str) and urlsplit(direct).scheme in ('http','https'):return direct
  for key in ('path','local_path','file_path','file'):
   value=file.get(key)
   if isinstance(value,str):
    local=Path(value)
    if local.is_absolute() and local.is_file():return local
  fid=file.get('id') or file.get('file_id') or file.get('file')
  if not fid:raise ValueError('Missing file id')
  attempts=self.group_file_actions(event,file,fid) if chat_kind(event)=='group' else self.private_file_actions(file,fid)
  errors=[];data={}
  for action,params in attempts:
   try:
    candidate=await self.call(action,params)
    local_path=candidate.get('file')
    if action=='get_file' and isinstance(local_path,str):
     local=Path(local_path)
     if local.is_absolute() and local.is_file():return local
    candidate_url=candidate.get('url') or candidate.get('file_url')
    if isinstance(candidate_url,str) and urlsplit(candidate_url).scheme in ('http','https'):
     data=candidate;break
    errors.append(f'{action}: no HTTP URL returned')
   except (RuntimeError,asyncio.TimeoutError) as exc:
    errors.append(str(exc) or f'{action}: timed out')
  else:raise RuntimeError('Could not obtain file download URL. '+' | '.join(errors))
  if not data:raise RuntimeError('Could not obtain file download URL. '+' | '.join(errors))
  url=data.get('url') or data.get('file_url')
  if not isinstance(url,str) or urlsplit(url).scheme not in ('http','https'):raise ValueError('Bot did not return an HTTP file URL')
  return url
 async def download(self,url,path):
  limit=self.config.max_mb*1024*1024
  if isinstance(url,Path):
   if not 0<url.stat().st_size<=limit:raise ValueError('Local file empty or exceeds size limit')
   await asyncio.to_thread(shutil.copyfile,url,path);return
  async with ClientSession(timeout=ClientTimeout(total=90)) as session:
   async with session.get(url) as response:
    response.raise_for_status()
    if response.content_length and response.content_length>limit:raise ValueError('File exceeds size limit')
    size=0
    with path.open('wb') as target:
     async for chunk in response.content.iter_chunked(65536):
      size+=len(chunk)
      if size>limit:raise ValueError('File exceeds size limit')
      target.write(chunk)
    if size==0:raise ValueError('Empty file')
 async def process(self,event,file):
  job=self.config.output/uuid.uuid4().hex;job.mkdir(parents=True)
  try:
   size=file.get('size',file.get('file_size',0))
   if int(size or 0)>self.config.max_mb*1024*1024:raise ValueError('File exceeds size limit')
   local=None
   cache=getattr(self.config,'file_cache',None)
   if cache:
    name=str(file.get('name') or file.get('file_name') or '')
    if name and '/' not in name and '\\' not in name:
     candidate=(cache/name).resolve()
     if candidate.parent==cache and candidate.is_file():
      actual=candidate.stat().st_size
      if 0<actual<=self.config.max_mb*1024*1024 and (not size or actual==int(size)):local=candidate
   (job/'source.json').write_text(json.dumps({'name':file.get('name') or file.get('file_name'),'id':file.get('id') or file.get('file_id'),'size':size,'source':'configured local cache' if local else 'QQBot download'},ensure_ascii=False,indent=2),encoding='utf-8')
   if local:
    await asyncio.to_thread(shutil.copyfile,local,job/'input.bin');LOG.info('Using configured local cache for job %s',job.name[:8])
   else:await self.download(await self.url(event,file),job/'input.bin')
   LOG.info('任务 %s | 已取得文件 %s 字节 | 正在解码绘图',job.name[:8],(job/'input.bin').stat().st_size)
   env=os.environ.copy();env['PYTHONPATH']=str(ROOT/'src')+os.pathsep+env.get('PYTHONPATH','')
   with (job/'render.log').open('wb') as log:
    proc=await asyncio.create_subprocess_exec(sys.executable,'-m','sekai_toolkit.cli.report',str(job/'input.bin'),'--output',str(job/'result'),'--mode','1+4','--format','png',cwd=ROOT,env=env,stdout=log,stderr=asyncio.subprocess.STDOUT)
    try:code=await asyncio.wait_for(proc.wait(),180)
    except (asyncio.TimeoutError,asyncio.CancelledError):
     proc.kill();await proc.wait();raise
   if code:
    tail=(job/'render.log').read_text(encoding='utf-8',errors='replace').splitlines()[-12:]
    LOG.error('Job %s renderer details:\n%s',job.name[:8],'\n'.join(tail))
    raise RuntimeError('Rendering failed; '+(tail[-1] if tail else 'see render.log'))
   reply_mode=self.group_preferences(event)[0]
   private_target=chat_kind(event)=='private' or reply_mode=='private'
   LOG.info('任务 %s | 绘图完成 | %s | 方式=%s',job.name[:8],'正在分开发送五张图片' if private_target else '正在发送一条含五张图片的消息',reply_mode)
   segments=[]
   for name in ['overview','site_5','site_6','site_7','site_8']:
    path=(job/'result'/f'{name}.png').resolve()
    if not path.is_file():raise FileNotFoundError(path)
    segments.append({'type':'image','data':{'file':str(path)}})
   if private_target:
    delivered=True
    for index,segment in enumerate(segments):
     if not await self.send_result(event,[segment],index):delivered=False;break
    else:LOG.info('任务 %s | 五张图片已分别发送完成',job.name[:8])
   else:
    await self.send_result(event,segments)
    LOG.info('任务 %s | 五图消息发送完成',job.name[:8])
    delivered=True
   if delivered:await self.recall_group_upload(event,file)
   if chat_kind(event)=='private':await self.notify_private_group(event,delivered)
  except asyncio.CancelledError:raise
  except Exception as exc:
   LOG.warning('任务 %s | 失败 | %s: %s',job.name[:8],type(exc).__name__,exc)
   (job/'error.txt').write_text(str(exc),encoding='utf-8')
   if 'Could not obtain file download URL' in str(exc):
    reply='无法取得文件下载地址，烤森解析未开始。请确认协议端已开启文件下载接口并重试；若使用 OpenQQ，请确认已更新到支持群文件下载的版本；其他情况请稍后重试或联系管理员查看日志。'
   else:reply='烤森文件处理失败，请检查文件是否完整或查看本地日志。'
   await self.send(event,[{'type':'text','data':{'text':f'{reply}任务：{job.name[:8]}'}}])
   if chat_kind(event)=='private':await self.notify_private_group(event,False)
 async def worker(self):
  while True:
   event,file=await self.queue.get()
   try:
    if chat_kind(event)=='group' and not self.config.group_settings.group_decode_enabled():
     LOG.info('跳过已排队的群聊烤森文件 | 群=%s | 文件=%s',event.get('group_id'),file.get('name'))
     continue
    async with self.semaphore:await self.process(event,file)
   except asyncio.CancelledError:raise
   except Exception:LOG.exception('Could not deliver job result')
   finally:self.queue.task_done()
 async def receive(self):
  worker=asyncio.create_task(self.worker());self.worker_task=worker
  reminders=asyncio.create_task(self.stamina_reminders())
  heartbeat=asyncio.create_task(self.heartbeat_reports()) if getattr(self.config,'heartbeat_group',0) else None
  try:
   async for msg in self.ws:
    if msg.type!=WSMsgType.TEXT:continue
    try:event=json.loads(msg.data)
    except (ValueError,TypeError):continue
    if not isinstance(event,dict):continue
    echo=event.get('echo')
    if isinstance(echo,str) and echo in self.pending:
     future=self.pending[echo]
     if not future.done():future.set_result(event)
     continue
    kind=chat_kind(event)
    if event.get('post_type') in ('message','notice') and kind:
     sender=event.get('sender') or {}
     LOG.info('收到%s | 群=%s | 发送者=%s(%s) | 内容：%s','私聊' if kind=='private' else '群聊',event.get('group_id','—'),sender.get('card') or sender.get('nickname') or '未知',event.get('user_id','—'),message_summary(event,getattr(self.config,'log_text_limit',500)))
    if kind=='group' and self.config.groups and str(event.get('group_id','')) not in self.config.groups:continue
    if self.config.users and str(event.get('user_id','')) not in self.config.users:continue
    if str(event.get('user_id',''))==str(event.get('self_id','-')):continue
    if event.get('post_type')=='message':
     raw=plain_text(event).strip()
     explicit=bool(raw) and raw[0] in COMMAND_PREFIXES
     command_text=command_body(event)
     if command_text is not None:
      name,arg=split_command(command_text)
      if name=='help':
       target=arg.strip().lower()
       if target in ('火','stamina'):
        text=stamina_help_text()
       elif target in ('转换器','converter'):
        text=converter_help_text()
       elif target in ('状态','status'):
        text=status_help_text()
       elif target in ('群抓包解析','group_decode'):
        text=group_decode_help_text()
       else:
        reply_mode,auto_recall=self.group_preferences(event)
        text=help_text(reply_mode,auto_recall,self.config.group_settings.group_decode_enabled())
       LOG.info('发送使用帮助 | 群=%s | 请求者=%s',event.get('group_id','—'),event.get('user_id','—'))
       asyncio.create_task(self.send(event,text))
       continue
      if name=='status':
       if arg and not help_requested(arg):
        asyncio.create_task(self.send(event,'参数错误：状态不接受参数。\n\n'+status_help_text()))
       elif help_requested(arg):
        asyncio.create_task(self.send(event,status_help_text()))
       else:
        asyncio.create_task(self.send_status(event))
       continue
      if name=='group_decode':
       if not arg or help_requested(arg):
        asyncio.create_task(self.send(event,group_decode_help_text()))
        continue
       value=parse_toggle(arg)
       if value=='query':
        answer='全局烤森群抓包解析：'+('开启' if self.config.group_settings.group_decode_enabled() else '关闭')+'。'
        asyncio.create_task(self.send(event,answer))
       elif value is None:
        asyncio.create_task(self.send(event,'参数错误：烤森群抓包解析只接受 开启/关闭/查询。\n\n'+group_decode_help_text()))
       elif str(event.get('user_id'))!=GROUP_DECODE_OWNER:
        LOG.warning('拒绝修改全局群聊解码 | QQ=%s',event.get('user_id'))
        asyncio.create_task(self.send(event,'只有指定管理 QQ 可以修改全局烤森群抓包解析设置。'))
       else:
        self.config.group_settings.set_group_decode(value)
        LOG.info('全局烤森群抓包解析=%s | 操作者=%s',value,event.get('user_id'))
        asyncio.create_task(self.send(event,'全局烤森群抓包解析已'+('开启。' if value else '关闭。')))
       continue
      if name=='reply':
       if kind!='group':
        asyncio.create_task(self.send(event,'请在群聊中设置/查询烤森解析回复模式。\n\n'+reply_help_text(self.group_preferences(event)[0])))
        continue
       reply_mode,auto_recall=self.group_preferences(event)
       if not arg or help_requested(arg):
        asyncio.create_task(self.send(event,reply_help_text(reply_mode)))
        continue
       value=parse_reply_mode(arg)
       if value=='query':
        asyncio.create_task(self.send(event,f'本群烤森解析回复模式：{"私聊上传者" if reply_mode=="private" else "群组"}。'))
       elif value is None:
        asyncio.create_task(self.send(event,'参数错误：烤森解析回复模式只接受 群组/私聊/查询。\n\n'+reply_help_text(reply_mode)))
       else:
        self.config.group_settings.set_reply(event['group_id'],value)
        self.seen.clear();self.uploads.clear()
        LOG.info('本群回复方式改为 %s | 操作者=%s | 群=%s',value,event.get('user_id'),event.get('group_id','—'))
        asyncio.create_task(self.send(event,'本群烤森解析回复模式已改为'+('群组' if value=='group' else '私聊上传者')+'。'))
       continue
      if name=='recall':
       if kind!='group':
        asyncio.create_task(self.send(event,'请在群聊中设置/查询自动撤回。\n\n'+recall_help_text(self.group_preferences(event)[1])))
        continue
       reply_mode,auto_recall=self.group_preferences(event)
       if not arg or help_requested(arg):
        asyncio.create_task(self.send(event,recall_help_text(auto_recall)))
        continue
       value=parse_toggle(arg)
       if value=='query':
        asyncio.create_task(self.send(event,f'本群自动撤回用户烤森抓包消息：{"开启" if auto_recall else "关闭"}。'))
       elif value is None:
        asyncio.create_task(self.send(event,'参数错误：自动撤回只接受 开启/关闭/查询。\n\n'+recall_help_text(auto_recall)))
       else:
        self.config.group_settings.set_auto_recall(event['group_id'],value)
        LOG.info('本群抓包消息自动撤回=%s | 操作者=%s | 群=%s',value,event.get('user_id'),event.get('group_id','—'))
        asyncio.create_task(self.send(event,'本群自动撤回用户烤森抓包消息已'+('开启。' if value else '关闭。')))
       continue
      if name=='stamina':
       if not arg or help_requested(arg):
        asyncio.create_task(self.send(event,stamina_help_text()))
        continue
       if arg=='查询':
        asyncio.create_task(self.send(event,self.config.stamina.query(int(event['user_id']))))
        continue
       valid=(re.fullmatch(r'最大值\s+(?:-v\s+)?\d+',arg,re.I)
              or re.fullmatch(r'记录\s+(?:(?:-cur\s+\d+\s+-min\s+\d+)|(?:\d+\s+\d+))',arg,re.I))
       if not valid:
        asyncio.create_task(self.send(event,'参数错误：体力指令格式不正确。\n\n'+stamina_help_text()))
        continue
       answer=self.config.stamina.command(int(event['user_id']),int(event['group_id']) if kind=='group' else None,command_text)
       if answer is None:
        asyncio.create_task(self.send(event,'参数错误：体力指令无法识别。\n\n'+stamina_help_text()))
       elif answer.startswith(('用法','请先','当前体力','剩余时间','需要')):
        asyncio.create_task(self.send(event,'参数错误：'+answer+'\n\n'+stamina_help_text()))
       else:
        LOG.info('体力记录 | QQ=%s | 指令=%s | 结果=%s',event['user_id'],command_text,answer)
        asyncio.create_task(self.send(event,answer))
       continue
      if name=='converter':
       if not arg or help_requested(arg):
        asyncio.create_task(self.send(event,converter_help_text()))
        continue
       if arg=='查询':
        asyncio.create_task(self.send(event,self.config.converter.query(int(event['user_id']))))
        continue
       if not re.fullmatch(r'(?:(?:-计时|-time)\s+)?\d+(?:\.\d+)?',arg,re.I):
        asyncio.create_task(self.send(event,'参数错误：转换器指令格式不正确。\n\n'+converter_help_text()))
        continue
       answer=self.config.converter.command(int(event['user_id']),int(event['group_id']) if kind=='group' else None,command_text)
       if answer is None or answer.startswith(('用法','剩余时间','需')):
        asyncio.create_task(self.send(event,'参数错误：'+str(answer or '转换器指令无法识别')+'\n\n'+converter_help_text()))
       else:
        LOG.info('转换器计时 | QQ=%s | 指令=%s | 结果=%s',event['user_id'],command_text,answer)
        asyncio.create_task(self.send(event,answer))
       continue
     if explicit:
      asyncio.create_task(self.send(event,'未知指令：'+command_text+'\n\n'+help_text(*self.group_preferences(event),self.config.group_settings.group_decode_enabled())))
    for file in attachments(event):
     if not isinstance(file,dict):continue
     file=dict(file)
     name=str(file.get('name') or file.get('file_name') or file.get('filename') or file.get('file') or '')
     if not PATTERN.match(name):
      LOG.debug('Ignored %s attachment: name=%r keys=%s',kind,name[:140],','.join(file));continue
     if kind=='group' and not self.config.group_settings.group_decode_enabled():
      LOG.info('群聊烤森解码已关闭，忽略文件 | 群=%s | 文件=%s',event.get('group_id'),name)
      continue
     file['name']=name
     if event.get('message_id'):file['_message_id']=event['message_id']
     if not (file.get('id') or file.get('file_id') or file.get('file')):file['id']=name
     key=(event.get('group_id'),event.get('user_id'),name)
     now=time.monotonic()
     while self.seen and (next(iter(self.seen.values()))<now-5 or len(self.seen)>1000):
      old,_=self.seen.popitem(last=False);self.uploads.pop(old,None)
     if key in self.seen:
      if file.get('_message_id') and key in self.uploads:self.uploads[key]['_message_id']=file['_message_id']
      LOG.info('跳过同次上传的重复事件 | 文件=%s | 群=%s | 发送者=%s',name,event.get('group_id','—'),event.get('user_id','—'))
      continue
     try:
      if self.queue.full():
       asyncio.create_task(self.send(event,'解析队列已满，请稍后再发一次。'))
       LOG.warning('Upload queue full; ignored upload')
       continue
      asyncio.create_task(self.acknowledge_upload(event))
      self.queue.put_nowait((event,file));self.seen[key]=now;self.uploads[key]=file
      LOG.info('已加入绘图队列 | 文件=%s | 等待任务=%s',name,self.queue.qsize())
     except asyncio.QueueFull:
      asyncio.create_task(self.send(event,'解析队列已满，请稍后再发一次。'))
      LOG.warning('Upload queue full; ignored upload')
  finally:
   tasks=[worker,reminders]+([heartbeat] if heartbeat else [])
   for task in tasks:task.cancel()
   await asyncio.gather(*tasks,return_exceptions=True)
   for future in self.pending.values():
    if not future.done():future.cancel()

def create_app(config):
 if not hasattr(config,'group_settings'):config.group_settings=GroupSettings(STATE/'group_settings.sqlite3' if config.output==JOBS else config.output/'group_settings.sqlite3')
 if not hasattr(config,'stamina'):config.stamina=StaminaStore(STATE/'stamina.sqlite3' if config.output==JOBS else config.output/'stamina.sqlite3')
 if not hasattr(config,'converter'):config.converter=ConverterStore(STATE/'stamina.sqlite3' if config.output==JOBS else config.output/'stamina.sqlite3')
 app=web.Application();semaphore=asyncio.Semaphore(1);connections=set()
 async def shutdown(app):
  LOG.info('Stopping: cancelling jobs and closing WebSocket connections')
  for connection in list(connections):
   task=getattr(connection,'worker_task',None)
   if task:task.cancel()
  await asyncio.gather(*(c.ws.close(code=1001,message=b'Server stopping') for c in list(connections)),return_exceptions=True)
  await asyncio.gather(*(c.worker_task for c in list(connections) if hasattr(c,'worker_task')),return_exceptions=True)
  LOG.info('Connections closed; server stopped')
 app.on_shutdown.append(shutdown)
 async def reverse(request):
  token=request.headers.get('Authorization','').removeprefix('Bearer ') or request.query.get('access_token','')
  if config.token and not hmac.compare_digest(token.encode('utf-8'),config.token.encode('utf-8')):raise web.HTTPUnauthorized()
  ws=web.WebSocketResponse(heartbeat=30,max_msg_size=2*1024*1024);await ws.prepare(request)
  connection=Connection(ws,config,semaphore,request);connections.add(connection)
  LOG.info('机器人已连接 | 协议端提示=%s',detect_protocol({},None,request.headers.get('User-Agent','')))
  try:await connection.receive()
  finally:connections.discard(connection);LOG.info('机器人已断开')
  return ws
 app.router.add_get('/onebot/v11/ws',reverse)
 return app

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--debug',action='store_true',help='Show API and protocol details')
 p.add_argument('--log-text-limit',type=int,default=500,help='Maximum received text characters logged')
 p.add_argument('--host',default='127.0.0.1');p.add_argument('--port',type=int,default=8765)
 p.add_argument('--token',default=os.environ.get('SEKAI_BOT_TOKEN',''))
 p.add_argument('--file-cache',type=Path,help='Optional directory containing already downloaded upload files')
 p.add_argument('--no-token',action='store_true',help='Ignore token environment variable (local listening only)')
 p.add_argument('--output',type=Path,default=JOBS);p.add_argument('--max-mb',type=int,default=20)
 p.add_argument('--groups',nargs='*',default=[]);p.add_argument('--users',nargs='*',default=[])
 p.add_argument('--heartbeat-group',type=int,default=2151080494,help='Group for periodic OneBot status reports; 0 disables')
 p.add_argument('--notify-group',type=int,default=None,help='Group for private upload completion notices; default: heartbeat group; 0 disables')
 p.add_argument('--heartbeat-minutes',type=float,default=5,help='Minutes between online reports (default: 5)')
 a=p.parse_args()
 if a.no_token:a.token=''
 if not a.token and a.host not in ('127.0.0.1','::1','localhost'):
  p.error('A token is required when listening beyond this computer')
 if a.max_mb<=0:p.error('--max-mb must be positive')
 if a.heartbeat_group<0:p.error('--heartbeat-group must be nonnegative')
 if a.notify_group is not None and a.notify_group<0:p.error('--notify-group must be nonnegative')
 if a.heartbeat_minutes<=0:p.error('--heartbeat-minutes must be positive')
 if a.file_cache:
  a.file_cache=a.file_cache.resolve()
  if not a.file_cache.is_dir():p.error('--file-cache must be an existing directory')
 a.output=a.output.resolve();a.output.mkdir(parents=True,exist_ok=True)
 try:
  from PIL import Image
  from cryptography.hazmat.primitives.ciphers import Cipher
 except ImportError as exc:
  p.error(f'Missing rendering dependency: {exc}. Run setup.cmd to install requirements into .venv.')
 logging.basicConfig(level=logging.DEBUG if a.debug else logging.INFO,format='%(asctime)s %(levelname)s %(message)s')
 LOG.info('Token authentication: %s', 'enabled' if a.token else 'disabled (local only)')
 web.run_app(create_app(a),host=a.host,port=a.port,shutdown_timeout=5,access_log=None)
if __name__=='__main__':main()
