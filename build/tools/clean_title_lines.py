"""Remove the isolated scanlines above the three translated title labels.

The frozen atlases contain a one-pixel remnant above each label. These are
separate from the letters (which start on the following scanline). Limit the
edit to those three strips; preserve every other RGBA pixel, including the
letter edges, shadows, button icons and surrounding title artwork.
"""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
STRIPS = ((0, 151, 568, 152), (0, 247, 280, 248), (0, 551, 284, 552))


def clean(before):
    height, width = before.shape[:2]
    assert (width, height) in ((1024, 1024), (512, 512))
    scale = 1024 // width
    after = before.copy()
    allowed = np.zeros((height, width), dtype=bool)
    strips = []
    for left, top, right, _ in STRIPS:
        x, y, end = left // scale, top // scale, right // scale
        strip = before[y, x:end]
        # Detect the expected faint horizontal debris, never a glyph stroke.
        assert 10 <= int(strip[:, 3].max()) <= 70
        assert np.count_nonzero(strip[:, 3] > 5) >= 40
        assert before[y + 1, x:end, 3].max() >= 250
        after[y, x:end] = 0
        allowed[y, x:end] = True
        strips.append([x, y, end, y + 1])
    assert np.array_equal(before[~allowed], after[~allowed])
    assert not after[allowed].any()
    return after, allowed, strips


def main():
    manifest_path = ROOT / 'build/out/MANIFEST.tsv'
    manifest = list(csv.DictReader(manifest_path.open(), delimiter='\t'))
    frozen = {r['path'].replace('\\', '/'): r['sha256'] for r in csv.DictReader(
        (ROOT / 'build/config/FROZEN_MANIFEST.tsv').open(), delimiter='\t')}
    records = []
    previews = []
    for region in ('us', 'fm'):
        for number in (8, 9, 10, 11):
            relative = f'remastered/menu/{region}/title.2ld/US_title_2ld{number}.png'
            source = ROOT / 'build/payload/kh2' / relative
            assert hashlib.sha256(source.read_bytes()).hexdigest() == frozen[relative]
            before = np.array(Image.open(source).convert('RGBA'))
            after, allowed, strips = clean(before)
            destination = ROOT / 'build/out/kh2' / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            Image.fromarray(after).save(destination)
            assert np.array_equal(np.array(Image.open(destination)), after)
            data = destination.read_bytes()
            row = next(r for r in manifest if r['path'].replace('\\', '/') == relative)
            row.update(size=str(len(data)), sha256=hashlib.sha256(data).hexdigest())
            records.append({'path': relative, 'source_sha256': frozen[relative],
                            'sha256': row['sha256'], 'strips': strips,
                            'removed_visible_pixels': int(np.count_nonzero(before[:, :, 3][allowed])),
                            'outside_changed_pixels': 0, 'dimensions_unchanged': True,
                            'glyph_pixels_unchanged': True})
            if region == 'us' and number == 8:
                for pixels in (before, after):
                    im = Image.fromarray(pixels)
                    bg = Image.new('RGBA', im.size, 'white')
                    bg.alpha_composite(im)
                    previews.append(bg.crop((0, 140, 568, 216)).convert('RGB'))
    with manifest_path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['path', 'size', 'sha256'], delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(manifest)
    report = ROOT / 'build/report'
    report.mkdir(parents=True, exist_ok=True)
    (report / 'TITLE_CLEANUP.json').write_text(json.dumps(
        {'files': records, 'in_game_verified': False}, indent=2) + '\n')
    sheet = Image.new('RGB', (568, 152), 'white')
    for index, preview in enumerate(previews):
        sheet.paste(preview, (0, index * 76))
    sheet.resize((1136, 304)).save(report / 'TITLE_CLEANUP.png')
    print('Title cleanup: 8 atlases; 3 isolated scanlines each; all glyph and outside pixels unchanged')


if __name__ == '__main__':
    main()
