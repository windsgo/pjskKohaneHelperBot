"""Status output names the OneBot implementation (NapCat, OpenQQ, ...)."""
import asyncio
from types import SimpleNamespace
from sekai_toolkit.bot.server import Connection,detect_protocol,status_text


def test_detection():
    assert detect_protocol({'app_name':'NapCat','app_version':'4.2.0'})=='NapCat'
    assert detect_protocol({'app_name':'OpenQQ','app_version':'0.5.0'})=='OpenQQ'
    assert detect_protocol({},None,'OpenQQ/0.5.0')=='OpenQQ'
    assert detect_protocol({},None,'NapCat/4.2.0')=='NapCat'
    assert detect_protocol({'app_name':'Lagrange.Core'})=='Lagrange.Core'
    assert detect_protocol({},None,'')=='OneBot v11'
    assert detect_protocol({'app_name':'SomeBot'})=='SomeBot'


def test_text():
    napcat=status_text({'online':True,'good':True,'uptime':5400},{'app_name':'NapCat','app_version':'4.2.0','protocol_version':'v11','platform':'win32','arch':'x64'},0)
    assert napcat.splitlines()[0]=='NapCat 信息（协议 v11）'
    assert '版本：4.2.0' in napcat and '平台：win32 (x64)' in napcat
    assert 'NapCat 运行时间：1小时 30分钟' in napcat
    assert '在线：是｜运行正常：是' in napcat
    openqq=status_text({'online':True,'good':True},{'app_name':'OpenQQ','app_version':'0.5.0'},0,'OpenQQ')
    assert openqq.splitlines()[0]=='OpenQQ 信息'
    assert 'Bot 与 OpenQQ 连续连接' in openqq


def test_send_status_reports_detected_endpoint():
    async def run():
        connection=Connection(None,SimpleNamespace(),asyncio.Semaphore(1))
        sent=[];logged=[]
        async def call(action,params):
            if action=='get_status':return {'online':True,'good':True}
            if action=='get_version_info':return {'app_name':'OpenQQ','app_version':'0.5.0'}
            raise AssertionError(action)
        async def send(event,message):sent.append(message)
        connection.call=call;connection.send=send
        await connection.send_status({'user_id':1,'group_id':2})
        assert sent[0].startswith('OpenQQ 信息')
        assert connection.protocol_name=='OpenQQ'
    asyncio.run(run())


if __name__=='__main__':
    test_detection();test_text();test_send_status_reports_detected_endpoint()
    print('PASS OneBot endpoint detection and protocol-aware status text')
