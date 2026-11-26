"""OneBot command round trip for per-group settings and timer queries."""
import asyncio
import tempfile
from pathlib import Path
from types import SimpleNamespace

from aiohttp import ClientSession, web
from sekai_toolkit.bot.server import create_app
from sekai_toolkit.bot.group_settings import GroupSettings


async def main():
    with tempfile.TemporaryDirectory() as tmp:
        cfg=SimpleNamespace(token='',groups=[],users=[],output=Path(tmp),max_mb=20)
        runner=web.AppRunner(create_app(cfg));await runner.setup()
        site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
        port=site._server.sockets[0].getsockname()[1]
        try:
            async with ClientSession() as client:
                async with client.ws_connect(f'http://127.0.0.1:{port}/onebot/v11/ws') as ws:
                    async def issue(group_id,text,user_id=9,at=False):
                        message=[{'type':'at','data':{'qq':7}}] if at else []
                        message.append({'type':'text','data':{'text':text}})
                        await ws.send_json({'post_type':'message','message_type':'group','group_id':group_id,'user_id':user_id,'self_id':7,'message':message})
                        reply=await asyncio.wait_for(ws.receive_json(),5)
                        assert reply['action']=='send_group_msg'
                        await ws.send_json({'status':'ok','retcode':0,'data':{'message_id':1},'echo':reply['echo']})
                        return reply['params']['message']
                    # Bare command, slash prefix and backslash prefix all work.
                    await issue(100,'烤森解析回复模式 私聊')
                    await issue(100,r'\自动撤回用户烤森抓包消息 关闭')
                    assert cfg.group_settings.get(100)==('private',False)
                    assert cfg.group_settings.get(200)==('group',True)
                    assert '关闭' in str(await issue(100,'自动撤回用户烤森抓包消息 查询'))
                    assert '上限' in str(await issue(100,'火 查询'))
                    assert '暂无' in str(await issue(100,'转换器 查询'))
                    assert '参数错误' in str(await issue(100,'烤森解析回复模式 错误'))
                    assert '只有指定管理 QQ' in str(await issue(100,'烤森群抓包解析 关闭'))
                    assert cfg.group_settings.group_decode_enabled()
                    assert '已关闭' in str(await issue(100,'/烤森群抓包解析 关闭',1245784195))
                    assert not cfg.group_settings.group_decode_enabled()
                    assert not GroupSettings(cfg.group_settings.path).group_decode_enabled()
                    assert '关闭' in str(await issue(200,'烤森群抓包解析 查询'))
                    help_body=str(await issue(200,'help'))
                    assert '全局烤森群抓包解析' in help_body and '本群烤森解析回复模式' in help_body
                    # @bot also triggers a bare command.
                    assert '上限' in str(await issue(200,'火 查询',at=True))
                    await ws.send_json({'post_type':'notice','notice_type':'group_upload','group_id':200,'user_id':9,'self_id':7,'file':{'id':'abc','name':'[428] response_mkcn_test.bin'}})
                    try:await asyncio.wait_for(ws.receive_json(),.3);raise AssertionError('group upload decoded while disabled')
                    except asyncio.TimeoutError:pass
                    assert '已开启' in str(await issue(100,'烤森群抓包解析 开启',1245784195))
        finally:await runner.cleanup()
    print('PASS per-group commands, prefixes, help and timer queries')


if __name__=='__main__':asyncio.run(main())
