"""Check per-group settings and the post-render file-message recall path."""
import asyncio
import tempfile
from pathlib import Path
from types import SimpleNamespace

from sekai_toolkit.bot.group_settings import GroupSettings
from sekai_toolkit.bot.server import Connection
from sekai_toolkit.bot.stamina import StaminaStore
from sekai_toolkit.bot.converter import ConverterStore


async def main():
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)
        settings=GroupSettings(root/'groups.db')
        settings.set_reply(100,'private')
        settings.set_auto_recall(100,True)
        settings.set_auto_recall(200,False)
        assert settings.get(100)==('private',True)
        assert settings.get(200)==('group',False)
        assert GroupSettings(root/'groups.db').get(100)==('private',True)
        cfg=SimpleNamespace(group_settings=settings)
        connection=Connection(None,cfg,None)
        calls=[]
        async def call(action,params):
            calls.append((action,params))
            return {'role':role} if action=='get_group_member_info' else {}
        connection.call=call
        event={'post_type':'notice','notice_type':'group_upload','group_id':100,'user_id':9,'self_id':7}
        file={'name':'[428] response_mkcn.bin','_message_id':12345}
        role='admin'
        await connection.recall_group_upload(event,file)
        assert [a for a,_ in calls]==['get_group_member_info','delete_msg','send_group_msg']
        assert calls[1][1]=={'message_id':12345}
        calls.clear();role='member'
        await connection.recall_group_upload(event,file)
        assert [a for a,_ in calls]==['get_group_member_info','send_group_msg']
        calls.clear();role='owner'
        await connection.recall_group_upload(event,{**file,'_message_id':None})
        assert [a for a,_ in calls]==['get_group_member_info','send_group_msg']
        calls.clear()
        await connection.recall_group_upload({**event,'group_id':200},file)
        assert calls==[]

        stamina=StaminaStore(root/'timers.db')
        assert '上限' in stamina.command(9,100,'火 最大值 50',1000)
        stamina.command(9,100,'火 记录 23 12',1000)
        assert '23/50' in stamina.query(9,1000)
        converter=ConverterStore(root/'timers.db')
        converter.command(9,100,'转换器 22',1000)
        assert '22小时' in converter.query(9,1000)
    print('PASS per-group settings, recall permissions, missing message ID, timer queries')


if __name__=='__main__':asyncio.run(main())
