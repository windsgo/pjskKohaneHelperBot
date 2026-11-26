"""Decode local SEKAI API responses: AES-CBC / PKCS7 -> MessagePack -> JSON."""
import argparse
import base64
import hashlib
import json
import sys
from pathlib import Path
try:
    import msgpack
except ImportError:
    from . import msgpack_reader as msgpack
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7

KEYSETS = {
    'cn': (b'PFSeUG9v6MpohZKO', b'rJn6VC6vJhEX2xLO'),
    'legacy': (b'g2fcC0ZczN9MTJ61', b'msx3IV0i9XE5uYZ1'),
}

def json_safe(value):
    if isinstance(value, msgpack.ExtType):
        return {'$ext': value.code, '$base64': base64.b64encode(value.data).decode()}
    if isinstance(value, bytes):
        return {'$base64': base64.b64encode(value).decode()}
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [json_safe(v) for v in value]
    return value

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    from sekai_toolkit.common.paths import RUNTIME
    parser.add_argument('--out', type=Path, default=RUNTIME / 'decoded')
    parser.add_argument('--keyset', choices=['auto', *KEYSETS], default='auto')
    parser.add_argument('--plain', action='store_true', help='Input is already decrypted MessagePack')
    args = parser.parse_args()
    raw = args.input.read_bytes()
    candidates = [args.keyset] if args.keyset != 'auto' else list(KEYSETS)
    failures = []
    for name in (['plain'] if args.plain else candidates):
        try:
            if name == 'plain':
                plain = raw
            else:
                if not raw or len(raw) % 16:
                    raise ValueError('AES ciphertext length must be a positive multiple of 16')
                key, iv = KEYSETS[name]
                decryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
                padded = decryptor.update(raw) + decryptor.finalize()
                unpadder = PKCS7(128).unpadder()
                plain = unpadder.update(padded) + unpadder.finalize()
            data = msgpack.unpackb(plain, raw=False, strict_map_key=False)
            if not isinstance(data, dict):
                raise ValueError('Expected a response dictionary')
            break
        except (ValueError, TypeError, msgpack.UnpackException) as exc:
            failures.append(f'{name}: {exc}')
    else:
        raise SystemExit('Cannot decode input. ' + '; '.join(failures))
    args.out.mkdir(parents=True, exist_ok=True)
    def save(name, value):
        (args.out / name).write_text(json.dumps(json_safe(value), ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
    (args.out / 'payload.msgpack').write_bytes(plain)
    save('response.json', data)
    fields = [{'field': k, 'type': type(v).__name__, 'count': len(v) if isinstance(v, (dict,list)) else None} for k,v in data.items()]
    save('summary.json', {'input_bytes': len(raw), 'input_sha256': hashlib.sha256(raw).hexdigest(), 'keyset': name, 'plaintext_bytes': len(plain), 'fields': fields})
    (args.out / 'fields').mkdir(exist_ok=True)
    for i, (k,v) in enumerate(data.items()):
        # Use generated filenames, never trust response strings as paths.
        save(f'fields/{i:02d}.json', {'field': k, 'value': v})
    print(json.dumps({'keyset': name, 'fields': fields}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()

