# Glossary decisions

Every glossary decision, one row each: the English term, the Arabic forms found
in `review/` (rows that contain each form), the chosen form, the reason, and the
rows changed. The rows are in `corrections/glossary_decisions.csv` (this round)
and `corrections/glossary_namine.csv` (Naminé, PR #7). `docs/glossary.md` lists
the chosen forms in its last section, «قرارات GLOSSARY (2026-10-08)».

**Rules, in order** (supervisor, 2026-10-08):

1. correct Arabic first;
2. for names, a transliteration that follows the English pronunciation, the same
   across the game;
3. otherwise the form already used most in `review/`;
4. if equal, the shorter form.

**sys rule** (docs/TASKS.md): for limit and attack names that differ between sys
and jm, the sys form wins unless it is linguistically wrong.

The length rule still applies. A change that makes a row too long is **not**
applied: it is listed in `corrections/needs_width_check.csv` (marked "(width
check)" below) and waits for a width check in the game.

The counts are rows of `review/` whose AR contains the form (with an attached
و ف ب ل ك or the article); for one-word forms only rows whose EN has the term are
counted. A form with count 0 is not used yet.

**Review before merge:** these changes rename terms across the whole game; a
person reads this table and `corrections/glossary_decisions.csv` before merging.

## Decisions

### Limit and attack names (sys wins unless it is wrong)

| EN | current forms (rows) | chosen form | reason | rows changed |
|---|---|---|---|---|
| Comet Rain | «مطر المذنبين» 1, «مطر المذنبات» 1 | «مطر المذنبات» | **rule 1:** sys «مطر المذنبين» means "rain of the guilty"; «المذنبات» = comets (decided in TASKS) | 1 row: sys 7764 |
| Flare Force | «قوة الفلاير» 1, «قوة التوهج» 1 | «قوة الفلاير» | **sys rule:** sys form (limit-name rule) | 1 row: jm 19158 |
| Duck Flare / Rocket Flare / Megaduck Flare | «فلاير البط» 3, «توهج البط» 1, «شعلة الصاروخ» 1, «توهج الصاروخ» 1, «ميجا فلاير البط» 1, «توهج البط العملاق» 1 | «فلاير البط» / «شعلة الصاروخ» / «ميجا فلاير البط» | **sys rule:** sys forms (limit-name rule) | 1 row: jm 19159 |
| Teamwork | «تعاون» 2, «عمل جماعي» 1 | «تعاون» | **sys rule:** sys form (limit-name rule) | 1 row: jm 19162 |
| Knocksmash / Duo Raid / Cosmo Boost | «دمار الكسر» 2, «الضرب القاضي» 1, «غارة ثنائية» 1, «كوزمو بوست» 1, «الدفعة الكونية» 1 | «دمار الكسر» / «غارة ثنائية» / «كوزمو بوست» | **sys rule:** sys forms (limit-name rule; the article on «الغارة الثنائية» is grammar, not a conflict) | 1 row: jm 19163 |
| Howling Moon | «عواء القمر» 1, «القمر العاوي» 1 | «عواء القمر» | **sys rule:** sys form (limit-name rule) | 1 row: jm 19164 |
| Twin Howl / Stalwart Fang / Outcry / Last Howl | «العواءان» 2, «العواء المزدوج» 1, «الناب المتين» 1, «الناب الصلب» 1, «الصراخ» 1, «الصرخة» 1, «آخر عواء» 1, «العواء الأخير» 1 | «العواءان» / «الناب المتين» / «الصراخ» / «آخر عواء» | **sys rule:** sys forms (limit-name rule) | 1 row: jm 19165 |
| Overdrive | «أوفردرايف» 1, «أوفر درايف» 1 | «أوفردرايف» | **sys rule:** sys form (limit-name rule) | 1 row: jm 19166 |
| Shooting Star / Spiral | «الشهاب» 1, «النجم الساقط» 2, «اللولب» 2, «الحلزون» 1 | «الشهاب» / «اللولب» | **sys rule:** sys forms (limit-name rule); «النجم الساقط» stays for Falling Star (sys 8313) | 1 row: jm 19167 |
| Banishing Blade | «النصل المطرد» 1, «نصل النفي» 1 | «نصل النفي» | **rule 1:** sys «النصل المطرد» reads as «المطّرد» (steady); "banishing" = نفي | 1 row: sys 1170 |
| Dragonblaze | «لهيب التنين» 1, «لهب التنين» 1 | «لهيب التنين» | **sys rule:** sys form (limit-name rule) | 1 row: jm 19168 |
| Trick Fantasy / Speedster / Trickster | «فانتازيا الحيلة» 1, «فانتازيا الخدع» 1, «الاندفاع» 2, «المتسابق» 1, «الحيلة» 2, «المخادع» 1 | «فانتازيا الحيلة» / «الاندفاع» / «الحيلة» | **sys rule:** sys forms (limit-name rule) | 2 rows: jm 19170, 19171 |
| Downbeat / Finale | «النبضة» 1, «الضربة الأولى» 1, «النهاية» 1, «الختام» 1 | «النبضة» / «النهاية» | **sys rule:** sys forms (limit-name rule) | 1 row: jm 19173 |
| Synchronization | «الالتزامن» 1, «التزامن» 1 | «التزامن» | **rule 1:** sys «الالتزامن» has a doubled article (typo); already fixed the same way by the sys proofreading; that row moves here | 1 row: sys 14613 |
| Treasure Isle | «كنز الجزيرة» 1, «جزيرة الكنز» 1 | «جزيرة الكنز» | **rule 1:** sys «كنز الجزيرة» = "the island´s treasure", the wrong way round | 1 row: sys 13133 |
| King´s Pride | «فخر الملك» 1, «كبرياء الملك» 1 | «فخر الملك» | **sys rule:** sys form (limit-name rule) | 1 row: jm 19176 |
| Proud Roar | «العواء الفخم» 1, «الزئير الفخور» 1 | «الزئير الفخور» | **rule 1:** sys «العواء» = howl; a lion roars: «زئير» | 1 row: sys 14092 |
| Setup / Cluster Code / Reprogram | «إعداد» 1, «التجهيز» 1, «رمز التجمع» 1, «شيفرة العنقود» 1, «برمجة» 2, «إعادة البرمجة» 1 | «الإعداد» / «رمز التجمع» / «إعادة البرمجة» | **sys rule, rule 1:** sys forms, except Reprogram: «برمجة» = "programming", the "re-" is lost | 2 rows (1 to width check): jm 19179; sys 14625 (width check) |
| Complete Compilement | «الإكمال الكامل» 1, «التجميع الكامل» 1 | «الإكمال الكامل» | **sys rule:** sys form (limit-name rule) | 1 row: jm 19178 |
| Eternal Session / Last Saber / Master Hearts / All´s End | «جلسة الأبدية» 1, «الجلسة الأبدية» 1, «النصل الأخير» 1, «السيف الأخير» 1, «القلوب المتقنة» 1, «قلوب السيد» 1, «نهاية الكل» 1, «النهاية الشاملة» 1 | «الجلسة الأبدية» / «النصل الأخير» / «القلوب المتقنة» / «نهاية الكل» | **rule 1, sys rule:** sys «جلسة الأبدية» is a broken construct → «الجلسة الأبدية»; the others: sys forms | 2 rows: sys 13129; jm 19181 |
| Trinity Limit / Trinity / Major Drive | «ترينتي ليميت» 1, «ليميت الثالوث» 1, «ترينتي» 3, «الثالوث» 2, «الدرايف الأكبر» 1, «الدرايف الكبير» 1 | «ترينتي ليميت» / «ترينتي» / «الدرايف الأكبر» | **sys rule:** sys forms (limit-name rule; also the glossary form) | 2 rows: jm 19182, 19183 |
| Ultima | «ألتيمة» 4, «ألتيما» 3 | «ألتيما» | **rule 2:** a foreign name ending in /a/ is written with alef, not taa marbuta | 4 rows: sys 1482, 1483, 15715, 15950 |
| Never Land | «نيفر لاند» 1, «نيفرلاند» 2 | «نيفر لاند» | **sys rule:** sys and glossary form (limit-name rule) | 2 rows: jm 11505, 19184 |
| FPS Mode / Firecracker | «منظور 1» 1, «وضع الرماية» 1, «الشماريخ» 1, «الألعاب النارية» 1 | «منظور 1» / «الشماريخ» | **sys rule:** sys forms (limit-name rule) | 2 rows: jm 19186, 19187 |
| Ukulele | «يوكيليلي» 2, «يوكوليلي» 0 | «يوكوليلي» | **rule 2:** «يوكوليلي» is the usual Arabic spelling and follows the pronunciation | 2 rows: sys 1600, 17034 |
| Sonic Rave / Sonic / Rave | «سونيك ريف» 2, «حفلة صوتية» 1, «الرنين» 1, «سونيك» 3, «حفلة» 3, «ريف» 3 | «سونيك ريف» / «الرنين» / «حفلة» | **sys rule, rule 2:** limit name: sys has both forms, the glossary and jm use «سونيك ريف»; parts: sys forms | 2 rows: sys 20222; jm 19191 |
| Strike Raid / Strike | «سترايك ريد» 2, «ضربة غازية» 1, «الضرب» 2, «الضربة» 3 | «سترايك ريد» / «الضرب» | **rule 1, sys rule:** limit name: «ضربة غازية» means "gaseous strike"; parts: sys forms | 2 rows: sys 20228; jm 19305 |
| Last Arcanum / Final Arcana / Arcana / Bash | «لاست أركانوم» 1, «أسرار النهاية» 2, «أركانا الأخيرة» 1, «الأسرار» 1, «أركانا» 2, «الكبس» 2, «الصدمة» 1 | «لاست أركانوم» / «أسرار النهاية» / «الأسرار» / «الكبس» | **rule 2, sys rule:** Last Arcanum: glossary transliteration; Final Arcana and the parts: sys forms | 3 rows: sys 20225; jm 19306, 19307 |
| Infinity / Impact | «إنفينيتي» 3, «اللانهاية» 3, «الصدم» 6, «التأثير» 1 | «إنفينيتي» / «الصدم» | **rule 2, sys rule:** limit name: glossary transliteration (sys has both); Impact: sys form | 4 rows: sys 17171, 20214, 21600; jm 19309 |
| Whirli-Goof / -ra / -ga | «دور غوفي» 4, «غوفي الدوار» 1, «دور غوفي را» 1, «غوفي الدوار 2» 1, «دور غوفي جا» 1, «غوفي الدوار 3» 1 | «غوفي الدوار» / «غوفي الدوار را» / «غوفي الدوار غا» | **rule 1:** sys «دور غوفي» means "Goofy´s turn"; "-ga" is written «غا» as in Firaga/Curaga | 5 rows (3 to width check): sys 1176 (width check), 1177 (width check), 1178 (width check), 13116; jm 19195 |
| "Valor"/"Wisdom"/"Master"/"Final" Genie | «جيني الشجاعة» 1, «الجني "الشجاعة"» 1, «جني الشجاعة» 0 | «جني الشجاعة» / «جني الحكمة» / «جني الإتقان» / «الجني النهائي» | **rule 1:** «جيني» is not the Genie´s name (glossary «الجني»); the construct form fits the sys space; Final takes an adjective | 8 rows: sys 17078, 17079, 17080, 17081; jm 19190, 19304, 19306, 19308 |
| Genie | «الجني» 30, «جيني» 6 | «الجني» | **rule 1, rule 3:** glossary form; «جيني» reads as a girl´s name | 2 rows: sys 17810, 17817 |

### Drive Forms

| EN | current forms (rows) | chosen form | reason | rows changed |
|---|---|---|---|---|
| Final (Drive Form name) | «الأخير» 15, «النهائي» 17 | «النهائي» | **rule 1, rule 3:** "Final" = نهائي («الأخير» = the last); also the majority | 3 rows: sys 488, 1121, 1608 |
| Valor/Wisdom/Master/Final Form (in a sentence) | «شكل الشجاعة» 3, «الشكل الشجاع» 4, «شكل الحكمة» 2, «الشكل الحكيم» 3, «شكل الإتقان» 3, «الشكل المتقن» 4, «شكل الأخير» 1, «الشكل الأخير» 1, «الشكل النهائي» 3 | «الشكل الشجاع» / «الحكيم» / «المتقن» / «النهائي» | **rule 3:** majority; «شكل الأخير» is ungrammatical, so Final needs the adjective form and the set follows it | 10 rows: sys 1118, 1120, 1122, 1603, 1605, 1607, 19343, 19344, 19345, 19346 |
| Limit Form | «شكل الليميت» 6, «فورم ليميت» 1, «شكل ليميت» 1 | «شكل الليميت» | **rule 1, rule 3:** «فورم» is the English word; Form = «شكل» everywhere else; majority | 2 rows: sys 20095, 20128 |

### Approved or used forms that are wrong Arabic

| EN | current forms (rows) | chosen form | reason | rows changed |
|---|---|---|---|---|
| Leave / Depart | «اغادر» 3, «غادر» 3 | «غادر» | **rule 1:** «اغادر» is not an Arabic imperative | 3 rows: sys 1220, 1221, 1254 |
| Magic Increased! | «ارتفعت السحر!» 1, «ارتفع السحر!» 0 | «ارتفع السحر!» | **rule 1:** «السحر» is masculine | 1 row: sys 2783 |
| Jump! (command) | «قفز!» 1, «اقفز!» 1 | «اقفز!» | **rule 1:** an order needs the imperative; the plain menu labels "Jump" stay «قفز» (noun) | 1 row: sys 9945 |
| Land (command) | «هبط» 1, «اهبط» 0 | «اهبط» | **rule 1:** «هبط» is past tense ("he landed"); the commands around it are imperatives (Stop = «قف») | 1 row: sys 14431 |
| Fail-Safe | «ضمان الفشل» 1, «صمام الأمان» 0 | «صمام الأمان» | **rule 1:** «ضمان الفشل» means "guaranteed failure", the opposite; «صمام الأمان» is the usual Arabic for fail-safe, same length | 1 row: sys 9933 |
| Key Counter | «عداد المفاتيح» 1, «الرد بالمفتاح» 0 | «الرد بالمفتاح» | **rule 1:** «عداد المفاتيح» is a key-counting meter; the command is a counter-attack with the Keyblade; same length | 1 row: sys 8995 |
| Full Bloom | «الازهار» 2, «الإزهار» 0 | «الإزهار» | **rule 1:** hamza of the verbal noun «إزهار» | 2 rows: sys 14921, 14925 |
| The Clocktower | «البرج الساعة» 1, «برج الساعة» 0 | «برج الساعة» | **rule 1:** a construct does not take the article on its first noun | 1 row: sys 15607 |
| Twilight Shard / Gem / Crystal | «شظية شفقة» 1, «جوهرة شفقاء» 1, «بلورة شفقاء» 1, «شظية الشفق» 0 | «شظية الشفق» / «جوهرة الشفق» / «بلورة الشفق» | **rule 1:** «شفقة» = pity, «شفقاء» is not a word; Twilight = «الشفق» as in «بلدة الشفق» | 3 rows: sys 15071, 15075, 15077 |
| Save the King | «منقاذ الملك» 2, «منقذ الملك» 0 | «منقذ الملك» | **rule 1:** «منقاذ» is not a word; matches Save the Queen «منقذة الملكة» | 2 rows: sys 15872, 15958 |
| Tinker Bell | «تيكر بيل» 2, «تينكر بيل» 0 | «تينكر بيل» | **rule 2:** the name has an /n/ (Tinker) | 2 rows: sys 17818; jm 11505 |
| Elixir | «إليكسير» 1, «إيليكسير» 0, «إكسير» 0 | «إكسير» | **rule 1:** «إكسير» is the real Arabic word (and shorter) | 1 row: sys 766 |
| Candy Cane Lane | «ممر العصا الحلوى» 1, «ممر عصا الحلوى» 0 | «ممر عصا الحلوى» | **rule 1:** «العصا الحلوى» puts the article on the first noun of a construct | 1 row: sys 703 |
| Sandlot | «الرملية» 11, «ساحة اللعب» 10 | «ساحة اللعب» | **rule 1:** «الرملية» ("the sandy") is an adjective with no noun; «ساحة اللعب» is already used in jm and sys | 11 rows (7 to width check): sys 743 (width check), 2637 (width check); tt 13227, 13292 (width check), 13641 (width check), 17297 (width check), 17304 (width check), 17359 (width check), 17613, 17664, 17670 |
| Wildebeest Valley | «وادي الغزلان» 8, «وادي النو» 0 | «وادي النو» | **rule 1:** «الغزلان» = gazelles; a wildebeest is «النو» | 9 rows: sys 606, 14853; jm 10795, 10797, 10798; lk 12899, 14229, 14233, 17174 |
| Curly Hill | «تل ملتوي» 2, «التل الملتوي» 0 | «التل الملتوي» | **rule 1:** a place name is definite (glossary form); indefinite «ملتوي» would also need «ملتو» | 2 rows (2 to width check): sys 700 (width check), 16099 (width check) |
| Cosmic Ring / Belt / Chain | «خاتم الكوني» 1, «حزام الكوني» 1, «سلسلة الكوني» 1, «الخاتم الكوني» 0, «سلسلة كونية» 0 | «الخاتم الكوني» / «الحزام الكوني» / «سلسلة كونية» | **rule 1:** an indefinite noun cannot take a definite adjective; all three are already fixed this way by the sys proofreading; those rows move here so the term change sits in a glossary file | 3 rows: sys 14909, 14939, 15005 |
| Groundshaker | «مهزز الأرض» 3, «مزلزل الأرض» 0 | «مزلزل الأرض» | **rule 1:** «مهزز» is not a word; «مزلزل» = earth-shaker | 3 rows: jm 12038; sys 15532; title 21265 |
| Grind | «الهرس» 1, «الانزلاق» 1 | «الانزلاق» | **rule 1:** «الهرس» = mashing; a rail grind is a slide (sys 22002) | 1 row (1 to width check): sys 16941 (width check) |
| Memory´s Contortion | «تواء الذاكرة» 1, «تشوه الذاكرة» 1 | «تشوه الذاكرة» | **rule 1, rule 4:** «تواء» is a broken word (the proofreading fixed it to «التواء»); of the two correct forms the shorter, as in sys 19995 | 1 row: sys 2619 |
| Shaman´s Relic | «آثار الشامان» 1, «تحفة الشامان» 1 | «تحفة الشامان» | **rule 1:** "Relic" is one item: «آثار» is plural (traces) | 1 row: sys 8863 |
| Dewey | «ديوي» 3, «دوي» 3 | «ديوي» | **rule 1, rule 2:** «دوي» = a bang; the name is «ديوي» (jm, glossary) | 3 rows: sys 2749, 2751, 2752 |
| Armor Shop | «متجر الدروع» 2, «للدرع» 2, «محل الدروع» 1 | «متجر ... للدروع» | **rule 1:** «الدرع» singular = one shield; armor shop sells «دروع» | 2 rows: sys 2745, 2750 |
| Cure (spell, in a sentence) | «كور» 3, «العلاج» 1 | «كور» | **rule 1:** the spell name is «كور» (decided); «إطلاق العلاج» reads as "releasing the treatment" | 1 row: sys 15341 |

### Names: one transliteration, one place name

| EN | current forms (rows) | chosen form | reason | rows changed |
|---|---|---|---|---|
| Port Royal | «ميناء رويال» 39, «ميناء الملك» 1 | «ميناء رويال» | **rule 1, rule 3:** «ميناء الملك» = "the King´s port"; glossary form | 1 row: sys 17088 |
| Hollow Bastion | «حصن هولو» 51, «هولو باستيون» 1 | «حصن هولو» | **rule 3:** glossary form | 1 row: sys 18064 |
| Disney Castle | «قلعة ديزني» 43, «قصر ديزني» 1 | «قلعة ديزني» | **rule 3:** glossary form | 1 row: sys 20398 |
| Destiny Island(s) | «جزيرة المصير» 2, «جزيرة القدر» 1, «الجزيرة» 0 | «جزيرة المصير» | **rule 3:** glossary form; «الجزيرة» in Sora´s dialogue (the island) is kept like «المدينة» | 1 row: sys 20001 |
| Auron | «آرون» 60, «أورون» 3 | «أورون» | **rule 2:** «أورون» follows the English pronunciation (/ˈɔːrɒn/, "OR-on"); «آرون» reads "Aaron". All rows changed so the name is the same everywhere | 60 rows: he 3472, 3503, 3594, 3771, 3798, 3820, 3823, 3830, 3843, 3846, 3849, 3852, 3857, 3879, 3888, 3889, 3891, 3932, 16145, 16164, 16167, 19357, 19358, 21500, 21508; jm 10616, 10618, 10648, 10652, 10653, 10654, 10655, 10656, 10658, 11080, 11097, 11098, 11099, 11100, 11101, 11318, 11319, 11329, 11642, 11643, 13143, 13149, 19166, 19167; sys 672, 1138, 1139, 1315, 13122; title 20851, 20859, 21195, 21199, 21202; wm 7711 |
| Gopher | «غوفر» 5, «جوفر» 1 | «غوفر» | **rule 2, rule 3:** glossary form; «غ» for /g/ as in غوفي | 1 row: sys 22035 |
| Zantetsuken | «زانتيتسوكين» 1, «زانتيتسوكن» 1 | «زانتيتسوكين» | **rule 2:** follows the pronunciation (-ken) | 1 row: sys 20117 |
| MCP | «برنامج التحكم الرئيسي» 70, «إم سي بي» 1 | «برنامج التحكم الرئيسي» | **rule 3:** glossary form | 1 row (1 to width check): sys 18066 (width check) |
| Central Computer Core | «نواة الحاسوب المركزي» 2, «قلب الحاسوب المركزي» 4, «نواة الحاسوب المركزية» 1 | «نواة الحاسوب المركزي» | **rule 1, rule 3:** glossary and sys form; core = «نواة»; «المركزي» qualifies «الحاسوب» | 5 rows: hb 2988, 2995, 2996, 2997; sys 16111 |
| Moogle | «موغل» 3, «الموغل» 14, «موج» 15, «الموجل» 10 | «موغل» | **rule 1, rule 3:** «موج» = wave, «الموجل» is a misspelling; «موغل» is the glossary form; rank titles become indefinite noun + adjective | 26 rows: sys 15218, 15253, 15292, 15506, 15570, 15571, 15572, 15573, 15574, 15575, 15576, 15577, 15578, 15584, 15617, 15619, 15621, 15623, 15669, 15671, 15673, 15675, 15677, 15754, 16054, 16081 |
| Fira / Firaga / Firagun | «فايرا» 2, «فيرا» 1, «فايراغا» 1, «فيراغا» 1, «فاياغا» 1, «فيراغون» 1, «فايراغون» 0 | «فايرا» / «فايراغا» / «فايراغون» | **rule 2:** glossary and sys spell forms; one transliteration for the whole series (sys 14957, 16036, 19428 were already fixed this way by the proofreading; those rows move here) | 6 rows: sys 14955, 14957, 16036, 19428; gumi 6250, 6251 |
| Thundara / Thundaga / Thundagun | «ثاندرا» 1, «ثوندارا» 1, «ثاندارا» 0, «ثاندراجا» 2, «ثونداغا» 1, «ثانداغا» 2, «ثونداغون» 1, «ثانداغون» 0 | «ثاندارا» / «ثانداغا» / «ثانداغون» | **rule 2:** follows the pronunciation (thun-DAR-a, thun-DA-ga) and the Fira/Firaga pattern («-ra» = را, «-ga» = غا) | 7 rows: gumi 6259; sys 1292, 1293, 14973, 14975, 14977; jm 10843 |
| Blizzara / Blizzaga | «بليزاردا» 1, «بليزارا» 2, «بليزاردجا» 1, «بليزاغا» 2 | «بليزارا» / «بليزاغا» | **rule 2, rule 3:** same pattern as Fira/Firaga; already used in sys items and gumi | 2 rows: sys 1295, 1296 |
| Magnega / Reflega | «ماغنيجا» 1, «ماغنيغا» 0, «ريفليجا» 1, «ريفليغا» 0 | «ماغنيغا» / «ريفليغا» | **rule 2:** "-ga" = «غا» as in Firaga/Curaga | 2 rows: sys 1302, 1305 |
| Fenrir | «فنرير» 2, «فينرير» 1 | «فنرير» | **rule 2, rule 3:** follows the pronunciation (FEN-rir); majority | 1 row: sys 15948 |
| Pence | «بنس» 11, «بينس» 13 | «بنس» | **rule 2:** follows the pronunciation /pɛns/; «بينس» reads "Pains" | 13 rows: tt 13361, 13362, 13432, 13497, 13578, 13676, 14328, 17295, 17985, 19554, 19557, 19923, 21479 |
| Keyblade | «كيبلايد» 21, «كيبليد» 1 | «كيبلايد» | **rule 3:** glossary form; «كيبليد» is a slip | 2 rows: ca 9958, 10319 |
| Rikku | «ريكا» 1, «ريكو» 1 | «ريكا» | **already decided:** Rikku is «ريكا» so that it does not collide with Riku «ريكو» (decided) | 1 row: hb 13020 |
| DTD | «دي تي دي» 18, «بإظ» 1, «باب الظلام» 8 | «دي تي دي» | **rule 3:** glossary form and majority; hb 2960 still spells out "Door To Darkness" after it | 2 rows (1 to width check): hb 2958 (width check), 12536 |
| Olympus Stone | «حجر أولمبيا» 18, «حجر أولمبوس» 1 | «حجر أولمبيا» | **rule 3:** majority and consistent with the world name «كولوسيوم أولمبيا» | 1 row: sys 15129 |
| Hades Paradox Cup | «كأس مفارقة هاديس» 5, «كأس هاديس المتناقض» 1 | «كأس مفارقة هاديس» | **rule 3:** the form of all 14 other Paradox Cup rows | 1 row: sys 19471 |

### One term, two forms

| EN | current forms (rows) | chosen form | reason | rows changed |
|---|---|---|---|---|
| Nobody / Nobodies | «اللا أحد» 113, «لا أحد» 46, «لا أحدا» 1 | «اللا أحد» | **rule 1:** glossary term kept («لا أحد» + pronoun for "his/your Nobody"); only the invalid inflection «لا أحدا» (hb 12597) is fixed. «لا أحده / لا أحدك» are the game´s coinage for "his/your Nobody" and stay | 1 row: hb 12597 |
| 100 Acre Wood | «غابة المئة فدان» 12, «الهبوط في المئة فدان» 1 | «غابة المئة فدان» | **rule 3:** glossary form; wm 18554 drops «غابة» | 1 row (1 to width check): wm 18554 (width check) |
| Canyon (Space Paranoids) | «الأخدود» 4, «الوادي» 5 | «الأخدود» | **rule 3:** the place name is «الأخدود» (sys 593, tr); «الوادي» = valley. Pride Lands rows that describe a gorge (jm 10788, 10796, 11166) are not the place and stay | 5 rows: jm 10962, 10963, 10964, 10965, 11253 |
| Wastelands | «بادية» 1, «الأراضي القاحلة» 1 | «بادية» | **rule 3:** glossary and sys place name (sys 610) | 1 row: jm 10799 |
| Optional / Support Gummi (labels) | «غامي الاختياري» 2, «غامي اختياري» 0, «غامي المساعد» 3, «غامي مساعد» 0 | «غامي اختياري» / «غامي مساعد» | **rule 1:** an indefinite first noun cannot take a definite adjective | 4 rows: gumi 6335, 14283, 15699, 16650 |
| Christmas / Christmas Town | «الميلاد» 42, «عيد الميلاد» 2, «الكريسماس» 21, «بلدة الميلاد» 12, «بلدة الكريسماس» 6, «بلدة عيد الميلاد» 1 | «الميلاد» / «بلدة الميلاد» | **rule 1, rule 3:** «الكريسماس» is the English word; «الميلاد» is the Arabic and the majority («عيد الميلاد» where «الميلاد» alone is ambiguous: the film title jm 10350, as in wm 7730) | 22 rows: jm 10350, 10876, 10880, 10882, 10884, 10894, 10895, 10896, 10898, 11211, 11213, 11220, 11223, 11407, 11409, 11837, 11839, 11855, 11857, 20161, 20163; sys 16097 |
| Gauge | «عداد» 34, «مقياس» 25 | «عداد» | **rule 3:** majority; the Drive and LIMIT gauges already say «عداد» | 38 rows: gumi 15438, 15439, 15440, 15441, 16648, 17747, 17749, 20519; hb 8070, 17624, 17625; mu 4592, 7946, 7947, 7948, 7949, 7950, 7951, 7952, 7953, 7954, 7955, 19155; sys 22007, 22008, 22010, 22013, 22015, 22016, 22017, 22040, 22045, 22053, 22054, 22061; tr 8135, 8136, 18712 |
| Auto | «تلقائي» 13, «آلي» 2 | «تلقائي» | **rule 3:** majority (Auto Valor «تلقائي: ...», Auto-Reload, gumi) | 3 rows (3 to width check): sys 14110 (width check), 17154 (width check), 17239 (width check) |
| Shop / Store | «متجر» 34, «محل» 6 | «متجر» | **rule 3:** majority and the glossary shop names | 6 rows: sys 16751, 16752, 16754; tt 13207, 13213, 14166 |
| Sunset Hill | «تل الغروب» 13, «تلة الغروب» 1 | «تل الغروب» | **rule 3:** glossary form | 1 row: tt 13460 |
| Reaction Command | «أمر التفاعل» 11, «أمر رد الفعل» 8 | «أمر التفاعل» / «أوامر التفاعل» | **rule 3:** glossary and majority; jm alone said «رد الفعل» | 19 rows: jm 11937, 11939, 11945, 11959, 11981, 11983, 12003, 12005, 12009, 12013, 12015, 12017, 12021, 12051, 12053, 12061, 14628, 20133, 20149 |
| Postern | «البوابة الخلفية» 2, «الباب الخلفي» 1 | «البوابة الخلفية» | **rule 3:** glossary (hb) and majority | 1 row (1 to width check): sys 732 (width check) |
| Journal | «يوميات» 25, «اليوميات» 4, «اليومية» 1 | «يوميات» / «اليوميات» | **rule 3:** majority; «اليومية» (singular) = "the daily" | 1 row: sys 17721 |
| The World of Nothing | «عالم العدم» 11, «عالم اللاشيء» 1 | «عالم العدم» | **rule 3:** majority | 1 row: sys 19996 |
| Station of Awakening | «محطة الاستيقاظ» 4, «محطة اليقظة» 1 | «محطة الاستيقاظ» | **rule 3:** majority (also «أحجية الاستيقاظ») | 1 row: jm 12063 |
| Hall of Empty Melodies | «قاعة اللحن الفارغ» 2, «قاعة الألحان الخالية» 1 | «قاعة اللحن الفارغ» | **rule 3, rule 4:** majority and shorter | 1 row: sys 19997 |
| Healing Light | «ضوء الشفاء» 3, «الضوء الشافي» 1 | «ضوء الشفاء» | **rule 3:** majority | 1 row: sys 15298 |
| Dark Aura | «هالة مظلمة» 2, «هالة الظلام» 1 | «هالة مظلمة» | **rule 3, rule 4:** majority and shorter | 1 row: sys 15528 |
| Reversal | «انعكاس» 4, «الانقلاب» 1 | «انعكاس» | **rule 3:** majority | 1 row: sys 20168 |
| The Great Maw | «الهاوية الكبرى» 2, «الفجوة العظيمة» 1, «الفم العظيم» 1 | «الهاوية الكبرى» | **rule 3:** glossary and sys place name | 3 rows: sys 16107; jm 10554, 10555 |
| Mountain Trail | «درب الجبل» 5, «ممر الجبل» 3 | «درب الجبل» | **rule 3:** majority | 2 rows: sys 582, 12135 |
| haunted mansion | «القصر المسكون» 4, «القصر المهجور» 3 | «القصر المسكون» | **rule 1, rule 3:** haunted = «مسكون» («مهجور» = abandoned); also the majority | 3 rows: sys 17485, 17732; tt 13500 |
| Garden of Assemblage | «حديقة التجمع» 2, «حديقة التجميع» 1 | «حديقة التجمع» | **rule 3:** majority | 1 row: sys 20400 |

### Checked: no row changed

| EN | current forms (rows) | chosen form | reason | rows changed |
|---|---|---|---|---|
| Naminé | «ناميني» 15, «نامين» 22 | «ناميني» | **already decided:** decided 2026-10-08 (PR #7, corrections/glossary_namine.csv) | 22 rows, in `corrections/glossary_namine.csv` (PR #7) |
| Twilight Town in dialogue | «بلدة الشفق» 56, «المدينة» 0 | «بلدة الشفق» | **already decided:** decided 2026-10-08: «المدينة» (the town) in dialogue is natural speech, not an error; the place name stays «بلدة الشفق» | none |
| LV / Lv. | «مستوى» 16, «مس» 35 | «مستوى» | **already decided:** «مس» only in rows wider than 130%; already decided 2026-10-03 (FIXLV, glossary line 96): a space rule, not a naming conflict | none |
| Captain | «قائد» 18, «قبطان» 6 | both, by sense | **rule 1:** every «قائد» row is a military or royal captain (Shang, Goofy), every «قبطان» row a ship captain (Jack, Barbossa): two meanings, no conflict | none |
| Heartless | «بلا قلب» 400 | «بلا قلب» | **already decided:** glossary term; awkward after «كل / المزيد من» (eh 16411, 16570, 19957) but correct; no change | none |
| Comet, Duo Raid, Red Rocket, Wildcat, Quickplay, Dark Cannon, Tiny Fairy, Balls, Shoot, Blast | «مذنب / المذنب», «غارة ثنائية / الغارة الثنائية» | sys form; the article follows the sentence | **sys rule:** sys and jm differ only by «ال» (TASKS: not a conflict) | none |
| Goddess of Fate / of Destiny | «إلهة القدر» 5 | «إلهة القدر» | **rule 3:** all 5 rows already use one form; the English varies, the Arabic does not | none |
| Zero (dog) / Zero District | «زيرو» 7, «صفر» 2 | «زيرو (the dog), صفر (the district)» | **rule 1:** two different things | none |
| Creations | «المصنوعات» 2 | «المصنوعات» | **rule 3:** both rows already use it; «المبتكرات» is not used | none |
| Retry, Hang On, Episode list, Auto-Reload ON/OFF, High Jump MAX | «أعد / إعادة», «تمسك / لا تفلت», «الحلقات» 4, «إعادة: تشغيل» 1, «قفز عال أقصى» 1 | kept | **rule 3, rule 4:** short menu labels: a matter of space or two different commands; all «X أقصى» MAX labels follow one pattern | none |
| Struggle Battle R | «معركة الصراع ر» 3 | «معركة الصراع ر» | **rule 3:** not in the glossary; added as used | none |
| power of the mystic (tt 17918) | «قوة الغامض» 1 | «قوة الغامض» | **already decided:** understandable; a wording question, not a glossary term | none |

## Proofreading rows merged into the glossary file

An id may have only one active correction. These 25 rows already had a
proofreading fix and also needed a glossary change (or their fix was itself the
glossary change). Each one is now a single row in
`corrections/glossary_decisions.csv` with both changes, and it is removed from
the proofreading file (that file´s summary says so; the round reports keep their
original counts):

- gumi_part01.csv: gumi 6259
- hb_part02.csv: hb 12597
- jm_part02.csv: jm 10898
- jm_part06.csv: jm 11855
- jm_part07.csv: jm 12061
- jm_part09.csv: jm 20163
- sys_part02.csv: sys 1122
- sys_part03.csv: sys 1603
- sys_part03.csv: sys 1605
- sys_part03.csv: sys 1607
- sys_part03.csv: sys 2619
- sys_part05.csv: sys 13116
- sys_part06.csv: sys 14613
- sys_part06.csv: sys 14909
- sys_part06.csv: sys 14939
- sys_part06.csv: sys 14957
- sys_part07.csv: sys 15005
- sys_part08.csv: sys 15584
- sys_part09.csv: sys 16036
- sys_part11.csv: sys 19428
- sys_part11.csv: sys 19471
- sys_part12.csv: sys 20398
- sys_part12.csv: sys 20400
- sys_part13.csv: sys 22035
- wm_part01.csv: wm 7711

## Changes waiting for a width check

21 rows, in `corrections/needs_width_check.csv` (not applied):

- hb 2958: «بإظ!» → «دي تي دي!» (قرار المسرد يزيد 5 أحرف والحد 2)
- sys 700: «تل ملتوي» → «التل الملتوي» (قرار المسرد يزيد 4 أحرف والحد 2)
- sys 732: «الباب الخلفي» → «البوابة الخلفية» (قرار المسرد يزيد 3 أحرف والحد 2)
- sys 743: «الرملية» → «ساحة اللعب» (قرار المسرد يزيد 3 أحرف والحد 2)
- sys 1176: «دور غوفي» → «غوفي الدوار» (قرار المسرد يزيد 3 أحرف والحد 2)
- sys 1177: «دور غوفي را» → «غوفي الدوار را» (قرار المسرد يزيد 3 أحرف والحد 2)
- sys 1178: «دور غوفي جا» → «غوفي الدوار غا» (قرار المسرد يزيد 3 أحرف والحد 2)
- sys 2637: «الرملية» → «ساحة اللعب» (قرار المسرد يزيد 3 أحرف والحد 2)
- sys 14110: «آلي» → «تلقائي» (قرار المسرد يزيد 3 أحرف والحد 2)
- sys 14625: «برمجة» → «إعادة البرمجة» (قرار المسرد يزيد 8 أحرف والحد 2)
- sys 16099: «خريطة تل ملتوي» → «خريطة التل الملتوي» (قرار المسرد يزيد 4 أحرف والحد 2)
- sys 16941: «الهرس» → «الانزلاق» (قرار المسرد يزيد 3 أحرف والحد 2)
- sys 17154: «آلي» → «تلقائي» (قرار المسرد يزيد 3 أحرف والحد 2)
- sys 17239: «الهجوم الآلي» → «الهجوم التلقائي» (قرار المسرد يزيد 3 أحرف والحد 2)
- sys 18066: «سورا: / المصاعد معطلة من إم سي بي!» → «سورا: / المصاعد معطلة من برنامج التحكم الرئيسي!» (قرار المسرد يزيد 13 أحرف والحد 3)
- tt 13292: «أسرع إلى الرملية<13 22 01 50 00><08 01 00 05>! / ستتأخر!» → «أسرع إلى ساحة اللعب<13 22 01 50 00><08 01 00 05>! / ستتأخر!» (قرار المسرد يزيد 3 أحرف والحد 2)
- tt 13641: «س-مساعدة! الرملية! سايفر!» → «س-مساعدة! ساحة اللعب! سايفر!» (قرار المسرد يزيد 3 أحرف والحد 2)
- tt 17297: «الرملية ⇾ ارتفاعات المحطة  ⇽» → «ساحة اللعب ⇾ ارتفاعات المحطة  ⇽» (قرار المسرد يزيد 3 أحرف والحد 2)
- tt 17304: «ارتفاعات المحطة ⇾ الرملية ⇽» → «ارتفاعات المحطة ⇾ ساحة اللعب ⇽» (قرار المسرد يزيد 3 أحرف والحد 2)
- tt 17359: «الرملية ⇾ ساحة الترام ⇽» → «ساحة اللعب ⇾ ساحة الترام ⇽» (قرار المسرد يزيد 3 أحرف والحد 2)
- wm 18554: «الهبوط في المئة فدان» → «الهبوط في غابة المئة فدان» (قرار المسرد يزيد 5 أحرف والحد 2)

## Notes on the Naminé rows

- The search covers all 75 review files: whole word «نامين» with an optional
  attached و ف ب ل ك. Only tt (19 rows), sys (2) and di (1) use the old form;
  every other bar already uses «ناميني» (15 rows) or does not name her.
- An id may have only one active correction (checked by the validator). Two
  Naminé rows also had a tt proofreading fix: tt 12316 («بما يحل» → «مما يحل»)
  and tt 13289 («نضيق من الوقت» → «الوقت ينفد»). Both fixes are combined into
  the one row in `glossary_namine.csv` and removed from `tt_part01.csv` and
  `tt_part02.csv`.
- `corrections/glossary_namine.csv` passes `python tools/validate_corrections.py`
  (glossary files skip the glossary-term check; the length rule still applies and
  every row is within it).
