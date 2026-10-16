"""Font gate: the Arabic cells must follow the game's own glyph conventions before the font is merged.

- every Arabic HD cell: no RGB behind transparent pixels (the 1.0.4 dialogue boxes), not empty, not solid;
- dialogue atlas (evt): white body in RGB plus the dark ring in alpha that every native dialogue glyph has;
- menu atlas (sys): RGB coverage equals alpha coverage (native menu glyphs have no ring);
- SD textures in msg/us/fontimage.bar: the game's 4bpp format, levels 0..3 per pixel only;
- baseline: the native digit 1 ends within 2 HD px of the Arabic connecting stroke."""
import csv
import io
from pathlib import Path
import struct
import zipfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
# atlas: PNG index, columns, HD cell width and height, SD rows, HD rows of the Arabic connecting stroke
ATLASES = {'sys': (0, 28, 36, 48, 256), 'evt': (1, 21, 48, 64, 512)}
LIGATURE, DIGIT_1, INI_BA = 36, 113, 163


def entries(data):
    result = {}
    for i in range(struct.unpack_from('<I', data, 4)[0]):
        _, name, offset, size = struct.unpack_from('<I4sII', data, 16 + i * 16)
        result[name.rstrip(b'\0').decode()] = data[offset:offset + size]
    return result


def bottom(rows):
    return max(y for y, row in enumerate(rows) if any(row))


def check_textures(archive):
    with (ROOT / 'build/tables/allocation.tsv').open(encoding='utf-8') as f:
        cells = {int(row['cell']) for row in csv.DictReader(f, delimiter='\t')}
    assert len(cells) == 117
    checked = 0
    with zipfile.ZipFile(archive) as z:
        sd = entries(z.read('kh2/msg/us/fontimage.bar'))
        for atlas, (index, cols, width, height, sd_rows) in ATLASES.items():
            image = Image.open(io.BytesIO(z.read(f'kh2/remastered/msg/us/fontimage.bar/US_fontimage_bar{index}.png'))).convert('RGBA')

            def tile(cell):
                x, y = cell % cols * width, cell // cols * height
                return list(image.crop((x, y, x + width, y + height)).get_flattened_data())

            for cell in sorted(cells | ({LIGATURE} if atlas == 'evt' else set())):
                pixels = tile(cell)
                assert any(a for _, _, _, a in pixels), f'Empty glyph {atlas}:{cell}'
                assert any(a == 0 for _, _, _, a in pixels), f'Solid glyph {atlas}:{cell}'
                assert not any(r or g or b for r, g, b, a in pixels if a == 0), f'RGB behind transparent pixels {atlas}:{cell}'
                if atlas == 'evt':
                    assert any(a >= 128 and r <= 16 for r, _, _, a in pixels), f'No dark ring {atlas}:{cell}'
                    assert any(r >= 100 for r, _, _, _ in pixels), f'No white body {atlas}:{cell}'
                else:
                    assert all(bool(r or g or b) == bool(a) for r, g, b, a in pixels), f'RGB/alpha coverage mismatch {atlas}:{cell}'
                checked += 1
            levels = sd[atlas]
            assert len(levels) == sd_rows * 256
            assert all(v & 15 <= 3 and v >> 4 <= 3 for v in levels), f'SD {atlas} texture is not 2-bit 4bpp'
            # Baseline: rows of the digit 1 body vs rows of the Arabic connecting stroke (ب initial, left edge).
            digit = tile(DIGIT_1)
            body = [(r >= 63) if atlas == 'evt' else (a >= 128) for r, _, _, a in digit]
            stroke = [a >= 128 for _, _, _, a in tile(INI_BA)]
            gap = bottom([body[y * width:(y + 1) * width] for y in range(height)]) - \
                bottom([[stroke[y * width]] for y in range(height)])
            assert abs(gap) <= 2, f'Digits sit {gap} HD px off the Arabic baseline in {atlas}'
    assert checked == 235
    print(f'Font: {checked} Arabic cells in game conventions (dialogue ring, no RGB behind transparency), '
          'SD 4bpp levels 0..3, digits on the Arabic baseline')


if __name__ == '__main__':
    import sys
    check_textures(Path(sys.argv[1]))
