#!/usr/bin/env python3
"""Lower the shared menu baseline without changing size, spacing or messages.

Both HD and SD glyphs move by the same two SD pixels. Each cell is translated
independently with transparent padding, so pixels cannot wrap into adjacent
cells. All system glyphs move together to preserve Arabic/digit baselines.
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
SOURCE = ROOT / 'experiments/fonts/menu-legibility'
spec = importlib.util.spec_from_file_location('font_formats', ROOT / 'experiments/fonts/outline-baseline/sources/fix_font.py')
F = importlib.util.module_from_spec(spec)
spec.loader.exec_module(F)
SHIFT_SD, SHIFT_HD = 2, 4


def shifted(tile, amount):
    visible = tile[:, :, 3] if tile.ndim == 3 else tile
    assert not visible[-amount:].any(), 'Translation would clip existing glyph pixels'
    result = np.zeros_like(tile)
    result[amount:] = tile[:-amount]
    assert np.array_equal(result[amount:], tile[:-amount])
    assert not result[:amount].any()
    return result


def build():
    archive = SOURCE / 'font-overlay.zip'
    expected = next(line.split()[0] for line in (SOURCE / 'SHA256SUMS.txt').read_text().splitlines()
                    if line.split(maxsplit=1)[1] == 'font-overlay.zip')
    assert F.sha(archive.read_bytes()) == expected
    previous = F.pixels(archive)
    out = {'info': previous['info'], 'evt_pixels': previous['evt'], 'sys_pixels': previous['sys'].copy()}
    image = bytearray(previous['image'])
    off, length = F.entries(image)['sys']
    original_sd = F.unpack4(image[off:off + length], 256)
    sd = original_sd.copy()
    _, count = F.entries(previous['info'])['sys']
    g = F.GEOMETRY['sys']
    moved, margins = 0, []
    for cell in range(count):
        region_hd, region_sd = F.cell_slice(cell, g, 2), F.cell_slice(cell, g, 1)
        old_hd, old_sd = previous['sys'][region_hd], original_sd[region_sd]
        out['sys_pixels'][region_hd] = shifted(old_hd, SHIFT_HD)
        sd[region_sd] = shifted(old_sd, SHIFT_SD)
        if old_hd[:, :, 3].any():
            moved += 1
            ys = np.flatnonzero(out['sys_pixels'][region_hd][:, :, 3].any(axis=1))
            margins.append(47 - int(ys.max()))
            assert int(old_hd[:, :, 3].sum()) == int(out['sys_pixels'][region_hd][:, :, 3].sum())
        assert int(old_sd.sum()) == int(sd[region_sd].sum())
    image[off:off + length] = F.pack4(sd)
    out['image'] = bytes(image)
    buf = io.BytesIO()
    Image.fromarray(out['sys_pixels']).save(buf, format='PNG')
    out['sys'] = buf.getvalue()
    with zipfile.ZipFile(archive) as z:
        out['evt'] = z.read(F.PATHS['evt'])
    # Every other BAR entry and all advance bytes retain the published values.
    assert out['info'] == previous['info']
    for name, (start, size) in F.entries(previous['image']).items():
        if name != 'sys':
            assert out['image'][start:start + size] == previous['image'][start:start + size]
    report = {'version': '1.0.13', 'shift_sd_pixels': SHIFT_SD, 'shift_hd_pixels': SHIFT_HD,
              'nonempty_system_cells_shifted': moved, 'minimum_hd_bottom_padding': min(margins),
              'glyph_pixels_clipped': 0, 'glyph_size_and_ink_unchanged': True,
              'advances_byte_identical': True, 'dialogue_byte_identical': True,
              'message_scale_unchanged': '18/16 from 1.0.12', 'in_game_verified': False}
    return out, previous, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    out, previous, report = build()
    if args.verify:
        committed = F.pixels(HERE / 'font-overlay.zip')
        for key in F.PATHS:
            if key in F.GEOMETRY:
                assert np.array_equal(out[key + '_pixels'], committed[key]), key
            else:
                assert out[key] == committed[key], key
        print('Menu alignment reproduced: exact HD/SD translation, zero clipped pixels, unchanged size/spacing/dialogue')
        return
    files = F.write(out, HERE)
    (HERE / 'SHA256SUMS.txt').write_text(F.sha((HERE / 'font-overlay.zip').read_bytes()) + '  font-overlay.zip\n')
    report['files'] = {name: F.sha(data) for name, data in files.items()}
    (HERE / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    before = {'info': previous['info'], 'sys_pixels': previous['sys']}
    F.PREVIEWS['sys'] = (['انطلق للإنقاذ', 'افحص الجدار', 'هجوم', 'أغراض 15'],
                         [((18, 65, 28), (255, 255, 255))])
    F.preview(before, out, 'sys', HERE / 'comparison-alignment.png', labels=('1.0.12', '1.0.13'))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
