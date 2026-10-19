#!/usr/bin/env python3
"""Match the oversized native colon to the Arabic menu font, in HD and SD.

Arabic glyphs retain the published 1.0.18 shapes and atlas placement.
Context-specific HUD/reaction tuning is done by enlarge_commands.py.
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
SOURCE = ROOT / 'experiments/fonts/menu-lower-baseline'
spec = importlib.util.spec_from_file_location('native_glyphs', ROOT / 'experiments/fonts/clean-joins/sources/build_font.py')
N = importlib.util.module_from_spec(spec)
spec.loader.exec_module(N)
F = N.F
COLON = 50


def build():
    archive = SOURCE / 'font-overlay.zip'
    expected = next(line.split()[0] for line in (SOURCE / 'SHA256SUMS.txt').read_text().splitlines()
                    if line.split(maxsplit=1)[1] == 'font-overlay.zip')
    assert F.sha(archive.read_bytes()) == expected
    previous = F.pixels(archive)
    with zipfile.ZipFile(archive) as z:
        out = {name: z.read(path) for name, path in F.PATHS.items()}
    hd = previous['sys'].copy()
    N.FONT = ROOT / 'experiments/fonts/menu-legibility/fonts/NotoSansArabic-CondensedMedium.ttf'
    assert F.sha(N.FONT.read_bytes()) == 'd291afc97a28d97ee0e4063e11314d091efd54261b2db2013daee31a7a6b5254'
    N.STROKE = 0
    # Same 26px Noto face as the Arabic sys glyphs. Lower dot ends on the
    # established Arabic/digit baseline (37); its width advance is retained.
    alpha, _ = N.render(26, ord(':'), 36)
    ys, xs = np.nonzero(alpha >= 8)
    x0, x1 = int(xs.min()), int(xs.max()) + 1
    off, _ = F.entries(out['info'])['sys']
    advance = out['info'][off + COLON]
    tile = np.zeros((48, 36, 4), np.uint8)
    left = (advance * 2 - (x1 - x0)) // 2
    assert left > 0 and 0 < ys.min() < ys.max() < 47
    tile[:, left:left + x1 - x0, 3] = alpha[:48, x0:x1]
    tile[:, :, :3] = np.where(tile[:, :, 3:] > 0, F.BODY_RGB, 0)
    region = F.cell_slice(COLON, F.GEOMETRY['sys'], 2)
    old = hd[region].copy()
    hd[region] = tile
    allowed = np.zeros(hd.shape[:2], bool)
    allowed[region] = True
    assert np.array_equal(hd[~allowed], previous['sys'][~allowed])
    buf = io.BytesIO()
    Image.fromarray(hd).save(buf, format='PNG')
    out['sys'] = buf.getvalue()
    image = bytearray(out['image'])
    start, size = F.entries(image)['sys']
    sd = F.unpack4(image[start:start + size], 256)
    old_sd = sd.copy()
    sd_region = F.cell_slice(COLON, F.GEOMETRY['sys'], 1)
    sd[sd_region] = F.sd_levels('sys', tile)
    sd_allowed = np.zeros(sd.shape, bool)
    sd_allowed[sd_region] = True
    assert np.array_equal(sd[~sd_allowed], old_sd[~sd_allowed])
    image[start:start + size] = F.pack4(sd)
    assert image[:start] == out['image'][:start] and image[start + size:] == out['image'][start + size:]
    out['image'] = bytes(image)
    assert out['info'] == previous['info']
    with zipfile.ZipFile(archive) as z:
        assert out['evt'] == z.read(F.PATHS['evt'])
    out.update(sys_pixels=hd, evt_pixels=previous['evt'])
    report = {'version': '1.0.19', 'colon_cell': COLON,
              'font_size_hd': 26, 'colon_advance_sd_unchanged': advance,
              'old_colon_ink_height_hd': int(np.ptp(np.nonzero(old[:, :, 3] >= 8)[0])) + 1,
              'new_colon_ink_height_hd': int(ys.max() - ys.min() + 1),
              'new_colon_bottom_hd': int(ys.max()),
              'other_hd_pixels_unchanged': True, 'other_sd_cells_unchanged': True,
              'fontinfo_byte_identical': True, 'dialogue_byte_identical': True,
              'arabic_glyphs_byte_identical': True, 'in_game_verified': False}
    return out, previous, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    out, previous, report = build()
    if args.verify:
        with zipfile.ZipFile(HERE / 'font-overlay.zip') as z:
            for key, path in F.PATHS.items():
                assert z.read(path) == out[key], key
        print('Colon reproduced in HD/SD; all other cells, advances and dialogue unchanged')
        return
    files = F.write(out, HERE)
    (HERE / 'SHA256SUMS.txt').write_text(F.sha((HERE / 'font-overlay.zip').read_bytes()) + '  font-overlay.zip\n')
    report['files'] = {name: F.sha(data) for name, data in files.items()}
    (HERE / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    F.PREVIEWS['sys'] = (['القصر: المكتبة', 'القصر: غرفة الطعام'],
                         [((36, 32, 42), (255, 255, 255))])
    F.preview({'info': previous['info'], 'sys_pixels': previous['sys']}, out,
              'sys', HERE / 'comparison-separator.png', labels=('1.0.18', '1.0.19'))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
