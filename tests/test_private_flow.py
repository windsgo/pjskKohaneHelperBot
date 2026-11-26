"""Local OneBot mock: private upload -> standard get_file -> five PNG replies (OpenQQ style)."""
import asyncio
from pathlib import Path
from types import SimpleNamespace
from aiohttp import web,ClientSession
from sekai_toolkit.bot.server import create_app
from _capture import require_capture

BIN=require_capture()
NAME='[428] response_mkcn_test.bin'


async def start(app):
 runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start();return runner,site._server.sockets[0].getsockname()[1]


async def main():
 root=Path(__file__).resolve().parents[1]/'runtime/temp/private_flow'
 root.mkdir(parents=True,exist_ok=True)
 cfg=SimpleNamespace(token='',groups=[],users=[],output=root,max_mb=20,cleanup_group_files=False,notify_group=456)
 br,bp=await start(create_app(cfg))
 try:
  async with ClientSession() as client:
   async with client.ws_connect(f'http://127.0.0.1:{bp}/onebot/v11/ws',headers={'User-Agent':'OpenQQ/0.5.0'}) as ws:
    event={'post_type':'message','message_type':'private','self_id':999,'user_id':123,'message_id':101,
           'message':[{'type':'file','data':{'file':NAME,'file_id':'uuid_1','name':NAME,'file_size':BIN.stat().st_size}}]}
    await ws.send_json(event)
    actions=[];images=[]
    while len(images)<5:
     message=await asyncio.wait_for(ws.receive_json(),60);actions.append(message['action'])
     if message['action']=='get_file':
      assert message['params']['file']==NAME,message['params']
      data={'file':str(BIN.resolve()),'file_name':NAME,'file_size':BIN.stat().st_size}
     else:
      assert message['action']=='send_private_msg' and message['params']['user_id']==123
      payload=message['params']['message']
      if isinstance(payload,str):
       assert '收到' in payload,payload
       data={'message_id':1}
      else:
       assert len(payload)==1
       segment=payload[0]
       if segment['type']=='text':
        assert '收到' in segment['data']['text'],segment
        data={'message_id':1}
       else:
        assert segment['type']=='image',segment
        raw=Path(segment['data']['file']).read_bytes()
        assert raw.startswith(b'\x89PNG\r\n\x1a\n');images.append(raw);data={'message_id':1}
     await ws.send_json({'status':'ok','retcode':0,'data':data,'echo':message['echo']})
    assert actions==['send_private_msg','get_file']+['send_private_msg']*5,actions
    response=await asyncio.wait_for(ws.receive_json(),5);assert response['action']=='send_group_msg'
    assert response['params']['group_id']==456 and '私聊' in response['params']['message']
    await ws.send_json({'status':'ok','retcode':0,'data':{'message_id':9},'echo':response['echo']})
    print('PASS private upload resolves via standard get_file and returns five PNGs')
 finally:await br.cleanup()


if __name__=='__main__':asyncio.run(main())
