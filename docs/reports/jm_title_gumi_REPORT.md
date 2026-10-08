round: PROOF-jm-title-gumi

# Proofreading report: jm, title, gumi

## Files done

15 of 15 files (jm 9, title 3, gumi 3) have a correction file and a summary (none existed before this round). All pass `python tools/validate_corrections.py`. Header-only files (nothing to correct): jm_part01, jm_part04, jm_part05, title_part01-03, gumi_part02, gumi_part03.

| file | rows reviewed | rows corrected |
|---|---:|---:|
| jm_part01 | 250 | 0 |
| jm_part02 | 250 | 4 |
| jm_part03 | 250 | 2 |
| jm_part04 | 250 | 0 |
| jm_part05 | 250 | 0 |
| jm_part06 | 250 | 2 |
| jm_part07 | 250 | 3 |
| jm_part08 | 250 | 11 |
| jm_part09 | 129 | 1 |
| title_part01 | 250 | 0 |
| title_part02 | 250 | 0 |
| title_part03 | 194 | 0 |
| gumi_part01 | 250 | 1 |
| gumi_part02 | 250 | 0 |
| gumi_part03 | 150 | 0 |
| **total** | **3473** | **24** |

## Corrections per type and severity

| type | severity 1 | severity 2 | severity 3 | total |
|---|---:|---:|---:|---:|
| grammar | 4 | 3 | 0 | 7 |
| meaning | 0 | 1 | 0 | 1 |
| spelling | 12 | 2 | 0 | 14 |
| phrasing | 1 | 1 | 0 | 2 |
| glossary | 0 | 0 | 0 | 0 |
| **total** | **17** | **7** | **0** | **24** |

## Top repeated error patterns

| # | pattern | rows | example |
|---|---|---:|---|
| 1 | Wrong imperative of «فاز»: «افز» → «فز» (Challenge goals in the journal) | 11 | jm 19276 «افز بفارق 100 نقطة» → «فز بفارق 100 نقطة» |
| 2 | Case ending (object or predicate of «كان» in the accusative) | 3 | jm 10796 «وادي ضخما» → «واديا ضخما»; jm 20163 «كان متردد» → «كان مترددا» |
| 3 | Verb does not agree with its subject in gender | 2 | jm 13168 «وأمطرتها» → «وأمطرها» (الانفجار) |
| 4 | Missing or wrong preposition | 2 | jm 10846 «لتحدث الملكة» → «لتحدث إلى الملكة» |
| 5 | Cut-off or garbled sentence | 2 | jm 10866 «أنهم كانوا.» → «أنهم كانوا فيه.» |
| 6 | Wrong word changes the sense | 1 | jm 11791 «أتراب البحر» (peers) → «رجال البحر» (mermen) |
| 7 | Letter slip in a name | 1 | gumi 6259 «ثانداررا» → «ثاندارا» |

No other pattern repeats. The `title` bar (chapter titles) and `gumi` bar (help text) are almost clean; jm journal text is clean apart from the rows above (24 corrections in 3473 rows, under 1%).

## Severity-3 corrections

None in this round. The one `meaning` row is severity 2: jm 11791 (EN "mermen and mermaids", AR «أتراب»).

## Fixes that were not applied (length rule)

None: no fix in this round exceeded the length rule, so `corrections/needs_width_check.csv` is unchanged (7 rows).

## Glossary conflicts seen (not changed)

- jm 10799 «الأراضي القاحلة» vs the approved «بادية» (Wastelands).
- jm 10962-10965 «الوادي» for Canyon vs the approved «الأخدود» (also 10788, 11166).
- gumi 6250, 6251 «فيرا» and «فيراغا» vs the glossary «فايرا» and «فايراغا».
- gumi 6259 «ثاندارا» (after the fix) vs the glossary «ثوندارا», which is listed for the Thunder Trinket item. The spelling fix removed an extra letter only; the spell name needs a decision in the GLOSSARY task.
- title 21265 «مهزز الأرض» (Groundshaker) looks like a typo but is the approved form in `glossary.md`.
- «اللا أحد» forms such as «لا أحده» (jm 14776, 18042) follow the glossary term.
- Limit/attack names that differ between sys and jm: none of these files contain them (the jm text here is the journal and character summaries), so nothing to compare in this round.
- Naminé «ناميني» (title 20710, 20749, 21327, 21357) and Riku «ريكو» (title 21183, 21330) already match the glossary.

## Notes on this round

- jm 11068 needed two fixes in one row; they are combined into one correction (one correction per id). The validator found no id in two files.
- Base branch is `main` after PR #8; this PR also corrects the tt report counts (`tt_part01` = 10, `tt_part02` = 20, total 67) after tt 12316 and tt 13289 moved into `glossary_namine.csv`.

## Unsure

- gumi «غامي الاختياري» (6335 and the help texts in `gumi_part02`) and «غامي المساعد» (14283, 15699, 16636, 16650): a definite adjective after an idafa head is not strictly correct (should be «غامي اختياري» / «غامي مساعد»), but it is used as a label across the bar, so it was left. Say if you want it unified.
- jm 14068 «من التحكم في ذكرياتهم» reads active where EN is passive; a fix would not fit the length rule.
- jm 11912 has the header "Vexen" but Saïx's bio; the English has the same text, so it is a source problem, not a translation one.
- jm 11181, 11193 «لكن لسيمبا سببا»: correct if «لكن» is read as «لكنّ»; left.
