"""Arabic message encoder/decoder for the KH2FM msg bars (Python port of Shape / ToVisualOrder / EncodeMsg
in reference/Program.cs). Stdlib only. Tables are read from ../tables (or the dir given to load()).

  decode(msg_bytes, arabic, lig) -> text (logical order; tags as <XX ..>, unknown cells <X hh>, newline ' ⏎ ')
  encode(text, lig)              -> msg bytes WITHOUT the End 0x00
  msgs(bar_bytes)                -> {id: raw message bytes}
  replace_msg(bar_bytes, id, new_bytes) -> new bar bytes (only that message changes)
  use_lig(bar, id)               -> lam+alef ligature on/off for this bar/id (tables/bar_options.tsv + noliga_ids.txt)
"""
import os, re, struct

TABLES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tables')
BOUND = (0x10, 0x14, 0x17)   # hard line-boundary commands: reordering restarts after them
ICON = 9                     # icon command: keeps its place between runs
LIG = 36                     # lam+alef ligature cell (evt atlas)
NL = ' ⏎ '
JOIN = {}
for _c in 'بتثجحخسشصضطظعغفقكلمنهيئ': JOIN[_c] = 'D'
for _c in 'ادذرزوةأإآؤى': JOIN[_c] = 'R'
JOIN['ء'] = 'U'

SZ, NOLIG, BAR_OPTS = {}, set(), {}
cell_ar, ar_enc, cell_ch, char_cell = {}, {}, {}, {}


def _rows(path):
    for l in open(path, encoding='utf-8-sig'):
        l = l.rstrip('\r\n')
        if l and not l.startswith('#'): yield l.split('\t')


def load(tables=TABLES):
    for d in (SZ, NOLIG, BAR_OPTS, cell_ar, ar_enc, cell_ch, char_cell): d.clear()
    for p in list(_rows(os.path.join(tables, 'cmd_sizes.tsv')))[1:]: SZ[int(p[0], 16)] = int(p[1])
    for l in open(os.path.join(tables, 'noliga_ids.txt'), encoding='utf-8-sig'):
        t = l.split('#')[0].strip()
        if t.isdigit(): NOLIG.add(int(t))
    for p in list(_rows(os.path.join(tables, 'bar_options.tsv')))[1:]: BAR_OPTS[p[0]] = (p[1], p[2] == '1')
    for l in open(os.path.join(tables, 'allocation.tsv'), encoding='utf-8').read().split('\n')[1:]:
        p = l.split('\t')
        if len(p) > 5 and p[4].isdigit(): cell_ar[int(p[4])] = p[0]; ar_enc[(p[0], int(p[2]))] = int(p[4])
    for l in open(os.path.join(tables, 'codemap.tsv'), encoding='utf-8').read().split('\n')[1:]:
        p = l.split('\t')
        if len(p) > 10 and p[10] == 'GLYPH' and p[1].lstrip('-').isdigit() and len(p[5]) == 1:
            c = int(p[1])
            if c < 0: continue
            cell_ch[c] = p[5]
            if c not in cell_ar and p[5] not in char_cell: char_cell[p[5]] = c
    # cell 46 = tight full stop (gumi only): kept as token <X 2E>
    cell_ch.pop(46, None)
    for k in [k for k, v in char_cell.items() if v == 46]: del char_cell[k]


def use_lig(bar, msg_id):
    return BAR_OPTS[bar][1] and msg_id not in NOLIG


def msgs(b):
    off, ln = struct.unpack_from('<II', b, 24)
    m = b[off:off + ln]
    n = struct.unpack_from('<I', m, 4)[0]
    ids = [struct.unpack_from('<I', m, 8 + i * 8)[0] for i in range(n)]
    of = [struct.unpack_from('<I', m, 12 + i * 8)[0] for i in range(n)]
    return {ids[i]: m[of[i]:(of[i + 1] if i + 1 < n else len(m))] for i in range(n)}


def replace_msg(b, msg_id, new):
    """Rebuild bar b with message msg_id = new + End 0x00. Other messages keep their bytes; sizes/offsets are fixed up."""
    off, ln = struct.unpack_from('<II', b, 24)
    m = b[off:off + ln]
    n = struct.unpack_from('<I', m, 4)[0]
    ids = [struct.unpack_from('<I', m, 8 + i * 8)[0] for i in range(n)]
    of = [struct.unpack_from('<I', m, 12 + i * 8)[0] for i in range(n)]
    k = ids.index(msg_id)
    end = of[k + 1] if k + 1 < n else len(m)
    new = new + b'\0'
    d = len(new) - (end - of[k])
    m2 = bytearray(m[:of[k]] + new + m[end:])
    for i in range(k + 1, n): struct.pack_into('<I', m2, 12 + i * 8, of[i] + d)
    out = bytearray(b[:off] + m2 + b[off + ln:])
    struct.pack_into('<I', out, 28, ln + d)
    for e in range(1, struct.unpack_from('<I', b, 4)[0]):
        o = struct.unpack_from('<I', out, 24 + e * 16)[0]
        if o >= off + ln: struct.pack_into('<I', out, 24 + e * 16, o + d)
    return bytes(out)


# ---------- reorder (port of ReverseRunOrder / ToVisualOrder); items = (char, isArabic); sentinels U+E000+k
def _rro(s, seg, icons):
    if not any(s[k][1] for k in seg): return seg
    runs = []
    for k in seg:
        isAr = s[k][1]; isSep = s[k][0] in ' \n'
        prevSep = bool(runs) and s[runs[-1][0]][0] in ' \n'
        isIcon = s[k][0] in icons; prevIcon = bool(runs) and s[runs[-1][0]][0] in icons
        if not runs or isSep or prevSep or isIcon != prevIcon or s[runs[-1][0]][1] != isAr: runs.append([])
        runs[-1].append(k)
    vis = []
    for r in reversed(runs):
        if s[r[0]][1]: r = r[::-1]
        vis += r
    return vis


def visual_order(s, hard, icons):
    res, seg = [], []
    for i, (c, a) in enumerate(s):
        if c == '\n' or c in hard: res += _rro(s, seg, icons); res.append(i); seg = []
        else: seg.append(i)
    return res + _rro(s, seg, icons)


def parse(m):
    """-> (items, endpos); items: ('c',cell)|('sp',)|('nl',)|('t',bytes). Raises on bad structure."""
    it, i = [], 0
    while True:
        if i >= len(m): raise ValueError('no End 0x00')
        b = m[i]
        if b == 0: break
        if b == 1: it.append(('sp',))
        elif b == 2: it.append(('nl',))
        elif b < 0x20:
            if b not in SZ: raise ValueError('unknown cmd %02X' % b)
            n = SZ[b]
            if i + n >= len(m): raise ValueError('truncated cmd')
            it.append(('t', bytes(m[i:i + n + 1]))); i += n
        else: it.append(('c', b - 0x20))
        i += 1
    if any(m[i:]): raise ValueError('non-zero after End')
    return it, i


def padded(m): return m[:parse(m)[1]]


def decode(m, arabic, lig):
    items, _ = parse(m)
    sent, flat, kinds = [], [], []
    for x in items:
        if x[0] == 'sp': flat.append((' ', False))
        elif x[0] == 'nl': flat.append(('\n', False))
        elif x[0] == 't':
            flat.append((chr(0xE000 + len(sent)), False)); sent.append('<' + ' '.join('%02X' % v for v in x[1]) + '>'); kinds.append(x[1][0])
        else:
            c = x[1]
            if arabic and c in cell_ar: flat.append((cell_ar[c], True))
            elif arabic and lig and c == LIG: flat.append(('ا', True)); flat.append(('ل', True))
            elif c in cell_ch and char_cell.get(cell_ch[c]) == c: flat.append((cell_ch[c], False))
            else:   # unknown cell, or a duplicate glyph (same char on two cells): keep the exact cell as <X hh>
                flat.append((chr(0xE000 + len(sent)), False)); sent.append('<X %02X>' % c); kinds.append(None)
    hard = {chr(0xE000 + k) for k, kd in enumerate(kinds) if kd in BOUND}
    icons = {chr(0xE000 + k) for k, kd in enumerate(kinds) if kd == ICON}
    order = visual_order(flat, hard, icons) if arabic else range(len(flat))
    out = []
    for k in order:
        c = flat[k][0]
        if c == '\n': out.append(NL)
        elif 0xE000 <= ord(c) <= 0xF8FF: out.append(sent[ord(c) - 0xE000])
        else: out.append(c)
    return ''.join(out)


def encode(s, lig):
    sent, flat = [], []
    s = s.replace(NL, '\n')
    i = 0
    while i < len(s):
        mt = re.match(r'<X ([0-9A-F]{2})>', s[i:])
        mt2 = re.match(r'<((?:[0-9A-F]{2})(?: [0-9A-F]{2})*)>', s[i:])
        if s[i] == '<' and mt:
            flat.append(chr(0xE000 + len(sent))); sent.append(bytes([int(mt.group(1), 16) + 0x20])); i += mt.end()
        elif s[i] == '<' and mt2:
            raw = bytes(int(x, 16) for x in mt2.group(1).split(' '))
            if raw[0] in SZ and len(raw) == SZ[raw[0]] + 1:
                flat.append(chr(0xE000 + len(sent))); sent.append(raw); i += mt2.end()
            else: flat.append(s[i]); i += 1
        else: flat.append(s[i]); i += 1
    n = len(flat)
    isA = [c in JOIN for c in flat]
    shaped = []
    for i, c in enumerate(flat):
        if not isA[i]: shaped.append((c, -1)); continue
        jp = i > 0 and isA[i - 1] and JOIN[flat[i - 1]] == 'D' and JOIN[c] != 'U'
        jn = i + 1 < n and isA[i + 1] and JOIN[flat[i + 1]] != 'U' and JOIN[c] == 'D'
        f = 3 if jp and jn else 1 if jp else 2 if jn else 0
        shaped.append((c, f))
    hard = {chr(0xE000 + k) for k, r in enumerate(sent) if r[0] in BOUND}
    icons = {chr(0xE000 + k) for k, r in enumerate(sent) if r[0] == ICON}
    vis = [shaped[k] for k in visual_order([(c, f >= 0) for c, f in shaped], hard, icons)]
    res = bytearray(); vi = 0
    while vi < len(vis):
        c, f = vis[vi]
        if lig and c == 'ا' and f == 1 and vi + 1 < len(vis) and vis[vi + 1] == ('ل', 2):
            res.append(LIG + 0x20); vi += 2; continue
        if 0xE000 <= ord(c) <= 0xF8FF: res += sent[ord(c) - 0xE000]
        elif f >= 0: res.append(ar_enc[(c, f)] + 0x20)
        elif c == ' ': res.append(1)
        elif c == '\n': res.append(2)
        else: res.append(char_cell[c] + 0x20)
        vi += 1
    return bytes(res)


load()
