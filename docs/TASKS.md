# TASKS

Three kinds of work, each done in its own cloud session and its own pull
request. Every output goes to `corrections/` and must pass
`python tools/validate_corrections.py` (the **validate** check runs it on the
pull request). `review/` is never edited.

Suggested order: GLOSSARY first (it settles the names the proofreaders must
keep), then the proofreading files in the order below, then SHORTEN.

A row should be corrected in one file only. If two merged correction files touch
the same `(bar, id)`, the second one must be redone against the first.

---

## (a) Proofreading — 75 files

One file per session, using the prompt in `docs/CLOUD_PROMPT.md`. Output:
`corrections/<FILE>.csv` and `corrections/<FILE>_summary.md`, pull request
**Proofreading: <FILE>**. Tick the box when the pull request is merged.

Order: `sys`, `tt`, the world bars (`di es wm hb mu bb he dc ca al nm lk lm tr po wi eh`), `jm`, `title`, `gumi`.

| bar | rows | files |
|---|---:|---:|
| sys | 3045 | 13 |
| tt | 1842 | 8 |
| di | 32 | 1 |
| es | 54 | 1 |
| wm | 214 | 1 |
| hb | 1029 | 5 |
| mu | 508 | 3 |
| bb | 490 | 2 |
| he | 664 | 3 |
| dc | 212 | 1 |
| ca | 542 | 3 |
| al | 415 | 2 |
| nm | 513 | 3 |
| lk | 476 | 2 |
| lm | 592 | 3 |
| tr | 311 | 2 |
| po | 309 | 2 |
| wi | 268 | 2 |
| eh | 563 | 3 |
| jm | 2129 | 9 |
| title | 694 | 3 |
| gumi | 650 | 3 |
| **total** | **15552** | **75** |

### Files

**sys** — 3045 rows, 13 files

- [ ] `review/sys_part01.csv` — 250 rows
- [ ] `review/sys_part02.csv` — 250 rows
- [ ] `review/sys_part03.csv` — 250 rows
- [ ] `review/sys_part04.csv` — 250 rows
- [ ] `review/sys_part05.csv` — 250 rows
- [ ] `review/sys_part06.csv` — 250 rows
- [ ] `review/sys_part07.csv` — 250 rows
- [ ] `review/sys_part08.csv` — 250 rows
- [ ] `review/sys_part09.csv` — 250 rows
- [ ] `review/sys_part10.csv` — 250 rows
- [ ] `review/sys_part11.csv` — 250 rows
- [ ] `review/sys_part12.csv` — 250 rows
- [ ] `review/sys_part13.csv` — 45 rows

**tt** — 1842 rows, 8 files

- [ ] `review/tt_part01.csv` — 250 rows
- [ ] `review/tt_part02.csv` — 250 rows
- [ ] `review/tt_part03.csv` — 250 rows
- [ ] `review/tt_part04.csv` — 250 rows
- [ ] `review/tt_part05.csv` — 250 rows
- [ ] `review/tt_part06.csv` — 250 rows
- [ ] `review/tt_part07.csv` — 250 rows
- [ ] `review/tt_part08.csv` — 92 rows

**di** — 32 rows, 1 file

- [ ] `review/di_part01.csv` — 32 rows

**es** — 54 rows, 1 file

- [ ] `review/es_part01.csv` — 54 rows

**wm** — 214 rows, 1 file

- [ ] `review/wm_part01.csv` — 214 rows

**hb** — 1029 rows, 5 files

- [ ] `review/hb_part01.csv` — 250 rows
- [ ] `review/hb_part02.csv` — 250 rows
- [ ] `review/hb_part03.csv` — 250 rows
- [ ] `review/hb_part04.csv` — 250 rows
- [ ] `review/hb_part05.csv` — 29 rows

**mu** — 508 rows, 3 files

- [ ] `review/mu_part01.csv` — 250 rows
- [ ] `review/mu_part02.csv` — 250 rows
- [ ] `review/mu_part03.csv` — 8 rows

**bb** — 490 rows, 2 files

- [ ] `review/bb_part01.csv` — 250 rows
- [ ] `review/bb_part02.csv` — 240 rows

**he** — 664 rows, 3 files

- [ ] `review/he_part01.csv` — 250 rows
- [ ] `review/he_part02.csv` — 250 rows
- [ ] `review/he_part03.csv` — 164 rows

**dc** — 212 rows, 1 file

- [ ] `review/dc_part01.csv` — 212 rows

**ca** — 542 rows, 3 files

- [ ] `review/ca_part01.csv` — 250 rows
- [ ] `review/ca_part02.csv` — 250 rows
- [ ] `review/ca_part03.csv` — 42 rows

**al** — 415 rows, 2 files

- [ ] `review/al_part01.csv` — 250 rows
- [ ] `review/al_part02.csv` — 165 rows

**nm** — 513 rows, 3 files

- [ ] `review/nm_part01.csv` — 250 rows
- [ ] `review/nm_part02.csv` — 250 rows
- [ ] `review/nm_part03.csv` — 13 rows

**lk** — 476 rows, 2 files

- [ ] `review/lk_part01.csv` — 250 rows
- [ ] `review/lk_part02.csv` — 226 rows

**lm** — 592 rows, 3 files

- [ ] `review/lm_part01.csv` — 250 rows
- [ ] `review/lm_part02.csv` — 250 rows
- [ ] `review/lm_part03.csv` — 92 rows

**tr** — 311 rows, 2 files

- [ ] `review/tr_part01.csv` — 250 rows
- [ ] `review/tr_part02.csv` — 61 rows

**po** — 309 rows, 2 files

- [ ] `review/po_part01.csv` — 250 rows
- [ ] `review/po_part02.csv` — 59 rows

**wi** — 268 rows, 2 files

- [ ] `review/wi_part01.csv` — 250 rows
- [ ] `review/wi_part02.csv` — 18 rows

**eh** — 563 rows, 3 files

- [ ] `review/eh_part01.csv` — 250 rows
- [ ] `review/eh_part02.csv` — 250 rows
- [ ] `review/eh_part03.csv` — 63 rows

**jm** — 2129 rows, 9 files

- [ ] `review/jm_part01.csv` — 250 rows
- [ ] `review/jm_part02.csv` — 250 rows
- [ ] `review/jm_part03.csv` — 250 rows
- [ ] `review/jm_part04.csv` — 250 rows
- [ ] `review/jm_part05.csv` — 250 rows
- [ ] `review/jm_part06.csv` — 250 rows
- [ ] `review/jm_part07.csv` — 250 rows
- [ ] `review/jm_part08.csv` — 250 rows
- [ ] `review/jm_part09.csv` — 129 rows

**title** — 694 rows, 3 files

- [ ] `review/title_part01.csv` — 250 rows
- [ ] `review/title_part02.csv` — 250 rows
- [ ] `review/title_part03.csv` — 194 rows

**gumi** — 650 rows, 3 files

- [ ] `review/gumi_part01.csv` — 250 rows
- [ ] `review/gumi_part02.csv` — 250 rows
- [ ] `review/gumi_part03.csv` — 150 rows

Total: 15552 rows in 75 files.

---

## (b) GLOSSARY — settle conflicting names

- [ ] GLOSSARY

Resolve the naming conflicts listed in `docs/consistency.md` (section "Top
findings → Still open", table C and the HUNT-1 table) and the open questions in
`docs/review_list.md`. This is the only task allowed to change glossary terms.

**Rule for limit and attack names (sys is canonical):** when a limit or attack
chain name differs between `sys` and `jm`, the canonical form is the **sys
form**, unless the sys form is linguistically wrong. Only then use the corrected
form (for example Comet Rain: sys 7764 «مطر المذنبين» means "the rain of the
guilty", so it becomes «مطر المذنبات»). Check every limit description page in jm
(ids 19156-19309, `jm_part08.csv`) against the sys names, not only the ones
below.

**Decisions to apply:**

| term | sys (id) | jm (id) | decision |
|---|---|---|---|
| Comet Rain | «مطر المذنبين» (7764) | «مطر المذنبات» (19157) | «مطر المذنبات» everywhere: the sys form is linguistically wrong («المذنبين» = the guilty) → change sys 7764 |
| Comet | «مذنب» (7763) | «المذنب» (19157) | sys form; the article alone is not a conflict, keep it where the sentence needs it |
| Knocksmash | «دمار الكسر» (12096, 13118) | «الضرب القاضي» (19163) | sys form unless it is wrong → change jm 19163 |
| Duo Raid | «غارة ثنائية» (12097) | «الغارة الثنائية» (19163) | sys form (article as the sentence needs) |
| Cosmo Boost | «كوزمو بوست» (12098) | «الدفعة الكونية» (19163) | sys form unless it is wrong → change jm 19163 |
| Twin Howl | «العواءان» (1164, 13124) | «العواء المزدوج» (19165) | sys form unless it is wrong → change jm 19165 |
| Stalwart Fang | «الناب المتين» (1165) | «الناب الصلب» (19165) | sys form unless it is wrong → change jm 19165 |
| Outcry | «الصراخ» (1166) | «الصرخة» (19165) | sys form unless it is wrong → change jm 19165 |
| Last Howl | «آخر عواء» (1167) | «العواء الأخير» (19165) | sys form unless it is wrong → change jm 19165 |
| Rikku / Riku | — | — | every row whose EN says **Rikku** uses «ريكا»; every row whose EN says **Riku** uses «ريكو». Rikku: hb 13020 says «ريكو» → «ريكا»; jm 11594 already «ريكا». Riku: 171 rows, all use «ريكو» now |

`docs/glossary.md` also lists the jm forms (line 1222: «مطر المذنبات, توهج البط,
الضرب القاضي, العواء المزدوج») next to the sys forms (lines 407, 570, 623); after
this task it must list one form per name.

**Already decided** (see `docs/glossary_decisions.md`): Naminé = «ناميني»
(`corrections/glossary_namine.csv`); «المدينة» for Twilight Town in dialogue is kept.

**Other open conflicts to decide** (choose one form, give the reason): Genie (جيني / الجني), MCP (إم سي بي / برنامج التحكم الرئيسي),
Central Computer Core (قلب / نواة), Christmas (ميلاد / كريسماس), Gauge (عداد /
مقياس), Captain (قائد / قبطان), Postern (الباب الخلفي / البوابة الخلفية),
Thundaga, Journal (يوميات / اليوميات), LV (مس / مستوى), Reaction Command in jm
(أوامر رد الفعل), Keyblade spelling (ca 9958 and ca 10319 «الكيبليد»). If a
choice is a matter of taste or space, keep the current majority form.

**Outputs:**

1. `corrections/glossary.csv` — one row for **every** affected row in `review/`
   (same columns as any correction file; `type=glossary`). Find the rows by
   searching both EN and AR in all 75 files, not only the examples above.
2. `docs/glossary_decisions.md` — **every** decision, one row each: term, sys
   form, jm/other form, chosen form, reason (why the sys form was kept, or why it
   is linguistically wrong), rows changed (bar and id). A decision without a
   reason is not accepted.
3. `docs/glossary.md` updated so every term has one approved form.

Pull request title: **Glossary decisions**.

**Review before merge:** glossary corrections change names across the whole
game, so the pull request is **never merged on a green check alone**. A person
reads `docs/glossary_decisions.md` and the rows in `corrections/glossary.csv`
and approves the pull request before it is merged.

---

## (c) SHORTEN — rows still over 150% width

- [ ] SHORTEN

Rows listed in `docs/long_rows.md` whose **current** `width_pct` in `review/` is
still above 150 (304 rows; the other rows listed there have already been
shortened). Write shorter Arabic with the **same meaning**, keeping tags, line
breaks, allowed characters and glossary terms as in RULES.md. If no shorter
wording with the same meaning exists (one-word interjections, or a row whose
width comes from a glossary name), leave the row out and list it in the pull
request description.

Output one file per bar, `corrections/shorten_<bar>.csv` (`type=phrasing`,
reason for example «تقصير لتناسب عرض الشاشة»). One pull request per bar or for
several bars, titled **Shorten: <bar>**.

| bar | rows | output | ids (current width_pct) |
|---|---:|---|---|
| sys | 1 | `corrections/shorten_sys.csv` | 15303: 175% |
| tt | 14 | `corrections/shorten_tt.csv` | 2916: 158%, 12250: 151%, 12254: 182%, 14192: 157%, 14311: 152%, 14356: 152%, 14387: 210%, 14548: 154%, 16473: 161%, 17541: 190%, 17964: 158%, 18396: 175%, 19693: 221%, 19893: 172% |
| es | 1 | `corrections/shorten_es.csv` | 16188: 152% |
| wm | 9 | `corrections/shorten_wm.csv` | 7684: 159%, 13852: 214%, 18084: 157%, 18085: 170%, 18545: 175%, 18555: 162%, 18560: 172%, 18561: 155%, 19474: 151% |
| hb | 30 | `corrections/shorten_hb.csv` | 2956: 171%, 2986: 232%, 2989: 151%, 2990: 152%, 2991: 151%, 2998: 158%, 8165: 180%, 8175: 163%, 8191: 169%, 8265: 161%, 8283: 155%, 12384: 171%, 12415: 153%, 12497: 156%, 12504: 168%, 12512: 155%, 12528: 186%, 12533: 173%, 12627: 161%, 12634: 151%, 12696: 151%, 12709: 160%, 12742: 155%, 12789: 167%, 12790: 161%, 12798: 155%, 12814: 250%, 12837: 176%, 16065: 172%, 18840: 158% |
| mu | 20 | `corrections/shorten_mu.csv` | 4211: 153%, 4270: 158%, 4271: 151%, 4311: 205%, 4312: 205%, 4313: 205%, 4314: 205%, 4317: 151%, 4323: 205%, 4324: 205%, 4325: 205%, 4326: 205%, 4330: 163%, 4337: 205%, 4369: 163%, 4414: 151%, 4459: 152%, 4511: 153%, 4516: 169%, 4606: 158% |
| bb | 6 | `corrections/shorten_bb.csv` | 3040: 155%, 3082: 180%, 3278: 160%, 3351: 176%, 3386: 169%, 7526: 161% |
| he | 9 | `corrections/shorten_he.csv` | 3611: 214%, 3683: 171%, 3719: 186%, 3770: 163%, 3773: 151%, 3825: 155%, 3840: 151%, 3980: 158%, 4041: 158% |
| dc | 3 | `corrections/shorten_dc.csv` | 5398: 181%, 5443: 172%, 5511: 164% |
| ca | 8 | `corrections/shorten_ca.csv` | 6217: 267%, 6218: 191%, 9960: 155%, 9966: 195%, 10078: 169%, 10115: 168%, 10125: 173%, 10235: 164% |
| al | 9 | `corrections/shorten_al.csv` | 103: 178%, 134: 161%, 184: 153%, 190: 191%, 280: 171%, 302: 167%, 331: 221%, 332: 171%, 4101: 167% |
| nm | 9 | `corrections/shorten_nm.csv` | 5839: 178%, 5881: 167%, 5914: 159%, 5918: 167%, 5962: 178%, 6014: 171%, 6030: 155%, 6061: 158%, 6130: 152% |
| lk | 6 | `corrections/shorten_lk.csv` | 8510: 152%, 8559: 158%, 8599: 154%, 8603: 155%, 8604: 153%, 8748: 187% |
| lm | 7 | `corrections/shorten_lm.csv` | 5051: 186%, 5102: 171%, 5250: 159%, 5251: 169%, 5331: 158%, 6435: 151%, 18726: 169% |
| tr | 15 | `corrections/shorten_tr.csv` | 850: 153%, 876: 261%, 878: 535%, 919: 154%, 996: 151%, 1037: 163%, 1047: 194%, 1048: 174%, 1076: 151%, 1078: 151%, 1081: 151%, 1087: 158%, 8053: 151%, 17876: 163%, 17899: 173% |
| po | 3 | `corrections/shorten_po.csv` | 4679: 153%, 4779: 214%, 18722: 219% |
| wi | 3 | `corrections/shorten_wi.csv` | 5550: 188%, 5589: 160%, 5693: 154% |
| eh | 8 | `corrections/shorten_eh.csv` | 16244: 164%, 16319: 157%, 16328: 169%, 16418: 155%, 16419: 171%, 16498: 180%, 16519: 156%, 21440: 177% |
| jm | 77 | `corrections/shorten_jm.csv` | 9914: 156%, 10793: 153%, 10989: 158%, 11444: 168%, 11446: 214%, 11450: 274%, 11460: 152%, 11464: 156%, 11482: 190%, 11486: 176%, 11496: 182%, 11532: 182%, 11552: 151%, 11570: 159%, 11580: 174%, 11620: 152%, 11640: 155%, 11650: 151%, 11656: 167%, 11657: 151%, 11664: 181%, 11668: 181%, 11724: 232%, 11756: 152%, 11774: 151%, 11776: 151%, 11794: 166%, 11806: 152%, 11842: 162%, 11886: 151%, 11888: 164%, 11890: 651%, 11918: 182%, 11924: 174%, 11930: 182%, 11944: 152%, 11948: 156%, 11950: 207%, 11974: 188%, 11990: 222%, 12030: 186%, 12036: 154%, 12046: 195%, 12048: 160%, 12052: 151%, 12064: 217%, 12065: 169%, 12066: 179%, 12067: 169%, 12130: 215%, 12881: 182%, 13943: 151%, 13989: 156%, 14773: 156%, 14781: 167%, 14783: 174%, 17250: 174%, 17923: 152%, 17943: 182%, 18587: 200%, 18636: 151%, 18651: 151%, 18653: 182%, 18961: 193%, 18963: 193%, 19162: 154%, 19206: 151%, 19214: 173%, 19228: 152%, 19243: 151%, 19246: 156%, 19255: 161%, 19378: 180%, 20140: 161%, 20142: 204%, 20284: 152%, 20298: 168% |
| title | 19 | `corrections/shorten_title.csv` | 20725: 176%, 20741: 222%, 20827: 186%, 20933: 214%, 20988: 168%, 21109: 151%, 21110: 176%, 21131: 152%, 21144: 171%, 21151: 167%, 21218: 154%, 21219: 153%, 21256: 166%, 21275: 188%, 21278: 168%, 21293: 187%, 21322: 182%, 21338: 174%, 21341: 182% |
| gumi | 47 | `corrections/shorten_gumi.csv` | 6222: 178%, 6265: 157%, 6271: 157%, 6273: 161%, 6311: 159%, 6329: 152%, 6342: 205%, 6344: 174%, 6345: 173%, 6350: 200%, 6355: 155%, 6356: 171%, 6416: 158%, 6422: 166%, 6425: 205%, 6427: 174%, 14079: 155%, 14080: 194%, 14087: 166%, 14280: 151%, 14291: 166%, 14692: 166%, 14699: 194%, 15148: 157%, 15680: 155%, 15681: 165%, 17746: 157%, 18321: 186%, 18322: 160%, 18497: 170%, 18500: 161%, 18501: 151%, 18504: 200%, 18506: 159%, 18510: 164%, 18513: 160%, 18686: 287%, 18687: 152%, 18694: 164%, 18786: 169%, 18796: 194%, 18797: 157%, 18925: 158%, 18927: 207%, 19134: 166%, 20500: 162%, 20691: 153% |
