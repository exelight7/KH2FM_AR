"""Emit the stable ownership manifest shipped by future KH2FM Arabic installers."""
import argparse
import csv
import json
import re
from pathlib import Path

PRODUCT_ID = '8F3C2A71-6E0B-4D5C-9A1E-2B7D4F60C3A9'

def create_manifest(payload_file, loader_file, version):
    match = re.fullmatch(r'(\d+)\.(\d+)\.(\d+)(?:-[0-9A-Za-z.-]+)?', version)
    if not match or tuple(map(int, match.groups())) < (1, 0, 1):
        raise ValueError('Translation version must be at least 1.0.1')
    with open(payload_file, encoding='utf-8-sig', newline='') as handle:
        payload = list(csv.DictReader(handle, delimiter='\t'))
    with open(loader_file, encoding='utf-8-sig', newline='') as handle:
        loader = list(csv.DictReader(handle))
    if not 1 <= len(payload) <= 10000 or len(loader) > 100:
        raise ValueError('Invalid manifest size')
    for entries, kind in [(payload, 'payload'), (loader, 'loader')]:
        seen = set()
        for entry in entries:
            path = entry['path'].replace('\\', '/')
            pattern = r'[A-Za-z0-9_./-]+\.(?:bar|png|dds)' if kind == 'payload' else r'(?:DBGHELP\.dll|dependencies/[A-Za-z0-9_-]+\.dll)'
            if not re.fullmatch(pattern, path, re.I) or path.startswith('/') or any(s in ('', '.', '..') for s in path.split('/')):
                raise ValueError('Unsafe resource path: ' + path)
            if path.lower() in seen or not re.fullmatch(r'[a-f0-9]{64}', entry['sha256']):
                raise ValueError('Duplicate path or invalid SHA256: ' + path)
            if kind == 'payload':
                if not re.fullmatch(r'\d+', entry['size']) or int(entry['size']) > 1073741824:
                    raise ValueError('Invalid resource size: ' + path)
                entry['size'] = int(entry['size'])
            seen.add(path.lower())
    return dict(Schema=1, ProductId=PRODUCT_ID, Version=version, Payload=payload, Loader=loader)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--payload-manifest', required=True, type=Path)
    parser.add_argument('--loader-manifest', type=Path, default=Path(__file__).parent/'src/manifest_panacea.csv')
    parser.add_argument('--version', required=True)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    manifest = create_manifest(args.payload_manifest, args.loader_manifest, args.version)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Ownership schema 1:', args.version, len(manifest['Payload']), 'resources')
