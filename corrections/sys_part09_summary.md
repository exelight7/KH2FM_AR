# Summary: sys_part09

- Rows reviewed: 250
- Rows corrected: 2

## Top repeated error patterns

1. Number agreement after 11 and above: «15 أنواع … 45 أنواع» should be «15 نوعا
   … 45 نوعا» (7 rows, 15985-15991). **Not corrected**: «أنواع» is a glossary
   term (Types, 15302), so the validator counts the fix as a glossary change.
2. Object noun without accusative ending: «اصنع أغراض جديدة» should be
   «أغراضا» (15979; 16485 already has the right form). **Not corrected**: the
   validator counts «أغراضا» as a change of the glossary term «أغراض».
3. Missing «أن» after «يبدو»: «لا يبدو بوسعنا» → «لا يبدو أن بوسعنا» (16701).
4. Letter dropped from a spell name: «فاياغون» → «فايراغون» (16036).
5. No other repeated pattern; options, synthesis messages and Roxas field lines
   are correct.

## Glossary conflicts seen (not changed)

- 15985-15991 «N أنواع» (see pattern 1): blocked by the glossary term «أنواع».
- 15979 «أغراض جديدة» → «أغراضا جديدة» (pattern 2): blocked by the term «أغراض».
- 17088 Port Royal: «في ميناء الملك» ("the King´s port"); the approved name is
  «ميناء رويال». Changes the place name; the fix adds a glossary term.
- 16940 The Underdrome: «الحلبة السفلي» should be «الحلبة السفلية» (the form
  in docs/review_list.md); the fix adds the glossary term.
- 16101 Oasis Map: «خريطة واحة» should be «خريطة الواحة» like the other maps;
  blocked by the term «الواحة».
- 16109 I/O Tower Map «خريطة البرج» (glossary: «برج الإدخال»).
- 16152 «بأورون» (glossary: «آرون»).
- 17078-17081 «جيني» for Genie (already in docs/consistency.md).
- 16752 «محل الملحقات» while shops elsewhere say «الإكسسوارات».
- 16480 Creations «المبتكرات» while the menu (15500, 16075) says «المصنوعات».
- 16941 Grind «الهرس» ("mashing") for the skateboard grind.
