round: PROOF-worlds

# Proofreading report: worlds

## Files done

39 of 39 world files have a correction file and a summary (none existed before this round). Bars: di es wm hb mu bb he dc ca al nm lk lm tr po wi eh. All pass `python tools/validate_corrections.py`. `es_part01`, `hb_part03`, `mu_part03`, `nm_part02`, `lk_part02`, `lm_part02`, `lm_part03`, `tr_part02`, `wi_part02`, `eh_part03` are header-only files: nothing to correct.

| file | rows reviewed | rows corrected |
|---|---:|---:|
| di_part01 | 32 | 1 |
| es_part01 | 54 | 0 |
| wm_part01 | 214 | 3 |
| hb_part01 | 250 | 1 |
| hb_part02 | 250 | 1 |
| hb_part03 | 250 | 0 |
| hb_part04 | 250 | 5 |
| hb_part05 | 29 | 1 |
| mu_part01 | 250 | 1 |
| mu_part02 | 250 | 2 |
| mu_part03 | 8 | 0 |
| bb_part01 | 250 | 2 |
| bb_part02 | 240 | 3 |
| he_part01 | 250 | 3 |
| he_part02 | 250 | 1 |
| he_part03 | 164 | 7 |
| dc_part01 | 212 | 2 |
| ca_part01 | 250 | 1 |
| ca_part02 | 250 | 1 |
| ca_part03 | 42 | 1 |
| al_part01 | 250 | 2 |
| al_part02 | 165 | 1 |
| nm_part01 | 250 | 4 |
| nm_part02 | 250 | 0 |
| nm_part03 | 13 | 1 |
| lk_part01 | 250 | 1 |
| lk_part02 | 226 | 0 |
| lm_part01 | 250 | 2 |
| lm_part02 | 250 | 0 |
| lm_part03 | 92 | 0 |
| tr_part01 | 250 | 1 |
| tr_part02 | 61 | 0 |
| po_part01 | 250 | 5 |
| po_part02 | 59 | 1 |
| wi_part01 | 250 | 4 |
| wi_part02 | 18 | 0 |
| eh_part01 | 250 | 1 |
| eh_part02 | 250 | 3 |
| eh_part03 | 63 | 0 |
| **total** | **7192** | **62** |

## Corrections per type and severity

| type | severity 1 | severity 2 | severity 3 | total |
|---|---:|---:|---:|---:|
| grammar | 17 | 23 | 0 | 40 |
| meaning | 0 | 6 | 0 | 6 |
| spelling | 3 | 2 | 0 | 5 |
| phrasing | 7 | 4 | 0 | 11 |
| glossary | 0 | 0 | 0 | 0 |
| **total** | **27** | **35** | **0** | **62** |

## Top 10 repeated error patterns

| # | pattern | rows | example |
|---|---|---:|---|
| 1 | Command after lam of command not jussive: «لنرى» → «لنر» | 13 | he 3687, wi 5654, hb 12961 |
| 2 | Wrong imperative form (وصل, تفادى, هاجم, اسطع, حمى) | 12 | he 19409 «اصل» → «صل»; ca 20614 «واهاجمه» → «وهاجمه» |
| 3 | «أن/إن» used wrongly (before a bare verb or noun; missing «أنه») | 7 | hb 12938 «أظن أن حان» → «أظن أنه حان»; po 4801 |
| 4 | Wrong word changes the sense (idiom or one word) | 6 | hb 15149 «ليس تماما!» → «في أحلامك!» (As if!) |
| 5 | Agreement in gender or number (demonstrative, verb, adjective, vocative, pronoun) | 5 | lm 5173 «أرادها» → «أراده» (Sebastian) |
| 6 | Wrong preposition or extra pronoun | 5 | hb 18839 «حذرا بها» → «حذرا منها» |
| 7 | Garbled or truncated phrase | 4 | he 3717; po 16087 «إلى أي الآن» → «إلى عسل الآن» |
| 8 | Word order or repeated word | 4 | lk 8518; bb 3215; wi 5638 |
| 9 | Jussive after «لم» / missing plural alef | 2 | eh 16691 «لم يتولى» → «لم يتول»; he 3647 |
| 10 | Unified wording across a group of rows | 2 | bb 7744, 7745 |

Most world files are clean: 10 of 39 files need no correction, and 62
corrections in 7192 rows is under 1%. Scans for bare alef, ه/ة, ى/ي, hamza after
«قال», doubled «ال» and «عن من» found nothing systematic in these bars.

## Severity-3 corrections

None in this round. The six `meaning` rows are all severity 2: wm 7731, hb 15149,
hb 15155, mu 4321, dc 5433, eh 19952.

## Fixes that were not applied (length rule)

`corrections/needs_width_check.csv` (header `bar,id,AR_old,AR_new,reason`)
lists fixes that are correct but longer than the length rule allows. It is a
report: the validator skips it. It now holds 7 rows: sys 14910, sys 20624, tt
12251, tt 13772, tt 13787, tt 19004, mu 4188 (the only one from the worlds
round). Each needs a width check in the game before it can be applied.

## Glossary conflicts seen (not changed)

- **Naminé**: di 16808 and the tt rows use «نامين»; the decision is «ناميني»
  and is applied by `corrections/glossary_namine.csv` (merged in PR #7).
- **Rikku**: hb 13020 uses «ريكو» (the glossary says «ريكا» for Rikku).
- **Keyblade**: ca 9958 and ca 10319 write «كيبليد» instead of «كيبلايد».
- **Nobodies** «اللا أحد»: hb 12597 «لا أحدا» is not a valid inflection and a
  fix would change the term; also hb 12744, hb 12756, hb 21488, eh 16231, 16542.
- **Heartless** «بلا قلب»: awkward in construct phrases (eh 16411, 16570, 19957).
- wm 18554 lacks «غابة» (glossary «غابة المئة فدان»); wm 19501 «ثانداغا» vs
  glossary «ثاندراجا»; hb 2987/2988 «برج الإدخال», «قلب الحاسوب المركزي» vs
  «نواة»; hb 16064 «بنس» vs tt «بينس»; he 16987 «إلهة القدر».

## Notes on this round

- `corrections/tt_followup.csv` (tt 13625, tt 16132): two tt fixes that the tt
  round wrongly filed as too long; they pass the length rule and are applied here.
- One correction per id: tt 12316 and tt 13289 were in both
  `glossary_namine.csv` and a tt file. Each is now one row in
  `glossary_namine.csv` (Naminé + the tt fix), removed from `tt_part01.csv` and
  `tt_part02.csv` (now 10 and 20 rows; the merged tt report counted 11 and 21).
  No other id appears in two files.
- `tools/validate_corrections.py`: checks that an id appears in only one correction
  file (a later file is an error), skips `needs_width_check.csv` (report file) and
  accepts a header-only correction file (a file with nothing to correct). Three
  new tests cover the three checks.
- The files were proofread in parallel by six reviewers. I read the proposed
  fixes and removed the ones that were taste, not errors (he 3760, lk 8683,
  lk 19254, lm 5011, nm 5827, wi 5728).

## Unsure

- (Resolved) eh 19952: the EN is "That anger will fuel him to get rid of his
  apprehension", i.e. his fear and hesitation, not anticipation, so the choice is
  «خوفه» (not «ترقبه»).
- he 3717: the line was garbled; the new wording «إنه بطلنا الفاشل ... المفضل
  للجميع» is a reading, not the only one.
- wi 5689 and 5692: «بيت الذي قابلناه» (relative pronoun after a name) needs a
  rewrite and would not fit the length rule; left.
- Tags in odd positions (he 4007, 16146; dc 5350, 7895; lk 4908, 19426) were kept
  byte-exact as the rules require.
