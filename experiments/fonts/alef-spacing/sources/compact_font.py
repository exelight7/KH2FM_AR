#!/usr/bin/env python3
"""Refine Arabic spacing globally using Noto Naskh; preserve Arabic joining rules."""
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

REPO = Path('/workspace/KH2FM_AR')
LAB = Path('/workspace/shared/kh2fm-cloud/font-lab')
SOURCE = LAB / 'NotoNaskhArabic/overlay/kh2'
OUT = LAB / 'NotoNaskhArabic-Compact'
FROZEN = REPO / 'build/payload/kh2'
sys.path.insert(0, str(REPO / 'build/tools'))
import arabic_msg as A
import width as W

def sha(data):
    return hashlib.sha256(data).hexdigest()

def entries(data):
    assert data[:4] == b'BAR\x01'
    result = {}
    for i in range(struct.unpack_from('<I', data, 4)[0]):
        _, name, off, size = struct.unpack_from('<I4sII', data, 16 + 16 * i)
        assert off + size <= len(data)
        result[name.rstrip(b'\0').decode()] = (off, size, data[off:off + size])
    return result

def box(cell, cols, width, height):
    x, y = cell % cols * width, cell // cols * height
    return x, y, x + width, y + height

allocation = list(csv.DictReader((REPO / 'build/tables/allocation.tsv').open(encoding='utf-8-sig'), delimiter='\t'))
assert A.char_cell['1'] != A.ar_enc['ا', 0]
assert A.char_cell['1'] != A.ar_enc['ا', 1]
geometry = {'sys': (28, 9, 24, 0, 256), 'evt': (21, 12, 32, 1, 512)}
source_info = (FROZEN / 'msg/us/fontinfo.bar').read_bytes()
info = bytearray(source_info)
info_entries = entries(source_info)
source_image = (SOURCE / 'msg/us/fontimage.bar').read_bytes()
image_entries = entries(source_image)
tables, textures, report = {}, {}, {'atlases': {}, 'input_fontinfo_sha256': sha(source_info)}
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'report.json').unlink(missing_ok=True)

for atlas, (cols, cw, ch, ix, height) in geometry.items():
    texture = Image.open(SOURCE / f'remastered/msg/us/fontimage.bar/US_fontimage_bar{ix}.png').convert('RGBA')
    textures[atlas] = texture
    sd = Image.frombytes('L', (256, height), image_entries[atlas][2])
    old = info_entries[atlas][2]
    new = bytearray(old)
    changes = []
    rows = allocation + ([{'cell': '36', 'letter': 'لا', 'formName': 'ISO'}] if atlas == 'evt' else [])
    forms = {int(r['cell']): r['formName'] for r in rows}
    # ISO/INI are separation boundaries in visual left-to-right order. FIN/MED
    # are joining boundaries and their advance must not be reduced.
    for r in rows:
        c = int(r['cell'])
        if r['formName'] not in ('ISO', 'INI'):
            continue
        hd_box = texture.getchannel('A').crop(box(c, cols, cw * 4, ch * 2)).point(lambda v: 255 if v >= 96 else 0).getbbox()
        sd_box = sd.crop(box(c, cols, cw, ch)).point(lambda v: 255 if v >= 19 else 0).getbbox()
        assert hd_box and sd_box
        # Keep at least one SD pixel of air beyond the widest HD/SD core.
        core_right_hd = max(hd_box[2], sd_box[2] * 4)
        required = math.ceil((core_right_hd + 4) / 2)
        new[c] = min(old[c], required)
        if new[c] != old[c]:
            assert new[c] * 2 - hd_box[2] >= 4
            assert new[c] * 2 - sd_box[2] * 4 >= 4
            changes.append({'letter': r['letter'], 'form': r['formName'], 'cell': c,
                            'old_advance_sd': old[c] / 2, 'new_advance_sd': new[c] / 2})
    for c in range(len(old)):
        assert new[c] <= old[c]
        if forms.get(c) not in ('ISO', 'INI'):
            assert new[c] == old[c]
    assert new[A.char_cell['1']] == old[A.char_cell['1']]
    tables[atlas] = bytes(new)
    off, length, _ = info_entries[atlas]
    info[off:off + length] = new
    used_pairs = set()
    for bar, (role, _) in A.BAR_OPTS.items():
        if role != atlas:
            continue
        for raw in A.msgs((FROZEN / f'msg/us/{bar}.bar').read_bytes()).values():
            for page in W.pages(raw):
                for line in page:
                    for a, b in zip(line, line[1:]):
                        if forms.get(a) in ('FIN', 'MED') and forms.get(b) in ('INI', 'MED'):
                            used_pairs.add((a, b))
    for a, b in used_pairs:
        assert new[a] == old[a]
        shift = new[a] * 2
        for raster, sx, sy, threshold in ((texture.getchannel('A'), 4, 2, 96), (sd, 1, 1, 33)):
            ma = np.array(raster.crop(box(a, cols, cw * sx, ch * sy))) >= threshold
            mb = np.array(raster.crop(box(b, cols, cw * sx, ch * sy))) >= threshold
            if sx == 1:
                ma = np.repeat(np.repeat(ma, 2, axis=0), 4, axis=1)
                mb = np.repeat(np.repeat(mb, 2, axis=0), 4, axis=1)
            common = max(0, min(ma.shape[1] - shift, mb.shape[1]))
            assert common and np.any(ma[:, shift:shift + common] & mb[:, :common]), (atlas, a, b)
    report['atlases'][atlas] = {'changed_advances': changes, 'connected_pairs_checked': len(used_pairs),
                               'disconnected_pairs': 0, 'digit_1_unchanged': True}

# Non-spacing BAR entries and headers remain byte-identical.
for name, (_, _, data) in entries(bytes(info)).items():
    if name not in geometry:
        assert data == info_entries[name][2]

review = [dict(r, file=p.name) for p in sorted((REPO / 'review').glob('*.csv'))
          for r in csv.DictReader(p.open(encoding='utf-8-sig'))]
widths = []
for r in review:
    atlas = A.BAR_OPTS[r['bar']][0]
    # Measure exact installed message bytes, including control-code boundaries.
    # Cache each bar for the full 15,552-row scan.
    r['atlas'] = atlas
bar_messages = {bar: A.msgs((FROZEN / f'msg/us/{bar}.bar').read_bytes()) for bar in A.BAR_OPTS}
for r in review:
    raw = bar_messages[r['bar']][int(r['id'])]
    old = W.maxw(raw, info_entries[r['atlas']][2])
    new = W.maxw(raw, tables[r['atlas']])
    assert new <= old, (r['bar'], r['id'], old, new)
    widths.append({'bar': r['bar'], 'id': r['id'], 'old_width_sd': old, 'new_width_sd': new})
report['width_scan'] = {'rows': len(widths), 'grew': 0,
                      'narrower': sum(r['new_width_sd'] < r['old_width_sd'] for r in widths),
                      'unchanged': sum(r['new_width_sd'] == r['old_width_sd'] for r in widths)}

overlay = OUT / 'overlay/kh2'
replacements = {'msg/us/fontimage.bar': source_image, 'msg/us/fontinfo.bar': bytes(info)}
for atlas, (_, _, _, ix, _) in geometry.items():
    rel = f'remastered/msg/us/fontimage.bar/US_fontimage_bar{ix}.png'
    replacements[rel] = (SOURCE / rel).read_bytes()
for relative, data in replacements.items():
    dest = overlay / relative
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
manifest = list(csv.DictReader((REPO / 'build/config/FROZEN_MANIFEST.tsv').open(), delimiter='\t'))
for r in manifest:
    relative = r['path'].replace('\\', '/')
    if relative in replacements:
        r.update(size=str(len(replacements[relative])), sha256=sha(replacements[relative]))
with (OUT / 'MANIFEST.tsv').open('w') as f:
    w = csv.DictWriter(f, fieldnames=['path', 'size', 'sha256'], delimiter='\t', lineterminator='\n')
    w.writeheader(); w.writerows(manifest)
with (OUT / 'widths.csv').open('w') as f:
    w = csv.DictWriter(f, fieldnames=list(widths[0]), lineterminator='\n')
    w.writeheader(); w.writerows(widths)
with zipfile.ZipFile(OUT / 'font-overlay.zip', 'w') as z:
    for relative, data in sorted(replacements.items()):
        item = zipfile.ZipInfo('kh2/' + relative, date_time=(1980, 1, 1, 0, 0, 0))
        item.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(item, data)

def compose(texture, atlas, advance, text):
    cols, cw, ch, _, _ = geometry[atlas]
    cells = W.pages(A.encode(text, atlas == 'evt'))[0][0]
    length = sum(20 if c is None else advance[c] * 2 for c in cells)
    strip = Image.new('RGBA', (math.ceil(length) + cw * 4, ch * 2))
    x = 0
    for c in cells:
        if c is None:
            x += 20
            continue
        glyph = texture.crop(box(c, cols, cw * 4, ch * 2))
        ink = Image.new('RGBA', glyph.size, 'white')
        ink.putalpha(glyph.getchannel('A'))
        strip.alpha_composite(ink, (round(x), 0))
        x += advance[c] * 2
    return strip

samples = ['أغراض', 'سورا:', 'مو هذا طريق هاديس.', 'سورا وروكساس وناميني',
           'القائمة الرئيسية', 'إعادة المحاولة', 'ا أ إ آ 1', 'باب دار نار هذا',
           'HP 100 MP 50', 'لا لأ لإ لآ', 'ببب تتت سسس ههه ممم']
labels = ['Current', 'Noto Naskh - fixed spacing']
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)
for atlas, (_, _, _, ix, _) in geometry.items():
    original = Image.open(FROZEN / f'remastered/msg/us/fontimage.bar/US_fontimage_bar{ix}.png').convert('RGBA')
    sheet = Image.new('RGB', (1800, 1230), '#142232')
    draw = ImageDraw.Draw(sheet)
    for col, (texture, advances, label) in enumerate(((original, info_entries[atlas][2], labels[0]),
                                                    (textures[atlas], tables[atlas], labels[1]))):
        draw.text((28 + col * 900, 20), label, font=font, fill='white')
        for row, text in enumerate(samples):
            strip = compose(texture, atlas, advances, text)
            assert strip.width < 850
            sheet.paste(strip, (875 + col * 900 - strip.width, 78 + row * 102), strip)
    sheet.save(OUT / f'comparison-{atlas}.png')
report['alef_is_not_digit_1'] = {'alef_iso_cell': A.ar_enc['ا', 0],
                                'alef_final_cell': A.ar_enc['ا', 1], 'digit_1_cell': A.char_cell['1']}
report['overlay_files'] = sorted(replacements)
report['in_game_verified'] = False
(OUT / 'report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
print(json.dumps({'atlases': {a: {'changed_advances': len(r['changed_advances']),
                                  'connected_pairs_checked': r['connected_pairs_checked']}
                             for a, r in report['atlases'].items()},
                  'width_scan': report['width_scan']}, ensure_ascii=False))
