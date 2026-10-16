"""Package only the verified Arabic mod files and pinned Panacea DLLs."""
import csv
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
APP = ROOT / 'apps/manager'
OUT = APP / 'data'
OUT.mkdir(parents=True, exist_ok=True)
config = json.loads((ROOT / 'build/config/panacea.json').read_text())
manifest = list(csv.DictReader((ROOT / 'build/out/MANIFEST.tsv').open(), delimiter='\t'))
catalog = json.loads((APP / 'catalog/legacy.json').read_text())
reference = {f['path']: f for v in catalog['versions'] if v['version'] == '1.0.2' for f in v['files']}
version = json.loads((APP / 'package.json').read_text())['version']
assert version == '1.0.5'
font_paths = {'msg/us/fontimage.bar', 'msg/us/fontinfo.bar',
              'remastered/msg/us/fontimage.bar/US_fontimage_bar0.png',
              'remastered/msg/us/fontimage.bar/US_fontimage_bar1.png'}
font_manifest = {f['path'].replace('\\', '/'): f for f in csv.DictReader(
    (ROOT / 'experiments/fonts/alef-spacing/MANIFEST.tsv').open(), delimiter='\t')}
files = []
with (OUT / 'payload.bin').open('wb') as blob:
    sources = []
    for entry in manifest:
        relative = entry['path'].replace('\\', '/')
        bar = ROOT / 'build/out/kh2' / relative
        source = bar if bar.is_file() else ROOT / 'build/payload/kh2' / relative
        expected = font_manifest[relative] if relative in font_paths else reference['kh2/' + relative]
        if expected['sha256'] != entry['sha256']:
            raise SystemExit('1.0.5 source does not match the approved translation/font: ' + relative)
        sources.append(('kh2/' + relative, 'payload', source, entry['sha256']))
    vendor = ROOT / 'build' / config['extract_to'] / config['files_under']
    for name, expected in config['files'].items():
        target = 'DBGHELP.dll' if name == 'OpenKH.Panacea.dll' else 'dependencies/' + name
        sources.append((target, 'loader', vendor / name, expected))
        if name == 'OpenKH.Panacea.dll':
            sources.append(('version.dll', 'loader', vendor / name, expected))
    for relative, group, source, expected in sources:
        data = source.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest != expected:
            raise SystemExit('Source SHA256 mismatch: ' + relative)
        compressed = gzip.compress(data, compresslevel=9, mtime=0)
        files.append({'path': relative, 'group': group, 'size': len(data),
                      'sha256': digest, 'offset': blob.tell(), 'compressedSize': len(compressed)})
        blob.write(compressed)
blob_hash = hashlib.file_digest((OUT / 'payload.bin').open('rb'), 'sha256').hexdigest()
result = {'schema': 1, 'version': version, 'blobHash': blob_hash, 'files': files}
(OUT / 'manifest.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'version': result['version'], 'files': len(files), 'payload_files': len(manifest),
                  'packed_bytes': (OUT / 'payload.bin').stat().st_size, 'blob_sha256': blob_hash,
                  'translation_text_1_0_2_identical': True, 'font_files_updated': 4}, indent=2))
