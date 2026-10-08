round: PROOF-tt

# Proofreading report: tt

## Files done

8 of 8 tt files have a correction file and a summary (none existed before this
round). All pass `python tools/validate_corrections.py`.

| file | rows reviewed | rows corrected |
|---|---:|---:|
| tt_part01 | 250 | 10 |
| tt_part02 | 250 | 20 |
| tt_part03 | 250 | 13 |
| tt_part04 | 250 | 5 |
| tt_part05 | 250 | 3 |
| tt_part06 | 250 | 6 |
| tt_part07 | 250 | 7 |
| tt_part08 | 92 | 3 |
| **total** | **1842** | **67** |

## Corrections per type and severity

| type | severity 1 | severity 2 | severity 3 | total |
|---|---:|---:|---:|---:|
| grammar | 12 | 17 | 0 | 29 |
| meaning | 0 | 13 | 1 | 14 |
| spelling | 7 | 8 | 0 | 15 |
| phrasing | 7 | 2 | 0 | 9 |
| **total** | **26** | **40** | **1** | **67** |

## Top 10 repeated error patterns

| # | pattern | rows | example |
|---|---|---:|---|
| 1 | One word changes the meaning | 14 | 13221 «يا حبيبتي» for "ma´am" → «يا سيدتي» |
| 2 | Case of a predicate or subject (منصوب/مرفوع) | 6 | 13334 «لست متأكد» → «لست متأكدا» |
| 3 | Gender of the speaker (Naminé speaks in the masculine) or of the noun | 7 | 13536 «أنا آسف» → «أنا آسفة» |
| 4 | Spelling slip inside a word | 9 | 13370 «اللاعمان» → «اللاعبان» |
| 5 | «عن من» → «عمن» | 4 | 2899 «أبحث عن من» → «أبحث عمن» |
| 6 | Jussive after lam of command | 3 | 12187 «لنرى» → «لنر» |
| 7 | Hamza of «إن» after a verb of saying | 3 | 13273 «أتقول أن» → «أتقول إن» |
| 8 | Missing word (هل, هو, من, أنت) | 5 | 13418 «إذن, لدى أحد» → «إذن, هل لدى أحد» |
| 9 | Repeated word in battle hints | 3 | 18602 «استخدام أوامر التفاعل باستخدام» → «… عبر» |
| 10 | Literal calque that does not read as Arabic | 4 | 13289 «نضيق من الوقت» → «الوقت ينفد» |

## Severity-3 corrections

| id | old | new | reason |
|---|---|---|---|
| tt 13177 | «انظر... هذا هو ما يزعجني حقا.» | «انظر... ليس هذا ما يزعجني حقا.» | الأصل ينفي والترجمة تثبت فانعكس المعنى |

(EN: "See...that´s not what really bugs me." The installed line says the
opposite, and the next line 13178 «ما يزعجني حقا…» only makes sense after the
negation.)

## Glossary conflicts seen

- **Naminé** is «نامين» in every tt row (about 30 rows); the glossary says
  «ناميني». Already in docs/consistency.md; the GLOSSARY task should settle it.
- **Twilight Town / the town**: many rows call it «المدينة» ("the city"; 13350,
  13422, 13423, 13553, 13603, 13668, 13741-13753) while others say «البلدة»
  and the glossary name is «بلدة الشفق».
- **Sunset Hill** «تلة الغروب» in 13460 vs «تل الغروب» elsewhere.
- **Destiny Islands** is «الجزيرة» (singular) in Sora´s lines (14359, 14490-14494,
  21474); the glossary name is «جزيرة المصير».
- **Shop**: «متجر» and «محل» both used (accessory shop, candy shop).
- **Struggle Battle R** «معركة الصراع ر» (19135-19146) has no glossary entry.
- 17918 «قوة الغامض» for "power of the mystic".

## Rule change made in this round

`RULES.md` now has `unprotected_terms` (the change is in PR #5 and copied
identically here): ordinary nouns that sit in the glossary only as menu words are
not protected. Two were added while doing tt: «المدافع» (Defender) for 13311
«الدافع عن اللقب» → «المدافع» and «استخدام» (Use) for the three battle hints in
pattern 9.

## Anything I was unsure about

1. **Length rule kept out some good fixes:** 12251 «صباحا» for the greeting
   "Morning" («صباح الخير»), 13772 «إذن بخير!» («إذن هو بخير!»), 13787 «علمت!»
   («كنت أعلم!»), 13625 «على الأكثر» for "at best" («في أحسن الأحوال»), 16132
   «حصل روكساس على استخدام القدرات». docs/review_list.md says some short forms
   were chosen on purpose.
2. **Speaker gender not certain:** 17947 «أنا سعيد» may be Olette («سعيدة»);
   14316 «شكرا لنامين» (journal line "Thank Naminé.") can be read either way.
   Left as is.
3. **Kept colloquial forms:** dialogue uses Gulf/Levantine touches («إيه», «طيب»,
   «غالي جدا»), which RULES.md does not forbid; I only changed lines that were
   wrong, not informal.
4. 13178 «الآن المدينة وأمهاتهم» is a literal rendering of the idiom "the whole
   town and their mothers"; left as is.

## Correction after the worlds round

Two tt rows, 12316 and 13289, were also Naminé rows. An id may have only one active
correction, so their tt fixes («بما يحل» → «مما يحل» and «نضيق من الوقت» → «الوقت ينفد»)
were combined with the Naminé change in `corrections/glossary_namine.csv`. The counts
above are updated: `tt_part01` has 10 rows, `tt_part02` 20, total 67.
