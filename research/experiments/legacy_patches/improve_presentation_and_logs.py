from pathlib import Path
p=Path('render_compact_report.py');s=p.read_text(encoding='utf-8')
s=s.replace('import os,json,csv','from functools import lru_cache\nimport os,json,csv')
s=s.replace('def f(n,bold=False):','@lru_cache(maxsize=32)\ndef f(n,bold=False):')
s=s.replace('SPECIAL={5,12,17,20}', '''# Catalog downloads take precedence; the old library remains a fallback.
for typ in TABLES:
 for path in (B/'assets/catalog'/typ).glob('*.png'):
  ICONS[(typ,int(path.stem))]=Image.open(path).convert('RGBA')
RECORDS={r['id']:r for r in load('mysekaiMusicRecords')}
for rid,record in RECORDS.items():
 cover=B/'assets/catalog/music'/f'{record.get("externalId",0)}.png'
 if record.get('mysekaiMusicTrackType')=='music' and cover.exists():ICONS[('mysekai_music_record',rid)]=Image.open(cover).convert('RGBA')
SPECIAL={5,12,17,20}''')
s=s.replace(" im=Image.new('RGB',(1400,1720),'#edf2fc');dr=ImageDraw.Draw(im)", " heights=[max(286,108+math.ceil(len(SITES[s]['counts'])/5)*63) for s in [5,6,7,8]]\n total_height=339+sum(heights)+18*3+90\n im=Image.new('RGB',(1400,total_height),'#edf2fc');dr=ImageDraw.Draw(im)")
s=s.replace('(18,18,1382,1702)','(18,18,1382,total_height-18)')
s=s.replace("dr.rounded_rectangle((34,34,1366,320),24,fill='#7186b1')", "dr.rounded_rectangle((34,38,1366,324),24,fill='#ccd5e8')\n dr.rounded_rectangle((34,34,1366,320),24,fill='#7186b1')")
s=s.replace('  x=60+i*139','  step=min(139,720/max(1,len(visitors)));x=60+int(i*step);cell=int(step)-8')
s=s.replace("portrait=B/'assets/visitors'/f'chibi_{v[\"unit_id\"]}.png'", "portrait=B/'assets/catalog/visitors'/f'{v[\"unit_id\"]}.png'\n  if not portrait.exists():portrait=B/'assets/visitors'/f'chibi_{v[\"unit_id\"]}.png'")
s=s.replace('(96,78)','(min(96,cell),78)').replace('(130-avatar.width)//2','(cell-avatar.width)//2').replace("(130-dr.textbbox((0,0),v['name'],font=f(15))[2])//2","(cell-dr.textbbox((0,0),v['name'],font=f(15))[2])//2")
s=s.replace(' for j,s in enumerate([5,6,7,8]):\n  y=339+j*310; info=SITES[s]', ' y=339\n for j,s in enumerate([5,6,7,8]):\n  info=SITES[s];card_height=heights[j]')
s=s.replace('(34,y,1366,y+(350 if s==8 else 293))','(34,y,1366,y+card_height)')
s=s.replace("im.paste(bg,(57,y+38))", "mask=Image.new('L',bg.size,0);ImageDraw.Draw(mask).rounded_rectangle((0,0,bg.width-1,bg.height-1),12,fill=255);im.paste(bg,(57,y+38),mask)")
s=s.replace(" text(dr,(48,1660)", "  y+=card_height+18\n text(dr,(48,total_height-58)")
s=s.replace("  for dx,dy in [(0,-43),(0,20),(width/2+12,-24),(-width/2-12,-24),(0,-75),(0,50)]:", "  for dx,dy in [(0,-43),(0,20),(width/2+12,-24),(-width/2-12,-24),(0,-75),(0,50),(-55,-65),(55,-65),(-75,35),(75,35)]:")
s=s.replace("dr.line((px,py,ax,ay),fill='#f8fafc',width=1)", "dr.line((px,py,ax,ay),fill='#475569',width=2);dr.line((px,py,ax,ay),fill='#f8fafc',width=1)")
p.write_text(s,encoding='utf-8')
p=Path('qqbot_server.py');s=p.read_text(encoding='utf-8')
pos=s.index('class Connection:')
helper='''def message_summary(event,limit=500):
 message=event.get('message',event.get('raw_message',''))
 if isinstance(message,str):
  if '[CQ:' in message:
   # CQ media can contain URLs/Base64; log only their type and actual text.
   message=re.sub(r'\\[CQ:([^,\\]]+)[^\\]]*\\]',lambda m:'['+m[1]+']',message)
  result=message
 elif isinstance(message,list):
  parts=[]
  for segment in message:
   if not isinstance(segment,dict):continue
   data=segment.get('data') or {};typ=segment.get('type','未知')
   if typ=='text':parts.append(str(data.get('text','')))
   elif typ=='file':parts.append('[文件：'+str(data.get('name') or data.get('file_name') or data.get('filename') or '未提供文件名')+']')
   elif typ=='at':parts.append('@'+str(data.get('qq','')))
   else:parts.append('['+str(typ)+']')
  result=''.join(parts)
 else:result=''
 if not result and event.get('file'):result='[文件：'+str(event['file'].get('name','未知'))+']'
 result=result.replace('\\r','\\\\r').replace('\\n','\\\\n')
 return result[:limit]+('…' if len(result)>limit else '')

'''
s=s[:pos]+helper+s[pos:]
s=s.replace("LOG.info('API request: %s'", "LOG.debug('API request: %s'").replace("LOG.info('API response: %s status=%s retcode=%s'", "LOG.debug('API response: %s status=%s retcode=%s'")
s=s.replace("LOG.info('Received %s event: post=%s message=%s notice=%s message_format=%s',kind,event.get('post_type'),event.get('message_type'),event.get('notice_type'),type(event.get('message')).__name__)", "sender=event.get('sender') or {}\n     LOG.info('收到%s | 群=%s | 发送者=%s(%s) | 内容：%s','私聊' if kind=='private' else '群聊',event.get('group_id','—'),sender.get('card') or sender.get('nickname') or '未知',event.get('user_id','—'),message_summary(event,getattr(self.config,'log_text_limit',500)))")
s=s.replace("LOG.info('Ignored %s attachment: name=%r keys=%s'","LOG.debug('Ignored %s attachment: name=%r keys=%s'")
s=s.replace("LOG.info('Queueing %s file: %s',kind,name)","LOG.info('匹配烤森文件 | %s | 等待任务=%s',name,self.queue.qsize())")
s=s.replace("LOG.info('Job %s: input ready (%s bytes), starting decode/render'", "LOG.info('任务 %s | 已取得文件 %s 字节 | 正在解码绘图'")
s=s.replace("LOG.info('Job %s: render complete, sending five images'", "LOG.info('任务 %s | 绘图完成 | 正在回复五张图片'")
s=s.replace("LOG.info('Job %s: sending %s (%s bytes)'","LOG.debug('Job %s: sending %s (%s bytes)'")
s=s.replace("LOG.info('Job completed: %s'", "LOG.info('任务 %s | 五张图片已全部发送'")
s=s.replace("LOG.warning('Job %s failed: %s: %s'", "LOG.warning('任务 %s | 失败 | %s: %s'")
s=s.replace("LOG.info('Bot connected')", "LOG.info('机器人已连接')").replace("LOG.info('Bot disconnected')", "LOG.info('机器人已断开')")
s=s.replace(" p.add_argument('--host'", " p.add_argument('--debug',action='store_true',help='Show API and protocol details')\n p.add_argument('--log-text-limit',type=int,default=500,help='Maximum received text characters logged')\n p.add_argument('--host'")
s=s.replace("logging.basicConfig(level=logging.INFO", "logging.basicConfig(level=logging.DEBUG if a.debug else logging.INFO")
s=s.replace('shutdown_timeout=5)','shutdown_timeout=5,access_log=None)')
p.write_text(s,encoding='utf-8')
