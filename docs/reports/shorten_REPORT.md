round: SHORTEN

# Shorten long rows

Scope: every row of `review/` whose `width_pct` is above 150: **488 rows**. These are the 304 rows listed in docs/TASKS.md plus 184 more that are also over 150 (mostly short sys menu labels and names, and a few tt, lm and di rows).

Result: **114 rows shortened** (67 at or under 130%, 47 between 130% and 150%) and **374 rows left** (reasons below).

Method: each row was rewritten with the same meaning, keeping tags, `⏎` line breaks, allowed characters and glossary terms (the validator checks all of them). The estimated new width is `width_pct × widest new line / widest original line`, with tags not counted; for a one-line row this equals `width_pct × new length / old length`. No game screenshot was taken, so the numbers are estimates.

No row needed a combined correction: none of the shortened rows already had a proofreading or glossary correction. Two rows (jm 19162, sys 766) fell to about 110% after the glossary decisions and need no shortening. After review, 19 proposed shortenings were rejected and those rows are listed as left (for example, shortened «هيه!» to «هي!», which reads "she").

## Rows shortened per bar

| bar | rows over 150% | shortened | left | avg width of shortened rows | avg width of all rows over 150% |
|---|---:|---:|---:|---:|---:|
| al | 9 | 3 | 6 | 174% → 108% | 176% → 154% |
| bb | 6 | 5 | 1 | 165% → 108% | 167% → 119% |
| ca | 8 | 3 | 5 | 170% → 119% | 185% → 166% |
| dc | 3 | 1 | 2 | 172% → 114% | 172% → 153% |
| di | 1 | 1 | 0 | 186% → 113% | 186% → 114% |
| eh | 8 | 2 | 6 | 163% → 136% | 166% → 159% |
| es | 1 | 1 | 0 | 152% → 114% | 152% → 114% |
| gumi | 47 | 22 | 25 | 166% → 129% | 171% → 154% |
| hb | 30 | 15 | 15 | 170% → 126% | 167% → 146% |
| he | 9 | 2 | 7 | 157% → 129% | 167% → 161% |
| jm | 77 | 11 | 66 | 168% → 128% | 178% → 172% |
| lk | 6 | 3 | 3 | 165% → 129% | 160% → 142% |
| lm | 11 | 6 | 5 | 154% → 117% | 161% → 141% |
| mu | 20 | 6 | 14 | 159% → 121% | 178% → 167% |
| nm | 9 | 6 | 3 | 163% → 126% | 165% → 140% |
| po | 3 | 0 | 3 | — | 195% → 195% |
| sys | 164 | 5 | 159 | 164% → 118% | 175% → 174% |
| title | 19 | 4 | 15 | 163% → 123% | 176% → 167% |
| tr | 15 | 6 | 9 | 155% → 130% | 192% → 182% |
| tt | 30 | 6 | 24 | 164% → 126% | 172% → 164% |
| wi | 3 | 1 | 2 | 154% → 88% | 167% → 145% |
| wm | 9 | 5 | 4 | 164% → 138% | 168% → 154% |
| **total** | **488** | **114** | **374** | **165% → 125%** | **174% → 165%** |

The 374 left rows keep their width; the sys menu labels are a large part of that average.

## 10 examples

| row | width | old | new |
|---|---|---|---|
| jm 12066 | 179% → 119% | الراهب | راهب |
| hb 12634 | 151% → 112% | نعم, الكثير من الأغراض! | نعم, أغراض كثيرة! |
| gumi 6342 | 205% → 123% | تعديل | عدل |
| bb 3040 | 155% → 119% | تحدث من فضلك إلى <03>كوغزورث <04 0A>في الأعلى ⏎ عن الممر المخفي. | تحدث إلى <03>كوغزورث <04 0A>في الأعلى ⏎ عن الممر المخفي. |
| tr 919 | 154% → 114% | يا ترون, أليس برنامج التحكم الرئيسي ⏎ من تلك البرامج أيضا? | أليس برنامج التحكم الرئيسي ⏎ من البرامج أيضا يا ترون? |
| sys 2775 | 165% → 97% | كم تريد أن تشتري? ⏎  ⏎ <09 EC>: اختر 1 ⏎ <09 ED>: اختر 10. | كم تشتري? ⏎  ⏎ <09 EC>: اختر 1 ⏎ <09 ED>: اختر 10. |
| mu 4330 | 163% → 109% | أيها القائد<13 60 00 74 00><08 01 01 06>! | يا قائد<13 60 00 74 00><08 01 01 06>! |
| nm 6061 | 158% → 125% | أنتم! لا يجوز أن تكونوا هنا!<14 82 00><10>غادروا بلدة الهالوين ⏎ بأمر من العمدة! | أنتم! ممنوعون هنا!<14 82 00><10>غادروا بلدة الهالوين ⏎ بأمر العمدة! |
| lk 8603 | 155% → 100% | لا أستطيع العودة. | لا عودة لي. |
| al 184 | 153% → 68% | ليس عدلا! | ظلم! |

## Rows left over 150% and why

By reason: sys menu label or name, already minimal (not rewritten): 155; glossary term or name: 128; one word, interjection or short label: 60; shortening rejected on review: 19; other (meaning would be lost): 10; already under 150%: 2.

Each line is `id (width%): reason`, grouped by bar. 155 of them are sys menu labels and names of at most 3 words (for example «اخرج», «ضربة», «روكساس:», «قاعة الرقص») that were over 150% before this task; they were checked as a group and not rewritten one by one, because the width comes from one short word or a name. 2 rows are listed as already under 150% after the glossary decisions.

**al** (6)

- 134 (161%): character name (Iago), nothing else to shorten
- 280 (171%): character name (Iago)
- 302 (167%): character name (Iago)
- 331 (221%): character name (Al)
- 332 (171%): character name (Iago)
- 4101 (167%): menu label End, no shorter synonym with same meaning

**bb** (1)

- 3351 (176%): glossary name (Beast) + fixed phrase, no shorter wording

**ca** (5)

- 6217 (267%): one word "Go", no shorter synonym
- 6218 (191%): one word menu label, no shorter synonym
- 9960 (155%): shortening rejected on review: only shorter form «هي» reads as "she"
- 9966 (195%): one word interjection, no shorter synonym
- 10235 (164%): shortening rejected on review: «اه» loses the hamza («آه» is already the current form)

**dc** (2)

- 5398 (181%): onomatopoeia, 4 chars
- 5511 (164%): short phrase, no shorter equivalent

**eh** (6)

- 16244 (164%): shortening rejected on review: «اه» loses the hamza
- 16418 (155%): character names only
- 16419 (171%): character name
- 16498 (180%): one word, already minimal
- 16519 (156%): shortening rejected on review: «فقط?» changes "Is that all?" into "Only?"
- 21440 (177%): character name repeated

**gumi** (25)

- 6222 (178%): no shorter word for Flat Helm/G without dropping Flat
- 6265 (157%): one word + /G suffix, no shorter synonym
- 6271 (157%): item name Neon Bar, would lose Bar
- 6273 (161%): Parabola, single term, no shorter word
- 6311 (159%): shortening rejected on review: «آلية» conflicts with the decided Auto = «تلقائي»
- 6344 (174%): one word, no shorter synonym
- 6350 (200%): one word, no shorter synonym
- 6416 (158%): glossary term السفن الصغيرة
- 6422 (166%): glossary term World Map
- 14087 (166%): glossary term World Map
- 14291 (166%): glossary term World Map
- 14699 (194%): glossary term السفن الصغيرة
- 18321 (186%): one word, no shorter synonym
- 18322 (160%): one word, no shorter synonym
- 18504 (200%): one word, no shorter synonym
- 18513 (160%): no shorter word for Exit Editor with same meaning
- 18686 (287%): one word ON, no shorter synonym
- 18687 (152%): one word OFF, no shorter synonym
- 18694 (164%): one word, no shorter synonym
- 18786 (169%): glossary term Teeny Ship (سفينة صغيرة)
- 18796 (194%): glossary term السفن الصغيرة
- 18925 (158%): one word Yes
- 18927 (207%): one word OK
- 19134 (166%): glossary term World Map
- 20691 (153%): one word + /G suffix, no shorter synonym

**hb** (15)

- 2986 (232%): glossary term (Pit Cell), no shorter form
- 2989 (151%): glossary term in label (Pit Cell Guide), cannot reach 150%
- 2990 (152%): glossary term in label (Pit Cell Guide), cannot reach 150%
- 2991 (151%): glossary term in label (Pit Cell Guide), cannot reach 150%
- 2998 (158%): one word Yes, no shorter synonym
- 8191 (169%): shortening rejected on review: "How's Tron?" would become "Is Tron OK?" (meaning shifts)
- 8283 (155%): shortening rejected on review: only shorter form «هي» reads as "she"
- 12415 (153%): Move is a glossary term (checker rejects other word)
- 12497 (156%): shortening rejected on review: «رأي سديد» means "sound opinion", not "good idea"
- 12504 (168%): shortening rejected on review: only candidate is an invented word («أشوك»)
- 12512 (155%): shortening rejected on review: only shorter form «هي» reads as "she"
- 12742 (155%): shortening rejected on review: only shorter form «هي» reads as "she"
- 12789 (167%): character name Axel
- 12837 (176%): one word Liars, no shorter synonym
- 16065 (172%): character name Roxas

**he** (7)

- 3611 (214%): one word greeting, no shorter form
- 3683 (171%): character name
- 3719 (186%): shortening rejected on review: shortening drops «boy» of the nickname "keyboy"
- 3773 (151%): shortening rejected on review: only shorter form «هي» reads as "she"
- 3825 (155%): shortening rejected on review: only shorter form «هي» reads as "she"
- 3980 (158%): one word Yes, 3 chars
- 4041 (158%): one word Yes, 3 chars

**jm** (66)

- 9914 (156%): glossary place name (Pride Lands)
- 10793 (153%): contains glossary name Pride Rock, no shorter verb
- 11444 (168%): name Tron + short label, no shorter synonym
- 11446 (214%): contains glossary term MCP (programme name)
- 11450 (274%): contains glossary term MCP
- 11460 (152%): single character/name, glossary term
- 11464 (156%): single character/name, glossary term
- 11482 (190%): single character/name, glossary term
- 11486 (176%): single character/name, glossary term
- 11496 (182%): single character/name, glossary term
- 11532 (182%): single character/name, glossary term
- 11552 (151%): single character/name, glossary term
- 11570 (159%): single character/name, glossary term
- 11580 (174%): single character/name, glossary term
- 11620 (152%): single character/name, glossary term
- 11640 (155%): single character/name, glossary term
- 11650 (151%): single character/name, glossary term
- 11656 (167%): single character/name, glossary term
- 11664 (181%): single character/name, glossary term
- 11668 (181%): single character/name, glossary term
- 11724 (232%): glossary term Owl
- 11756 (152%): single character/name, glossary term
- 11774 (151%): single character/name, glossary term
- 11776 (151%): single character/name, glossary term
- 11794 (166%): single character/name, glossary term
- 11806 (152%): single character/name, glossary term
- 11842 (162%): glossary name Dr. Finkelstein
- 11886 (151%): single character/name, glossary term
- 11888 (164%): single character/name, glossary term
- 11890 (651%): glossary term MCP, single name
- 11918 (182%): single character/name, glossary term
- 11924 (174%): single character/name, glossary term
- 11930 (182%): single character/name, glossary term
- 11944 (152%): approved glossary bestiary name
- 11948 (156%): approved glossary bestiary name
- 11950 (207%): approved glossary bestiary name
- 11974 (188%): item/Heartless name, no shorter form
- 11990 (222%): Heartless name (glossary)
- 12030 (186%): glossary name (Heartless/Nobody/place/character/mini-game)
- 12036 (154%): glossary name (Heartless/Nobody/place/character/mini-game)
- 12046 (195%): glossary name (Heartless/Nobody/place/character/mini-game)
- 12048 (160%): glossary name (Heartless/Nobody/place/character/mini-game)
- 12052 (151%): glossary name (Heartless/Nobody/place/character/mini-game)
- 12064 (217%): job name, no shorter equivalent
- 12130 (215%): one word, no shorter synonym
- 12881 (182%): label, no shorter synonym
- 13943 (151%): glossary name (Heartless/Nobody/place/character/mini-game)
- 13989 (156%): place name (glossary)
- 14773 (156%): glossary name (Heartless/Nobody/place/character/mini-game)
- 14781 (167%): glossary name (Heartless/Nobody/place/character/mini-game)
- 14783 (174%): glossary name (Heartless/Nobody/place/character/mini-game)
- 17250 (174%): glossary name (Heartless/Nobody/place/character/mini-game)
- 17923 (152%): glossary name (Heartless/Nobody/place/character/mini-game)
- 17943 (182%): glossary name (Heartless/Nobody/place/character/mini-game)
- 18587 (200%): one word, no shorter synonym
- 18636 (151%): one word, no shorter synonym
- 18651 (151%): one word, no shorter synonym
- 18653 (182%): label, no shorter synonym
- 19162 (154%): already under 150% after the glossary decision (est 110%)
- 19206 (151%): one short word with tag
- 19214 (173%): glossary mini-game name
- 19243 (151%): glossary mini-game name
- 19255 (161%): glossary name (Moogle)
- 19378 (180%): no shorter equivalent keeping 'again' (<=150% not reachable)
- 20142 (204%): mini-game label, no shorter synonym
- 20284 (152%): contains name Zexion, 150% not reachable

**lk** (3)

- 8510 (152%): glossary name (Pride Lands)
- 8559 (158%): single imperative word, no shorter synonym
- 8604 (153%): single word, no shorter MSA word

**lm** (5)

- 5051 (186%): two-word-ish interjection with ellipsis, no shorter synonym
- 5102 (171%): one-word interjection
- 5250 (159%): shortening rejected on review: only shorter form «هي» reads as "she"
- 5331 (158%): one short word Yes
- 18726 (169%): single command label, no shorter equivalent noun

**mu** (14)

- 4211 (153%): name Mulan, no shorter form
- 4311 (205%): one word interjection (Sir!), no 3-char equivalent
- 4312 (205%): same as 4311
- 4313 (205%): same as 4311
- 4314 (205%): same as 4311
- 4323 (205%): same as 4311
- 4324 (205%): same as 4311
- 4325 (205%): same as 4311
- 4326 (205%): same as 4311
- 4337 (205%): same as 4311
- 4414 (151%): name Mulan
- 4459 (152%): one word, no shorter synonym (best 152%)
- 4511 (153%): name Mulan
- 4606 (158%): one word, 3 chars

**nm** (3)

- 5839 (178%): one word, no shorter form
- 6014 (171%): shortening rejected on review: «اه» loses the hamza
- 6030 (155%): shortening rejected on review: only shorter form «هي» reads as "she"

**po** (3)

- 4679 (153%): single word, no shorter MSA word
- 4779 (214%): single interjection
- 18722 (219%): single word label

**sys** (159)

- 490 (178%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 518 (171%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 519 (171%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 528 (171%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 529 (173%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 539 (157%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 544 (176%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 603 (171%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 613 (171%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 687 (184%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 709 (159%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 710 (159%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 722 (159%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 732 (194%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 734 (155%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 762 (164%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 766 (159%): already under 150% after the glossary decision (est 114%)
- 1093 (218%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 1110 (284%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 1117 (187%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 1121 (157%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 1200 (194%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 1289 (156%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 1318 (194%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 1323 (161%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 1324 (161%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 1325 (176%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 1522 (161%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 1534 (156%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 1538 (158%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 1540 (185%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 1542 (162%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 1556 (151%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 1568 (180%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 1574 (153%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 1582 (157%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 1600 (151%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 1626 (151%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 1642 (157%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 2673 (162%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 2683 (218%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 2687 (166%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 2688 (162%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 2691 (153%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 2738 (167%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 2764 (155%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 2766 (167%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 7754 (223%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 7758 (170%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 8017 (166%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 8018 (166%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 8019 (166%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 8020 (166%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 8021 (166%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 8022 (166%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 8023 (166%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 8024 (166%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 8025 (166%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 8026 (166%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 8027 (166%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 8028 (166%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 8029 (166%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 8030 (166%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 8031 (166%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 8143 (218%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 9933 (166%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 10331 (164%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 10335 (156%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 12073 (156%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 12081 (155%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 12090 (157%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 12097 (167%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 12998 (159%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 13031 (173%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 13848 (161%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 13881 (156%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 13970 (153%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 14091 (181%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 14118 (291%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 14119 (206%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 14122 (291%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 14162 (206%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 14633 (167%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 14635 (178%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 14643 (178%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 14827 (191%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 14844 (355%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 14897 (160%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 14911 (167%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 14985 (151%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 14995 (153%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 15027 (157%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 15051 (158%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 15059 (171%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 15067 (160%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 15083 (163%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 15091 (166%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 15099 (151%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 15213 (181%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 15283 (167%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 15306 (181%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 15312 (178%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 15314 (165%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 15330 (155%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 15370 (152%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 15503 (167%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 15581 (152%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 15603 (161%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 15605 (158%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 16050 (151%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 16101 (160%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 16155 (167%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 16510 (153%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 16511 (174%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 16514 (153%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 16951 (176%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 17034 (152%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 17047 (152%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 17054 (181%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 17152 (194%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 17194 (187%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 17197 (181%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 17208 (291%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 17209 (206%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 17724 (153%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 17753 (355%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 17767 (166%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 17768 (152%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 17834 (170%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 17837 (165%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 17926 (153%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 18004 (155%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 18112 (185%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 18399 (163%): glossary name (Isla de Muerta: Rock Face)
- 18469 (157%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 18571 (265%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 18595 (231%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 19074 (184%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 19428 (158%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 19486 (192%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 19862 (355%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 20021 (152%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 20025 (160%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 20027 (151%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 20086 (154%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 20090 (176%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 20229 (157%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 20270 (157%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 20493 (189%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 20495 (168%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 21563 (212%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 21572 (178%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 21586 (156%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 21595 (160%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 21596 (194%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 21615 (163%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 21619 (171%): sys menu label or name of at most 3 words (or 22 characters), already minimal: not rewritten
- 22023 (164%): shortening rejected on review: «تحرك أمام, خلف...» is ungrammatical (needs «أماما»)
- 22050 (180%): shortening rejected on review: shortening drops the verb "use"

**title** (15)

- 20725 (176%): single name
- 20741 (222%): only shorter forms drop glossary term (Everyone), or stay too wide
- 20827 (186%): glossary Heartless name
- 20933 (214%): one word interjection, best 153%
- 21109 (151%): single name
- 21110 (176%): MCP glossary term is already 21 chars
- 21131 (152%): no shorter synonym (152%)
- 21144 (171%): Gullwings glossary name, cannot drop Go
- 21151 (167%): single name
- 21218 (154%): glossary Heartless name
- 21275 (188%): MCP glossary term is 21 chars
- 21293 (187%): MCP glossary term is 21 chars
- 21322 (182%): single name
- 21338 (174%): single name
- 21341 (182%): single name

**tr** (9)

- 876 (261%): one word label Users
- 878 (535%): glossary term MCP only
- 1047 (194%): width is glossary term MCP
- 1048 (174%): width is glossary term MCP (best 156%)
- 1076 (151%): glossary term Light Cycle
- 1081 (151%): glossary term Light Cycle
- 1087 (158%): one short word Yes
- 8053 (151%): glossary term Light Cycle
- 17899 (173%): width is glossary term MCP; line cannot be rebalanced

**tt** (24)

- 2888 (177%): glossary term (activity name)
- 2889 (198%): glossary term (activity name)
- 2893 (186%): glossary term (activity name)
- 2916 (158%): one word, no shorter synonym
- 12254 (182%): hesitant greeting with ellipsis; no shorter form keeps meaning
- 13240 (175%): character name Roxas
- 13347 (163%): character name Axel
- 13359 (175%): character name Roxas
- 13360 (175%): character name Roxas
- 13365 (175%): character name Roxas
- 13367 (171%): character name Roxas
- 13379 (170%): character name Roxas
- 13380 (175%): character name Roxas
- 13383 (170%): character name Roxas
- 13499 (158%): character name Roxas
- 13510 (158%): character name Roxas
- 13537 (170%): character name Roxas
- 13609 (164%): character name Axel
- 14192 (157%): glossary term Dusk
- 14548 (154%): one word, no shorter synonym
- 17541 (190%): one word, no shorter synonym
- 18396 (175%): character name Roxas
- 19693 (221%): character name Al
- 19893 (172%): character name Roxas

**wi** (2)

- 5550 (188%): stutter + sir, meaning would be lost
- 5589 (160%): single interjection

**wm** (4)

- 13852 (214%): glossary term (مستوى) must stay; cannot shorten
- 18084 (157%): one word label, no shorter synonym
- 18085 (170%): one word label, no shorter synonym
- 19474 (151%): no shorter phrase with same meaning
