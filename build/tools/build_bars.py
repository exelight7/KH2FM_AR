"""Build the corrected text bars from the installed payload + corrections/, with gates.

  python build/tools/build_bars.py --payload <dir containing kh2/> --version 1.0.1 [--repo .] [--out build/out]

Steps (each one reported in build/report/BUILD_REPORT.md):
  b) consistency gate: kit decode of the installed bar == review/*.csv AR for every row
     (rows in config/consistency_known.tsv are accepted while they have no correction)
  c) apply every corrections/*.csv except needs_width_check.csv (AR_old must equal the current text)
  d) needs_width_check.csv: real widths from fontinfo.bar; a term is applied only if ALL its rows fit
  e) gates: intended ids only, untouched messages byte-identical, round-trip, tags and line breaks,
     allowed cells only, bars re-parse, all other payload files unchanged
Writes <out>/kh2/msg/us/<bar>.bar for changed bars, <out>/MANIFEST.tsv (full payload manifest with the new
bars), build/report/BUILD_REPORT.md and build/report/CHANGELOG.md. Exit 1 if any gate fails."""
import argparse, collections, csv, glob, hashlib, os, re, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import arabic_msg as A
import width as W

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument('--payload', required=True, help='folder that contains kh2/msg/us/*.bar (full payload for the file gate)')
ap.add_argument('--version', required=True)
ap.add_argument('--repo', default=os.path.dirname(KIT))
ap.add_argument('--out', default=os.path.join(KIT, 'out'))
ap.add_argument('--report', default=os.path.join(KIT, 'report'))
args = ap.parse_args()

MSG = os.path.join(args.payload, 'kh2', 'msg', 'us')
TAG = re.compile(r'<[0-9A-F]{2}(?: [0-9A-F]{2})*>')
UNK = re.compile(r'<X [0-9A-F]{2}>')
sha = lambda b: hashlib.sha256(b).hexdigest()
BARS = list(A.BAR_OPTS)
gates = collections.OrderedDict()      # name -> (ok, detail)
fatal = []


def gate(name, ok, detail):
    gates[name] = (ok, detail)
    if not ok: fatal.append(name)


def tags(s): return TAG.findall(s.replace('<X ', '<x '))   # control tags only (<X hh> cells are text)


def decode_any(bar, i, raw):
    """kit decode; plain (non-Arabic) mode for retail-English rows that do not round-trip as Arabic."""
    lig = A.use_lig(bar, i)
    try:
        t = A.decode(raw, True, lig)
        if A.encode(t, lig) == A.padded(raw): return t, 'ar'
    except Exception:
        pass
    return A.decode(raw, False, False), 'plain'


# ---------------------------------------------------------------- inputs
orig = {b: open(os.path.join(MSG, b + '.bar'), 'rb').read() for b in BARS}
omsgs = {b: A.msgs(orig[b]) for b in BARS}
review = {}
for f in sorted(glob.glob(os.path.join(args.repo, 'review', '*.csv'))):
    for r in csv.DictReader(open(f, encoding='utf-8-sig')):
        review[(r['bar'], int(r['id']))] = r
known = {}
for l in open(os.path.join(KIT, 'config', 'consistency_known.tsv'), encoding='utf-8'):
    if l.startswith('#') or l.startswith('bar\t') or not l.strip(): continue
    p = l.rstrip('\n').split('\t'); known[(p[0], int(p[1]))] = p[2]

corr, corr_src, dup = {}, {}, []
for f in sorted(glob.glob(os.path.join(args.repo, 'corrections', '*.csv'))):
    name = os.path.basename(f)
    if name == 'needs_width_check.csv': continue
    for r in csv.DictReader(open(f, encoding='utf-8')):
        k = (r['bar'], int(r['id']))
        if k in corr: dup.append((k, corr_src[k], name))
        corr[k] = r; corr_src[k] = name
width_rows = list(csv.DictReader(open(os.path.join(args.repo, 'corrections', 'needs_width_check.csv'), encoding='utf-8')))

# ---------------------------------------------------------------- b) consistency
cur, mism, plain_rows = {}, collections.defaultdict(list), 0
for (bar, i), r in sorted(review.items()):
    raw = omsgs[bar].get(i)
    if raw is None: mism[bar].append((i, 'missing in bar')); continue
    t, mode = decode_any(bar, i, raw)
    cur[(bar, i)] = t
    plain_rows += mode == 'plain'
    if t != r['AR']: mism[bar].append((i, mode))
bars_with_corr = {b for b, _ in corr} | {r['bar'] for r in width_rows}
unexpected = [(b, i) for b in mism for i, _ in mism[b] if (b, i) not in known]
known_with_corr = [(b, i) for b in mism for i, _ in mism[b] if (b, i) in known and ((b, i) in corr or any(w['bar'] == b and int(w['id']) == i for w in width_rows))]
bad_bars = sorted({b for b, i in unexpected if b in bars_with_corr})
n_mism = sum(len(v) for v in mism.values())
gate('b. consistency (kit decode == review AR)', not bad_bars and not known_with_corr,
     '%d review rows compared, %d differ: %d accepted (config/consistency_known.tsv: %s), %d unexpected%s%s'
     % (len(review), n_mism, n_mism - len(unexpected), ', '.join('%s %d' % k for k in sorted(known)),
        len(unexpected), (' in bars with corrections: %s' % bad_bars) if bad_bars else '',
        ('; known rows that have a correction: %s' % known_with_corr) if known_with_corr else ''))

# ---------------------------------------------------------------- c) corrections
gate('c0. one correction per id', not dup, 'duplicates: %s' % dup if dup else '%d corrections in %d files, no id twice'
     % (len(corr), len(set(corr_src.values()))))
plan = {}          # (bar,id) -> dict(new_text, source, type)
cerr = []
for k, r in sorted(corr.items()):
    bar, i = k
    if bar not in omsgs or i not in omsgs[bar]: cerr.append('%s %d: id not in bar' % k); continue
    if r['AR_old'] != cur.get(k):
        cerr.append('%s %d: AR_old differs from the current text' % k); continue
    plan[k] = dict(new=r['AR_new'], src=corr_src[k], type=r['type'], old=r['AR_old'])
gate('c1. AR_old equals the current text', not cerr, '; '.join(cerr[:20]) or 'all %d rows' % len(corr))

# ---------------------------------------------------------------- d) width-check terms (real widths)
adv = {a: W.advances(os.path.join(MSG, 'fontinfo.bar'), a) for a in ('sys', 'evt')}
units = collections.OrderedDict()
for r in width_rows:
    key = r.get('term') or '(row) %s %s' % (r['bar'], r['id'])
    units.setdefault(key, []).append(r)
wres = []   # (unit, applied, rows[(bar,id,eng,old,new,pct_new,ok)])
werr = []
for unit, rows in units.items():
    det, allok = [], True
    for r in rows:
        bar, i = r['bar'], int(r['id'])
        if r['AR_old'] != cur.get((bar, i)):
            werr.append('%s %d: AR_old differs from the current text' % (bar, i)); allok = False; continue
        lig = A.use_lig(bar, i)
        a = adv[A.BAR_OPTS[bar][0]]
        try:
            nb = A.encode(r['AR_new'], lig)
        except Exception as e:
            werr.append('%s %d: cannot encode (%s)' % (bar, i, e)); allok = False; continue
        old_w = W.maxw(A.padded(omsgs[bar][i]), a); new_w = W.maxw(nb, a)
        pct = float(review[(bar, i)]['width_pct'])
        eng = old_w / (pct / 100.0) if pct else 0
        ok = (eng and new_w <= 1.30 * eng) or new_w <= old_w
        det.append((bar, i, eng, old_w, new_w, (100.0 * new_w / eng) if eng else 0, pct, ok))
        allok = allok and ok
    wres.append((unit, allok, det))
    if allok:
        for bar, i, *_ in det:
            r = next(x for x in rows if x['bar'] == bar and int(x['id']) == i)
            prev = plan.get((bar, i))
            plan[(bar, i)] = dict(new=r['AR_new'], src='needs_width_check.csv (%s)' % unit,
                                  type='glossary' if r.get('term') else (prev['type'] if prev else 'phrasing'), old=r['AR_old'])
gate('d0. width rows readable', not werr, '; '.join(werr) or '%d rows in %d terms/rows measured' % (len(width_rows), len(units)))

# ---------------------------------------------------------------- apply
newbar, enc, aerr = {}, {}, []
for bar in BARS:
    b = orig[bar]
    for (bb, i), p in sorted(plan.items()):
        if bb != bar: continue
        lig = A.use_lig(bar, i)
        try:
            nb = A.encode(p['new'], lig)
        except Exception as e:
            aerr.append('%s %d: cannot encode (%r)' % (bar, i, e)); continue
        enc[(bar, i)] = nb
        if nb != A.padded(omsgs[bar][i]): b = A.replace_msg(b, i, nb)
    newbar[bar] = b
gate('e0. every correction encodes (allowed characters)', not aerr, '; '.join(aerr[:20]) or 'all %d encoded' % len(enc))

# ---------------------------------------------------------------- e) gates
intended = {k for k, nb in enc.items() if nb != A.padded(omsgs[k[0]][k[1]])}
noop = sorted(k for k in enc if k not in intended)
chg, untouched_bad, parse_bad, rt_bad, tag_bad, cell_bad = set(), [], [], [], [], []
for bar in BARS:
    try:
        nm = A.msgs(newbar[bar])
        for i, m in nm.items(): A.parse(m)
        if set(nm) != set(omsgs[bar]): parse_bad.append('%s: id set changed' % bar)
    except Exception as e:
        parse_bad.append('%s: %s' % (bar, e)); continue
    for i in omsgs[bar]:
        if nm[i] != omsgs[bar][i]:
            chg.add((bar, i))
            if (bar, i) not in intended: untouched_bad.append('%s %d' % (bar, i))
for k in sorted(intended):
    bar, i = k; p = plan[k]; lig = A.use_lig(bar, i)
    m = A.msgs(newbar[bar])[i]
    try:
        t = A.decode(m, True, lig)
        if t != p['new'] or A.encode(t, lig) != A.padded(m): rt_bad.append('%s %d' % k)
    except Exception:
        rt_bad.append('%s %d' % k)
    if tags(p['new']) != tags(p['old']) or p['new'].count('⏎') != p['old'].count('⏎'): tag_bad.append('%s %d' % k)
    if sorted(UNK.findall(p['new'])) != sorted(UNK.findall(p['old'])): cell_bad.append('%s %d' % k)
gate('e1. only intended ids differ', chg == intended, '%d messages changed, %d intended%s' % (len(chg), len(intended),
     '' if chg == intended else '; unexpected: %s; missing: %s' % (sorted(chg - intended)[:10], sorted(intended - chg)[:10])))
gate('e2. every untouched message byte-identical', not untouched_bad, ', '.join(untouched_bad[:20]) or
     '%d untouched messages identical' % (sum(len(v) for v in omsgs.values()) - len(chg)))
gate('e3. round-trip (decode == AR_new, re-encode identical)', not rt_bad, ', '.join(rt_bad[:20]) or 'all %d changed messages' % len(intended))
gate('e4. tags and line breaks equal to the old row', not tag_bad, ', '.join(tag_bad[:20]) or 'all %d changed messages' % len(intended))
gate('e5. allowed cells only (no new unknown cell)', not cell_bad, ', '.join(cell_bad[:20]) or 'all %d changed messages' % len(intended))
gate('e6. bars re-parse', not parse_bad, '; '.join(parse_bad) or '%d bars, %d messages parsed' % (len(BARS), sum(len(v) for v in omsgs.values())))

# other payload files
man = [l.rstrip('\n').split('\t') for l in open(os.path.join(KIT, 'config', 'FROZEN_MANIFEST.tsv'), encoding='utf-8')][1:]
changed_bars = sorted(b for b in BARS if newbar[b] != orig[b])
changed_paths = {'msg\\us\\%s.bar' % b for b in changed_bars}
ferr, nfiles = [], 0
for path, size, h in man:
    p = os.path.join(args.payload, 'kh2', *path.split('\\'))
    if not os.path.isfile(p): ferr.append('missing ' + path); continue
    d = open(p, 'rb').read(); nfiles += 1
    if len(d) != int(size) or sha(d) != h: ferr.append('changed ' + path)
gate('e7. payload files = FROZEN_MANIFEST (input)', not ferr, '; '.join(ferr[:10]) or '%d files, size and SHA256 match' % nfiles)

# ---------------------------------------------------------------- outputs
os.makedirs(os.path.join(args.out, 'kh2', 'msg', 'us'), exist_ok=True)
os.makedirs(args.report, exist_ok=True)
newman = []
for path, size, h in man:
    if path in changed_paths:
        b = path.split('\\')[-1][:-4]; d = newbar[b]
        open(os.path.join(args.out, 'kh2', 'msg', 'us', b + '.bar'), 'wb').write(d)
        newman.append((path, str(len(d)), sha(d)))
    else:
        newman.append((path, size, h))
others_same = all(tuple(r[1:]) == tuple(m[1:]) for r, m in zip(newman, man) if r[0] not in changed_paths)
gate('e8. all other payload files unchanged in the new manifest', others_same and len(newman) == len(man),
     '%d of %d files unchanged, %d bars replaced' % (len(man) - len(changed_paths), len(man), len(changed_paths)))
with open(os.path.join(args.out, 'MANIFEST.tsv'), 'w', encoding='utf-8', newline='') as fh:
    fh.write('path\tsize\tsha256\n'); fh.writelines('\t'.join(r) + '\n' for r in newman)

# ---------------------------------------------------------------- report
srcs = collections.Counter(); per_bar = collections.defaultdict(collections.Counter); types = collections.Counter()
for k in intended:
    s = plan[k]['src']; grp = ('glossary' if s.startswith('glossary') else 'shorten' if s.startswith('shorten')
                                else 'width-check term' if s.startswith('needs_width') else 'proofreading')
    srcs[grp] += 1; per_bar[k[0]][grp] += 1; per_bar[k[0]]['total'] += 1; types[plan[k]['type']] += 1
ok_all = not fatal
L = ['round: BUILD-%s' % args.version, '', '# Build report %s' % args.version, '',
     '**Result: %s.** %d messages changed in %d bars; %d other messages byte-identical.' %
     ('ALL GATES PASS' if ok_all else 'FAILED (%s)' % ', '.join(fatal), len(intended), len(changed_bars),
      sum(len(v) for v in omsgs.values()) - len(intended)), '',
     '## Gates', '', '| gate | result | detail |', '|---|---|---|']
L += ['| %s | %s | %s |' % (g, 'PASS' if ok else '**FAIL**', d.replace('|', '/')) for g, (ok, d) in gates.items()]
L += ['', '## Changes per bar', '', '| bar | proofreading | glossary | shorten | width-check term | total | new SHA256 |', '|---|---:|---:|---:|---:|---:|---|']
for b in BARS:
    c = per_bar.get(b, collections.Counter())
    L.append('| %s | %d | %d | %d | %d | %d | `%s` |' % (b, c['proofreading'], c['glossary'], c['shorten'], c['width-check term'], c['total'],
             sha(newbar[b])[:16] + '…' if b in changed_bars else 'unchanged'))
L.append('| **total** | **%d** | **%d** | **%d** | **%d** | **%d** | |' % (srcs['proofreading'], srcs['glossary'], srcs['shorten'], srcs['width-check term'], len(intended)))
if noop: L += ['', 'Corrections that encode to the installed bytes (no change): %s' % ', '.join('%s %d' % k for k in noop)]
L += ['', '## needs_width_check.csv: real widths', '',
      'Width = widest line in font units from `fontinfo.bar` (sys or evt atlas). English width = old width / (width_pct / 100). '
      'A row fits if new ≤ 130% of English or new ≤ old. A term is applied only if all its rows fit.', '',
      '| term / row | applied | rows: bar id — English → old → new width (new % of English, review width_pct) |', '|---|---|---|']
for unit, okk, det in wres:
    L.append('| %s | %s | %s |' % (unit, 'yes' if okk else 'no', '; '.join('%s %d — %.0f → %.0f → %.0f (%.0f%%, was %.0f%%)%s' % (b, i, e, o, n, pn, pc, '' if ok else ' ✗')
                                                                     for b, i, e, o, n, pn, pc, ok in det)))
L += ['', '## Consistency (review CSV vs installed bars)', '', '%d rows compared; %d decoded in plain-English mode; differences: %s.' %
      (len(review), plain_rows, ', '.join('%s %d' % k for k in sorted((b, i) for b in mism for i, _ in mism[b])) or 'none'), '',
      'Inputs: payload from the `build-payload` release, verified against `config/FROZEN_MANIFEST.tsv`; corrections from `corrections/`.']
open(os.path.join(args.report, 'BUILD_REPORT.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')

# ---------------------------------------------------------------- changelog (Arabic, for players)
TN = {'spelling': 'إملاء', 'grammar': 'نحو وصرف', 'phrasing': 'صياغة وتقصير', 'meaning': 'تصحيح معنى', 'glossary': 'توحيد الأسماء والمصطلحات'}
ex, seen = [], set()
for k in sorted(intended, key=lambda k: (plan[k]['type'], k)):
    t = plan[k]['type']
    if list(x[2] for x in ex).count(t) >= 2: continue
    o, n = plan[k]['old'], plan[k]['new']
    if len(o) > 70 or '<' in o: continue
    ex.append((k, o, t)); seen.add(k)
    if len(ex) >= 10: break
CL = ['# سجل التغييرات — الإصدار %s' % args.version, '',
      'تحديث للنصوص العربية فقط: %d جملة مصححة في %d ملفا من ملفات النصوص. لا تغيير في الخطوط أو الصور.' % (len(intended), len(changed_bars)), '',
      '## التصحيحات حسب النوع', '']
CL += ['- %s: %d' % (TN.get(t, t), n) for t, n in types.most_common()]
CL += ['', '## أمثلة', '']
for k, o, t in ex:
    CL.append('- قبل: «%s» — بعد: «%s»' % (o.replace(' ⏎ ', ' '), plan[k]['new'].replace(' ⏎ ', ' ')))
CL += ['', '## قرارات المسرد (أسماء موحدة في كل اللعبة)', '',
       '- Auron: «أورون» بدل «آرون» (تتبع النطق الإنجليزي).',
       '- Naminé: «ناميني» في كل المواضع.',
       '- Sandlot: «الساحة». Moogle: «موغل». Christmas: «الميلاد» و«بلدة الميلاد».',
       '- Gauge: «عداد». Reaction Command: «أمر التفاعل». Wildebeest Valley: «وادي النو».',
       '- أسماء ليميت jm موحدة مع قائمة الأوامر (مثل «مطر المذنبات»، «العواءان»، «جزيرة الكنز»).',
       '- سلاسل السحر: «ثاندارا / ثانداغا»، «بليزارا / بليزاغا»، «فايرا / فايراغا».',
       '', 'التفاصيل الكاملة: docs/glossary_decisions.md في المستودع.']
open(os.path.join(args.report, 'CHANGELOG.md'), 'w', encoding='utf-8').write('\n'.join(CL) + '\n')

print('\n'.join('%-55s %s' % (g, 'PASS' if ok else 'FAIL: ' + d) for g, (ok, d) in gates.items()))
print('changed messages %d, bars %s' % (len(intended), changed_bars))
sys.exit(1 if fatal else 0)
