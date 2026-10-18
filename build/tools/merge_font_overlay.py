"""Merge the verified menu font, with the published dialogue preserved."""
import argparse
import csv
import hashlib
from pathlib import Path
import zipfile
from check_font_texture import check_textures

ROOT = Path(__file__).resolve().parents[2]
ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--out', type=Path, default=ROOT / 'build/out')
args = ap.parse_args()
preview = ROOT / 'experiments/fonts/menu-fine-alignment'
archive = preview / 'font-overlay.zip'
expected_zip = next(line.split()[0] for line in (preview / 'SHA256SUMS.txt').read_text().splitlines()
                    if line.split(maxsplit=1)[1] == 'font-overlay.zip')
assert hashlib.sha256(archive.read_bytes()).hexdigest() == expected_zip, 'Font ZIP SHA256 mismatch'
check_textures(archive)
allowed = {'msg/us/fontimage.bar', 'msg/us/fontinfo.bar',
           'remastered/msg/us/fontimage.bar/US_fontimage_bar0.png',
           'remastered/msg/us/fontimage.bar/US_fontimage_bar1.png'}
font_manifest = {r['path'].replace('\\', '/'): r
                 for r in csv.DictReader((preview / 'MANIFEST.tsv').open(), delimiter='\t')}
manifest_path = args.out / 'MANIFEST.tsv'
manifest = list(csv.DictReader(manifest_path.open(), delimiter='\t'))
assert len(manifest) == 798 and len({r['path'] for r in manifest}) == 798
replacements = {}
with zipfile.ZipFile(archive) as z:
    assert len(z.namelist()) == 4 and set(z.namelist()) == {'kh2/' + p for p in allowed}
    for relative in allowed:
        data = z.read('kh2/' + relative)
        expected = font_manifest[relative]
        assert len(data) == int(expected['size']) and hashlib.sha256(data).hexdigest() == expected['sha256']
        replacements[relative] = data
for r in manifest:
    relative = r['path'].replace('\\', '/')
    if relative in replacements:
        data = replacements[relative]
        path = args.out / 'kh2' / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        r.update(size=str(len(data)), sha256=hashlib.sha256(data).hexdigest())
    else:
        generated = args.out / 'kh2' / relative
        source = generated if generated.is_file() else ROOT / 'build/payload/kh2' / relative
        assert source.stat().st_size == int(r['size'])
        with source.open('rb') as stream:
            assert hashlib.file_digest(stream, 'sha256').hexdigest() == r['sha256'], relative
with manifest_path.open('w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['path', 'size', 'sha256'], delimiter='\t', lineterminator='\n')
    writer.writeheader()
    writer.writerows(manifest)
print('Full payload: 798 files verified; natural-proportion font files integrated with corrected message bars')
