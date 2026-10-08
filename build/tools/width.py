"""Width tool: line widths of messages from the advance table in fontinfo.bar (read at build time; fontinfo.bar is not shipped).
  advances(fontinfo_path, atlas)  atlas 'sys' | 'evt' -> bytes; advance of cell c = list[c]/2 px units
  maxw(msg, adv)                  widest line (any page) of a raw message
CLI: python tools/width.py <fontinfo.bar> <bar> [id ...]"""
import os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import arabic_msg as A


def advances(fontinfo, atlas):
    d = open(fontinfo, 'rb').read()
    for i in range(struct.unpack_from('<I', d, 4)[0]):
        e = 16 + i * 16
        if d[e + 4:e + 8].split(b'\0')[0].decode() == atlas:
            o, s = struct.unpack_from('<II', d, e + 8)
            return d[o:o + s]
    raise KeyError(atlas)


def pages(m):
    """pages -> lines -> cells (None = space). A page ends at command 0x10."""
    pgs, lines, cur, i = [], [], [], 0
    while i < len(m):
        b = m[i]
        if b == 0: break
        if b == 1: cur.append(None); i += 1; continue
        if b == 2: lines.append(cur); cur = []; i += 1; continue
        if b < 0x20:
            if b == 0x10:
                lines.append(cur); cur = []
                if any(c is not None for l in lines for c in l): pgs.append(lines)
                lines = []
            i += 1 + A.SZ.get(b, 0); continue
        cur.append(b - 0x20); i += 1
    lines.append(cur)
    if any(c is not None for l in lines for c in l): pgs.append(lines)
    return pgs


def lw(line, adv): return sum(5 if c is None else adv[c] / 2.0 for c in line)
def maxw(m, adv): return max((lw(l, adv) for p in pages(m) for l in p), default=0.0)


if __name__ == '__main__':
    fi, bar = sys.argv[1], sys.argv[2]
    adv = advances(fi, A.BAR_OPTS[os.path.basename(bar)[:-4]][0])
    ms = A.msgs(open(bar, 'rb').read())
    for i in ([int(x) for x in sys.argv[3:]] or sorted(ms)[:10]): print(i, maxw(ms[i], adv))
