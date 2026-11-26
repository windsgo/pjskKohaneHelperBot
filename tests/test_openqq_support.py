"""OpenQQ file identifiers and action ordering."""
import asyncio
from types import SimpleNamespace

from sekai_toolkit.bot.server import Connection, detect_protocol


def make_connection():
    return Connection(None, SimpleNamespace(max_mb=20), asyncio.Semaphore(1))


def test_openqq_group_url_falls_back_to_file_name():
    conn = make_connection()
    actions = conn.group_file_actions(
        {'group_id': 123},
        {'file': 'x.bin', 'file_id': 'uuid_1', 'name': 'x.bin', 'busid': 102},
        'uuid_1',
    )
    assert actions[0] == ('get_group_file_url', {'group_id': 123, 'file_id': 'uuid_1', 'busid': 102})
    assert actions[1] == ('get_group_file_url', {'group_id': 123, 'file_id': 'uuid_1', 'busid': 102, 'file': 'x.bin'})
    assert actions[2][0] == 'get_file'
    assert actions[2][1]['group_id'] == 123 and actions[2][1]['file'] == 'x.bin'


def test_openqq_private_prefers_file_name():
    conn = make_connection()
    actions = conn.private_file_actions({'file': 'x.bin', 'file_id': 'uuid_1', 'name': 'x.bin'}, 'uuid_1')
    assert actions[0] == ('get_file', {'file': 'x.bin', 'file_id': 'uuid_1'})
    assert actions[-1] == ('get_private_file_url', {'file_id': 'uuid_1'})


def test_openqq_protocol_label():
    assert detect_protocol({'app_name': 'OpenQQ'}) == 'OpenQQ'
    assert detect_protocol({}, user_agent='OpenQQ/0.6') == 'OpenQQ'


if __name__ == '__main__':
    test_openqq_group_url_falls_back_to_file_name()
    test_openqq_private_prefers_file_name()
    test_openqq_protocol_label()
    print('PASS OpenQQ group/private file action ordering and protocol label')
