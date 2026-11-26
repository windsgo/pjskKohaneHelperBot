"""Small strict MessagePack reader; used when optional msgpack wheel is unavailable."""
import struct
from collections import namedtuple
ExtType = namedtuple('ExtType', 'code data')
UnpackException = ValueError

def unpackb(data, **kwargs):
    pos = 0
    def take(n):
        nonlocal pos
        if n < 0 or pos+n > len(data): raise ValueError('Truncated MessagePack')
        b = data[pos:pos+n]; pos += n
        return b
    def number(fmt): return struct.unpack('>'+fmt, take(struct.calcsize('>'+fmt)))[0]
    def array(n):
        if n > len(data)-pos: raise ValueError('Invalid array length')
        return [read() for _ in range(n)]
    def mapping(n):
        if n*2 > len(data)-pos: raise ValueError('Invalid map length')
        result = {}
        for _ in range(n):
            k = read(); v = read()
            if k in result: raise ValueError('Duplicate map key')
            result[k] = v
        return result
    def ext(n): return ExtType(number('b'), take(n))
    def read():
        t = take(1)[0]
        if t < 0x80: return t
        if t >= 0xe0: return t-256
        if 0x80 <= t <= 0x8f: return mapping(t & 15)
        if 0x90 <= t <= 0x9f: return array(t & 15)
        if 0xa0 <= t <= 0xbf: return take(t & 31).decode('utf-8')
        if t == 0xc0: return None
        if t in (0xc2, 0xc3): return t == 0xc3
        formats = {0xca:'f',0xcb:'d',0xcc:'B',0xcd:'H',0xce:'I',0xcf:'Q',0xd0:'b',0xd1:'h',0xd2:'i',0xd3:'q'}
        if t in formats: return number(formats[t])
        if t in (0xc4,0xc5,0xc6): return take(number({0xc4:'B',0xc5:'H',0xc6:'I'}[t]))
        if t in (0xd9,0xda,0xdb): return take(number({0xd9:'B',0xda:'H',0xdb:'I'}[t])).decode('utf-8')
        if t in (0xdc,0xdd): return array(number('H' if t == 0xdc else 'I'))
        if t in (0xde,0xdf): return mapping(number('H' if t == 0xde else 'I'))
        if 0xd4 <= t <= 0xd8: return ext(1 << (t-0xd4))
        if t in (0xc7,0xc8,0xc9): return ext(number({0xc7:'B',0xc8:'H',0xc9:'I'}[t]))
        raise ValueError(f'Unsupported tag {t:02x}')
    result = read()
    if pos != len(data): raise ValueError(f'Trailing bytes: {len(data)-pos}')
    return result
