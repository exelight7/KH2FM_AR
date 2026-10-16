"""Replace the baked HUD Drive label, preserving every pixel outside its UV box."""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import arabic_msg as A
import width as W

ROOT = Path(__file__).resolve().parents[2]
BOX = (6, 96, 79, 115)  # Verified DRIVE pill UV window; excludes MP/MAX/gauge artwork.
FONT = ROOT / 'experiments/fonts/natural-proportions/fonts/NotoSansArabic-Regular.ttf'


def label():
    forms = {int(r['cell']): int(r['pfCode'], 16) for r in csv.DictReader(
        (ROOT / 'build/tables/allocation.tsv').open(encoding='utf-8'), delimiter='\t')}
    cells = W.pages(A.encode('التحول', False) + b'\0')[0][0]
    visual = ''.join(chr(forms[c]) for c in cells)
    font = ImageFont.truetype(str(FONT), 72, layout_engine=ImageFont.Layout.BASIC)
    mask = Image.new('L', (512, 180))
    ImageDraw.Draw(mask).text((10, 10), visual, font=font, fill=255, stroke_width=1)
    mask = mask.crop(mask.getbbox())
    scale = min(68 / mask.width, 14 / mask.height)
    return mask.resize((round(mask.width * scale), round(mask.height * scale)), Image.Resampling.LANCZOS)


def main():
    manifest_path = ROOT / 'build/out/MANIFEST.tsv'
    manifest = list(csv.DictReader(manifest_path.open(encoding='utf-8'), delimiter='\t'))
    originals = {r['path'].replace('\\', '/'): r for r in csv.DictReader(
        (ROOT / 'build/config/FROZEN_MANIFEST.tsv').open(encoding='utf-8-sig'), delimiter='\t')}
    targets = [r for r in manifest if '/field2d/us/' in '/' + r['path'].replace('\\', '/')
               and r['path'].endswith('field_2dd1.png')]
    assert len(targets) == 19
    ink = label()
    records, previews = [], []
    for row in targets:
        relative = row['path'].replace('\\', '/')
        source = ROOT / 'build/payload/kh2' / relative
        raw = source.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == originals[relative]['sha256']
        before = np.array(Image.open(source).convert('RGBA'))
        after = before.copy()
        x0, y0, x1, y1 = BOX
        crop = before[y0:y1, x0:x1]
        old = (crop[:, :, :3].min(axis=2) > 70) & (crop[:, :, 3] > 200)
        assert 20 < int(old.sum()) < 500, (relative, 'unexpected source label')
        erase = np.array(Image.fromarray(old.astype('uint8') * 255).filter(ImageFilter.MaxFilter(3))) > 0
        erase &= crop[:, :, 3] > 200
        after[y0:y1, x0:x1, :3][erase] = 0
        x, y = 8 + (68 - ink.width) // 2, 98 + (14 - ink.height) // 2
        alpha = np.array(ink, dtype=float) / 255
        patch = after[y:y + ink.height, x:x + ink.width, :3]
        patch[:] = np.rint(patch * (1 - alpha[:, :, None]) + 126 * alpha[:, :, None]).astype('uint8')
        allowed = np.zeros(before.shape[:2], bool)
        allowed[y0:y1, x0:x1] = True
        assert np.array_equal(before[~allowed], after[~allowed]), relative
        assert np.array_equal(before[:, :, 3], after[:, :, 3]), relative
        destination = ROOT / 'build/out/kh2' / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(after).save(destination)
        data = destination.read_bytes()
        row.update(size=str(len(data)), sha256=hashlib.sha256(data).hexdigest())
        records.append({'path': relative, 'sha256': row['sha256'], 'box': BOX,
                        'outside_changed_pixels': 0, 'alpha_unchanged': True})
        if len(previews) < 4:
            previews.append((Image.fromarray(before).crop(BOX), Image.fromarray(after).crop(BOX)))
    with manifest_path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['path', 'size', 'sha256'], delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(manifest)
    report = ROOT / 'build/report'
    report.mkdir(parents=True, exist_ok=True)
    (report / 'HUD_TRANSFORM.json').write_text(json.dumps({'label': 'التحول', 'files': records}, ensure_ascii=False, indent=2), encoding='utf-8')
    preview = Image.new('RGB', (584, len(previews) * 76), (30, 30, 30))
    for index, (old, new) in enumerate(previews):
        preview.paste(old.convert('RGB').resize((292, 76)), (0, index * 76))
        preview.paste(new.convert('RGB').resize((292, 76)), (292, index * 76))
    preview.save(report / 'HUD_TRANSFORM.png')
    print('HUD: التحول replaces درايف in all 19 world atlases; UV/alpha/outside-pixel checks PASS')


if __name__ == '__main__':
    main()
