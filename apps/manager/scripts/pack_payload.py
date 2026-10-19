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
previous = {f['path']: f for v in catalog['versions'] if v['version'] == '1.0.7' for f in v['files']}
published119 = {f['path']: f for v in catalog['versions'] if v['version'] == '1.0.19' for f in v['files']}
version = json.loads((APP / 'package.json').read_text())['version']
assert version == '1.0.20'
font_paths = {'msg/us/fontimage.bar', 'msg/us/fontinfo.bar',
              'remastered/msg/us/fontimage.bar/US_fontimage_bar0.png',
              'remastered/msg/us/fontimage.bar/US_fontimage_bar1.png'}
font_manifest = {f['path'].replace('\\', '/'): f for f in csv.DictReader(
    (ROOT / 'experiments/fonts/menu-context-alignment/MANIFEST.tsv').open(), delimiter='\t')}
# 1.0.19 ships text corrections: a text bar may differ from 1.0.2 only when
# build_bars.py rebuilt it (all its gates passed) and wrote it to build/out.
hud_manifest = {r['path']: r for r in json.loads((ROOT / 'build/report/HUD_TRANSFORM.json').read_text(encoding='utf-8'))['files']}
assert len(hud_manifest) == 19
command_manifest = {r['path']: r for r in json.loads((ROOT / 'build/report/HUD_COMMANDS.json').read_text(encoding='utf-8'))['files']}
assert len(command_manifest) == 5
reaction_report = json.loads((ROOT / 'build/report/REACTION_COMMANDS.json').read_text(encoding='utf-8'))
title_manifest = {r['path']: r for r in json.loads((ROOT / 'build/report/TITLE_CLEANUP.json').read_text())['files']}
assert len(title_manifest) == 8
layout_report = json.loads((ROOT / 'build/report/GREEN_COMMAND_LAYOUT.json').read_text())
layout_manifest = {r['path']: r for r in layout_report['files']}
assert len(layout_manifest) == 27
assert set(layout_manifest) == {r['path'] for r in json.loads((ROOT / 'build/config/green-command-layout.json').read_text())['files']}
assert len(manifest) == 825 and len({r['path'] for r in manifest}) == 825
assert {'kh2/' + r['path'].replace('\\', '/') for r in manifest} == set(published119) | {'kh2/' + p for p in layout_manifest}
assert all(r['only_text_y_changed'] and r['groups'] == [0, 1, 2, 3, 5] for r in layout_manifest.values())
text_changed = []
files = []
with (OUT / 'payload.bin').open('wb') as blob:
    sources = []
    for entry in manifest:
        relative = entry['path'].replace('\\', '/')
        bar = ROOT / 'build/out/kh2' / relative
        source = bar if bar.is_file() else ROOT / 'build/payload/kh2' / relative
        if relative in layout_manifest:
            expected = layout_manifest[relative]['sha256']
        elif relative in font_paths:
            expected = font_manifest[relative]['sha256']
        elif relative in title_manifest:
            expected = title_manifest[relative]['sha256']
        elif relative in hud_manifest:
            expected = hud_manifest[relative]['sha256']
        elif relative in command_manifest:
            expected = command_manifest[relative]['sha256']
        elif relative.startswith('msg/us/') and relative.endswith('.bar') and bar.is_file():
            expected = hashlib.sha256(bar.read_bytes()).hexdigest()
            if expected != previous['kh2/' + relative]['sha256']:
                text_changed.append(relative)
        else:
            expected = reference['kh2/' + relative]['sha256']
        if expected != entry['sha256']:
            raise SystemExit('1.0.19 source does not match the approved translation/font: ' + relative)
        if relative == reaction_report['path']:
            assert expected == reaction_report['sha256']
        if relative not in layout_manifest and entry['sha256'] != published119['kh2/' + relative]['sha256']:
            raise SystemExit('1.0.20 unexpectedly changes published 1.0.19 content: ' + relative)
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
                  'text_bars_changed_from_1_0_7': sorted(text_changed),
                  'font_files_changed_from_1_0_7': sum(previous['kh2/' + p]['sha256'] != font_manifest[p]['sha256'] for p in font_paths)},
                 indent=2))
