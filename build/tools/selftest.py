"""Self-test. Input: the INSTALLED msg bars (dir with sys.bar, tt.bar, ...) - nothing else from the game.
  python tools/selftest.py <bars_dir>
1. SHA256 of every bar == config/expected_bars.sha256
2. every message of every bar: decode -> encode == original bytes
3. one fake correction (re-encoded text of one id altered): only that id changes, all other ids byte-identical
Exit code 0 = all pass."""
import hashlib, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import arabic_msg as A
KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bars_dir = sys.argv[1]
fail = 0

exp = dict(l.split()[::-1] for l in open(os.path.join(KIT, 'config', 'expected_bars.sha256')) if l.strip())
for bar in A.BAR_OPTS:
    h = hashlib.sha256(open(os.path.join(bars_dir, bar + '.bar'), 'rb').read()).hexdigest()
    if exp[bar + '.bar'] != h: print('SHA MISMATCH', bar); fail += 1
print('1. sha256: %d bars checked' % len(A.BAR_OPTS))

tot = 0
data, plain = {}, []
for bar in A.BAR_OPTS:
    b = data[bar] = open(os.path.join(bars_dir, bar + '.bar'), 'rb').read()
    ms = A.msgs(b)
    bad = []
    for i, raw in ms.items():
        if not any(raw): continue                      # empty slot
        lig = A.use_lig(bar, i)
        try:
            ok = A.encode(A.decode(raw, True, lig), lig) == A.padded(raw)
        except Exception:
            ok = False
        if not ok:   # untranslated retail-English row whose cells overlap Arabic glyph cells: plain (non-Arabic) mode
            try:
                ok = A.encode(A.decode(raw, False, False), False) == A.padded(raw)
                plain.append((bar, i))
            except Exception:
                ok = False
        tot += 1
        if not ok: bad.append(i)
    print('2. %-6s msgs %5d  mismatches %d %s' % (bar, len(ms), len(bad), bad[:5]))
    fail += len(bad)
print('2. total messages round-tripped: %d (of which %d via plain-English mode: %s)' % (tot, len(plain), plain))

# 3. fake correction on tt: append the word "اختبار" (test) to the first Arabic message
bar = 'tt'
ms = A.msgs(data[bar])
tid = next(i for i, r in sorted(ms.items()) if any(r) and any(0x0600 <= ord(c) <= 0x06FF for c in A.decode(r, True, A.use_lig(bar, i))))
lig = A.use_lig(bar, tid)
txt = A.decode(ms[tid], True, lig)
new = A.encode(txt + ' اختبار', lig)
nb = A.replace_msg(data[bar], tid, new)
ms2 = A.msgs(nb)
changed = [i for i in ms if ms[i] != ms2.get(i)]
ok3 = changed == [tid] and set(ms) == set(ms2) and A.decode(ms2[tid], True, lig) == txt + ' اختبار'
ok3 = ok3 and len(nb) - len(data[bar]) == len(ms2[tid]) - len(ms[tid])
print('3. fake correction on tt id %d: changed ids %s -> %s' % (tid, changed, 'PASS' if ok3 else 'FAIL'))
fail += 0 if ok3 else 1
print('SELFTEST', 'PASS' if not fail else 'FAIL (%d)' % fail)
sys.exit(1 if fail else 0)
