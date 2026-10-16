#!/usr/bin/env python3
"""Correct the v1.0.5 Arabic font overlay in place, without re-rendering any glyph.

1. Dialogue atlas (evt): Arabic cells take the game's own glyph encoding. RGB
   carries the white body; alpha adds the dark ring that every native dialogue
   glyph has, calibrated from the game's digits and capitals.
2. Baseline: every native cell (digits, punctuation, Latin) moves up 6 HD px
   (3 SD px) so it sits on the Arabic baseline instead of below it.
3. SD textures in msg/us/fontimage.bar: Arabic cells are re-encoded in the
   game's 4bpp format (low nibble = left pixel, levels 0..3; in evt 1 = ring,
   2 = edge, 3 = body). 1.0.4/1.0.5 wrote one 0..51 value per byte instead.

The advance table (fontinfo.bar) is not changed, so no line gets wider.
Input: experiments/fonts/alef-spacing/font-overlay.zip, checked against its SHA256SUMS.txt.
Needs Python 3.12, Pillow and NumPy.
"""
import argparse
import collections
import csv
import hashlib
import io
import json
from pathlib import Path
import struct
import sys
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]
SOURCE_DIR = ROOT / 'experiments/fonts/alef-spacing'
sys.path.insert(0, str(ROOT / 'build/tools'))
import arabic_msg as A  # noqa: E402
import width as W  # noqa: E402

# SD geometry; HD textures are exactly twice as large in both directions.
GEOMETRY = {'sys': {'index': 0, 'cols': 28, 'cw': 18, 'ch': 24, 'sd_rows': 256},
            'evt': {'index': 1, 'cols': 21, 'cw': 24, 'ch': 32, 'sd_rows': 512}}
SHIFT_HD = 6          # native glyph bottom (digits, Latin) sits 5-7 HD px below the Arabic baseline
BODY_RGB = 126        # the value used by the game's own glyph bodies and by 1.0.5
# Ring opacity by distance (HD px) from the nearest body pixel, measured on the
# game's own dialogue digits and capitals (offset 0.25 px toward the lower right).
RING = [(0.0, 232), (1.25, 226), (1.75, 198), (2.25, 130), (2.75, 72), (3.25, 26), (3.75, 6), (4.0, 0)]
RING_OFFSET = 0.25
# SD levels from 2x2 HD averages. The game's SD glyphs are separate pixel art
# (not a downscale of HD), so the levels follow its convention, not its pixels:
# sys = coverage in thirds; evt = 1 ring, 2 edge, 3 body by thirds of BODY_RGB.
SYS_LEVELS = (43, 128, 213)
EVT_ALPHA, EVT_EDGE, EVT_BODY = 64, 42, 84
PATHS = {'image': 'kh2/msg/us/fontimage.bar', 'info': 'kh2/msg/us/fontinfo.bar',
         'sys': 'kh2/remastered/msg/us/fontimage.bar/US_fontimage_bar0.png',
         'evt': 'kh2/remastered/msg/us/fontimage.bar/US_fontimage_bar1.png'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def entries(data):
    assert data[:4] == b'BAR\x01'
    result = {}
    for i in range(struct.unpack_from('<I', data, 4)[0]):
        _, name, offset, size = struct.unpack_from('<I4sII', data, 16 + 16 * i)
        assert offset + size <= len(data)
        result[name.rstrip(b'\0').decode()] = (offset, size)
    return result


def cell_slice(cell, g, scale):
    x, y = cell % g['cols'] * g['cw'] * scale, cell // g['cols'] * g['ch'] * scale
    return slice(y, y + g['ch'] * scale), slice(x, x + g['cw'] * scale)


def distance_to(mask, offset):
    """Euclidean distance from every pixel to the nearest True pixel (small cells only)."""
    ys, xs = np.nonzero(mask)
    yy, xx = np.mgrid[0:mask.shape[0], 0:mask.shape[1]].astype(float)
    best = np.full(mask.shape, np.inf)
    for start in range(0, len(ys), 256):
        by, bx = ys[start:start + 256, None, None], xs[start:start + 256, None, None]
        best = np.minimum(best, np.hypot(yy - offset - by, xx - offset - bx).min(axis=0))
    return best


def ring_alpha(distance):
    d, a = zip(*RING)
    return np.interp(distance, d, a, right=0.0)


def unpack4(raw, rows):
    data = np.frombuffer(raw, dtype=np.uint8).reshape(rows, 256)
    levels = np.zeros((rows, 512), dtype=np.uint8)
    levels[:, 0::2], levels[:, 1::2] = data & 15, data >> 4
    return levels


def pack4(levels):
    assert levels.max() <= 3
    return (levels[:, 0::2] | (levels[:, 1::2] << 4)).astype(np.uint8).tobytes()


def sd_levels(atlas, rgba):
    """2x2 HD block -> SD level, in the game's convention for that atlas."""
    h, w = rgba.shape[0] // 2, rgba.shape[1] // 2
    blocks = rgba.reshape(h, 2, w, 2, 4).astype(float).mean(axis=(1, 3))
    alpha, rgb = blocks[:, :, 3], blocks[:, :, 0]
    if atlas == 'sys':
        return np.digitize(alpha, SYS_LEVELS).astype(np.uint8)
    levels = np.where(rgb >= EVT_BODY, 3, np.where(rgb >= EVT_EDGE, 2, 1)).astype(np.uint8)
    return np.where(alpha >= EVT_ALPHA, levels, 0).astype(np.uint8)


def load_overlay(path):
    expected = next(line.split()[0] for line in (SOURCE_DIR / 'SHA256SUMS.txt').read_text().splitlines()
                    if line.split(maxsplit=1)[1] == 'font-overlay.zip')
    data = path.read_bytes()
    assert sha(data) == expected, 'v1.0.5 font overlay SHA256 mismatch'
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        assert sorted(z.namelist()) == sorted(PATHS.values())
        return {k: z.read(p) for k, p in PATHS.items()}


def used_text_cells():
    """Adjacent cell pairs of the shipped text, per atlas: review rows plus corrected rows."""
    pairs = {a: collections.Counter() for a in GEOMETRY}
    rows = [(r['bar'], r['id'], r['AR']) for path in sorted((ROOT / 'review').glob('*.csv'))
            for r in csv.DictReader(path.open(encoding='utf-8-sig'))]
    rows += [(r['bar'], r['id'], r['AR_new']) for path in sorted((ROOT / 'corrections').glob('*.csv'))
             for r in csv.DictReader(path.open(encoding='utf-8-sig')) if r.get('AR_new')]
    for bar, msg_id, text in rows:
        if bar in A.BAR_OPTS:
            atlas = A.BAR_OPTS[bar][0]
            try:
                raw = A.encode(text, A.use_lig(bar, int(msg_id)))
            except (KeyError, ValueError):
                continue          # the 15 retail-English rows that cannot be shaped
            for page in W.pages(raw + b'\0'):
                for line in page:
                    for a, b in zip(line, line[1:]):
                        if a is not None and b is not None:
                            pairs[atlas][a, b] += 1
    return pairs


def build(source):
    allocation = list(csv.DictReader((ROOT / 'build/tables/allocation.tsv').open(encoding='utf-8-sig'), delimiter='\t'))
    assert len(allocation) == 117
    info = entries(source['info'])
    image_entries = entries(source['image'])
    image_bar = bytearray(source['image'])
    out, report = {'info': source['info']}, {'atlases': {}}
    pairs = used_text_cells()
    for atlas, g in GEOMETRY.items():
        offset, size = info[atlas]
        advance = source['info'][offset:offset + size]
        hd_before = np.array(Image.open(io.BytesIO(source[atlas])).convert('RGBA'))
        assert hd_before.shape[:2] == (g['sd_rows'] * 2, 1024)
        hd = hd_before.copy()
        cells = len(advance)
        assert cells == g['sd_rows'] // g['ch'] * g['cols']
        forms = {int(r['cell']): r['formName'] for r in allocation}
        if atlas == 'evt':
            forms[A.LIG] = 'ISO'    # lam+alef ligature cell, dialogue atlas only
        native = [c for c in range(cells) if c not in forms and hd[cell_slice(c, g, 2)][:, :, 3].any()]
        rec = {'arabic_cells': len(forms), 'native_cells_moved': len(native)}

        # 1. Dialogue ring and body, from the 1.0.5 coverage.
        if atlas == 'evt':
            ini = [c for c, f in forms.items() if f == 'INI']
            band = set.intersection(*(set(np.nonzero(hd[cell_slice(c, g, 2)][:, 0, 3] >= 128)[0]) for c in ini))
            band = sorted(int(y) for y in band)
            assert len(band) == 3 and band[-1] - band[0] == 2, band
            rec['join_rows_hd'] = band
            bridges = {}
            for c, form in sorted(forms.items()):
                tile = hd[cell_slice(c, g, 2)]
                body = tile[:, :, 3].astype(float) / 255
                seed = body >= 0.5
                if form in ('INI', 'MED'):
                    # The left part of these cells is only the connecting stroke,
                    # and the previous glyph (drawn first) overhangs it by up to
                    # 14 px. A ring around this bridge would be drawn over that
                    # glyph, so the bridge gets no ring of its own here.
                    off_band = seed.copy()
                    off_band[band[0] - 1:band[-1] + 2] = False
                    bridge = int(np.nonzero(off_band.any(axis=0))[0].min())
                    seed[:, :bridge] = False
                    bridges[c] = bridge
                ring = ring_alpha(distance_to(seed, RING_OFFSET)) / 255
                if form in ('INI', 'MED'):
                    # The overhanging stroke of the previous glyph is up to 3 px
                    # thicker than the bridge; keep this glyph's ring off it.
                    ring[band[0] - 3:band[-1] + 4, :bridges[c]] = 0
                if form in ('FIN', 'MED'):
                    # The next glyph's connecting stroke starts at the advance:
                    # no ring may close the stroke across the join.
                    ring[band[0]:band[-1] + 1, advance[c] * 2:] = 0
                alpha = np.round(np.maximum(body, ring) * 255).astype(np.uint8)
                value = np.round(body * BODY_RGB).astype(np.uint8)
                value[alpha == 0] = 0
                tile[:, :, 0] = tile[:, :, 1] = tile[:, :, 2] = value
                tile[:, :, 3] = alpha

        # 2. Native glyphs move up onto the Arabic baseline.
        for c in native:
            tile = hd[cell_slice(c, g, 2)]
            assert not tile[:SHIFT_HD, :, 3].any(), f'{atlas} cell {c} has no room to move up'
            tile[:] = np.roll(tile, -SHIFT_HD, axis=0)

        # 3. SD texture in the game's 4bpp format.
        sd_offset, sd_size = image_entries[atlas]
        sd_before = unpack4(source['image'][sd_offset:sd_offset + sd_size], g['sd_rows'])
        sd = sd_before.copy()
        partial = {}
        for c in native:
            tile = sd[cell_slice(c, g, 1)]
            inked = np.nonzero(tile.any(axis=1))[0]
            if not len(inked):
                continue             # cell drawn in HD only
            step = min(SHIFT_HD // 2, int(inked[0]))
            if step < SHIFT_HD // 2:
                partial[c] = step    # SD pixel art drawn higher than its HD glyph
            tile[:] = np.roll(tile, -step, axis=0)
        rec['sd_native_cells_moved_less'] = partial
        for c in forms:
            sd[cell_slice(c, g, 1)] = sd_levels(atlas, hd[cell_slice(c, g, 2)])
        image_bar[sd_offset:sd_offset + sd_size] = pack4(sd)
        hist = {'native': np.zeros(4, int), 'arabic': np.zeros(4, int)}
        for c in native:
            hist['native'] += np.bincount(sd[cell_slice(c, g, 1)].ravel(), minlength=4)
        for c in forms:
            hist['arabic'] += np.bincount(sd[cell_slice(c, g, 1)].ravel(), minlength=4)
        rec['sd_level_share_of_ink'] = {k: [round(float(v[i] / v[1:].sum()), 3) for i in (1, 2, 3)] for k, v in hist.items()}
        rec['sd_bytes_with_level_above_3'] = int((unpack4(bytes(image_bar[sd_offset:sd_offset + sd_size]), g['sd_rows']) > 3).sum())
        assert rec['sd_bytes_with_level_above_3'] == 0

        # Checks: only Arabic and moved native cells changed; transparent pixels carry no RGB.
        changed = np.zeros(hd.shape[:2], dtype=bool)
        for c in list(forms) + native:
            changed[cell_slice(c, g, 2)] = True
        assert np.array_equal(hd[~changed], hd_before[~changed])
        for c in forms:
            tile = hd[cell_slice(c, g, 2)]
            assert not tile[:, :, :3][tile[:, :, 3] == 0].any(), (atlas, c)
            if atlas == 'evt':
                assert ((tile[:, :, 3] >= 128) & (tile[:, :, 0] <= 16)).any(), (atlas, c, 'no ring')
                assert tile[:, :, 0].max() <= BODY_RGB and (tile[:, :, 0] >= 100).any(), (atlas, c)
        rec.update(join_check(atlas, g, hd, advance, forms, pairs[atlas]))
        rec.update(baseline_check(atlas, g, hd, forms))
        report['atlases'][atlas] = rec
        buf = io.BytesIO()
        Image.fromarray(hd, 'RGBA').save(buf, format='PNG')
        out[atlas] = buf.getvalue()
        out[atlas + '_pixels'] = hd
    # Headers, the icon atlas and padding stay byte-identical.
    keep = np.ones(len(image_bar), dtype=bool)
    for atlas in GEOMETRY:
        o, s = image_entries[atlas]
        keep[o:o + s] = False
    assert np.array_equal(np.frombuffer(bytes(image_bar), np.uint8)[keep], np.frombuffer(source['image'], np.uint8)[keep])
    out['image'] = bytes(image_bar)
    return out, report


def join_check(atlas, g, hd, advance, forms, pairs):
    """Composite every adjacent pair of the installed text in drawing order (left glyph first).
    Joined pairs must keep a continuous white stroke; no ring may cover the other glyph's body."""
    joined = broken = covered = worst = 0
    for (a, b), count in pairs.items():
        if a not in forms or b not in forms:
            continue
        ta, tb = hd[cell_slice(a, g, 2)].astype(int), hd[cell_slice(b, g, 2)].astype(int)
        shift = advance[a] * 2
        width = ta.shape[1] - shift
        if width <= 0:
            continue
        under, over = ta[:, shift:], tb[:, :width]
        # Body of the left glyph darkened by a ring pixel of the right glyph.
        darkened = int(((under[:, :, 0] >= 63) & (over[:, :, 3] >= 128) & (over[:, :, 0] < 63)).sum())
        covered += count * darkened
        worst = max(worst, darkened)
        if forms[a] in ('FIN', 'MED') and forms[b] in ('INI', 'MED'):
            joined += 1
            white_a = (ta[:, :, 0] >= 63) if atlas == 'evt' else (ta[:, :, 3] >= 96)
            white_b = (tb[:, :, 0] >= 63) if atlas == 'evt' else (tb[:, :, 3] >= 96)
            if not np.any(white_a[:, shift:shift + width] & white_b[:, :width]):
                broken += 1
    assert broken == 0, (atlas, broken, 'broken joins')
    # Isolated anti-aliasing pixels where a ring meets an overhanging stroke are tolerated.
    assert worst <= 6, (atlas, worst, 'ring pixels cover a neighbouring body')
    return {'joined_pairs_checked': joined, 'broken_joins': broken,
            'max_body_pixels_covered_by_ring_per_pair': worst, 'body_pixels_covered_by_ring_in_text': covered}


def baseline_check(atlas, g, hd, forms):
    """Bottom of the digit 1 body vs. bottom of the Arabic connecting stroke (HD px)."""
    one = A.char_cell['1']
    tile = hd[cell_slice(one, g, 2)]
    body = tile[:, :, 0] >= 63 if atlas == 'evt' else tile[:, :, 3] >= 128
    digit_bottom = int(np.nonzero(body.any(axis=1))[0].max())
    ini = next(c for c, f in forms.items() if f == 'INI')
    stroke = np.nonzero(hd[cell_slice(ini, g, 2)][:, 0, 3] >= 128)[0]
    arabic_bottom = int(stroke.max())
    gap = digit_bottom - arabic_bottom
    assert abs(gap) <= 2, (atlas, digit_bottom, arabic_bottom)
    return {'digit_1_body_bottom_hd': digit_bottom, 'arabic_stroke_bottom_hd': arabic_bottom, 'baseline_gap_hd': gap}


PREVIEWS = {
    # Dialogue box, a bright scene behind it, and a speech bubble (dark text).
    'evt': (['حجر أولمبيا رفع لعنة', 'العالم السفلي كليا.', 'لديك 15 نوعا, HP 100'],
            [((30, 40, 90), (255, 255, 255)), ((200, 200, 200), (255, 255, 255)), ((236, 196, 70), (60, 40, 10))]),
    'sys': (['أغراض 15', 'HP 100/120 MP 50', 'المستوى 7: سورا.'], [((40, 45, 60), (255, 255, 255))]),
}


def preview(before, after, atlas, path):
    """Atlas simulation (not a game screenshot), before and after."""
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 22)
    samples, colours = PREVIEWS[atlas]
    rows = []
    for label, data in (('1.0.5', before), ('1.0.6', after)):
        for bg, ink in colours:
            for text in samples:
                rows.append((label, compose(data, atlas, text, bg, ink)))
    width = max(r[1].shape[1] for r in rows) * 2 + 160
    sheet = Image.new('RGB', (width, sum(r[1].shape[0] * 2 + 4 for r in rows)), (24, 24, 24))
    draw, y = ImageDraw.Draw(sheet), 0
    for label, strip in rows:
        im = Image.fromarray(strip)
        im = im.resize((im.width * 2, im.height * 2), Image.Resampling.NEAREST)
        sheet.paste(im, (width - im.width - 8, y))
        draw.text((8, y + 8), label, font=font, fill='white')
        y += im.height + 4
    sheet.save(path)


def compose(data, atlas, text, bg, ink):
    g = GEOMETRY[atlas]
    hd = data[atlas + '_pixels'].astype(float)
    off, size = entries(data['info'])[atlas]
    advance = data['info'][off:off + size]
    cells = W.pages(A.encode(text, atlas == 'evt'))[0][0]
    total = int(sum(20 if c is None else advance[c] * 2 for c in cells)) + g['cw'] * 2
    canvas = np.zeros((g['ch'] * 2, total, 3))
    canvas[:] = bg
    x = 0
    for c in cells:
        if c is None:
            x += 20
            continue
        tile = hd[cell_slice(c, g, 2)]
        w = min(tile.shape[1], total - x)
        color = tile[:, :w, :1] / BODY_RGB * np.array(ink, dtype=float)   # RGB 0 = dark ring, 126 = text colour
        alpha = tile[:, :w, 3:] / 255
        canvas[:, x:x + w] = np.clip(color, 0, 255) * alpha + canvas[:, x:x + w] * (1 - alpha)
        x += advance[c] * 2
    return canvas.astype(np.uint8)


def write(out, directory):
    directory.mkdir(parents=True, exist_ok=True)
    files = {PATHS['image']: out['image'], PATHS['info']: out['info'], PATHS['sys']: out['sys'], PATHS['evt']: out['evt']}
    archive = directory / 'font-overlay.zip'
    with zipfile.ZipFile(archive, 'w') as z:
        for name in sorted(files):
            item = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            item.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(item, files[name])
    rows = list(csv.DictReader((SOURCE_DIR / 'MANIFEST.tsv').open(), delimiter='\t'))
    for r in rows:
        name = 'kh2/' + r['path'].replace('\\', '/')
        if name in files:
            r.update(size=str(len(files[name])), sha256=sha(files[name]))
    with (directory / 'MANIFEST.tsv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['path', 'size', 'sha256'], delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    return files


def pixels(archive):
    with zipfile.ZipFile(archive) as z:
        return {k: (np.array(Image.open(io.BytesIO(z.read(p))).convert('RGBA')) if k in GEOMETRY else z.read(p))
                for k, p in PATHS.items()}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument('--verify', action='store_true',
                    help='rebuild in memory and compare with the committed overlay (decoded pixels and bytes)')
    args = ap.parse_args()
    source = load_overlay(SOURCE_DIR / 'font-overlay.zip')
    out, report = build(source)
    if args.verify:
        committed = pixels(args.out / 'font-overlay.zip')
        for key in PATHS:
            if key in GEOMETRY:
                assert np.array_equal(out[key + '_pixels'], committed[key]), key
            else:
                assert out[key] == committed[key], key
        print('Font overlay reproduced: identical pixels and BAR bytes')
        return
    files = write(out, args.out)
    report.update({
        'version': '1.0.6',
        'input_overlay_sha256': sha((SOURCE_DIR / 'font-overlay.zip').read_bytes()),
        'advance_table_changed_bytes': 0,
        'native_shift_hd_px': SHIFT_HD, 'native_shift_sd_px': SHIFT_HD // 2,
        'ring_profile_hd': RING, 'body_rgb': BODY_RGB,
        'overlay_files': {name: sha(data) for name, data in sorted(files.items())},
        'in_game_verified': False,
    })
    (args.out / 'report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    before = dict(source, **{a + '_pixels': np.array(Image.open(io.BytesIO(source[a])).convert('RGBA')) for a in GEOMETRY})
    preview(before, out, 'evt', args.out / 'comparison-dialogue.png')
    preview(before, out, 'sys', args.out / 'comparison-menu.png')
    print(json.dumps(report['atlases'], ensure_ascii=False))


if __name__ == '__main__':
    main()
