from pathlib import Path
p=Path('render_compact_report.py');s=p.read_text(encoding='utf-8')
a=s.index('SPECIAL=')
s=s[:a]+'''# Resolve all cached resources, not only the first captured sample.
for typ,table in TABLES.items():
 for rid,record in table.items():
  key=(typ,rid)
  if key in ICONS:continue
  base=record.get('iconAssetbundleName')
  candidates=list((B/'assets/library/icon/Texture2D').glob(f'*_{rid}.png')) if typ=='mysekai_fixture' else []
  if base:candidates.insert(0,B/'assets/library/icon/Texture2D'/f'{base}.png')
  for candidate in candidates:
   if candidate.is_file():ICONS[key]=Image.open(candidate).convert('RGBA');break
''' +s[a:]
s=s.replace("typ=M[i].get('mysekaiMaterialType','other')", "typ=M.get(i,{}).get('mysekaiMaterialType','other')")
s=s.replace("return TABLES[k[0]][k[1]]['name']", "return TABLES.get(k[0],{}).get(k[1],{}).get('name',f'{k[0]} #{k[1]}')")
s=s.replace("k=(t,i);assert k in ICONS,(site,k)","k=(t,i)\n  if k not in ICONS:\n   if t=='mysekai_music_record':ICONS[k]=ICONS[('mysekai_music_record',182)]\n   else:\n    placeholder=Image.new('RGBA',(64,64),'#e2e8f0');pd=ImageDraw.Draw(placeholder);pd.text((3,20),str(i),font=f(18),fill='#334155');ICONS[k]=placeholder\n    print(f'WARNING: missing icon {t} #{i}; using labelled placeholder',flush=True)")
s=s.replace('assert sum(TOTAL.values())==661',"assert all(q>=0 for q in TOTAL.values())")
p.write_text(s,encoding='utf-8')
p=Path('qqbot_server.py');s=p.read_text(encoding='utf-8')
s=s.replace("  echo=uuid.uuid4().hex;future=", "  LOG.info('API request: %s',action)\n  echo=uuid.uuid4().hex;future=")
s=s.replace("   reply=await asyncio.wait_for(future,30)","   reply=await asyncio.wait_for(future,30)\n   LOG.info('API response: %s status=%s retcode=%s',action,reply.get('status'),reply.get('retcode'))")
s=s.replace("   env=os.environ.copy();", "   LOG.info('Job %s: input ready (%s bytes), starting decode/render',job.name,(job/'input.bin').stat().st_size)\n   env=os.environ.copy();")
s=s.replace("   if code:raise RuntimeError('Rendering failed; see render.log')", "   if code:\n    tail=(job/'render.log').read_text(encoding='utf-8',errors='replace').splitlines()[-12:]\n    LOG.error('Job %s renderer details:\\n%s',job.name,'\\n'.join(tail))\n    raise RuntimeError('Rendering failed; '+(tail[-1] if tail else 'see render.log'))\n   LOG.info('Job %s: render complete, sending five images',job.name)")
s=s.replace("    await self.send(event,[{'type':'image'", "    LOG.info('Job %s: sending %s (%s bytes)',job.name,name,len(data))\n    await self.send(event,[{'type':'image'")
s=s.replace("  worker=asyncio.create_task(self.worker())", "  worker=asyncio.create_task(self.worker());self.worker_task=worker")
s=s.replace(" app=web.Application();semaphore=asyncio.Semaphore(1)"," app=web.Application();semaphore=asyncio.Semaphore(1);connections=set()\n async def shutdown(app):\n  LOG.info('Stopping: cancelling jobs and closing WebSocket connections')\n  for connection in list(connections):\n   task=getattr(connection,'worker_task',None)\n   if task:task.cancel()\n  await asyncio.gather(*(c.ws.close(code=1001,message=b'Server stopping') for c in list(connections)),return_exceptions=True)\n  await asyncio.gather(*(c.worker_task for c in list(connections) if hasattr(c,'worker_task')),return_exceptions=True)\n  LOG.info('Connections closed; server stopped')\n app.on_shutdown.append(shutdown)")
s=s.replace("  await Connection(ws,config,semaphore).receive();return ws", "  connection=Connection(ws,config,semaphore);connections.add(connection)\n  try:await connection.receive()\n  finally:connections.discard(connection);LOG.info('Bot disconnected')\n  return ws")
s=s.replace("web.run_app(create_app(a),host=a.host,port=a.port)","web.run_app(create_app(a),host=a.host,port=a.port,shutdown_timeout=5)")
p.write_text(s,encoding='utf-8')
