#!/usr/bin/env python3
"""Translate the PC HD menu ink down one texel without any message Position.

The published atlas has one unused bottom row in the deepest cells. Move
each cell independently by exactly that amount, retaining every visible
pixel. Native SD is unchanged: the half-SD-pixel adjustment is HD-only.
"""
import argparse
import importlib.util
import io
import json
from pathlib import Path
import zipfile

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
SOURCE = ROOT / 'experiments/fonts/menu-alignment'
spec = importlib.util.spec_from_file_location('font_formats', ROOT / 'experiments/fonts/outline-baseline/sources/fix_font.py')
F = importlib.util.module_from_spec(spec)
spec.loader.exec_module(F)


def build():
    archive = SOURCE / 'font-overlay.zip'
    expected = next(line.split()[0] for line in (SOURCE / 'SHA256SUMS.txt').read_text().splitlines()
                    if line.split(maxsplit=1)[1] == 'font-overlay.zip')
    assert F.sha(archive.read_bytes()) == expected
    previous = F.pixels(archive)
    with zipfile.ZipFile(archive) as z:
        out = {name: z.read(path) for name, path in F.PATHS.items()}
    out['sys_pixels'] = previous['sys'].copy()
    out['evt_pixels'] = previous['evt']
    _, count = F.entries(previous['info'])['sys']
    moved = 0
    margins = []
    for cell in range(count):
        region = F.cell_slice(cell, F.GEOMETRY['sys'], 2)
        before = previous['sys'][region]
        assert not before[-1, :, 3].any(), (cell, 'would clip visible ink')
        after = np.zeros_like(before)
        after[1:] = before[:-1]
        out['sys_pixels'][region] = after
        assert np.array_equal(after[1:], before[:-1])
        assert not after[0].any()
        assert int(before[:, :, 3].sum()) == int(after[:, :, 3].sum())
        assert np.count_nonzero(before[:, :, 3]) == np.count_nonzero(after[:, :, 3])
        if before[:, :, 3].any():
            moved += 1
            margins.append(47 - int(np.flatnonzero(after[:, :, 3].any(axis=1)).max()))
    buf = io.BytesIO()
    Image.fromarray(out['sys_pixels']).save(buf, format='PNG')
    out['sys'] = buf.getvalue()
    for name in ('image', 'info', 'evt'):
        with zipfile.ZipFile(archive) as z:
            assert out[name] == z.read(F.PATHS[name])
    report = {'version': '1.0.17', 'hd_translation_down_pixels': 1,
              'nonempty_cells_shifted': moved, 'visible_pixels_clipped': 0,
              'glyph_ink_and_dimensions_unchanged': True,
              'advances_byte_identical': True, 'native_sd_byte_identical': True,
              'dialogue_byte_identical': True, 'message_position_commands_added': 0,
              'minimum_bottom_padding_hd': min(margins), 'in_game_verified': False}
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
        print('HD menu ink translated down exactly one texel; no clipped ink; SD, metrics and dialogue byte-identical')
        return
    files = F.write(out, HERE)
    (HERE / 'SHA256SUMS.txt').write_text(F.sha((HERE / 'font-overlay.zip').read_bytes()) + '  font-overlay.zip\n')
    report['files'] = {name: F.sha(data) for name, data in files.items()}
    (HERE / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    F.PREVIEWS['sys'] = (['انطلق للإنقاذ', 'حفظ', 'هجوم', 'أغراض 15'],
                         [((18, 65, 28), (255, 255, 255))])
    F.preview({'info': previous['info'], 'sys_pixels': previous['sys']}, out,
              'sys', HERE / 'comparison-alignment.png', labels=('1.0.16', '1.0.17'))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
