"""OneBot file URL is preferred; a local get_file result is a fallback."""
import asyncio
import tempfile
from pathlib import Path
from types import SimpleNamespace
from sekai_toolkit.bot.server import Connection


async def main():
    with tempfile.TemporaryDirectory() as tmp:
        local=Path(tmp,'sample.bin');local.write_bytes(b'example')
        conn=Connection(None,SimpleNamespace(),asyncio.Semaphore(1))
        calls=[]
        async def call(action,params):
            calls.append(action)
            if action=='get_group_file_url':raise RuntimeError('retcode=1501; timeout')
            if action=='get_file':return {'file':str(local),'url':''}
            raise AssertionError(action)
        conn.call=call
        result=await conn.url({'message_type':'group','group_id':123},{'file_id':'/upload-id','busid':102})
        assert result==local
        assert calls==['get_group_file_url','get_file']
    print('PASS OneBot URL lookup and local file fallback')


if __name__=='__main__':asyncio.run(main())
