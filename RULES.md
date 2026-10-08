# RULES — proofreading the Arabic (AR) column

These rules apply to every file in `corrections/`. `tools/validate_corrections.py`
reads the `rules` block below and checks each correction automatically; a pull
request that breaks a rule fails the **validate** check.

## 1. What you may edit

- Only the `AR` text of rows in `review/*.csv`, and only through a correction
  file in `corrections/`. Never edit `review/` itself.
- Each correction quotes the current text exactly (`AR_old`) and gives the new
  text (`AR_new`).

## 2. Allowed characters

`AR_new` may contain only:

| kind | characters |
|---|---|
| Arabic letters | ء to غ and ف to ي (U+0621–U+063A, U+0641–U+064A) |
| punctuation (ASCII) | `?` `,` `.` `:` `!` `-` `(` `)` `+` |
| digits | `0`–`9` (ASCII digits only) |
| Latin letters | `A` `H` `I` `M` `P` `S` `T` `W` (capitals only) |
| space and line break | the space, and the line-break marker `⏎` |

Never allowed:

- the Arabic question mark `؟`, Arabic comma `،` and Arabic semicolon `؛`
  (use ASCII `?` and `,`);
- diacritics (tashkeel: fatha, damma, kasra, sukun, shadda, tanween, superscript alef, …);
- tatweel `ـ`.

Some installed rows already contain characters outside this list (game symbols
drawn by the font, such as `⤷ ★ ₓ % / "`, or English left untranslated). A
correction may **keep** them as they are, but may never **add** one.

## 3. Tags

Tags are control codes, written in angle brackets, for example `<10>`,
`<13 00 01 40 01>`, `<08 02 00 06>`, `<09 DA>` (button icon), `<X 5E>` (a raw
font cell), `<C 14 41 00>`. Every tag must be kept **exactly** (same bytes) and in
the **same order** as in `AR_old`. Do not add, remove, move past another tag, or
rewrite a tag. Text in angle brackets that is not a control code (for example
`<جمع القطع>`) is ordinary text.

## 4. Line breaks

The visible line-break marker is `⏎`, written ` ⏎ ` (one space on each side).
`AR_new` must have the **same number** of `⏎` as `AR_old`. You may move words
from one line to another, but not add or remove a line.

## 5. Glossary

The approved forms in `docs/glossary.md` (names, places, items, abilities,
menu terms) are **never changed** in a proofreading correction, even when you
think they are wrong. Report such cases under "glossary conflicts seen" in your
summary instead. Glossary terms are changed only by the GLOSSARY task (files
named `corrections/glossary*.csv`).

The validator compares how many times each approved form (3 or more Arabic
letters, whole word, with an attached و ف ب ل ك or the article allowed) occurs in
`AR_old` and `AR_new`; any difference is an error outside `glossary*.csv`.

Some glossary entries are ordinary nouns that sit in the glossary only as menu
words (for example «أنواع» Types, «أغراض» Items, «الشكل» Form, «المدافع» Defender). They are listed
under `unprotected_terms` below and are **not** protected, so a normal grammar
fix such as «15 أنواع» → «15 نوعا» or «أغراض جديدة» → «أغراضا جديدة» is allowed.

## 6. Length

`AR_new` may be longer than `AR_old` by at most **10% of the original length or
2 characters, whichever is larger**, counted in characters with tags removed
(spaces and `⏎` count). So a 5-character menu label may grow by 2 characters, a
40-character line by 4. Text that does not fit the screen breaks the game box.
Shorter is always fine.

## 7. Correction file format

`corrections/<FILE>.csv`, UTF-8, one header line:

```
bar,id,AR_old,AR_new,type,severity,reason
```

| column | value |
|---|---|
| `bar`, `id` | copied from the review file |
| `AR_old` | the current `AR`, copied exactly |
| `AR_new` | the corrected text |
| `type` | `spelling` \| `grammar` \| `phrasing` \| `meaning` \| `glossary` |
| `severity` | `1` minor, `2` clear error, `3` changes the meaning |
| `reason` | in Arabic, 8 words at most |

One row per corrected `(bar, id)`; `AR_new` must differ from `AR_old`.

## 8. Reading the review files

`review/<bar>_partNN.csv` columns: `bar,id,EN,AR,width_pct,flags` (UTF-8 with BOM,
at most 250 rows per part).

- `AR` is the installed Arabic in **logical (reading) order**, decoded from the
  game files. Tags sit where the game needs them, which is often not where they
  are in `EN`.
- `width_pct` = widest line of the Arabic ÷ widest line of the English, measured
  with the game font. Above 130 the row is flagged `wide`; above 150 it usually
  overflows.
- `flags`: `dblspace`, `space_before_punct`, `forbidden_char`, `latin:<letters>`,
  `repeat_word`, `wide`, `same_as_en` (row left in English). Flags are hints,
  not errors to fix by themselves.
- In the world bars (`tt` and the world codes) the lam-alef ligature is shown as
  `لا`; in `sys`, `jm`, `title`, `gumi` the same font cell is the Latin `W`.

## Machine-readable rules (read by the validator)

```rules
allowed_space: yes
allowed_punctuation: ? , . : ! - ( ) +
allowed_digits: 0-9
allowed_latin: A H I M P S T W
forbidden: U+061F U+060C U+061B U+0640 U+064B-U+065F U+0670
line_break_marker: ⏎
max_growth_percent: 10
min_growth_chars: 2
unprotected_terms: أنواع أغراض الأغراض الشكل حماية الحماية ضربة الواحة المدافع استخدام
```
