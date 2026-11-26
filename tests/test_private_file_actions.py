"""Private files use the standard OneBot get_file first; URL API is only a fallback."""
import asyncio
import tempfile
from pathlib import Path
from types import SimpleNamespace
from sekai_toolkit.bot.server import Connection


def make_connection():
    return Connection(None, SimpleNamespace(max_mb=20), asyncio.Semaphore(1))


def test_openqq_prefers_event_file_name():
    conn = make_connection()
    actions = conn.private_file_actions({'file': 'x.bin', 'file_id': 'uuid_1', 'name': 'x.bin'}, 'uuid_1')
    assert actions[0] == ('get_file', {'file': 'x.bin', 'file_id': 'uuid_1'})
    assert actions[1] == ('get_file', {'file_id': 'uuid_1'})
    assert actions[-1] == ('get_private_file_url', {'file_id': 'uuid_1'})


def test_napcat_keeps_encoded_id_first():
    conn = make_connection()
    actions = conn.private_file_actions({'file': 'encoded-id', 'id': 'encoded-id', 'name': 'x.bin'}, 'encoded-id')
    assert actions[0] == ('get_file', {'file_id': 'encoded-id'})
    assert actions[1] == ('get_file', {'file': 'x.bin', 'file_id': 'encoded-id'})


def test_url_uses_local_path_from_event():
    async def run():
        with tempfile.TemporaryDirectory() as tmp:
            local = Path(tmp, 'sample.bin'); local.write_bytes(b'data')
            conn = make_connection(); calls = []
            async def call(action, params):
                calls.append(action); raise AssertionError(action)
            conn.call = call
            result = await conn.url({'message_type': 'private'}, {'path': str(local), 'file_id': 'x'})
            assert result == local and calls == []
    asyncio.run(run())


def test_url_openqq_get_file_returns_local_file():
    async def run():
        with tempfile.TemporaryDirectory() as tmp:
            local = Path(tmp, 'sample.bin'); local.write_bytes(b'data')
            conn = make_connection(); calls = []
            async def call(action, params):
                calls.append((action, params))
                assert params['file'] == 'x.bin'
                return {'file': str(local)}
            conn.call = call
            result = await conn.url({'message_type': 'private'}, {'file': 'x.bin', 'file_id': 'uuid_1', 'name': 'x.bin'})
            assert result == local
            assert [a for a, _ in calls] == ['get_file']
    asyncio.run(run())


def test_url_private_falls_back_to_url_api():
    async def run():
        conn = make_connection(); calls = []
        async def call(action, params):
            calls.append(action)
            if action == 'get_private_file_url': return {'url': 'http://example.test/f'}
            raise RuntimeError(f'{action}; retcode=1500; download timeout')
        conn.call = call
        result = await conn.url({'message_type': 'private'}, {'file': 'x.bin', 'file_id': 'uuid_1'})
        assert result == 'http://example.test/f'
        assert calls == ['get_file', 'get_file', 'get_private_file_url']
    asyncio.run(run())


if __name__ == '__main__':
    test_openqq_prefers_event_file_name()
    test_napcat_keeps_encoded_id_first()
    test_url_uses_local_path_from_event()
    test_url_openqq_get_file_returns_local_file()
    test_url_private_falls_back_to_url_api()
    print('PASS private file uses standard get_file with implementation-appropriate key')
