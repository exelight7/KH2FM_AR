#!/usr/bin/env python3
"""Lower HD menu bodies another texel; retain the two deepest ya dot groups.

Two ya forms already put their lower dots on the last cell row. Keep those
dot groups at their original Y while moving the body down one texel. Every
body and dot pixel is retained, with no rescaling or message positioning.
"""
import argparse
import csv
import importlib.util
import io
import json
from pathlib import Path
import zipfile

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
SOURCE = ROOT / 'experiments/fonts/menu-fine-alignment'
spec = importlib.util.spec_from_file_location('font_formats', ROOT / 'experiments/fonts/outline-baseline/sources/fix_font.py')
F = importlib.util.module_from_spec(spec)
spec.loader.exec_module(F)
YA = {20, 31}


def components(tile):
    mask = tile[:, :, 3] >= 128
    seen, sizes = set(), []
    for y, x in zip(*np.nonzero(mask)):
        if (y, x) in seen:
            continue
        queue, size = [(y, x)], 0
        seen.add((y, x))
        while queue:
            yy, xx = queue.pop()
            size += 1
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                point = yy + dy, xx + dx
                if 0 <= point[0] < 48 and 0 <= point[1] < 36 and mask[point] and point not in seen:
                    seen.add(point)
                    queue.append(point)
        sizes.append(size)
    return sorted(sizes)


def build():
    archive = SOURCE / 'font-overlay.zip'
    expected = next(line.split()[0] for line in (SOURCE / 'SHA256SUMS.txt').read_text().splitlines()
                    if line.split(maxsplit=1)[1] == 'font-overlay.zip')
    assert F.sha(archive.read_bytes()) == expected
    previous = F.pixels(archive)
    with zipfile.ZipFile(archive) as z:
        out = {name: z.read(path) for name, path in F.PATHS.items()}
    out['sys_pixels'], out['evt_pixels'] = previous['sys'].copy(), previous['evt']
    _, count = F.entries(previous['info'])['sys']
    moved, retained_dots = 0, []
    for cell in range(count):
        region = F.cell_slice(cell, F.GEOMETRY['sys'], 2)
        before = previous['sys'][region]
        after = np.zeros_like(before)
        if cell in YA:
            # The source-pinned ya body ends at row 42; the dots start at 44.
            assert not before[43, :, 3].any()
            assert before[44:, :, 3].any() and before[-1, :, 3].any()
            after[1:44] = before[:43]
            after[44:] = before[44:]
            assert np.array_equal(after[1:44], before[:43])
            assert np.array_equal(after[44:], before[44:])
            old_parts, new_parts = components(before), components(after)
            assert old_parts == new_parts and len(new_parts) == 3
            retained_dots.append({'cell': cell, 'dot_rows': [44, 47], 'opaque_component_sizes': new_parts})
        else:
            assert not before[-1, :, 3].any(), (cell, 'would clip visible ink')
            after[1:] = before[:-1]
            assert np.array_equal(after[1:], before[:-1])
        assert not after[0].any()
        assert int(before[:, :, 3].sum()) == int(after[:, :, 3].sum())
        assert np.count_nonzero(before[:, :, 3]) == np.count_nonzero(after[:, :, 3])
        out['sys_pixels'][region] = after
        moved += bool(before[:, :, 3].any())
    assert moved == 264 and len(retained_dots) == 2
    buf = io.BytesIO()
    Image.fromarray(out['sys_pixels']).save(buf, format='PNG')
    out['sys'] = buf.getvalue()
    for name in ('image', 'info', 'evt'):
        with zipfile.ZipFile(archive) as z:
            assert out[name] == z.read(F.PATHS[name])
    report = {'version': '1.0.18', 'hd_body_translation_down_pixels': 1,
              'nonempty_cells_shifted': moved, 'visible_pixels_clipped': 0,
              'body_and_dot_shapes_unchanged': True, 'retained_ya_dots': retained_dots,
              'ya_dot_gap_reduced_hd_pixels': 1, 'advances_byte_identical': True,
              'native_sd_byte_identical': True, 'dialogue_byte_identical': True,
              'message_position_commands_added': 0, 'in_game_verified': False}
    forms = {int(r['cell']): r['formName'] for r in csv.DictReader(
        (ROOT / 'build/tables/allocation.tsv').open(), delimiter='\t')}
    off, length = F.entries(out['info'])['sys']
    report['arabic_joins'] = F.join_check('sys', F.GEOMETRY['sys'], out['sys_pixels'],
                                        out['info'][off:off + length], forms, F.used_text_cells()['sys'])
    report['baseline'] = F.baseline_check('sys', F.GEOMETRY['sys'], out['sys_pixels'], forms)
    return out, previous, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    out, previous, report = build()
    if args.verify:
        with zipfile.ZipFile(HERE / 'font-overlay.zip') as z:
            for name, path in F.PATHS.items():
                assert z.read(path) == out[name], name
        print('HD bodies down one texel; every ink pixel retained; ya dots intact and separate; metrics, SD and dialogue unchanged')
        return
    files = F.write(out, HERE)
    (HERE / 'SHA256SUMS.txt').write_text(F.sha((HERE / 'font-overlay.zip').read_bytes()) + '  font-overlay.zip\n')
    report['files'] = {name: F.sha(data) for name, data in files.items()}
    (HERE / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    F.PREVIEWS['sys'] = (['انطلق للإنقاذ', 'حفظ', 'تحدث', 'في يدي'],
                         [((18, 65, 28), (255, 255, 255))])
    F.preview({'info': previous['info'], 'sys_pixels': previous['sys']}, out,
              'sys', HERE / 'comparison-alignment.png', labels=('1.0.17', '1.0.18'))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
