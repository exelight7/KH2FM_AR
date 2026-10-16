#!/usr/bin/env python3
"""Make the Arabic dialogue font (evt atlas) smaller, then apply the 1.0.6 corrections.

The 1.0.5 dialogue coverage of every Arabic cell is scaled by SCALE about the
cell origin (x) and the connecting stroke (y), the connecting bridges are
redrawn at full strength on the same rows, and the advances are scaled the same
way. The 1.0.6 tool (../../outline-baseline/sources/fix_font.py) then adds the
ring, moves the native glyphs to the baseline and re-encodes SD. The menu atlas
(sys) and the native glyphs keep their size; no line gets wider.

Input: experiments/fonts/alef-spacing/font-overlay.zip (v1.0.5), SHA-checked.
Needs Python 3.12, Pillow and NumPy.
"""
import argparse
import csv
import importlib.util
import io
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location('fix_font', ROOT / 'experiments/fonts/outline-baseline/sources/fix_font.py')
F = importlib.util.module_from_spec(spec)
spec.loader.exec_module(F)
A, W = F.A, F.W

SCALE = 0.9            # dialogue Arabic glyphs and their advances
SUPERSAMPLE = 4


def scale_tile(alpha, anchor_y):
    """Scale a coverage tile by SCALE about (0, anchor_y), supersampled."""
    h, w = alpha.shape
    big = Image.fromarray(alpha).resize((w * SUPERSAMPLE, h * SUPERSAMPLE), Image.Resampling.LANCZOS)
    y0 = anchor_y * SUPERSAMPLE
    # Output pixel (x, y) samples the input at (x / s, y0 + (y - y0) / s).
    big = big.transform(big.size, Image.Transform.AFFINE,
                        (1 / SCALE, 0, 0, 0, 1 / SCALE, y0 - y0 / SCALE), resample=Image.Resampling.BICUBIC)
    return np.array(big.reduce(SUPERSAMPLE))


def shrink(source):
    """Return a copy of the v1.0.5 overlay with smaller dialogue glyphs and advances."""
    g = F.GEOMETRY['evt']
    allocation = list(csv.DictReader((ROOT / 'build/tables/allocation.tsv').open(encoding='utf-8-sig'), delimiter='\t'))
    forms = {int(r['cell']): r['formName'] for r in allocation}
    forms[A.LIG] = 'ISO'
    hd = np.array(Image.open(io.BytesIO(source['evt'])).convert('RGBA'))
    info = bytearray(source['info'])
    offset, size = F.entries(source['info'])['evt']
    advance = bytes(info[offset:offset + size])
    ini = [c for c, f in forms.items() if f == 'INI']
    band = sorted(set.intersection(*(set(np.nonzero(hd[F.cell_slice(c, g, 2)][:, 0, 3] >= 128)[0]) for c in ini)))
    assert len(band) == 3
    anchor = (band[0] + band[-1] + 1) / 2          # centre of the connecting stroke
    changes = []
    for c, form in sorted(forms.items()):
        tile = hd[F.cell_slice(c, g, 2)]
        old = int(advance[c])
        new = max(1, round(old * SCALE))
        alpha = scale_tile(tile[:, :, 3], anchor)
        # Redraw the connecting bridges on the original rows, as font_lab drew them.
        for y in band:
            xs = np.flatnonzero(alpha[y] >= 96)
            if not len(xs):
                continue
            if form in ('INI', 'MED'):
                alpha[y, :xs[0] + 1] = 255
            if form in ('FIN', 'MED'):
                alpha[y, xs[-1]:min(alpha.shape[1], new * 2 + 2)] = 255
        tile[:, :, 3] = alpha
        tile[:, :, :3] = np.where(alpha[:, :, None] > 0, F.BODY_RGB, 0)
        info[offset + c] = new          # advance table of the evt atlas, one byte per cell
        changes.append((c, old, new))
    buf = io.BytesIO()
    Image.fromarray(hd, 'RGBA').save(buf, format='PNG')
    return dict(source, evt=buf.getvalue(), info=bytes(info)), changes


def collisions(out):
    """Glyph bodies of neighbouring letters that do not join must not touch."""
    g = F.GEOMETRY['evt']
    hd = out['evt_pixels']
    off, size = F.entries(out['info'])['evt']
    advance = out['info'][off:off + size]
    allocation = list(csv.DictReader((ROOT / 'build/tables/allocation.tsv').open(encoding='utf-8-sig'), delimiter='\t'))
    forms = {int(r['cell']): r['formName'] for r in allocation}
    forms[A.LIG] = 'ISO'
    touching = 0
    for (a, b), count in F.used_text_cells()['evt'].items():
        if forms.get(a) not in ('ISO', 'INI') or b not in forms:
            continue
        ta, tb = hd[F.cell_slice(a, g, 2)], hd[F.cell_slice(b, g, 2)]
        shift = advance[a] * 2
        width = ta.shape[1] - shift
        if width > 0 and np.any((ta[:, shift:, 0] >= 96) & (tb[:, :width, 0] >= 96)):
            touching += count
    assert touching == 0, touching
    return touching


def widths(before_info, after_info):
    """Widest line of every evt-atlas row of the shipped text, before and after."""
    rows = [(r['bar'], r['id'], r['AR']) for p in sorted((ROOT / 'review').glob('*.csv'))
            for r in csv.DictReader(p.open(encoding='utf-8-sig'))]
    fixed = {(r['bar'], r['id']): r['AR_new'] for p in sorted((ROOT / 'corrections').glob('*.csv'))
             for r in csv.DictReader(p.open(encoding='utf-8-sig')) if r.get('AR_new') and 'needs_width' not in p.name}
    tables = {}
    for name, data in (('before', before_info), ('after', after_info)):
        off, size = F.entries(data)['evt']
        tables[name] = data[off:off + size]
    narrower = same = wider = 0
    for bar, msg_id, text in rows:
        if A.BAR_OPTS[bar][0] != 'evt':
            continue
        try:
            raw = A.encode(fixed.get((bar, msg_id), text), A.use_lig(bar, int(msg_id))) + b'\0'
        except (KeyError, ValueError):
            continue
        b, a = W.maxw(raw, tables['before']), W.maxw(raw, tables['after'])
        narrower += a < b
        same += a == b
        wider += a > b
    assert wider == 0
    return {'rows': narrower + same, 'narrower': narrower, 'unchanged': same, 'wider': wider}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', type=Path, default=HERE)
    ap.add_argument('--verify', action='store_true', help='rebuild and compare with the committed overlay')
    args = ap.parse_args()
    source = F.load_overlay(F.SOURCE_DIR / 'font-overlay.zip')
    small, changes = shrink(source)
    out, report = F.build(small)
    if args.verify:
        committed = F.pixels(args.out / 'font-overlay.zip')
        for key in F.PATHS:
            if key in F.GEOMETRY:
                assert np.array_equal(out[key + '_pixels'], committed[key]), key
            else:
                assert out[key] == committed[key], key
        print('Font overlay reproduced: identical pixels and BAR bytes')
        return
    report['atlases']['evt']['touching_unjoined_pairs'] = collisions(out)
    files = F.write(out, args.out)
    report.update({
        'version': '1.0.7',
        'input_overlay_sha256': F.sha((F.SOURCE_DIR / 'font-overlay.zip').read_bytes()),
        'dialogue_scale': SCALE,
        'dialogue_advances_changed': sum(o != n for _, o, n in changes),
        'width_scan_evt': widths(source['info'], out['info']),
        'native_shift_hd_px': F.SHIFT_HD,
        'overlay_files': {name: F.sha(data) for name, data in sorted(files.items())},
        'in_game_verified': False,
    })
    (args.out / 'report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    previous, _ = F.build(source)       # the 1.0.6 font, for the comparison sheet
    F.preview(previous, out, 'evt', args.out / 'comparison-dialogue.png', labels=('1.0.6', '1.0.7'))
    print(json.dumps({k: v for k, v in report.items() if k != 'overlay_files'}, ensure_ascii=False)[:2000])


if __name__ == '__main__':
    main()
