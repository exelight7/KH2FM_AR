"""Give reaction labels a uniform 18/16 scale without altering their text.

The game's sys 1444..1449 command-name lists identify the reaction family.
Only exact, single-line system labels from that family and the primary HUD
commands are changed. Dialogue, help descriptions and ability explanations
are never selected. Every original control byte is retained after the prefix.
"""
import csv
import hashlib
import json
import re
from pathlib import Path

import arabic_msg as A
import width as W

ROOT = Path(__file__).resolve().parents[2]
SCALE = b'\x0a\x12'


def command_ids():
    rows = [r for p in sorted((ROOT / 'review').glob('sys_*.csv'))
            for r in csv.DictReader(p.open(encoding='utf-8-sig'))]
    clean = lambda text: re.sub(r'<[^>]*>', '', text).strip()
    names = {clean(line) for row in rows if 1444 <= int(row['id']) <= 1449
             for line in row['EN'].split('⏎') if clean(line)}
    ids = {int(r['id']) for r in rows if not 1444 <= int(r['id']) <= 1449
           and '⏎' not in r['EN'] and clean(r['EN']) in names
           and all(tag.startswith('<0B ') for tag in re.findall(r'<[^>]*>', r['AR']))}
    return ids | {480, 481, 482, 483, 490, 491, 1284, 1286, 1287}


def main():
    out = ROOT / 'build/out'
    target = out / 'kh2/msg/us/sys.bar'
    before = target.read_bytes()
    messages = A.msgs(before)
    old_adv = W.advances(str(ROOT / 'build/payload/kh2/msg/us/fontinfo.bar'), 'sys')
    new_adv = W.advances(str(out / 'kh2/msg/us/fontinfo.bar'), 'sys')
    result = before
    records = []
    ids = command_ids()
    for msg_id in sorted(ids):
        raw = A.padded(messages[msg_id])
        items, _ = A.parse(raw + b'\0')
        assert not any(x[0] == 'nl' or (x[0] == 't' and x[1][0] not in (0x0b,)) for x in items), (msg_id, 'unexpected command state')
        # Compare the same corrected label against its original font budget.
        # Retained width multipliers affect both sides equally.
        width = W.maxw(raw, new_adv) * 18 / 16
        previous_width = W.maxw(raw, old_adv)
        assert width <= previous_width, (msg_id, 'larger than original label budget')
        result = A.replace_msg(result, msg_id, SCALE + raw)
        records.append({'id': msg_id, 'text': A.decode(messages[msg_id], True, False),
                        'width': width, 'original_font_budget': previous_width})
    final = A.msgs(result)
    for msg_id, raw in messages.items():
        if msg_id in ids:
            assert A.padded(final[msg_id]) == SCALE + A.padded(raw)
        else:
            assert final[msg_id] == raw
    target.write_bytes(result)
    manifest_path = out / 'MANIFEST.tsv'
    manifest = list(csv.DictReader(manifest_path.open(), delimiter='\t'))
    row = next(r for r in manifest if r['path'].replace('\\', '/') == 'msg/us/sys.bar')
    row.update(size=str(len(result)), sha256=hashlib.sha256(result).hexdigest())
    with manifest_path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['path', 'size', 'sha256'], delimiter='\t', lineterminator='\n')
        writer.writeheader(); writer.writerows(manifest)
    report = {'version': '1.0.13', 'scale': 18 / 16, 'labels': records,
              'all_other_messages_byte_identical': True, 'original_control_bytes_preserved': True,
              'all_labels_within_original_font_width_budget': True,
              'path': 'msg/us/sys.bar', 'sha256': row['sha256'], 'in_game_verified': False}
    (ROOT / 'build/report/REACTION_COMMANDS.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(f'Reaction/HUD labels: {len(records)} enlarged, original controls retained, original width budgets passed')


if __name__ == '__main__':
    main()
