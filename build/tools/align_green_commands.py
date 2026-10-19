"""Adjust only the text Y of the five green-row animation states in each world."""
import csv
import hashlib
import json
import struct
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def check(condition, message):
    if not condition:
        raise ValueError(message)


def layout(data):
    check(len(data) >= 48 and data[:4] == b'BAR\x01', 'Invalid BAR header')
    count = struct.unpack_from('<I', data, 4)[0]
    check(count == 2, 'Expected image and sequence entries')
    entries = [struct.unpack_from('<I4sII', data, 16 + i * 16) for i in range(count)]
    for kind, name, offset, size in entries:
        check(offset >= 48 and size > 0 and offset + size <= len(data), 'Invalid BAR bounds')
    check([e[0] for e in entries] == [24, 25], 'Unexpected BAR entry types')
    _, _, base, length = entries[1]
    check(data[base:base + 4] == b'SEQD' and length >= 52, 'Invalid SEQD header')
    sections = [struct.unpack_from('<II', data, base + 8 + 8 * i) for i in range(5)]
    ends = []
    for (count, offset), size in zip(sections, (44, 20, 4, 144, 36)):
        check(count > 0 and offset >= 48 and offset + count * size <= length, 'Invalid SEQD table bounds')
        ends.append((offset, offset + count * size))
    check(all(a[1] <= b[0] for a, b in zip(ends, ends[1:])), 'Overlapping SEQD tables')
    (ns, os), (np, op), (nf, of), (na, oa), (ng, og) = sections

    def animation(index):
        check(0 <= index < na, 'Animation index out of bounds')
        flags, group = struct.unpack_from('<ii', data, base + oa + index * 144)
        check(0 <= group < nf, 'Sprite group index out of bounds')
        start, count = struct.unpack_from('<hh', data, base + of + group * 4)
        check(start >= 0 and count >= 0 and start + count <= np, 'Sprite part range out of bounds')
        sprites = {struct.unpack_from('<i', data, base + op + i * 20 + 16)[0]
                   for i in range(start, start + count)}
        check(all(0 <= i < ns for i in sprites), 'Sprite index out of bounds')
        return flags, sprites

    first = struct.unpack_from('<h', data, base + og)[0]
    flags, green = animation(first)
    check(flags & 2 and green, 'Missing green frame anchor')
    groups = []
    for index in range(ng):
        start, count = struct.unpack_from('<hh', data, base + og + index * 36)
        check(start >= 0 and count >= 0 and start + count <= na, 'Animation range out of bounds')
        if any(flags & 2 and green <= sprites
               for flags, sprites in (animation(i) for i in range(start, start + count))):
            groups.append(index)
    check(groups == [0, 1, 2, 3, 5], 'Unexpected green-row states')
    return base + og, ng, groups


def patch(data, text_y):
    table, count, groups = layout(data)
    result = bytearray(data)
    changed = set()
    for group in groups:
        offset = table + group * 36 + 0x14
        old = struct.unpack_from('<i', data, offset)[0]
        check(old in (0, text_y), 'Unexpected existing text Y')
        struct.pack_into('<i', result, offset, text_y)
        changed.update(range(offset, offset + 4))
    check(all(a == b or i in changed for i, (a, b) in enumerate(zip(data, result))),
          'Changed bytes outside text Y fields')
    check(layout(result) == (table, count, groups), 'Layout changed after patch')
    return bytes(result)


def main():
    config = json.loads((ROOT / 'build/config/green-command-layout.json').read_text())
    check(config['groups'] == [0, 1, 2, 3, 5] and config['text_y'] == 10, 'Unexpected layout policy')
    check(len(config['files']) == 27, 'Expected all 27 world layouts')
    out = ROOT / 'build/out'
    rows = list(csv.DictReader((out / 'MANIFEST.tsv').open(), delimiter='\t'))
    existing = {r['path'].replace('\\', '/'): r for r in rows}
    reports = []
    for entry in config['files']:
        relative = entry['path']
        cache = ROOT / 'build/layout-source' / relative
        if not cache.exists():
            url = 'https://raw.githubusercontent.com/exelight7/KH2FM_AR/' + config['commit'] + '/' + relative
            with urllib.request.urlopen(url, timeout=60) as response:
                data = response.read()
            check(len(data) == entry['size'] and hashlib.sha256(data).hexdigest() == entry['sha256'],
                  'Downloaded layout SHA256 mismatch: ' + relative)
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_bytes(data)
        data = cache.read_bytes()
        check(len(data) == entry['size'] and hashlib.sha256(data).hexdigest() == entry['sha256'],
              'Source layout SHA256 mismatch: ' + relative)
        result = patch(data, config['text_y'])
        check(patch(result, config['text_y']) == result, 'Layout patch is not idempotent')
        target = out / 'kh2' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(result)
        row = {'path': relative, 'size': str(len(result)), 'sha256': hashlib.sha256(result).hexdigest()}
        if relative in existing:
            existing[relative].update(row)
        else:
            rows.append(row)
        table, count, groups = layout(data)
        reports.append({**row, 'source_sha256': entry['sha256'], 'groups': groups,
                        'group_count': count, 'text_y_before': 0, 'text_y_after': config['text_y'],
                        'changed_byte_offsets': [i for i, (a, b) in enumerate(zip(data, result)) if a != b],
                        'only_text_y_changed': True})
    with (out / 'MANIFEST.tsv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['path', 'size', 'sha256'], delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    report = {'version': '1.0.20', 'source_commit': config['commit'], 'files': reports,
              'frame_geometry_unchanged': True, 'message_bytes_and_font_unchanged': True,
              'primary_rows_and_button_state_unchanged': True, 'in_game_verified': False}
    (ROOT / 'build/report/GREEN_COMMAND_LAYOUT.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Green row: 27 layouts, five text-Y fields each; all other bytes unchanged')


if __name__ == '__main__':
    main()
