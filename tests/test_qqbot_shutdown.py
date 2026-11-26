import asyncio
from pathlib import Path
from types import SimpleNamespace
from aiohttp import web,ClientSession
from sekai_toolkit.bot.server import create_app,Connection
async def main():
 started=asyncio.Event();cancelled=asyncio.Event()
 original=Connection.process
 async def blocking(self,event,file):
  started.set()
  try:await asyncio.sleep(100)
  finally:cancelled.set()
 Connection.process=blocking
 cfg=SimpleNamespace(token='',groups=[],users=[],output=Path('output/shutdown_test'),max_mb=20,cleanup_group_files=False)
 runner=web.AppRunner(create_app(cfg),shutdown_timeout=2);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start();port=site._server.sockets[0].getsockname()[1]
 async with ClientSession() as client:
  async with client.ws_connect(f'http://127.0.0.1:{port}/onebot/v11/ws') as ws:
   await ws.send_json({'post_type':'message','message_type':'private','user_id':1,'message':[{'type':'file','data':{'name':'[1] response_mkcn_test','id':'x'}}]})
   await asyncio.wait_for(started.wait(),2)
   reader=asyncio.create_task(ws.receive())
   await asyncio.wait_for(runner.cleanup(),4)
   await reader;assert cancelled.is_set()
 Connection.process=original
 print('PASS: active WebSocket and running job close during server shutdown')
asyncio.run(main())
