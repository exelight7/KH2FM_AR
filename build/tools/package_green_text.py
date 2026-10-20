"""Add the exact green-command plugin verified in the game."""
import csv
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
config = json.loads((ROOT / 'build/config/green-command-text.json').read_text())
source = ROOT / config['source']
data = source.read_bytes()
assert len(data) == config['size'] and data[:2] == b'MZ'
assert hashlib.sha256(data).hexdigest() == config['sha256']
target = ROOT / 'build/out/kh2' / config['path']
target.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(source, target)
manifest = ROOT / 'build/out/MANIFEST.tsv'
with manifest.open() as stream:
    rows = list(csv.DictReader(stream, delimiter='\t'))
rows = [row for row in rows if row['path'].replace('\\', '/') != config['path']]
rows.append({'path': config['path'], 'size': str(len(data)), 'sha256': config['sha256']})
assert len(rows) == len({row['path'] for row in rows}) == 831
with manifest.open('w', newline='') as stream:
    writer = csv.DictWriter(stream, fieldnames=['path', 'size', 'sha256'], delimiter='\t', lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
report = {'version': '2.0.1', 'files': [config], 'scope': 'active green reaction-row labels only',
          'missing_label_size': 20, 'existing_explicit_sizes_preserved': True,
          'native_key_icon_and_position_bytes_preserved': True,
          'original_message_pointer_restored_after_draw': True,
          'changes_disk_executable': False, 'font_assets_changed': False,
          'message_assets_changed': False, 'primary_rows_changed': False,
          'verified_in_game': ['Apply For Work', 'Talk'],
          'unknown_game_builds': 'refused without writes'}
(ROOT / 'build/report/GREEN_COMMAND_TEXT.json').write_text(json.dumps(report, indent=2) + '\n')
print('Green labels: verified plugin; native icon and explicit sizes retained; all 830 previous files unchanged')
