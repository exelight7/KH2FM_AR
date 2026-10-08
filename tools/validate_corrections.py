#!/usr/bin/env python3
"""Validate corrections/*.csv against the review files and RULES.md.

Every correction file has the columns
    bar,id,AR_old,AR_new,type,severity,reason
and each row must satisfy the rules in RULES.md (see the ``rules`` block there):

  * (bar, id) exists in review/*.csv and AR_old equals the current AR exactly
  * AR_new uses allowed characters only (forbidden characters never; other
    characters outside the allowed set only if they were already in AR_old)
  * the same tags in the same order, the same number of line-break markers
  * glossary terms unchanged (skipped for files named corrections/glossary*.csv;
    the ``unprotected_terms`` of RULES.md are not treated as glossary terms)
  * AR_new at most max(``max_growth_percent`` of AR_old, ``min_growth_chars``)
    characters longer than AR_old
  * type / severity / reason are valid

Prints one table of results and exits 1 if any row (or file) has an error.

Usage:
    python tools/validate_corrections.py                 # all corrections/*.csv
    python tools/validate_corrections.py corrections/x.csv ...
"""
import argparse
import collections
import csv
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

COLUMNS = ['bar', 'id', 'AR_old', 'AR_new', 'type', 'severity', 'reason']
TYPES = ('spelling', 'grammar', 'phrasing', 'meaning', 'glossary')
SEVERITIES = ('1', '2', '3')
REASON_MAX_WORDS = 8

# A tag is a control code written as hex bytes (<13 00 01 40 01>, <10>), or a
# one-letter token with operands (<X 5E>, <C 14 41 00>).
TAG_RE = re.compile(r'<(?:[0-9A-F]{2}(?: [0-9A-F]{2})*|[A-Z](?: [^<>\s][^<>]*)?)>')

ARABIC_LETTER_RANGES = ((0x0621, 0x063A), (0x0641, 0x064A))
# Tashkeel, superscript alef and other Arabic marks.
DIACRITICS = set(chr(c) for c in list(range(0x064B, 0x0660)) + [0x0670] + list(range(0x06D6, 0x06EE)))
TATWEEL = 'ـ'


def is_arabic_letter(ch):
    o = ord(ch)
    return any(a <= o <= b for a, b in ARABIC_LETTER_RANGES)


# ---------------------------------------------------------------- RULES.md
class Rules:
    def __init__(self, allowed, forbidden, marker, max_growth, min_growth_chars, unprotected=()):
        self.allowed = allowed        # set of non-letter characters allowed besides Arabic letters
        self.forbidden = forbidden    # set of characters never allowed
        self.marker = marker          # visible line-break marker
        self.max_growth = max_growth  # percent
        self.min_growth_chars = min_growth_chars  # growth always allowed, in characters
        self.unprotected = set(unprotected)  # glossary entries that are ordinary words

    def growth_limit(self, old_len):
        """How many characters longer than the original a correction may be."""
        return max(old_len * self.max_growth / 100.0, self.min_growth_chars)


def load_rules(path):
    """Read the fenced ```rules block of RULES.md (key: value lines)."""
    with open(path, encoding='utf-8') as fh:
        text = fh.read()
    m = re.search(r'```rules\n(.*?)```', text, re.S)
    if not m:
        raise SystemExit('%s: no ```rules block found' % path)
    kv = {}
    for line in m.group(1).splitlines():
        if ':' in line and not line.lstrip().startswith('#'):
            k, v = line.split(':', 1)
            kv[k.strip()] = v.strip()
    need = ('allowed_punctuation', 'allowed_digits', 'allowed_latin', 'allowed_space',
            'forbidden', 'line_break_marker', 'max_growth_percent', 'min_growth_chars')
    missing = [k for k in need if k not in kv]
    if missing:
        raise SystemExit('%s: rules block is missing %s' % (path, ', '.join(missing)))
    allowed = set(kv['allowed_punctuation'].split())
    allowed |= set(kv['allowed_latin'].split())
    if kv['allowed_digits'] == '0-9':
        allowed |= set('0123456789')
    else:
        allowed |= set(kv['allowed_digits'].split())
    if kv['allowed_space'].lower() == 'yes':
        allowed.add(' ')
    forbidden = set()
    for tok in kv['forbidden'].split():
        if re.fullmatch(r'U\+[0-9A-Fa-f]{4}-U\+[0-9A-Fa-f]{4}', tok):
            a, b = tok.split('-')
            forbidden |= set(chr(c) for c in range(int(a[2:], 16), int(b[2:], 16) + 1))
        elif re.fullmatch(r'U\+[0-9A-Fa-f]{4}', tok):
            forbidden.add(chr(int(tok[2:], 16)))
        else:
            forbidden |= set(tok)
    forbidden |= DIACRITICS | {TATWEEL}
    unprotected = kv.get('unprotected_terms', '').replace('،', ' ').replace(',', ' ').split()
    return Rules(allowed, forbidden, kv['line_break_marker'], float(kv['max_growth_percent']),
                 int(kv['min_growth_chars']), unprotected)


# ---------------------------------------------------------------- glossary
AR_HEADERS = ('AR', 'العربي', 'العربي المعتمد')
MIN_TERM_LETTERS = 3
MAX_TERM_WORDS = 4


def _clean_term(s):
    s = s.split(' — ')[0]                 # text after an em dash is a note
    s = re.sub(r'\*\*|`|«|»|"', '', s)
    s = re.sub(r'\([^)]*\)?', '', s)      # parenthetical notes
    s = re.sub(r'\s+', ' ', s)
    return s.strip(' .!?؟:+-()')


def load_glossary_terms(path):
    """Approved Arabic forms from the AR column of every glossary table."""
    terms = set()
    ar_col = None
    with open(path, encoding='utf-8') as fh:
        lines = fh.read().splitlines()
    for line in lines:
        line = line.strip()
        if not line.startswith('|'):
            ar_col = None
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if all(re.fullmatch(r':?-+:?', c) for c in cells if c):
            continue
        if ar_col is None:
            ar_col = next((i for i, c in enumerate(cells) if c in AR_HEADERS), -1)
            continue
        if ar_col < 0 or ar_col >= len(cells):
            continue
        cell = cells[ar_col]
        if 'معلّق' in cell or 'معلق' in cell:
            continue                      # pending, not approved
        for part in re.split(r' / |/|,|،|;| - |: | \+ ', cell):
            t = _clean_term(part)
            if not t or re.search(r'[a-z]', t) or len(t.split()) > MAX_TERM_WORDS:
                continue                  # empty, a note, or a sentence rather than a term
            if '<' in TAG_RE.sub('', t):
                continue                  # placeholder such as <العالم>
            letters = sum(1 for ch in TAG_RE.sub('', t) if is_arabic_letter(ch))
            if letters >= MIN_TERM_LETTERS:
                terms.add(t)
    return terms


def load_glossary(path, rules):
    """The protected glossary: every approved form except the rules' unprotected_terms."""
    return Glossary(load_glossary_terms(path) - rules.unprotected)


_LETTER_CLASS = 'ء-غف-ي'


def _term_regex(term):
    """Whole-word match, allowing the attached prefixes و ف ب ل ك and the article."""
    if term.startswith('ال'):
        alts = ['[وف]?[بلك]?' + re.escape(term), '[وف]?لل' + re.escape(term[2:])]
    else:
        alts = ['[وف]?(?:[بك]?ال|لل|[بلك])?' + re.escape(term)]
    return re.compile('(?<![%s])(?:%s)(?![%s])' % (_LETTER_CLASS, '|'.join(alts), _LETTER_CLASS))


class Glossary:
    def __init__(self, terms):
        self.terms = sorted(terms)
        self.regex = {t: _term_regex(t) for t in self.terms}

    def counts(self, text):
        c = {}
        for t in self.terms:
            if t in text:
                n = len(self.regex[t].findall(text))
                if n:
                    c[t] = n
        return c

    def changed(self, old, new):
        a, b = self.counts(old), self.counts(new)
        return sorted(t for t in set(a) | set(b) if a.get(t, 0) != b.get(t, 0))


# ---------------------------------------------------------------- review data
def load_review(review_dir):
    rows = {}
    for f in sorted(glob.glob(os.path.join(review_dir, '*.csv'))):
        with open(f, encoding='utf-8-sig', newline='') as fh:
            for r in csv.DictReader(fh):
                rows[(r['bar'], r['id'])] = r['AR']
    return rows


def tags(s):
    return TAG_RE.findall(s)


def visible_len(s):
    return len(TAG_RE.sub('', s))


# ---------------------------------------------------------------- checks
def check_row(row, review, rules, glossary, check_glossary):
    errors = []
    key = (row['bar'].strip(), row['id'].strip())
    if key not in review:
        return ['id %s not found in bar %s' % (key[1], key[0])]
    cur = review[key]
    old, new = row['AR_old'], row['AR_new']
    if old != cur:
        errors.append('AR_old differs from current AR')
    if new == old:
        errors.append('AR_new is identical to AR_old')

    # characters (outside tags)
    old_plain, new_plain = TAG_RE.sub('', old), TAG_RE.sub('', new)
    old_count = collections.Counter(old_plain)
    bad = []
    for ch, n in sorted(collections.Counter(new_plain).items()):
        if ch in rules.forbidden:
            bad.append(ch)
        elif is_arabic_letter(ch) or ch in rules.allowed or ch == rules.marker:
            continue
        elif n > old_count.get(ch, 0):
            bad.append(ch)                # not allowed, and not just kept from the original
    if bad:
        errors.append('characters not allowed: %s' % ' '.join('%r(U+%04X)' % (c, ord(c)) for c in bad))

    if tags(new) != tags(old):
        errors.append('tags differ: old %s new %s' % (' '.join(tags(old)) or '-', ' '.join(tags(new)) or '-'))
    if new.count(rules.marker) != old.count(rules.marker):
        errors.append('line breaks: old %d new %d' % (old.count(rules.marker), new.count(rules.marker)))

    if check_glossary:
        changed = glossary.changed(old, new)
        if changed:
            errors.append('glossary term changed: %s' % ' | '.join(changed))

    lo, ln = visible_len(old), visible_len(new)
    if ln - lo > rules.growth_limit(lo):
        errors.append('too long: %d -> %d chars (+%d, max +%d = max(%g%%, %d chars))'
                      % (lo, ln, ln - lo, int(rules.growth_limit(lo)), rules.max_growth, rules.min_growth_chars))

    t = row['type'].strip()
    if t not in TYPES:
        errors.append('type %r not in %s' % (t, '|'.join(TYPES)))
    if row['severity'].strip() not in SEVERITIES:
        errors.append('severity %r not in 1|2|3' % row['severity'])
    reason = row['reason'].strip()
    if not reason or not any(is_arabic_letter(c) for c in reason):
        errors.append('reason must be in Arabic')
    elif len(reason.split()) > REASON_MAX_WORDS:
        errors.append('reason has %d words (max %d)' % (len(reason.split()), REASON_MAX_WORDS))
    return errors


def validate_file(path, review, rules, glossary):
    """Return a list of (line, bar, id, [errors]) for one corrections file."""
    check_glossary = not os.path.basename(path).lower().startswith('glossary')
    try:
        with open(path, encoding='utf-8-sig', newline='') as fh:
            text = fh.read()
    except UnicodeDecodeError:
        return [('-', '', '', ['file is not UTF-8'])]
    reader = csv.DictReader(io.StringIO(text, newline=''))
    try:
        header = reader.fieldnames or []
        if header != COLUMNS:
            return [('header', '', '', ['header must be %s (got %s)' % (','.join(COLUMNS), ','.join(header))])]
        rows = []
        for row in reader:
            rows.append((reader.line_num, row))
    except csv.Error as e:
        return [('-', '', '', ['cannot read CSV: %s' % e])]
    if not rows:
        return [('-', '', '', ['no rows'])]
    results = []
    seen = set()
    for n, row in rows:
        if None in row or any(row[c] is None for c in COLUMNS):
            results.append((str(n), row.get('bar') or '', row.get('id') or '', ['wrong number of columns']))
            continue
        key = (row['bar'].strip(), row['id'].strip())
        errs = check_row(row, review, rules, glossary, check_glossary)
        if key in seen:
            errs.append('duplicate row for this id')
        seen.add(key)
        results.append((str(n), key[0], key[1], errs))
    return results


def print_table(all_results, out):
    head = ('file', 'line', 'bar', 'id', 'status', 'details')
    lines = []
    for path, results in all_results:
        name = os.path.relpath(path, ROOT) if os.path.isabs(path) else path
        for line, bar, rid, errs in results:
            if errs:
                for i, e in enumerate(errs):
                    lines.append((name, line, bar, rid, 'ERROR', e) if i == 0 else ('', '', '', '', '', e))
            else:
                lines.append((name, line, bar, rid, 'ok', ''))
    w = [max(len(head[i]), *(len(l[i]) for l in lines)) if lines else len(head[i]) for i in range(5)]
    fmt = ' | '.join('%%-%ds' % x for x in w) + ' | %s'
    out.write(fmt % head + '\n')
    out.write('-+-'.join('-' * x for x in w) + '-+-' + '-' * 7 + '\n')
    for l in lines:
        out.write(fmt % l + '\n')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('files', nargs='*', help='correction files (default: corrections/*.csv)')
    ap.add_argument('--root', default=ROOT, help='repository root (review/, RULES.md, docs/glossary.md)')
    ap.add_argument('--errors-only', action='store_true', help='list only rows with errors')
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    rules = load_rules(os.path.join(args.root, 'RULES.md'))
    glossary = load_glossary(os.path.join(args.root, 'docs', 'glossary.md'), rules)
    review = load_review(os.path.join(args.root, 'review'))
    if not review:
        raise SystemExit('no review rows found in %s' % os.path.join(args.root, 'review'))
    files = args.files or sorted(glob.glob(os.path.join(args.root, 'corrections', '*.csv')))

    all_results = [(f, validate_file(f, review, rules, glossary)) for f in files]
    n_rows = sum(len(r) for _, r in all_results)
    n_bad = sum(1 for _, r in all_results for x in r if x[3])
    shown = [(f, [x for x in r if x[3]]) for f, r in all_results] if args.errors_only else all_results
    if not files:
        print('No correction files found.')
    else:
        print_table(shown, sys.stdout)
    print()
    print('Files: %d  Rows: %d  OK: %d  Errors: %d' % (len(files), n_rows, n_rows - n_bad, n_bad))
    print('RESULT: %s' % ('FAIL' if n_bad else 'PASS'))
    return 1 if n_bad else 0


if __name__ == '__main__':
    sys.exit(main())
