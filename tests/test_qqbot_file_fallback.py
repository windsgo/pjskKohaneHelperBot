"""Local-only end-to-end OneBot mock: upload -> URL API -> bin -> five PNGs."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src')) if sys.prefix==sys.base_prefix else None
import asyncio,base64,json
from types import SimpleNamespace
from aiohttp import web,ClientSession,WSServerHandshakeError
from sekai_toolkit.bot.server import create_app
from _capture import require_capture
BIN=require_capture()
async def start(app):
 runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start();return runner,site._server.sockets[0].getsockname()[1]
async def test():
 file_app=web.Application();file_app.router.add_get('/sample',lambda _:web.Response(body=BIN.read_bytes()))
 fr,fp=await start(file_app)
 cfg=SimpleNamespace(token='local-test-only',groups=[],users=[],output=ROOT/'output/ws_test',max_mb=20,cleanup_group_files=False)
 br,bp=await start(create_app(cfg));url=f'http://127.0.0.1:{bp}/onebot/v11/ws'
 try:
  async with ClientSession() as client:
   try:await client.ws_connect(url);raise AssertionError('Unauthenticated connection accepted')
   except WSServerHandshakeError as e:assert e.status==401
   async with client.ws_connect(url,headers={'Authorization':'Bearer local-test-only'}) as ws:
    event={'post_type':'notice','notice_type':'group_upload','self_id':999,'user_id':123,'group_id':456,'file':{'id':'test-file','name':'[428] response_mkcn_test.bin','size':BIN.stat().st_size,'busid':102}}
    await ws.send_json({**event,'file':{**event['file'],'name':'ignore.bin'}})
    await ws.send_json(event);await ws.send_json(event)
    actions=[];images=[]
    while not images:
     message=await asyncio.wait_for(ws.receive_json(),60);actions.append(message['action'])
     if message['action']=='get_group_file_url':
      await ws.send_json({'status':'failed','retcode':1200,'wording':'mock incompatible group-file API','echo':message['echo']});continue
     elif message['action']=='get_file':data={'url':f'http://127.0.0.1:{fp}/sample'}
     else:
      assert message['action']=='send_group_msg';assert message['params']['group_id']==456
      segments=message['params']['message']
      if isinstance(segments,str):
       assert '收到' in segments,segments
       data={'message_id':1}
      else:
       segment=segments[0];assert segment['type']=='image',segment
       assert len(segments)==5
       images=[Path(s['data']['file']).read_bytes() for s in segments]
       assert all(raw.startswith(b'\x89PNG\r\n\x1a\n') for raw in images);data={'message_id':1}
     await ws.send_json({'status':'ok','retcode':0,'data':data,'echo':message['echo']})
    assert actions.count('get_group_file_url')==2
    assert actions.count('get_file')==1
    print('PASS: token rejection, file filtering, duplicate suppression, API correlation, real bin rendering, five valid PNG replies')
 finally:await br.cleanup();await fr.cleanup()
if __name__=='__main__':asyncio.run(test())
