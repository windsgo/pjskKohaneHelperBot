import asyncio,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from types import SimpleNamespace
from aiohttp import web,ClientSession,WSServerHandshakeError
from sekai_toolkit.bot.server import create_app
async def case(configured,supplied,expected):
 cfg=SimpleNamespace(token=configured,groups=[],users=[],output=Path('output/test_auth'),max_mb=20,cleanup_group_files=False)
 runner=web.AppRunner(create_app(cfg));await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start();port=site._server.sockets[0].getsockname()[1]
 try:
  async with ClientSession() as c:
   try:
    ws=await c.ws_connect(f'http://127.0.0.1:{port}/onebot/v11/ws',params={'access_token':supplied});await ws.close();actual=101
   except WSServerHandshakeError as e:actual=e.status
   assert actual==expected,(actual,expected)
 finally:await runner.cleanup()
async def main():
 for configured,supplied,expected in [('中文令牌','中文令牌',101),('中文令牌','错误',401),('中文令牌','',401),('','',101),('abc','abc',101)]:await case(configured,supplied,expected)
 print('PASS: matching/mismatching/missing Unicode token, no-token and ASCII connections')
asyncio.run(main())
