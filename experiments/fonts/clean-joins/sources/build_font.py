#!/usr/bin/env python3
"""Render proportional Noto Sans Arabic cells, without stretching individual letters.

Requires Python 3.12, Pillow and NumPy. The font is bundled under SIL OFL.
The previous game's atlas cells supply only the layout and baseline, never
individual letter widths. Native glyphs, icons, text and control codes are kept.
"""
import argparse
import csv
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location('font_formats', ROOT / 'experiments/fonts/outline-baseline/sources/fix_font.py')
F = importlib.util.module_from_spec(spec)
spec.loader.exec_module(F)
FONT = ROOT / 'experiments/fonts/natural-proportions/fonts/NotoSansArabic-Regular.ttf'
# A quarter-HD-pixel stroke produces a medium weight from the licensed source.
SIZES = {'sys': 22, 'evt': 30}
SUPERSAMPLE, STROKE = 4, 1
# A light outline keeps white dialogue legible without bloating dark bubble text.
RING = [(0.0, 232), (0.8, 210), (1.25, 160), (1.75, 70), (2.25, 12), (2.75, 0)]
F.RING = RING
ALLOC = list(csv.DictReader((ROOT / 'build/tables/allocation.tsv').open(), delimiter='\t'))


def render(size, cp, target_y):
    """Rasterize one presentation form with a uniform scale on both axes."""
    ss = SUPERSAMPLE
    font = ImageFont.truetype(str(FONT), size * ss, layout_engine=ImageFont.Layout.BASIC)
    scratch = Image.new('L', (160 * ss, 110 * ss))
    tatweel = Image.new('L', scratch.size)
    ImageDraw.Draw(tatweel).text((20 * ss, 60 * ss), 'ـ', font=font,
                                anchor='ls', fill=255, stroke_width=STROKE)
    rows = np.nonzero(np.array(tatweel.resize((160, 110), Image.Resampling.LANCZOS)) >= 128)[0]
    join_y = (int(rows.min()) + int(rows.max())) / 2
    ImageDraw.Draw(scratch).text((20 * ss, (60 + target_y - join_y) * ss), chr(cp),
                                font=font, anchor='ls', fill=255, stroke_width=STROKE)
    mask = np.array(scratch.resize((160, 110), Image.Resampling.LANCZOS))
    mask[mask < 8] = 0
    return mask, float(font.getlength(chr(cp))) / ss


def build():
    source = F.load_overlay(F.SOURCE_DIR / 'font-overlay.zip')
    info = bytearray(source['info'])
    previous_info = F.pixels(ROOT / 'experiments/fonts/natural-proportions/font-overlay.zip')['info']
    metrics = {}
    for atlas, g in F.GEOMETRY.items():
        hd = np.array(Image.open(io.BytesIO(source[atlas])).convert('RGBA'))
        offset, _ = F.entries(info)[atlas]
        forms = ALLOC + ([{'cell': str(F.A.LIG), 'pfCode': 'FEFB', 'formName': 'ISO'}] if atlas == 'evt' else [])
        initial = next(int(r['cell']) for r in forms if r['formName'] == 'INI')
        band = np.nonzero(hd[F.cell_slice(initial, g, 2)][:, 0, 3] >= 128)[0]
        assert len(band) == 3
        target_y = float(band.mean())
        reference, _ = render(SIZES[atlas], 0xFE91, target_y)
        band = np.flatnonzero(reference[:, 20] >= 128)
        assert 1 <= len(band) <= 3
        cells = []
        for row in forms:
            cell, cp, form = int(row['cell']), int(row['pfCode'], 16), row['formName']
            alpha, length = render(SIZES[atlas], cp, target_y)
            ys, xs = np.nonzero(alpha >= 8)
            left, right = int(xs.min()), int(xs.max()) + 1
            # Preserve the font's real joining stroke. Artificial full-opacity
            # bridges used to redraw long segments through the antialiased edge.
            stroke = alpha[band].min(axis=0)
            ends = np.flatnonzero(stroke >= 128)
            if form != 'ISO':
                assert len(ends), (atlas, cell, 'missing natural connector')
            origin = 20 if form in ('INI', 'MED') else left - 2
            shift = -origin
            width = right + shift
            mask = np.zeros((g['ch'] * 2, g['cw'] * 2), dtype=np.uint8)
            assert width < mask.shape[1] - 1, (atlas, cell, 'glyph clipped')
            assert 0 < int(ys.min()) and int(ys.max()) < mask.shape[0] - 1
            y0, y1 = int(ys.min()), int(ys.max()) + 1
            x0, x1 = max(0, -shift), min(alpha.shape[1], mask.shape[1] - shift)
            mask[y0:y1, x0 + shift:x1 + shift] = alpha[y0:y1, x0:x1]
            if form in ('FIN', 'MED'):
                advance = max(1, (int(ends[-1]) + shift) // 2)
            else:
                advance = math.ceil((width + 3) / 2)
            advance = min(advance, previous_info[offset + cell])
            assert advance * 2 + 2 <= mask.shape[1], (atlas, cell, 'advance outside cell')
            tile = hd[F.cell_slice(cell, g, 2)]
            tile[:, :, 3] = mask
            tile[:, :, :3] = np.where(mask[:, :, None] > 0, F.BODY_RGB, 0)
            info[offset + cell] = advance
            cells.append({'cell': cell, 'form': form, 'advance_hd': advance * 2, 'body_right_hd': width})
        buf = io.BytesIO()
        Image.fromarray(hd).save(buf, format='PNG')
        source[atlas] = buf.getvalue()
        metrics[atlas] = {'font_size_hd': SIZES[atlas], 'body_scale_x_equals_y': True, 'cells': cells}
    source['info'] = bytes(info)
    out, report = F.build(source, natural=True)
    # Quantize the real two-pixel connector into a visible SD pixel; never
    # draw a new horizontal bridge or alter the HD letter's native coverage.
    image = bytearray(out['image'])
    for atlas, g in F.GEOMETRY.items():
        offset, size = F.entries(image)[atlas]
        sd = F.unpack4(image[offset:offset + size], g['sd_rows'])
        off, _ = F.entries(out['info'])[atlas]
        changes = 0
        for row in ALLOC:
            cell, form = int(row['cell']), row['formName']
            tile = out[atlas + '_pixels'][F.cell_slice(cell, g, 2)]
            small = sd[F.cell_slice(cell, g, 1)]
            columns = ([0] if form in ('INI', 'MED') else []) + ([out['info'][off + cell]] if form in ('FIN', 'MED') else [])
            for x in columns:
                coverage = tile[:, x * 2:x * 2 + 2, 0] if atlas == 'evt' else tile[:, x * 2:x * 2 + 2, 3]
                ys = np.flatnonzero(coverage.max(axis=1) >= (63 if atlas == 'evt' else 96))
                assert len(ys), (atlas, cell, 'no real connector at SD boundary')
                y = int(ys[len(ys) // 2]) // 2
                assert coverage[y * 2:y * 2 + 2].any(), (atlas, cell, 'SD connector has no HD coverage')
                changes += int(small[y, x] < 2)
                small[y, x] = max(2, small[y, x])
        image[offset:offset + size] = F.pack4(sd)
        report['atlases'][atlas]['sd_connector_pixels_promoted'] = changes
    out['image'] = bytes(image)
    report.update(font='Noto Sans Arabic Regular, native connecting strokes',
                  font_sha256=F.sha(FONT.read_bytes()), metrics=metrics, outline=RING,
                  in_game_verified=False)
    return out, report


def verify_pairs_and_native(out):
    """Check SD joins, nonjoining HD bodies, and unchanged native cells/advances."""
    previous = F.pixels(ROOT / 'experiments/fonts/natural-proportions/font-overlay.zip')
    pairs, report = F.used_text_cells(), {}
    for atlas, g in F.GEOMETRY.items():
        forms = {int(r['cell']): r['formName'] for r in ALLOC}
        if atlas == 'evt':
            forms[F.A.LIG] = 'ISO'
        off, size = F.entries(out['info'])[atlas]
        advances = out['info'][off:off + size]
        old_advances = previous['info'][off:off + size]
        off, size = F.entries(out['image'])[atlas]
        sd = F.unpack4(out['image'][off:off + size], g['sd_rows'])
        old_sd = F.unpack4(previous['image'][off:off + size], g['sd_rows'])
        joined = separated = 0
        for cell in range(len(advances)):
            if cell not in forms:
                assert advances[cell] == old_advances[cell]
                assert np.array_equal(out[atlas + '_pixels'][F.cell_slice(cell, g, 2)], previous[atlas][F.cell_slice(cell, g, 2)])
                assert np.array_equal(sd[F.cell_slice(cell, g, 1)], old_sd[F.cell_slice(cell, g, 1)])
        for (a, b) in pairs[atlas]:
            if a not in forms or b not in forms:
                continue
            ta, tb = (out[atlas + '_pixels'][F.cell_slice(c, g, 2)] for c in (a, b))
            shift, width = advances[a] * 2, ta.shape[1] - advances[a] * 2
            if forms[a] in ('FIN', 'MED') and forms[b] in ('INI', 'MED'):
                joined += 1
                sa, sb = (np.repeat(np.repeat(sd[F.cell_slice(c, g, 1)], 2, 0), 2, 1) for c in (a, b))
                assert width > 0 and np.any((sa[:, shift:shift + width] >= 2) & (sb[:, :width] >= 2)), (atlas, a, b, 'SD join broken')
            elif forms[a] in ('ISO', 'INI'):
                separated += 1
                assert width <= 0 or not np.any((ta[:, shift:, 0] >= 63) & (tb[:, :width, 0] >= 63)), (atlas, a, b, 'unjoined bodies touch')
        report[atlas] = {'sd_joined_pairs': joined, 'unjoined_pairs': separated,
                         'broken_sd_joins': 0, 'touching_unjoined_bodies': 0, 'native_cells_unchanged': True}
    # Other BAR entries and all headers remain pinned to the previous release.
    for key in ('info', 'image'):
        old, new = previous[key], out[key]
        keep = np.ones(len(old), dtype=bool)
        for atlas in F.GEOMETRY:
            off, size = F.entries(old)[atlas]
            keep[off:off + size] = False
        assert np.array_equal(np.frombuffer(old, np.uint8)[keep], np.frombuffer(new, np.uint8)[keep])
    return report


def widths(out):
    previous = F.pixels(ROOT / 'experiments/fonts/natural-proportions/font-overlay.zip')
    tables = {}
    for name, data in [('previous', previous), ('new', out)]:
        for atlas in F.GEOMETRY:
            off, size = F.entries(data['info'])[atlas]
            tables[name, atlas] = data['info'][off:off + size]
    fixed = {(r['bar'], r['id']): r['AR_new'] for p in sorted((ROOT / 'corrections').glob('*.csv'))
             if p.name != 'needs_width_check.csv' for r in csv.DictReader(p.open())}
    result, skipped = [], []
    for path in sorted((ROOT / 'review').glob('*.csv')):
        for row in csv.DictReader(path.open(encoding='utf-8-sig')):
            atlas = F.A.BAR_OPTS[row['bar']][0]
            text = fixed.get((row['bar'], row['id']), row['AR'])
            try:
                raw = F.A.encode(text, F.A.use_lig(row['bar'], int(row['id']))) + b'\0'
            except (KeyError, ValueError):
                skipped.append([row['bar'], row['id']])
                continue  # Fifteen retail-English rows cannot use the Arabic encoder.
            before, after = (F.W.maxw(raw, tables[name, atlas]) for name in ('previous', 'new'))
            assert after <= before, (row['bar'], row['id'], before, after)
            result.append({'bar': row['bar'], 'id': row['id'], 'before': before, 'after': after})
    assert len(result) + len(skipped) == 15552
    return {'rows': len(result), 'narrower': sum(r['after'] < r['before'] for r in result),
            'unchanged': sum(r['after'] == r['before'] for r in result), 'wider': 0,
            'retail_english_rows_skipped': skipped}, result


def previews(out, directory):
    previous = F.pixels(ROOT / 'experiments/fonts/natural-proportions/font-overlay.zip')
    previous.update({a + '_pixels': previous[a] for a in F.GEOMETRY})
    F.PREVIEWS['evt'] = (['هيه!', 'ألا تشبه تلك الصخرة ميغارا قليلا?', 'حجر أولمبيا رفع لعنة', 'العالم السفلي كليا.',
                          'ا أ إ آ 1', 'HP 100 MP 50'], [((236, 196, 70), (60, 40, 10)), ((30, 40, 90), (255, 255, 255))])
    F.PREVIEWS['sys'] = (['الأوامر', 'أغراض', 'سحر', 'التحول', 'ا أ إ آ 1'], [((40, 45, 60), (255, 255, 255))])
    for atlas, name in [('evt', 'dialogue'), ('sys', 'menu')]:
        F.preview(previous, out, atlas, directory / f'comparison-{name}.png', labels=('1.0.8', '1.0.9 - native joins'))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, default=HERE)
    ap.add_argument('--verify', action='store_true')
    args = ap.parse_args()
    out, report = build()
    report['pair_checks'] = verify_pairs_and_native(out)
    report['width_scan'], rows = widths(out)
    if args.verify:
        committed = F.pixels(args.out / 'font-overlay.zip')
        for key in F.PATHS:
            if key in F.GEOMETRY:
                assert np.array_equal(out[key + '_pixels'], committed[key]), key
            else:
                assert out[key] == committed[key], key
        print('Natural font reproduced; HD/SD joins, native glyphs and all Arabic message widths verified')
        return
    files = F.write(out, args.out)
    report['overlay_files'] = {name: F.sha(data) for name, data in sorted(files.items())}
    (args.out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    with (args.out / 'widths.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['bar', 'id', 'before', 'after'], lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    previews(out, args.out)
    print(json.dumps({'widths': report['width_scan'], 'pairs': report['pair_checks']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
