"""Tests for tools/validate_corrections.py.

Run from the repository root:
    python -m unittest discover -s tests -v
"""
import contextlib
import io
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAMPLES = os.path.join(HERE, 'samples')
sys.path.insert(0, os.path.join(ROOT, 'tools'))

import validate_corrections as vc  # noqa: E402


def make_root():
    """A small repository: the real RULES.md and glossary, a frozen fixture review file."""
    root = tempfile.mkdtemp(prefix='vc_test_')
    shutil.copy(os.path.join(ROOT, 'RULES.md'), root)
    os.makedirs(os.path.join(root, 'docs'))
    shutil.copy(os.path.join(ROOT, 'docs', 'glossary.md'), os.path.join(root, 'docs'))
    shutil.copytree(os.path.join(HERE, 'fixtures', 'review'), os.path.join(root, 'review'))
    os.makedirs(os.path.join(root, 'corrections'))
    return root


def run_main(args):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = vc.main(args)
    return code, out.getvalue()


class ValidatorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = make_root()
        cls.rules = vc.load_rules(os.path.join(cls.root, 'RULES.md'))
        cls.glossary = vc.Glossary(vc.load_glossary_terms(os.path.join(cls.root, 'docs', 'glossary.md')))
        cls.review = vc.load_review(os.path.join(cls.root, 'review'))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root)

    def validate(self, path):
        return vc.validate_file(path, self.review, self.rules, self.glossary)

    # -- RULES.md and glossary parsing
    def test_rules_block(self):
        r = self.rules
        for ch in '?,.:!-()+0123456789 AHIMPSTW':
            self.assertIn(ch, r.allowed)
        for ch in 'BCabz;"%/':
            self.assertNotIn(ch, r.allowed)
        for ch in '؟،؛ـَّٰ':
            self.assertIn(ch, r.forbidden)
        self.assertEqual(r.marker, '⏎')
        self.assertEqual(r.max_growth, 10)
        self.assertEqual(r.min_growth_chars, 2)

    def test_glossary_terms(self):
        terms = set(self.glossary.terms)
        for t in ('سورا', 'دونالد', 'غوفي', 'ريكو', 'كيبلايد', 'منظمة <X 5E>', 'بلا قلب'):
            self.assertIn(t, terms)
        for t in terms:
            self.assertNotIn('معلّق', t)   # pending entries are not approved

    def test_glossary_matching(self):
        g = vc.Glossary({'سورا', 'كيبلايد', 'القوة'})
        self.assertEqual(g.counts('وسورا والكيبلايد بالقوة وللقوة'), {'سورا': 1, 'كيبلايد': 1, 'القوة': 2})
        self.assertEqual(g.counts('سوراه كيبلايدات'), {})
        self.assertEqual(g.changed('قال سورا', 'قالت سورا'), [])
        self.assertEqual(g.changed('قال سورا', 'قال سوار'), ['سورا'])

    def test_tags_and_length(self):
        s = 'نص<13 00 01 40 01><X 5E><C 14 41 00> ⏎ <جمع القطع>'
        self.assertEqual(vc.tags(s), ['<13 00 01 40 01>', '<X 5E>', '<C 14 41 00>'])
        self.assertEqual(vc.visible_len(s), len('نص ⏎ <جمع القطع>'))

    def test_length_limit(self):
        self.assertEqual(self.rules.growth_limit(4), 2)      # short row: 2 characters
        self.assertEqual(self.rules.growth_limit(20), 2)
        self.assertEqual(self.rules.growth_limit(55), 5.5)   # long row: 10%

        def errors(bar, rid, new):
            row = dict(bar=bar, id=rid, AR_old=self.review[(bar, rid)], AR_new=new,
                       type='spelling', severity='1', reason='تصحيح')
            return vc.check_row(row, self.review, self.rules, self.glossary, True)

        # sys 480 'هجوم' (4 characters): +2 allowed, +3 too long
        self.assertEqual(errors('sys', '480', 'هجوم!!'), [])
        self.assertIn('too long', ' '.join(errors('sys', '480', 'هجوم!!!')))
        # hb 13020 (55 characters without tags): +5 allowed, +6 too long
        old = self.review[('hb', '13020')]
        self.assertEqual(vc.visible_len(old), 55)
        self.assertEqual(errors('hb', '13020', old.replace('أنتم!?', 'أنتم!!!!!!?')), [])
        self.assertIn('too long', ' '.join(errors('hb', '13020', old.replace('أنتم!?', 'أنتم!!!!!!!?'))))

    # -- valid samples
    def test_valid_sample_passes(self):
        results = self.validate(os.path.join(SAMPLES, 'valid.csv'))
        self.assertEqual(len(results), 3)
        for line, bar, rid, errs in results:
            self.assertEqual(errs, [], 'line %s (%s %s)' % (line, bar, rid))

    def test_glossary_file_may_change_terms(self):
        for line, bar, rid, errs in self.validate(os.path.join(SAMPLES, 'glossary_sample.csv')):
            self.assertEqual(errs, [], 'line %s (%s %s)' % (line, bar, rid))

    def test_same_change_outside_glossary_file_fails(self):
        path = os.path.join(self.root, 'corrections', 'sys_part01.csv')
        shutil.copy(os.path.join(SAMPLES, 'glossary_sample.csv'), path)
        try:
            results = self.validate(path)
        finally:
            os.remove(path)
        self.assertTrue(all(any('glossary term changed' in e for e in errs) for _, _, _, errs in results))

    # -- invalid samples
    def test_invalid_rows(self):
        expected = {}
        with open(os.path.join(SAMPLES, 'invalid_rows_expected.txt'), encoding='utf-8') as f:
            for line in f:
                n, msg = line.rstrip('\n').split('\t')
                expected[n] = msg
        results = self.validate(os.path.join(SAMPLES, 'invalid_rows.csv'))
        self.assertEqual(sorted(r[0] for r in results), sorted(expected))
        dup_seen = False
        for line, bar, rid, errs in results:
            main = [e for e in errs if not e.startswith('duplicate')]
            dup_seen |= len(main) != len(errs)
            self.assertEqual(len(main), 1, 'line %s: %s' % (line, errs))
            self.assertIn(expected[line], main[0], 'line %s' % line)
        self.assertTrue(dup_seen, 'duplicate ids were not reported')

    def test_invalid_header(self):
        results = self.validate(os.path.join(SAMPLES, 'invalid_header.csv'))
        self.assertEqual(len(results), 1)
        self.assertIn('header must be', results[0][3][0])

    def test_kept_legacy_symbol_is_allowed_but_added_one_is_not(self):
        old = self.review[('jm', '19157')]
        row = dict(bar='jm', id='19157', AR_old=old, AR_new=old.replace('وهاجم!', 'وهاجمه!'),
                   type='grammar', severity='1', reason='تصحيح')
        self.assertEqual(vc.check_row(row, self.review, self.rules, self.glossary, True), [])
        row['AR_new'] = old.replace('وهاجم!', 'وهاجم★')
        self.assertIn('not allowed', vc.check_row(row, self.review, self.rules, self.glossary, True)[0])

    # -- command line
    def test_cli_exit_codes(self):
        code, out = run_main(['--root', self.root, os.path.join(SAMPLES, 'valid.csv')])
        self.assertEqual(code, 0, out)
        self.assertIn('RESULT: PASS', out)
        self.assertIn('| status |', out)
        code, out = run_main(['--root', self.root, os.path.join(SAMPLES, 'valid.csv'),
                              os.path.join(SAMPLES, 'invalid_rows.csv')])
        self.assertEqual(code, 1)
        self.assertIn('RESULT: FAIL', out)
        self.assertIn('Errors: 18', out)

    def test_cli_no_files(self):
        code, out = run_main(['--root', self.root])
        self.assertEqual(code, 0)
        self.assertIn('No correction files found', out)


class RepositoryTest(unittest.TestCase):
    """The real review data and the real corrections/ folder."""

    def test_review_data_loads(self):
        review = vc.load_review(os.path.join(ROOT, 'review'))
        self.assertEqual(len(review), 15552)


if __name__ == '__main__':
    unittest.main()
