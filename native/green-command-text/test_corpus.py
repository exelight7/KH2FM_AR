"""Exercise the compiled C normalizer against labels in the actual payload."""
import argparse
import ctypes as C
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'build/tools'))
import arabic_msg as A

parser = argparse.ArgumentParser()
parser.add_argument('--library', required=True)
parser.add_argument('--data', required=True)
parser.add_argument('--output', required=True)
args = parser.parse_args()
A.load()
data = Path(args.data)
manifest = json.loads((data / 'manifest.json').read_text())
blob = (data / 'payload.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest() == manifest['blobHash']
ids = json.loads(Path(__file__).with_name('label-ids.json').read_text())
library = C.CDLL(str(Path(args.library).resolve()))
normalize = library.TestNormalize
normalize.argtypes = [C.c_void_p, C.c_size_t, C.c_void_p, C.c_size_t]
normalize.restype = C.c_size_t
wrapper = bytes.fromhex('11ebff1c0009df1102001c00')
records = []
for entry in manifest['files']:
    path = entry['path']
    if entry['group'] != 'payload' or not path.startswith('kh2/msg/us/') or not path.endswith('.bar'):
        continue
    name = Path(path).stem
    if name in ['fontimage', 'fontinfo']:
        continue
    content = gzip.decompress(blob[entry['offset']:entry['offset'] + entry['compressedSize']])
    assert hashlib.sha256(content).hexdigest() == entry['sha256']
    messages = A.msgs(content)
    chosen = set(ids['system_ids'] if name == 'sys' else ids['world_ids']) & messages.keys()
    for message_id in sorted(chosen):
        raw = A.padded(messages[message_id]) + b'\0'
        message = wrapper + raw
        output = C.create_string_buffer(1026)
        size = normalize(message, len(message), output, len(output))
        explicit = raw[0] == 10
        if explicit:
            assert size == 0, (name, message_id, 'explicit size changed')
        else:
            assert output.raw[:size] == wrapper + b'\x0a\x14' + raw, (name, message_id)
            assert normalize(output, size, C.create_string_buffer(1026), 1026) == 0
        records.append({'bar': name, 'id': message_id, 'normalized': bool(size), 'explicit': explicit})
assert len(records) == 555
assert sum(r['normalized'] for r in records) == 328
assert sum(r['explicit'] for r in records) == 227
report = {'passed': True, 'actualPayload': True, 'cases': len(records), 'normalized': 328,
          'explicitSizesPreserved': 227, 'iconPositionAndTextBytesPreserved': True,
          'idempotent': True, 'records': records}
Path(args.output).write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: v for k, v in report.items() if k != 'records'}))
