import importlib.util
from pathlib import Path
import struct
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'build/tools'))
import unittest

spec = importlib.util.spec_from_file_location('green_layout', Path(__file__).resolve().parents[1] / 'build/tools/align_green_commands.py')
green = importlib.util.module_from_spec(spec)
spec.loader.exec_module(green)
from green_anchor import parse


def fixture():
    sections = []
    offset = 48
    for count, size in [(4, 44), (4, 20), (2, 4), (6, 144), (6, 36)]:
        sections.append((count, offset))
        offset += count * size
    seq = bytearray(offset)
    seq[:4] = b'SEQD'
    for i, section in enumerate(sections):
        struct.pack_into('<II', seq, 8 + i * 8, *section)
    for i in range(4):
        struct.pack_into('<i', seq, sections[1][1] + i * 20 + 16, i)
    struct.pack_into('<hhhh', seq, sections[2][1], 0, 3, 3, 1)
    for i in range(6):
        struct.pack_into('<ii', seq, sections[3][1] + i * 144, 2, int(i == 4))
        struct.pack_into('<hh', seq, sections[4][1] + i * 36, i, 1)
    bar = bytearray(64) + seq
    bar[:4] = b'BAR\x01'
    struct.pack_into('<I', bar, 4, 2)
    struct.pack_into('<I4sII', bar, 16, 24, b'comw', 48, 16)
    struct.pack_into('<I4sII', bar, 32, 25, b'comw', 64, len(seq))
    return bar


class GreenLayoutTests(unittest.TestCase):
    def test_invisible_anchor_moves_text_and_preserves_drawable_records(self):
        original = fixture()
        result = green.patch(original, 10)
        _, _, _, before, _ = parse(original)
        _, _, _, after, _ = parse(result)
        self.assertEqual(after[:2], before[:2])
        self.assertEqual(after[2][:-4], before[2])
        self.assertEqual(after[2][-4:], b'\0' * 4)
        self.assertEqual(len(after[3]) - len(before[3]), 5 * 144)
        empty = len(before[2]) // 4
        kept = [after[3][i:i + 144] for i in range(0, len(after[3]), 144)
                if struct.unpack_from('<i', after[3], i + 4)[0] != empty]
        self.assertEqual(b''.join(kept), before[3])
        for group in range(6):
            self.assertEqual(after[4][group * 36 + 4:(group + 1) * 36],
                             before[4][group * 36 + 4:(group + 1) * 36])
        self.assertEqual(green.patch(original, 10), result)

    def test_rejects_truncated_bar_and_invalid_sequence_bounds(self):
        for data in [fixture()[:40], fixture()[:-1]]:
            with self.assertRaises(ValueError):
                green.patch(data, 10)
        data = fixture()
        struct.pack_into('<I', data, 64 + 44, len(data))
        with self.assertRaisesRegex(ValueError, 'table bounds'):
            green.patch(data, 10)

    def test_rejects_unexpected_existing_position(self):
        data = fixture()
        table, _, _ = green.layout(data)
        struct.pack_into('<i', data, table + 20, 5)
        with self.assertRaisesRegex(ValueError, 'existing text Y'):
            green.patch(data, 10)

    def test_rejects_sprite_reference_outside_table(self):
        data = fixture()
        parts = struct.unpack_from('<I', data, 64 + 20)[0]
        struct.pack_into('<i', data, 64 + parts + 16, 999)
        with self.assertRaisesRegex(ValueError, 'Sprite index'):
            green.patch(data, 10)
