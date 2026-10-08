"""Privacy scan of the kit (or any folder). Needles are passed on the command line / env so they are not stored in the repo.
  python tools/privacy_scan.py <folder> <needle> [<needle> ...]     e.g. user name, cloud-folder name, mail domain
Also flags e-mail addresses, tokens, Windows user paths. Case-insensitive, raw bytes + UTF-16LE. Exit 1 on any hit."""
import os, re, sys
root, needles = sys.argv[1], [n.lower() for n in sys.argv[2:]]
rx = {'email': rb'[A-Za-z0-9._%+-]{2,}@[A-Za-z0-9-]+\.[A-Za-z0-9.-]*[A-Za-z]{2,}',
      'token': rb'(ghp_[A-Za-z0-9]{20,}|github_pa[t]_|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16})',
      'user_path': rb'(?i)[a-z]:\\users\\[^\\\s"\']+'}
ALLOW = (b'creator.club.ne.jp',)   # upstream vgmstream copyright notice inside the shipped license texts
hits = 0
for d, _, fs in os.walk(root):
    for n in fs:
        p = os.path.join(d, n); b = open(p, 'rb').read(); low = b.lower()
        for nd in needles:
            if nd.encode() in low or nd.encode('utf-16-le') in low: print('HIT', nd, p); hits += 1
        for k, r in rx.items():
            m = re.search(r, b)
            if m and m.group(0).split(b'@')[-1] not in ALLOW: print('HIT', k, p, m.group(0)[:60]); hits += 1
print('privacy scan: %d hits' % hits)
sys.exit(1 if hits else 0)
