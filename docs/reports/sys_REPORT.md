round: PROOF-sys

# Proofreading report: sys

## Files done

13 of 13 sys files have a correction file and a summary. `sys_part01` was done
in an earlier round (merged); `sys_part02` to `sys_part13` were done in this
round. All 13 files pass `python tools/validate_corrections.py`.

| file | rows reviewed | rows corrected |
|---|---:|---:|
| sys_part01 (earlier round) | 250 | 2 |
| sys_part02 | 250 | 5 |
| sys_part03 | 250 | 8 |
| sys_part04 | 250 | 1 |
| sys_part05 | 250 | 4 |
| sys_part06 | 250 | 7 |
| sys_part07 | 250 | 5 |
| sys_part08 | 250 | 5 |
| sys_part09 | 250 | 11 |
| sys_part10 | 250 | 16 |
| sys_part11 | 250 | 11 |
| sys_part12 | 250 | 4 |
| sys_part13 | 45 | 2 |
| **total** | **3045** | **81** |

This round alone: 2,795 rows reviewed, 79 rows corrected (68 first pass + 11
fixes allowed after `unprotected_terms` was added to RULES.md).

## Corrections per type and severity (all 13 files)

| type | severity 1 | severity 2 | severity 3 | total |
|---|---:|---:|---:|---:|
| grammar | 9 | 24 | 0 | 33 |
| spelling | 1 | 16 | 0 | 17 |
| meaning | 0 | 17 | 0 | 17 |
| phrasing | 9 | 5 | 0 | 14 |
| **total** | **19** | **62** | **0** | **81** |

## Top 10 repeated error patterns

| # | pattern | rows | example |
|---|---|---:|---|
| 1 | «المتحققة» ("verified") used for "obtained/acquired" → «المكتسبة» | 8 | 17797 «الأشكال المتحققة» → «الأشكال المكتسبة» |
| 2 | Comma lost between two clauses, leaving a double space | 6 | 1601 «بمساعدة صديقين  استخدم» → «بمساعدة صديقين, استخدم» |
| 3 | Adjective attached to an indefinite noun like an idafa | 5 fixed, 2 blocked | 14909 «خاتم الكوني» → «الخاتم الكوني» |
| 4 | Gender agreement (demonstrative, pronoun, adjective, verb) | 7 | 17740 «تلك القطار» → «ذلك القطار» |
| 5 | «ليست هذه الطريقة» ("not this method") for "not this way" | 4 | 18033 → «ليس هذا الطريق» |
| 6 | Letters dropped from a word | 6 | 2619 «تواء الذاكرة» → «التواء الذاكرة»; 16036 «فاياغون» → «فايراغون» |
| 7 | Verbal noun with alef maqsura: «تلقى» → «تلقي» | 3 | 15367 «بعد تلقى ضرر» → «بعد تلقي ضرر» |
| 8 | Wrong word for the meaning | 6 | 15349 «اجمع الفريق كله» (gather) → «جهز الفريق كله» (equip) |
| 9 | Accusative ending missing (object, numbers above 10, adverbs) | 10 | 22018 «تحرك يمين ويسار» → «تحرك يمينا ويسارا» |
| 10 | Wrong tense or person | 3 | 19562 «سأل الآخرين» ("he asked") → «سأسأل الآخرين» ("I´ll ask") |

## Severity-3 corrections

None. No correction in this bar was rated severity 3. The meaning errors that
were fixed (16 rows) change a word, not the sense of the whole line, so they are
severity 2. The two rows that do reverse the English are blocked by the
glossary (see below: 9933 Fail-Safe, 17088 Port Royal).

## Glossary conflicts seen

The validator does not allow a proofreading file to change the count of any
approved glossary form, so these were **not** changed. They need the GLOSSARY
task or a supervisor decision.

**Approved form is itself wrong:**

- 1220, 1221, 1254 «اغادر» (Leave/Depart): not an Arabic imperative; should be
  «غادر» (glossary lines 431-432).
- 2783 «ارتفعت السحر!»: «السحر» is masculine → «ارتفع السحر!» (glossary line 548).
- 9945 «قفز!» (Jump!) and 14431 «هبط» (Land): commands should be «اقفز!» / «اهبط».
- 9933 Fail-Safe «ضمان الفشل» = "guaranteed failure", the opposite of the
  English; 8995 Key Counter «عداد المفاتيح» = a key-counting meter.
- 13129 «جلسة الأبدية» → «الجلسة الأبدية»; 13133 Treasure Isle «كنز الجزيرة» →
  «جزيرة الكنز».
- 14921/14925 «الازهار» → «الإزهار»; 15570 «موج الهاو» → «موج الهاوي»;
  15607 «البرج الساعة» → «برج الساعة».
- 15071/15075/15077 Twilight materials «شظية شفقة» (pity), «جوهرة شفقاء»,
  «بلورة شفقاء» → «شفقية» (glossary line 742).
- 15872/15958 «منقاذ الملك» («منقاذ» is not a word; «منقذ الملك»).
- 17818 «تيكر بيل» → «تينكر بيل».

**A row does not use the approved name:**

- 17088 Port Royal «ميناء الملك» ("the King´s port"; glossary «ميناء رويال»).
- 18064 «هولو باستيون» (glossary «حصن هولو»); 20398 «قصر ديزني» (glossary
  «قلعة ديزني»); 20001 «جزيرة القدر» (glossary «جزيرة المصير»).
- 15131/15132/16152 «أورون» (glossary «آرون»).
- 14955 «فاياغا», 20326 «زانتيتسوكين», 22035 «جوفر»: a fix to the glossary
  spelling adds the glossary term, so it was blocked.
- Known open items seen again: Genie «جيني» (17078-17081, 17810, 17817), MCP
  «إم سي بي» (18066), Naminé «نامين» (15125/15126), Moogle «موج/الموجل»,
  Comet Rain 7764, Knocksmash 12096/13118, Twin Howl 1164/13124, LV «مس».

**One item, two names:**

- Drive forms: «شكل الشجاعة / الحكمة / الإتقان / الأخير» vs «الشكل الشجاع /
  الحكيم / المتقن / النهائي» (15307-15313, 17790-17807) and Final =
  «الأخير» / «النهائي».
- Healing Light «ضوء الشفاء» vs «الضوء الشافي» (15298); Sonic Rave «سونيك ريف» /
  «حفلة صوتية»; Last Arcanum «لاست أركانوم» / «أسرار النهاية»; Strike Raid
  «سترايك ريد» / «ضربة غازية» («غازية» = gaseous); Grind «الهرس» / «الانزلاق»;
  Creations «المصنوعات» / «المبتكرات»; Shaman´s Relic «آثار» / «تحفة»;
  Memory´s Contortion «التواء» / «تشوه»; Garden of Assemblage «التجمع» /
  «التجميع»; Journal «يوميات» / «اليومية».

## Unsure / blocked by the validator

1. **Grammar fixes once blocked by common-word glossary terms (now fixed).**
   «أنواع», «أغراض», «الأغراض», «الشكل», «حماية», «الحماية», «ضربة» and «الواحة» are
   now `unprotected_terms` in RULES.md, so these fixes are included:
   15985-15991 «N أنواع» → «N نوعا», 15979 «أغراضا», 1122 «في الشكل الأخير»,
   20083 «يخترق الحماية … حمايتك», 16101 «خريطة الواحة».
2. **Length rule.** 14910 and 20624 «يزيد/يرفع … AP هائلا» are awkward, but a
   correct rewrite is longer than allowed.
3. **Line breaks.** 18468 has one more «⏎» than the English; the rules don't
   allow fixing the count.
4. **Untranslated rows.** 17838/17839 «<0D>´s Status.», 19388 «Sora: ⏎ ₓₓₓ»
   and the debug rows 1445-1449 are untranslated. They need an in-game check of
   where the name tag sits before translating.
5. **Kept as possibly intended.** 13112 «سحر دونالد القوي المذنب» can read as
   "the guilty magic". It is kept because «مذنب» is the approved form of Comet;
   the GLOSSARY task should look at it together with Comet Rain.
