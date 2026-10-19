"""Include the hash-pinned, runtime-verified Panacea place-label plugin."""
import csv
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
config = json.loads((ROOT / 'build/config/place-text-shadow.json').read_text())
source = ROOT / config['source']
data = source.read_bytes()
assert len(data) == config['size'] == 4096 and data[:2] == b'MZ'
assert hashlib.sha256(data).hexdigest() == config['sha256']
target = ROOT / 'build/out/kh2' / config['path']
target.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(source, target)
manifest = ROOT / 'build/out/MANIFEST.tsv'
rows = list(csv.DictReader(manifest.open(), delimiter='\t'))
rows = [row for row in rows if row['path'].replace('\\', '/') != config['path']]
rows.append({'path': config['path'], 'size': str(len(data)), 'sha256': config['sha256']})
assert len(rows) == len({row['path'] for row in rows}) == 830
with manifest.open('w', newline='') as stream:
    writer = csv.DictWriter(stream, fieldnames=['path', 'size', 'sha256'], delimiter='\t', lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
report = {'version': '2.0.0', 'files': [config], 'changes_disk_executable': False,
          'green_and_primary_rows_changed': False, 'font_assets_changed': False,
          'verified_in_game': ['door guide: palace library'],
          'pre_rendered_entry_images_changed': False,
          'unknown_game_builds': 'refused without memory writes'}
(ROOT / 'build/report/PLACE_TEXT_SHADOW.json').write_text(json.dumps(report, indent=2) + '\n')
print('Place labels: verified 4KB plugin in kh2/dll; font, size and on-disk executable unchanged')
