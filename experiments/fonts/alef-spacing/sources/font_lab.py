#!/usr/bin/env python3
"""Build isolated Arabic font candidates; never write to the repository or input payload."""
import argparse
import collections
import csv
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--repo', type=Path, default=Path('/workspace/KH2FM_AR'))
ap.add_argument('--out', type=Path, default=Path('/workspace/shared/kh2fm-cloud/font-lab'))
args = ap.parse_args()
repo, out = args.repo.resolve(), args.out.resolve()
payload = repo / 'build/payload'
if out == payload or payload in out.parents or out == repo or repo in out.parents:
    raise SystemExit('Output must be outside the source checkout and frozen payload')
out.mkdir(parents=True, exist_ok=True)
(out / 'report.json').unlink(missing_ok=True)
sys.path.insert(0, str(repo / 'build/tools'))
import arabic_msg as A
import width as W

def sha(data):
    return hashlib.sha256(data).hexdigest()

def entries(data):
    assert data[:4] == b'BAR\x01'
    result = {}
    for i in range(struct.unpack_from('<I', data, 4)[0]):
        kind, name, offset, size = struct.unpack_from('<I4sII', data, 16 + i * 16)
        assert offset + size <= len(data)
        result[name.rstrip(b'\0').decode()] = (offset, size, data[offset:offset + size])
    return result

def cell_box(cell, cols, cw, ch):
    x, y = cell % cols * cw, cell // cols * ch
    return x, y, x + cw, y + ch

image_bar = (payload / 'kh2/msg/us/fontimage.bar').read_bytes()
info_bar = (payload / 'kh2/msg/us/fontinfo.bar').read_bytes()
image_entries, info_entries = entries(image_bar), entries(info_bar)
allocation = list(csv.DictReader((repo / 'build/tables/allocation.tsv').open(encoding='utf-8-sig'), delimiter='\t'))
assert len(allocation) == 117
geometries = {'sys': (28, 9, 24, 0, 256), 'evt': (21, 12, 32, 1, 512)}
original = {atlas: Image.open(payload / f'kh2/remastered/msg/us/fontimage.bar/US_fontimage_bar{ix}.png').convert('RGBA')
            for atlas, (_, _, _, ix, _) in geometries.items()}
font_paths = {name: Path('/usr/share/fonts/truetype/noto') / f'{name}-Bold.ttf'
              for name in ('NotoSansArabic', 'NotoNaskhArabic')}
required_cp = {int(r['pfCode'], 16) for r in allocation} | {0xFEFB, 0x640}
samples = ['القائمة الرئيسية', 'القدرات والأغراض', 'إعادة المحاولة',
           'سورا وروكساس وناميني', 'علينا التحدث مع الوحش أولا.',
           'لا نستطيع البقاء معا للأبد...', 'حسنا, اتفقنا. HP 100 MP 50',
           'ببب تتت سسس ههه ممم لا لأ لإ لآ']
report = {'input_fontimage_sha256': sha(image_bar), 'input_fontinfo_sha256': sha(info_bar), 'candidates': {}}

def make_mask(cp, font, baseline, size):
    # Render individual presentation forms; shaping is already handled by the game encoder.
    scale = 4
    f = ImageFont.truetype(str(font), size * scale, layout_engine=ImageFont.Layout.BASIC)
    mask = Image.new('L', (256 * scale, 160 * scale))
    ImageDraw.Draw(mask).text((40 * scale, baseline * scale), chr(cp), font=f, fill=255, anchor='ls')
    mask = mask.resize((256, 160), Image.Resampling.LANCZOS)
    return mask

def compose(texture, atlas, text, normalize=False):
    cols, cw, ch, _, _ = geometries[atlas]
    adv = info_entries[atlas][2]
    cells = W.pages(A.encode(text, atlas == 'evt'))[0][0]
    length = sum(20 if c is None else adv[c] * 2 for c in cells)
    strip = Image.new('RGBA', (math.ceil(length) + cw * 4, ch * 2))
    x = 0
    for c in cells:
        if c is None:
            x += 20
            continue
        glyph = texture.crop(cell_box(c, cols, cw * 4, ch * 2))
        if normalize:
            ink = Image.new('RGBA', glyph.size, 'white')
            ink.putalpha(glyph.getchannel('A'))
            glyph = ink
        strip.alpha_composite(glyph, (round(x), 0))
        x += adv[c] * 2
    return strip

for name, font in font_paths.items():
    with TTFont(font) as ft:
        missing = required_cp - set(ft.getBestCmap())
    assert not missing, (name, missing)
    candidate = out / name
    overlay = candidate / 'overlay/kh2'
    overlay.mkdir(parents=True, exist_ok=True)
    built_bar = bytearray(image_bar)
    rec = {'font_file': str(font), 'font_sha256': sha(font.read_bytes()), 'atlases': {}}
    for atlas, (cols, cw, ch, ix, sd_height) in geometries.items():
        texture = original[atlas].copy()
        atlas_rows = allocation + ([{'cell': '36', 'pfCode': 'FEFB', 'formName': 'ISO'}] if atlas == 'evt' else [])
        changed_cells = {int(r['cell']) for r in atlas_rows}
        original_alpha = original[atlas].getchannel('A')
        alef = next(int(r['cell']) for r in allocation if r['pfCode'] == 'FE8D')
        alef_box = original_alpha.crop(cell_box(alef, cols, cw * 4, ch * 2)).getbbox()
        original_baseline = alef_box[3] - 1
        # Choose one size and baseline per atlas; do not stretch glyphs vertically.
        size = None
        for trial in range(ch * 3, 10, -1):
            f = ImageFont.truetype(str(font), trial, layout_engine=ImageFont.Layout.BASIC)
            bounds = [f.getbbox(chr(int(r['pfCode'], 16)), anchor='ls') for r in atlas_rows]
            ascender = -min(b[1] for b in bounds)
            descender = max(b[3] for b in bounds)
            if ascender + descender <= ch * 2 - 6:
                size = trial
                baseline = min(original_baseline, ch * 2 - 3 - descender)
                break
        assert size is not None
        while size > 10:
            rendered = {int(r['pfCode'], 16): make_mask(int(r['pfCode'], 16), font, 60, size)
                        for r in atlas_rows}
            ink_bounds = [m.getbbox() for m in rendered.values()]
            min_y, max_y = min(b[1] for b in ink_bounds), max(b[3] for b in ink_bounds)
            baseline = min(original_baseline, ch * 2 - 2 - (max_y - 60))
            if min_y + baseline - 60 >= 1:
                break
            size -= 1
        assert size > 10
        f = ImageFont.truetype(str(font), size, layout_engine=ImageFont.Layout.BASIC)
        join_bbox = f.getbbox('\u0640', anchor='ls')
        join_y = baseline + (join_bbox[1] + join_bbox[3]) // 2
        adv = info_entries[atlas][2]
        masks, bounds_report = {}, []
        for r in atlas_rows:
            c, cp, form = int(r['cell']), int(r['pfCode'], 16), r['formName']
            box = cell_box(c, cols, cw * 4, ch * 2)
            old_box = original_alpha.crop(box).getbbox()
            assert old_box
            left = 0 if form in ('INI', 'MED') else old_box[0]
            right = old_box[2]
            if form in ('FIN', 'MED'):
                right = min(cw * 4, max(right, adv[c] * 2 + 2))
            source = rendered[cp]
            bbox = source.getbbox()
            assert bbox
            glyph_top = bbox[1] + baseline - 60
            assert glyph_top >= 0 and bbox[3] + baseline - 60 <= ch * 2
            glyph = source.crop(bbox).resize((right - left, bbox[3] - bbox[1]), Image.Resampling.LANCZOS)
            mask = Image.new('L', (cw * 4, ch * 2))
            mask.paste(glyph, (left, glyph_top))
            # Carry existing connecting strokes to the same fixed pitch boundaries.
            a = np.array(mask)
            bridges = 0
            if form in ('INI', 'MED', 'FIN'):
                for y in range(max(0, join_y - 1), min(ch * 2, join_y + 2)):
                    xs = np.flatnonzero(a[y] >= 96)
                    if len(xs):
                        if form in ('INI', 'MED'):
                            a[y, :xs[0] + 1] = 255
                        if form in ('FIN', 'MED'):
                            a[y, xs[-1]:right] = 255
                        bridges += 1
            mask = Image.fromarray(a)
            assert mask.getbbox() and mask.getbbox()[3] <= ch * 2
            ink = Image.new('RGBA', mask.size, (126, 126, 126, 0))
            ink.putalpha(mask)
            texture.paste(ink, box[:2])
            masks[c] = np.array(mask) >= 96
            bounds_report.append({'cell': c, 'form': form, 'font_size_hd': size, 'bridge_rows': bridges})
        # Pixels outside allocated Arabic cells, including Latin W in sys and XIII, must not change.
        before, after = np.array(original[atlas]), np.array(texture)
        allowed = np.zeros(before.shape[:2], dtype=bool)
        for c in changed_cells:
            x0, y0, x1, y1 = cell_box(c, cols, cw * 4, ch * 2)
            allowed[y0:y1, x0:x1] = True
        assert np.array_equal(before[~allowed], after[~allowed])
        target = overlay / f'remastered/msg/us/fontimage.bar/US_fontimage_bar{ix}.png'
        target.parent.mkdir(parents=True, exist_ok=True)
        texture.save(target)
        # Regenerate the matching SD cells in the existing 0..51 coverage convention.
        offset, count, source_sd = image_entries[atlas]
        sd = Image.frombytes('L', (256, sd_height), source_sd)
        for c in changed_cells:
            alpha = texture.getchannel('A').crop(cell_box(c, cols, cw * 4, ch * 2))
            small = alpha.resize((cw, ch), Image.Resampling.LANCZOS).point(lambda v: round(v * 51 / 255))
            sd.paste(small, cell_box(c, cols, cw, ch)[:2])
        sd_before, sd_after = np.frombuffer(source_sd, dtype=np.uint8).reshape(sd_height, 256), np.array(sd)
        sd_allowed = np.zeros_like(sd_before, dtype=bool)
        for c in changed_cells:
            x0, y0, x1, y1 = cell_box(c, cols, cw, ch)
            sd_allowed[y0:y1, x0:x1] = True
        assert np.array_equal(sd_before[~sd_allowed], sd_after[~sd_allowed])
        built_bar[offset:offset + count] = sd.tobytes()
        forms = {int(r['cell']): r['formName'] for r in atlas_rows}
        used_pairs = collections.Counter()
        for bar, (bar_atlas, _) in A.BAR_OPTS.items():
            if bar_atlas != atlas:
                continue
            for raw in A.msgs((payload / f'kh2/msg/us/{bar}.bar').read_bytes()).values():
                for page in W.pages(raw):
                    for line in page:
                        for a, b in zip(line, line[1:]):
                            if forms.get(a) in ('FIN', 'MED') and forms.get(b) in ('INI', 'MED'):
                                used_pairs[a, b] += 1
        broken, broken_sd = [], []
        for (a, b), count in sorted(used_pairs.items()):
            shift = adv[a] * 2
            ma, mb = masks[a], masks[b]
            common = max(0, min(ma.shape[1] - shift, mb.shape[1]))
            if not common or not np.any(ma[:, shift:shift + common] & mb[:, :common]):
                broken.append({'left': a, 'right': b, 'occurrences': count})
            sa = np.repeat(np.repeat(np.array(sd.crop(cell_box(a, cols, cw, ch))) >= 33, 2, axis=0), 4, axis=1)
            sb = np.repeat(np.repeat(np.array(sd.crop(cell_box(b, cols, cw, ch))) >= 33, 2, axis=0), 4, axis=1)
            if not common or not np.any(sa[:, shift:shift + common] & sb[:, :common]):
                broken_sd.append({'left': a, 'right': b, 'occurrences': count})
        rec['atlases'][atlas] = {'cells': len(changed_cells), 'font_size_hd': size,
            'baseline_hd': baseline, 'join_y_hd': join_y, 'unique_connected_pairs': len(used_pairs),
            'connected_pair_occurrences': sum(used_pairs.values()), 'broken_hd_pairs': broken,
            'broken_sd_pairs': broken_sd,
            'outside_arabic_pixels_changed': 0, 'glyphs': bounds_report}
        assert not broken and not broken_sd, (name, atlas, 'disconnected raster pairs')
    # All BAR headers, icon data, and padding remain byte-identical.
    allowed_bytes = np.zeros(len(image_bar), dtype=bool)
    for atlas in geometries:
        off, size, _ = image_entries[atlas]
        allowed_bytes[off:off + size] = True
    assert np.array_equal(np.frombuffer(image_bar, dtype=np.uint8)[~allowed_bytes],
                          np.frombuffer(built_bar, dtype=np.uint8)[~allowed_bytes])
    msg = overlay / 'msg/us/fontimage.bar'
    msg.parent.mkdir(parents=True, exist_ok=True)
    msg.write_bytes(built_bar)
    assert entries(bytes(built_bar))['icon'][2] == image_entries['icon'][2]
    assert (payload / 'kh2/msg/us/fontinfo.bar').read_bytes() == info_bar
    rec['advance_table_changed_bytes'] = 0
    rec['overlay_files'] = []
    manifest = list(csv.DictReader((repo / 'build/config/FROZEN_MANIFEST.tsv').open(), delimiter='\t'))
    for r in manifest:
        relative = Path(*r['path'].split('\\'))
        replacement = overlay / relative
        if replacement.is_file():
            data = replacement.read_bytes()
            r.update(size=str(len(data)), sha256=sha(data))
            rec['overlay_files'].append(str(relative))
        else:
            data = (payload / 'kh2' / relative).read_bytes()
            assert len(data) == int(r['size']) and sha(data) == r['sha256']
    assert len(rec['overlay_files']) == 3
    with (candidate / 'MANIFEST.tsv').open('w') as f:
        writer = csv.DictWriter(f, fieldnames=['path', 'size', 'sha256'], delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(manifest)
    with zipfile.ZipFile(candidate / 'font-overlay.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted(overlay.rglob('*')):
            if p.is_file():
                item = zipfile.ZipInfo(str(p.relative_to(overlay.parent)), date_time=(1980, 1, 1, 0, 0, 0))
                item.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(item, p.read_bytes())
    report['candidates'][name] = rec

# This is an atlas-layout preview, not a screenshot of the game renderer.
label_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)
labels = ['Current', 'Noto Sans Arabic Bold', 'Noto Naskh Arabic Bold']
names = [None, 'NotoSansArabic', 'NotoNaskhArabic']
for atlas, (cols, cw, ch, ix, _) in geometries.items():
    sheet = Image.new('RGB', (2600, 1050), '#142232')
    draw = ImageDraw.Draw(sheet)
    for column, (name, label) in enumerate(zip(names, labels)):
        draw.text((24 + column * 865, 20), label, font=label_font, fill='white')
        texture = original[atlas] if name is None else Image.open(out / name / f'overlay/kh2/remastered/msg/us/fontimage.bar/US_fontimage_bar{ix}.png').convert('RGBA')
        for row, text in enumerate(samples):
            strip = compose(texture, atlas, text, normalize=True)
            if strip.width > 820:
                strip = strip.resize((820, round(strip.height * 820 / strip.width)), Image.Resampling.LANCZOS)
            sheet.paste(strip, (24 + column * 865, 90 + row * 112), strip)
    sheet.save(out / f'comparison-{atlas}.png')
report['notes'] = ['Prototype; requires in-game validation before adoption.',
    'Previews use white ink for comparison; overlay retains the original neutral RGB 126.',
    'Advance tables are byte-identical: font changes add no advance-based line-width growth.',
    'Embedded text in other textures and the icon atlas are separate work, unchanged here.',
    'Observed-pair raster checks are horizontal-layout checks, not proof of in-game appearance.']
(out / 'report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
print(json.dumps({n: {a: {k: v for k, v in r.items() if k != 'glyphs'}
                     for a, r in c['atlases'].items()} for n, c in report['candidates'].items()}, ensure_ascii=False))
