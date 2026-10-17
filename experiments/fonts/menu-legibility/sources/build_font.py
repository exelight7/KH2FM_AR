#!/usr/bin/env python3
"""Larger menu/reaction glyphs; keep the published dialogue atlas unchanged."""
import argparse
import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location('native_joins', ROOT / 'experiments/fonts/clean-joins/sources/build_font.py')
N = importlib.util.module_from_spec(spec)
spec.loader.exec_module(N)
F = N.F
SOURCE = ROOT / 'experiments/fonts/clean-joins'
SIZE, STROKE = 26, 0  # Native Medium weight, rather than a synthetic stroke.
FONT = HERE / 'fonts/NotoSansArabic-CondensedMedium.ttf'


def build():
    archive = SOURCE / 'font-overlay.zip'
    expected = next(line.split()[0] for line in (SOURCE / 'SHA256SUMS.txt').read_text().splitlines()
                    if line.split(maxsplit=1)[1] == 'font-overlay.zip')
    assert F.sha(archive.read_bytes()) == expected
    assert F.sha(FONT.read_bytes()) == 'd291afc97a28d97ee0e4063e11314d091efd54261b2db2013daee31a7a6b5254'
    previous = F.pixels(archive)
    out = {key: previous[key] for key in ('info', 'image')}
    out.update({a + '_pixels': previous[a].copy() for a in F.GEOMETRY})
    info, image = bytearray(out['info']), bytearray(out['image'])
    off, count = F.entries(info)['sys']
    img_off, img_size = F.entries(image)['sys']
    sd = F.unpack4(image[img_off:img_off + img_size], 256)
    g = F.GEOMETRY['sys']
    N.STROKE = STROKE
    N.FONT = FONT
    records = []
    for row in N.ALLOC:
        cell, cp, form = int(row['cell']), int(row['pfCode'], 16), row['formName']
        alpha, _ = N.render(SIZE, cp, 30)
        ys, xs = np.nonzero(alpha >= 8)
        left, right = int(xs.min()), int(xs.max()) + 1
        # Keep the native stem and natural join on a shared baseline. No
        # per-letter stretching, synthetic horizontal bridges or hard clipping.
        origin = 20 if form in ('INI', 'MED') else left - 2
        mask = np.zeros((48, 36), np.uint8)
        width = right - origin
        assert 0 < width <= 35 and 0 < int(ys.min()) and int(ys.max()) < 47, (cell, 'clipped glyph')
        mask[:, :width] = alpha[:48, origin:right]
        stroke = mask[29:32].max(axis=0)
        ends = np.flatnonzero(stroke >= 128)
        if form in ('FIN', 'MED'):
            # The rightmost native connector, rather than the letter body,
            # determines where the next letter starts.
            assert len(ends)
            advance = max(1, int(ends[-1]) // 2)
        else:
            advance = math.ceil((width + 3) / 2)
        assert form in ('ISO', 'INI') or advance < 18, (cell, 'connector outside cell')
        info[off + cell] = advance
        tile = out['sys_pixels'][F.cell_slice(cell, g, 2)]
        tile[:, :, 3] = mask
        tile[:, :, :3] = np.where(mask[:, :, None] > 0, F.BODY_RGB, 0)
        small = F.sd_levels('sys', tile)
        for x in ([0] if form in ('INI', 'MED') else []) + ([advance] if form in ('FIN', 'MED') else []):
            coverage = mask[:, x * 2:x * 2 + 2]
            rows = np.flatnonzero(coverage.max(axis=1) >= 96)
            assert len(rows), (cell, 'no SD connector')
            y = int(rows[len(rows) // 2]) // 2
            small[y, x] = max(2, small[y, x])
        sd[F.cell_slice(cell, g, 1)] = small
        records.append({'cell': cell, 'form': form, 'advance': advance,
                        'body_top': int(ys.min()), 'body_bottom': int(ys.max()),
                        'previous_ink_pixels': int((previous['sys'][F.cell_slice(cell, g, 2)][:, :, 3] >= 128).sum()),
                        'ink_pixels': int((mask >= 128).sum())})
    image[img_off:img_off + img_size] = F.pack4(sd)
    out.update(info=bytes(info), image=bytes(image))
    import io
    for atlas in F.GEOMETRY:
        buf = io.BytesIO()
        Image.fromarray(out[atlas + '_pixels']).save(buf, format='PNG')
        out[atlas] = buf.getvalue()
    # Byte identity matters for the untouched dialogue PNG too.
    import zipfile
    with zipfile.ZipFile(archive) as z:
        out['evt'] = z.read(F.PATHS['evt'])
    return out, previous, records


def verify(out, previous, records):
    forms = {int(r['cell']): r['formName'] for r in N.ALLOC}
    off, count = F.entries(out['info'])['sys']
    adv = out['info'][off:off + count]
    old = previous['info'][off:off + count]
    img_off, img_size = F.entries(out['image'])['sys']
    sd = F.unpack4(out['image'][img_off:img_off + img_size], 256)
    joined = separated = 0
    for a, b in F.used_text_cells()['sys']:
        if a not in forms or b not in forms:
            continue
        shift = adv[a] * 2
        ta, tb = (out['sys_pixels'][F.cell_slice(c, F.GEOMETRY['sys'], 2)][:, :, 3] for c in (a, b))
        if forms[a] in ('FIN', 'MED') and forms[b] in ('INI', 'MED'):
            joined += 1
            assert np.any((ta[:, shift:] >= 128) & (tb[:, :36 - shift] >= 128)), (a, b, 'broken HD join')
            sa, sb = (sd[F.cell_slice(c, F.GEOMETRY['sys'], 1)] for c in (a, b))
            assert np.any((sa[:, adv[a]:] >= 2) & (sb[:, :18 - adv[a]] >= 2)), (a, b, 'broken SD join')
        elif forms[a] in ('ISO', 'INI'):
            separated += 1
            assert shift >= 36 or not np.any((ta[:, shift:] >= 128) & (tb[:, :36 - shift] >= 128)), (a, b, 'unjoined bodies touch')
    for cell in range(count):
        if cell not in forms:
            assert adv[cell] == old[cell]
            assert np.array_equal(out['sys_pixels'][F.cell_slice(cell, F.GEOMETRY['sys'], 2)], previous['sys'][F.cell_slice(cell, F.GEOMETRY['sys'], 2)])
    for key in ('info', 'image'):
        for entry, (start, size) in F.entries(previous[key]).items():
            if entry != 'sys':
                assert out[key][start:start + size] == previous[key][start:start + size]
    assert np.array_equal(out['evt_pixels'], previous['evt'])
    frozen = (ROOT / 'build/payload/kh2/msg/us/fontinfo.bar').read_bytes()
    start, size = F.entries(frozen)['sys']
    original_adv = frozen[start:start + size]
    fixed = {(r['bar'], r['id']): r['AR_new'] for p in (ROOT / 'corrections').glob('*.csv')
             if p.name != 'needs_width_check.csv' for r in csv.DictReader(p.open())}
    scanned = skipped = 0
    for p in (ROOT / 'review').glob('*.csv'):
        for row in csv.DictReader(p.open(encoding='utf-8-sig')):
            if F.A.BAR_OPTS[row['bar']][0] != 'sys':
                continue
            text = fixed.get((row['bar'], row['id']), row['AR'])
            try:
                raw = F.A.encode(text, F.A.use_lig(row['bar'], int(row['id']))) + b'\0'
            except KeyError:
                skipped += 1  # Retail-English debug tables; their cells stay native.
                continue
            assert F.W.maxw(raw, adv) <= F.W.maxw(raw, original_adv), (row['bar'], row['id'], 'exceeds original width budget')
            scanned += 1
    ink_ratio = sum(r['ink_pixels'] for r in records) / sum(r['previous_ink_pixels'] for r in records)
    assert ink_ratio > 1.10
    return {'joined_pairs_hd_and_sd': joined, 'separated_pairs': separated,
            'dialogue_entries_unchanged': True, 'native_cells_unchanged': True,
            'total_ink_ratio': round(ink_ratio, 3),
            'glyphs_with_more_ink': sum(r['ink_pixels'] > r['previous_ink_pixels'] for r in records),
            'menu_rows_within_original_width_budget': scanned, 'retail_english_rows_skipped': skipped}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--verify', action='store_true')
    args = ap.parse_args()
    out, previous, records = build()
    checks = verify(out, previous, records)
    if args.verify:
        committed = F.pixels(HERE / 'font-overlay.zip')
        for key in F.PATHS:
            if key in F.GEOMETRY:
                assert np.array_equal(out[key + '_pixels'], committed[key])
            else:
                assert out[key] == committed[key]
        print('Menu font reproduced: larger cells, HD/SD joins, native glyphs and dialogue preserved')
        return
    files = F.write(out, HERE)
    hashes = {name: F.sha(data) for name, data in files.items()}
    (HERE / 'SHA256SUMS.txt').write_text(F.sha((HERE / 'font-overlay.zip').read_bytes()) + '  font-overlay.zip\n')
    (HERE / 'report.json').write_text(json.dumps({'version': '1.0.12', 'font_size_hd': SIZE,
        'previous_font_size_hd': 22, 'stroke_hd': STROKE / N.SUPERSAMPLE,
        'checks': checks, 'cells': records, 'overlay_files': hashes, 'in_game_verified': False}, indent=2) + '\n')
    before = {a + '_pixels': previous[a] for a in F.GEOMETRY}
    before.update(info=previous['info'])
    F.PREVIEWS['sys'] = (['انطلق للإنقاذ', 'افحص الجدار', 'ادخل البطولة', 'هجوم', 'أغراض', 'سحر'],
                         [((18, 65, 28), (255, 255, 255))])
    F.preview(before, out, 'sys', HERE / 'comparison-menu.png', labels=('1.0.11', '1.0.12'))
    print(json.dumps(checks))


if __name__ == '__main__':
    main()
