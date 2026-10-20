"""Move green-row text anchors while preserving every original drawable record."""
import csv
import hashlib
import json
import struct
import urllib.request
import zlib
from green_anchor import build as anchor_build
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
    check(text_y == 10, 'Unexpected anchor displacement')
    table, _, groups = layout(data)
    check(all(struct.unpack_from('<i', data, table + group * 36 + 20)[0] == 0 for group in groups),
          'Unexpected existing text Y')
    return anchor_build(data)[0]


def source_layout(entry, entries, commit):
    cache = ROOT / 'build/layout-source' / entry['path']
    if not cache.exists():
        if 'delta' in entry:
            delta = (ROOT / entry['delta']).read_bytes()
            check(hashlib.sha256(delta).hexdigest() == entry['delta_sha256'], 'Layout delta SHA256 mismatch')
            check(delta[:4] == b'XOR1' and struct.unpack_from('<I', delta, 4)[0] == entry['size'], 'Invalid layout delta')
            base = source_layout(entries[entry['base']], entries, commit)
            difference = zlib.decompress(delta[8:])
            check(len(difference) == max(len(base), entry['size']), 'Invalid layout delta length')
            data = bytes(a ^ b for a, b in zip(base.ljust(len(difference), b'\0'), difference))[:entry['size']]
        else:
            url = 'https://raw.githubusercontent.com/exelight7/KH2FM_AR/' + commit + '/' + entry['path']
            with urllib.request.urlopen(url, timeout=60) as response:
                data = response.read()
        check(len(data) == entry['size'] and hashlib.sha256(data).hexdigest() == entry['sha256'], 'Source layout SHA256 mismatch')
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_bytes(data)
    data = cache.read_bytes()
    check(len(data) == entry['size'] and hashlib.sha256(data).hexdigest() == entry['sha256'], 'Source layout SHA256 mismatch')
    return data


def main():
    config = json.loads((ROOT / 'build/config/green-command-layout.json').read_text())
    check(config['groups'] == [0, 1, 2, 3, 5] and config['text_y'] == 10, 'Unexpected layout policy')
    check(len(config['files']) == 31, 'Expected all 31 world layouts')
    entries = {entry['path']: entry for entry in config['files']}
    out = ROOT / 'build/out'
    rows = list(csv.DictReader((out / 'MANIFEST.tsv').open(), delimiter='\t'))
    existing = {r['path'].replace('\\', '/'): r for r in rows}
    reports = []
    for entry in config['files']:
        relative = entry['path']
        data = source_layout(entry, entries, config['commit'])
        layout(data)
        result, proof = anchor_build(data)
        check(patch(data, config['text_y']) == result, 'Anchor build is not deterministic')
        target = out / 'kh2' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(result)
        row = {'path': relative, 'size': str(len(result)), 'sha256': hashlib.sha256(result).hexdigest()}
        if relative in existing:
            existing[relative].update(row)
        else:
            rows.append(row)
        table, count, groups = layout(data)
        reports.append({**row, **proof, 'groups': groups, 'group_count': count})
    with (out / 'MANIFEST.tsv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['path', 'size', 'sha256'], delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    report = {'version': '2.0.1', 'source_commit': config['commit'], 'files': reports,
              'frame_geometry_unchanged': True, 'message_bytes_and_font_unchanged': True,
              'primary_rows_and_button_state_unchanged': True, 'in_game_verified': False}
    (ROOT / 'build/report/GREEN_COMMAND_LAYOUT.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Green row: 31 layouts; invisible active anchors; all original drawable records preserved')


if __name__ == '__main__':
    main()
