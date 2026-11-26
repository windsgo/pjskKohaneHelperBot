"""Local OneBot mock: global reply command, duplicate notices, one private five-image reply."""
import asyncio
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
from aiohttp import web,ClientSession
from sekai_toolkit.bot.server import create_app
from sekai_toolkit.bot.group_settings import GroupSettings
from _capture import require_capture

BIN=require_capture()
async def start(app):
 runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start();return runner,site._server.sockets[0].getsockname()[1]
async def main():
 with tempfile.TemporaryDirectory() as tmp:
  root=Path(tmp)
  file_app=web.Application();file_app.router.add_get('/sample',lambda _:web.Response(body=BIN.read_bytes()))
  fr,fp=await start(file_app)
  cfg=SimpleNamespace(token='',groups=[],users=[],output=root,max_mb=20,cleanup_group_files=False)
  br,bp=await start(create_app(cfg))
  try:
   async with ClientSession() as client:
    async with client.ws_connect(f'http://127.0.0.1:{bp}/onebot/v11/ws') as ws:
     command={'post_type':'message','message_type':'group','group_id':456,'user_id':777,'self_id':999,'message':[{'type':'text','data':{'text':'烤森解析回复模式 私聊'}}]}
     await ws.send_json(command)
     response=await asyncio.wait_for(ws.receive_json(),5)
     assert response['action']=='send_group_msg'
     await ws.send_json({'status':'ok','retcode':0,'data':{'message_id':1},'echo':response['echo']})
     assert GroupSettings(root/'group_settings.sqlite3').get(456)[0]=='private'
     await ws.send_json({**command,'message':[{'type':'text','data':{'text':'help'}}]})
     response=await asyncio.wait_for(ws.receive_json(),5)
     assert response['action']=='send_group_msg'
     help_body=response['params']['message'][0]['data']['text']
     assert '本群烤森解析回复模式' in help_body and '[数字] response_mkcn' in help_body and '四张地图' in help_body and 'https://upload.sakura-bot.cn/about' in help_body
     await ws.send_json({'status':'ok','retcode':0,'data':{'message_id':11},'echo':response['echo']})
     notice={'post_type':'notice','notice_type':'group_upload','group_id':456,'user_id':123,'self_id':999,'file':{'id':'uuid-1','name':'[428] response_mkcn.bin','size':BIN.stat().st_size,'busid':102}}
     message={'post_type':'message','message_type':'group','group_id':456,'user_id':123,'self_id':999,'message':[{'type':'file','data':{'id':'uuid-2','name':notice['file']['name'],'size':BIN.stat().st_size}}]}
     await ws.send_json(notice);await ws.send_json(message)
     actions=[]
     for _ in range(7):
      response=await asyncio.wait_for(ws.receive_json(),30);actions.append(response['action'])
      if response['action']=='get_group_file_url':data={'url':f'http://127.0.0.1:{fp}/sample'}
      else:
       assert response['action']=='send_private_msg' and response['params']['user_id']==123
       payload=response['params']['message']
       if isinstance(payload,str):
        assert '收到' in payload,payload
       else:
        assert len(payload)==1
        segment=payload[0]
        if segment.get('type')=='text':
         assert '收到' in segment['data']['text'],segment
        else:
         assert Path(segment['data']['file']).is_file()
       data={'message_id':2}
      await ws.send_json({'status':'ok','retcode':0,'data':data,'echo':response['echo']})
     assert actions==['send_private_msg','get_group_file_url']+['send_private_msg']*5
     await ws.send_json({**command,'message':[{'type':'text','data':{'text':'烤森解析回复模式 群组'}}]})
     response=await asyncio.wait_for(ws.receive_json(),5);assert response['action']=='send_group_msg'
     await ws.send_json({'status':'ok','retcode':0,'data':{'message_id':3},'echo':response['echo']})
     await ws.send_json(notice)
     response=await asyncio.wait_for(ws.receive_json(),10);assert response['action']=='send_group_msg'
     ack=response['params']['message']
     assert '收到' in (ack if isinstance(ack,str) else ack[0]['data']['text'])
     await ws.send_json({'status':'ok','retcode':0,'data':{'message_id':3},'echo':response['echo']})
     response=await asyncio.wait_for(ws.receive_json(),10);assert response['action']=='get_group_file_url'
     await ws.send_json({'status':'ok','retcode':0,'data':{'url':f'http://127.0.0.1:{fp}/sample'},'echo':response['echo']})
     response=await asyncio.wait_for(ws.receive_json(),30);assert response['action']=='send_group_msg' and len(response['params']['message'])==5
     await ws.send_json({'status':'ok','retcode':0,'data':{'message_id':4},'echo':response['echo']})
     try:await asyncio.wait_for(ws.receive_json(),.3);raise AssertionError('duplicate upload triggered another action')
     except asyncio.TimeoutError:pass
  finally:await br.cleanup();await fr.cleanup()
 print('PASS persisted global private mode, duplicate group events, five separate private images')

if __name__=='__main__':asyncio.run(main())
