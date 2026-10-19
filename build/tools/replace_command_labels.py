"""Redraw the small baked menu labels, preserving all surrounding artwork.

Most worlds already have large labels. These five atlases retain the tiny
shared label strip. Keep every replacement inside its original strip slot;
do not resize the atlas, move icons or expand the game's texture coordinates.
"""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import arabic_msg as A
import width as W

ROOT = Path(__file__).resolve().parents[2]
FONT = ROOT / 'experiments/fonts/menu-legibility/fonts/NotoSansArabic-CondensedMedium.ttf'
LABELS = ['الأوامر', 'الفريق', 'دمج', 'اختصارات', 'الأصدقاء', 'استدعاء', 'الأشكال', 'أغراض', 'سحر', 'الذروة', 'زر']
SLOTS = {'di0': (576, 0, 128, 20), 'tt1': (576, 0, 128, 28),
         'wm0': (576, 0, 128, 28), 'zz0': (576, 0, 128, 28),
         'he0': (576, 98, 96, 30)}


def label(text, width, height):
    forms = {int(r['cell']): int(r['pfCode'], 16) for r in csv.DictReader(
        (ROOT / 'build/tables/allocation.tsv').open(), delimiter='\t')}
    cells = W.pages(A.encode(text, False) + b'\0')[0][0]
    visual = ''.join(' ' if c is None else chr(forms[c]) if c in forms else A.cell_ch[c] for c in cells)
    # A single uniform scale per word preserves proportions and joins.
    font = ImageFont.truetype(str(FONT), 104, layout_engine=ImageFont.Layout.BASIC)
    mask = Image.new('L', (1400, 240))
    ImageDraw.Draw(mask).text((10, 10), visual, font=font, fill=255, stroke_width=2)
    mask = mask.crop(mask.getbbox())
    scale = min((width - 8) / mask.width, (height - 4) / mask.height)
    mask = mask.resize((max(1, round(mask.width * scale)), max(1, round(mask.height * scale))), Image.Resampling.LANCZOS)
    body = Image.new('L', (width, height))
    body.paste(mask, ((width - mask.width) // 2, (height - mask.height) // 2))
    alpha = body.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.4))
    pixels = np.zeros((height, width, 4), np.uint8)
    pixels[:, :, 3] = np.maximum(np.array(alpha), np.array(body))
    pixels[:, :, 3][pixels[:, :, 3] < 12] = 0
    assert not np.array(body)[[0, -1]].any()
    # Fade only the optional ring at the slot boundary, never the glyph body.
    pixels[[0, -1], :, 3] = 0
    pixels[:, [0, -1], 3] = 0
    # Premultiplication is not used in these atlas files: dark ring in RGB 0,
    # body 126, coverage in alpha, matching the game's native tint convention.
    coverage = np.array(body, dtype=float)
    a = pixels[:, :, 3].astype(float)
    value = np.divide(126 * coverage, a, out=np.zeros_like(a), where=a > 0)
    pixels[:, :, :3] = np.rint(value[:, :, None]).astype(np.uint8)
    assert not pixels[0, :, 3].any() and not pixels[-1, :, 3].any()
    return pixels


def main():
    path = ROOT / 'build/out/MANIFEST.tsv'
    manifest = list(csv.DictReader(path.open(), delimiter='\t'))
    frozen = {r['path'].replace('\\', '/'): r['sha256'] for r in csv.DictReader(
        (ROOT / 'build/config/FROZEN_MANIFEST.tsv').open(), delimiter='\t')}
    records, previews = [], []
    for world, (x, top, width, step) in SLOTS.items():
        row = next(r for r in manifest if '/' + world + 'command.2dd/' in '/' + r['path'].replace('\\', '/'))
        relative = row['path'].replace('\\', '/')
        source = ROOT / 'build/payload/kh2' / relative
        assert hashlib.sha256(source.read_bytes()).hexdigest() == frozen[relative]
        before = np.array(Image.open(source).convert('RGBA'))
        after = before.copy(); allowed = np.zeros(before.shape[:2], bool)
        boxes = []
        for i, text in enumerate(LABELS):
            if world == 'di0' and i == 9:
                text = 'كومبو!'
            y = top + step * i
            height = step
            original = before[y:y + height, x:x + width]
            assert original[:, :, 3].any(), (world, i, 'missing source label')
            after[y:y + height, x:x + width] = label(text, width, height)
            allowed[y:y + height, x:x + width] = True
            boxes.append({'text': text, 'box': [x, y, x + width, y + height]})
        assert np.array_equal(before[~allowed], after[~allowed])
        destination = ROOT / 'build/out/kh2' / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(after).save(destination)
        reread = np.array(Image.open(destination).convert('RGBA'))
        assert np.array_equal(reread, after), (world, 'image round-trip changed pixels')
        data = destination.read_bytes(); row.update(size=str(len(data)), sha256=hashlib.sha256(data).hexdigest())
        records.append({'path': relative, 'sha256': row['sha256'], 'labels': boxes,
                        'outside_changed_pixels': 0, 'image_dimensions_unchanged': True})
        def preview(a):
            img = Image.fromarray(a).crop((x, top, x + width, top + step * 11))
            bg = Image.new('RGBA', img.size, (24, 47, 30, 255)); bg.alpha_composite(img)
            return bg.convert('RGB')
        previews.append((preview(before), preview(after)))
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['path', 'size', 'sha256'], delimiter='\t', lineterminator='\n')
        writer.writeheader(); writer.writerows(manifest)
    report = ROOT / 'build/report'
    (report / 'HUD_COMMANDS.json').write_text(json.dumps({'files': records, 'in_game_verified': False}, ensure_ascii=False, indent=2) + '\n')
    sheet = Image.new('RGB', (sum(a.width * 2 + 12 for a, _ in previews), max(a.height for a, _ in previews)), (24, 24, 24))
    x = 0
    for old, new in previews:
        sheet.paste(old, (x, 0)); sheet.paste(new, (x + old.width, 0)); x += old.width * 2 + 12
    sheet.save(report / 'HUD_COMMANDS.png')
    print('Baked command labels: 55 labels in 5 small-label world atlases, outside pixels unchanged')


if __name__ == '__main__':
    main()
