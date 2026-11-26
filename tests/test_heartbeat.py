"""Periodic report names the detected OneBot implementation and sends to the configured group."""
import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from sekai_toolkit.bot.server import Connection


def test_heartbeat_report():
 async def run():
  connection=Connection(None,SimpleNamespace(heartbeat_group=2151080494),None)
  actions=[]
  async def call(action,params):
   actions.append((action,params))
   if action=='get_version_info':return {'app_name':'NapCat','app_version':'4.2.0'}
   return {'online':True,'good':True} if action=='get_status' else {'message_id':1}
  connection.call=call
  await connection.heartbeat_once()
  assert [action for action,_ in actions]==['get_version_info','get_status','send_group_msg']
  assert actions[2][1]['group_id']==2151080494
  assert 'NapCat 在线报告' in actions[2][1]['message']
  assert '在线：是' in actions[2][1]['message']
  assert '运行正常：是' in actions[2][1]['message']
 asyncio.run(run())


if __name__=='__main__':
 test_heartbeat_report()
 print('PASS periodic report uses detected protocol name and status API')
