"""Add invisible active text anchors, retaining every original drawable record."""
import hashlib
import struct as S

TARGETS = {0, 1, 2, 3, 5}
SIZES = [44, 20, 4, 144, 36]
SHIFT = 10


def parse(bar):
    assert bar[:4] == b'BAR\x01' and S.unpack_from('<I', bar, 4)[0] == 2
    kind, _, base, length = S.unpack_from('<I4sII', bar, 32)
    assert kind == 25 and base + length <= len(bar)
    seq = bar[base:base + length]
    assert seq[:4] == b'SEQD'
    sections = [S.unpack_from('<II', seq, 8 + 8 * i) for i in range(5)]
    arrays = [seq[offset:offset + count * size] for (count, offset), size in zip(sections, SIZES)]
    assert all(len(a) == count * size for a, (count, _), size in zip(arrays, sections, SIZES))
    assert all(sections[i + 1][1] == sections[i][1] + sections[i][0] * SIZES[i] for i in range(4))
    tail = seq[sections[-1][1] + sections[-1][0] * SIZES[-1]:]
    return base, length, seq[:sections[0][1]], arrays, tail


def first_active(animations, frame):
    for record in animations:
        flags, _, start, end = S.unpack_from('<4i', record)
        if flags & 2 and start <= frame <= end:
            return record
    return None


def build(original):
    base, length, header, arrays, tail = parse(original)
    sprites, parts, frame_groups, raw_animations, raw_states = arrays
    empty_group = len(frame_groups) // 4
    new_animations = []
    new_states = bytearray(raw_states)
    cursor = 0
    clones = []
    intervals_checked = 0
    for group in range(len(raw_states) // 36):
        state_offset = group * 36
        start, count = S.unpack_from('<hh', raw_states, state_offset)
        assert start == cursor, 'Source animation groups are not contiguous'
        cursor += count
        old_records = [raw_animations[i * 144:(i + 1) * 144] for i in range(start, start + count)]
        new_start = len(new_animations)
        expanded = []
        for index, record in enumerate(old_records):
            assert len(record) == 144
            if group in TARGETS and S.unpack_from('<I', record)[0] & 2:
                assert not S.unpack_from('<I', record)[0] & 0x80000, 'Unexpected tag callback'
                dummy = bytearray(record)
                S.pack_into('<i', dummy, 4, empty_group)
                for offset in [0x18, 0x1c]:
                    S.pack_into('<i', dummy, offset, S.unpack_from('<i', dummy, offset)[0] + SHIFT)
                expanded.append(bytes(dummy))
                clones.append({'group': group, 'original_animation': start + index})
            expanded.append(record)
        new_animations.extend(expanded)
        S.pack_into('<hh', new_states, state_offset, new_start, len(expanded))
        if group in TARGETS:
            # Native Steam GetActiveXY chooses the FIRST flagged animation in range.
            # Match its selection at every integer frame and at half-frame boundaries.
            maximum = max((S.unpack_from('<i', r, 12)[0] for r in old_records), default=0)
            for tick in range(maximum * 2 + 1):
                old = first_active(old_records, tick / 2)
                new = first_active(expanded, tick / 2)
                if old is None:
                    assert new is None
                    continue
                assert new is not None
                permitted = {4, 5, 6, 7, 24, 25, 26, 27, 28, 29, 30, 31}
                assert all(a == b or i in permitted for i, (a, b) in enumerate(zip(old, new)))
                assert S.unpack_from('<i', new, 4)[0] == empty_group
                for offset in [24, 28]:
                    assert S.unpack_from('<i', new, offset)[0] == S.unpack_from('<i', old, offset)[0] + SHIFT
                intervals_checked += 1
        else:
            assert expanded == old_records
    assert cursor * 144 == len(raw_animations)
    arrays = [sprites, parts, frame_groups + S.pack('<hh', 0, 0), b''.join(new_animations), bytes(new_states)]
    new_header = bytearray(header)
    offset = len(header)
    for i, (data, size) in enumerate(zip(arrays, SIZES)):
        assert len(data) % size == 0
        S.pack_into('<II', new_header, 8 + 8 * i, len(data) // size, offset)
        offset += len(data)
    seq = bytes(new_header) + b''.join(arrays) + tail
    before = bytearray(original[:base])
    S.pack_into('<I', before, 44, len(seq))
    result = bytes(before) + seq + original[base + length:]
    # All original renderable animation rows, image data, UVs and vertices remain exact.
    _, _, _, decoded, decoded_tail = parse(result)
    assert decoded[0] == sprites and decoded[1] == parts
    assert decoded[2][:-4] == frame_groups and decoded[2][-4:] == b'\0' * 4
    kept = []
    for i in range(len(decoded[3]) // 144):
        record = decoded[3][i * 144:(i + 1) * 144]
        if S.unpack_from('<i', record, 4)[0] != empty_group:
            kept.append(record)
    assert b''.join(kept) == raw_animations
    assert decoded_tail == tail
    assert result[:44] == original[:44] and result[48:base] == original[48:base]
    for group in range(len(raw_states) // 36):
        assert decoded[4][group * 36 + 4:(group + 1) * 36] == raw_states[group * 36 + 4:(group + 1) * 36]
    return result, {'invisible_anchors': len(clones), 'native_first_anchor_cases_checked': intervals_checked,
                    'all_original_drawable_records_identical': True, 'all_images_uvs_vertices_identical': True,
                    'button_and_primary_states_identical': True, 'text_y_delta': SHIFT,
                    'source_sha256': hashlib.sha256(original).hexdigest(),
                    'sha256': hashlib.sha256(result).hexdigest(), 'size': len(result),
                    'in_game_verified': False}


