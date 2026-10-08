"""Verify a payload folder against a manifest (path, size, sha256).
  python tools/verify_payload.py <dir containing kh2/> [manifest.tsv]   (default config/FROZEN_MANIFEST.tsv)
Exit 0 only if every listed file exists with the listed size and SHA256 and no extra file is present."""
import hashlib, os, sys
KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root = os.path.join(sys.argv[1], 'kh2')
man = sys.argv[2] if len(sys.argv) > 2 else os.path.join(KIT, 'config', 'FROZEN_MANIFEST.tsv')
rows = [l.rstrip('\n').split('\t') for l in open(man, encoding='utf-8')][1:]
bad, listed = [], set()
for path, size, sha in rows:
    p = os.path.join(root, *path.split('\\')); listed.add(os.path.normcase(os.path.normpath(p)))
    if not os.path.isfile(p): bad.append('missing ' + path); continue
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for blk in iter(lambda: f.read(1 << 20), b''): h.update(blk)
    if os.path.getsize(p) != int(size) or h.hexdigest() != sha: bad.append('mismatch ' + path)
extra = [os.path.relpath(os.path.join(d, f), root) for d, _, fs in os.walk(root) for f in fs
         if os.path.normcase(os.path.normpath(os.path.join(d, f))) not in listed]
for b in bad[:30]: print(b)
for e in extra[:30]: print('extra', e)
print('payload: %d listed, %d verified, %d bad, %d extra' % (len(rows), len(rows) - len(bad), len(bad), len(extra)))
sys.exit(1 if bad or extra else 0)
