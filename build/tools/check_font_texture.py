"""Reject colored transparent backgrounds that become solid glyph boxes in game."""
import csv
import io
from pathlib import Path
import zipfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]

def check_textures(archive):
    # The allocation export stores literal escaped tabs.
    rows = csv.DictReader((ROOT / 'build/tables/allocation.tsv').read_text().replace('\\t', '\t').splitlines(), delimiter='\t')
    cells = {int(row['cell']) for row in rows}
    assert len(cells) == 117
    checked = 0
    with zipfile.ZipFile(archive) as z:
        for index, cols, width, height in [(0, 28, 36, 48), (1, 21, 48, 64)]:
            image = Image.open(io.BytesIO(z.read(f'kh2/remastered/msg/us/fontimage.bar/US_fontimage_bar{index}.png'))).convert('RGBA')
            for cell in sorted(cells | ({36} if index == 1 else set())):
                x, y = cell % cols * width, cell // cols * height
                pixels = list(image.crop((x, y, x + width, y + height)).get_flattened_data())
                assert any(a for _, _, _, a in pixels), f'Empty glyph {index}:{cell}'
                assert any(a == 0 for _, _, _, a in pixels), f'Solid glyph {index}:{cell}'
                for red, green, blue, alpha in pixels:
                    assert bool(red or green or blue) == bool(alpha), f'RGB/alpha coverage mismatch {index}:{cell}'
                checked += 1
    assert checked == 235
    print(f'Font backgrounds: {checked} Arabic cells have matching RGB/alpha coverage and zero transparent RGB')

if __name__ == '__main__':
    import sys
    check_textures(Path(sys.argv[1]))
