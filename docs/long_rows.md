# long_rows - rows over 150% of the English width (deferred, kept in the build)

batchF (tt.bar) new rows >150% by real metric, plus 1 sys row from sysB21. Most are 1-2 word interjections where the pixel gap is tiny; shorten only if the screenshot shows a problem.

| id | % | EN | AR now | shorter option |
|---|---|---|---|---|
| 13799 | 152 | Do ya have any idea what\nthe password might be? | هل لديك فكرة عما قد تكون\nكلمة السر? | هل تعرف كلمة السر? |
| 13826 | 153 | Why? | لماذا? | ليش? |
| 14219 | 157 | "Updating job information!\nPlease come back later." | يجري تحديث معلومات المهمة!\nيرجى العودة لاحقا. | جار تحديث المهام!\nعد لاحقا. |
| 14220 | 157 | "Updating job information!\nPlease come back later." | يجري تحديث معلومات المهمة!\nيرجى العودة لاحقا. | جار تحديث المهام!\nعد لاحقا. |
| 14311 | 152 | Yep. | أجل. | نعم. |
| 14342 | 200 | Later! | إلى اللقاء! | وداعا! |
| 14356 | 152 | Yep. | أجل. | نعم. |
| 14364 | 156 | To...where again? | إلى... أين مرة أخرى? | إلى أين? |
| 14366 | 153 | Oh yeah. | آه صحيح. | صحيح. |
| 14387 | 210 | Bye! | وداعا! | وداعا! |
| 14408 | 172 | Man, what a jerk. | يا رجل, يا له من أحمق. | يا له من أحمق. |
| 14453 | 171 | Says who? | من قال هذا? | من? |
| 15303 (sys, sysB21) | 175 | <X 53>Total | <X 53>الإجمالي | <X 53>المجموع |

Skipped ids (not translated): tt 13845, 14318, 14377, 14409, 14470, 14510 (interior 0x00 - dump cannot read them), 14185 and 14192 (start with the symbol cells). sys 1444, 1445, 1446-1449, 14091, 15501 (dev text / long command lists / per-letter colour tags) left for a decision.

## batchG (2026-10-01) - new rows >150% (real metric), kept in the build

| id | % | EN | AR now | shorter option |
|---|---|---|---|---|
| 14192 | 157 | ₓₓDusk | ₓₓالداسك | ₓₓداسك |
| 14516 | 151 | Nobodies...<C 14 41 00><C 10><C 14 32 00>They don´t exist... | اللا أحد...<C 14 41 00><C 10><C 14 32 00>إنهم غير موجودين... | اللا أحد...<C 14 41 00><C 10><C 14 32 00>لا وجود لهم... |
| 14548 | 154 | Blue! | أزرق! | زرقاء! |
| 16473 | 211 | Yo, Roxas. | مرحبا يا روكساس. | يا روكساس. |
| 17384 | 151 | This is the pod Sora was sleeping in. | هذه هي الكبسولة التي كان سورا نائما فيها. | هذه كبسولة سورا. |
| 17421 | 154 | Where could that cat be? It´d be funny\nif it was somewhere real close. | أين يمكن أن تكون تلك القطة? سيكون مضحكا\nلو كانت قريبة جدا. | أين القطة? سيكون مضحكا لو كانت قريبة. |
| 17441 | 163 | Oh, hello, Roxas. | آه, مرحبا يا روكساس. | آه, يا روكساس. |

Not translated in batchG: tt empty messages (00 00, nothing to translate): 13845, 14318, 14377, 14409, 14470, 14510 (the earlier 'interior 0x00' error was only the dump tool; fixed, now reports #EMPTY). Ids 14185/14192 (symbol prefix) are now translated.

## batchH (2026-10-01) - new rows >150% (real metric), kept in the build

| id | % | EN | AR now |
|---|---|---|---|
| 17541 | 190 | Lucky. | محظوظ. |
| 17553 | 157 | Listen to the rules?\n<C 15 33 00>Not right now.\n<C 15 09 00>I´d better listen. | هل تستمع إلى القواعد?\n<C 15 33 00>ليس الآن.\n<C 15 09 00>الأفضل أن أستمع. |
| 17611 | 162 | Fool. | أحمق. |
| 17964 | 158 | Upset. | منزعج. |
| 18396 | 175 | Roxas! | روكساس! |
| 18514 | 211 | Yikes! | يا للهول! |
| 19686 | 154 | So...this is the key. | إذن... هذا هو المفتاح. |
| 19693 | 221 | Al! | علاء! |
| 19710 | 220 | All for one and one for all. | الجميع من أجل واحد وواحد من أجل الجميع. |
| 19890 | 151 | You seek answers. | أنت تبحث عن إجابات. |
| 19893 | 172 | Roxas. | روكساس. |
| 19895 | 158 | Guess that's that. | أظن أن هذا كل شيء. |
| 19904 | 229 | Go. | اذهب. |
| 19916 | 165 | I dunno.<C 14 A9 00><C 10>I can't...just look inside. | لا أدري.<C 14 A9 00><C 10>لا أستطيع... أن أنظر في داخلي. |
| 19922 | 161 | Man, I miss the old times.\nStill got it memorized?<C 14 E3 00><C 10>The day we met, when you got your\nnew name, you and I sat right here<C 14 2B 01><C 10>and watched the sun set. | يا رجل, أشتاق إلى الأيام القديمة.\nهل ما زلت تحفظها?<C 14 E3 00><C 10>في اليوم الذي التقينا فيه, عندما حصلت على\nاسمك الجديد, جلسنا هنا أنا وأنت<C 14 2B 01><C 10>وشاهدنا الشمس تغرب. |

Also: sysB22 new rows >150%: 16480 (159), 19421 (213, "مساعدة"); di.bar: 16816 (191). Recap screens 21373-21630 and the Struggle/tutorial rows have many lines >130%; check on screen (line overflow) before the next batch.

## batchI (2026-10-01) - new rows >150% (real metric), kept in the build

Mostly 1-3 word replies where the pixel gap is small.

| id | % | EN | AR now |
|---|---|---|---|
| 2891 | 173 | Poster Duty | مهمة الملصقات |
| 2916 | 158 | Yes | نعم |
| 2919 | 170 | Choose this Job? | هل تختار هذا العمل? |
| 12151 | 152 | So, how about this? | إذن, ما رأيكم في هذا? |
| 12163 | 169 | Go get ´em! | اذهبا وأرياهم! |
| 12171 | 159 | Pretzels, of course!\nWhat else is there? | البسكويت المملح بالطبع!\nماذا غيره? |
| 12174 | 206 | Pretzels it is. | إذن البسكويت المملح. |
| 12185 | 180 | All present and\naccounted for? | هل الجميع حاضرون\nومعهم الحصيلة? |
| 12190 | 180 | All present and\naccounted for? | هل الجميع حاضرون\nومعهم الحصيلة? |
| 12196 | 180 | All present and\naccounted for? | هل الجميع حاضرون\nومعهم الحصيلة? |
| 12223 | 155 | Guy? | رجل? |
| 12250 | 210 | Hey. | مرحبا. |
| 12251 | 170 | Morning. | صباح الخير. |
| 12253 | 174 | Hello, Roxas. | مرحبا يا روكساس. |
| 12254 | 227 | Hi... | مرحبا... |
| 12272 | 175 | Not good... | هذا ليس جيدا... |
| 12282 | 214 | How´s this? | ما رأيكم في هذه? |
| 12309 | 169 | Go get ´em! | اذهبا وأرياهم! |

Not translated: tt 17913 (a single space). Nothing else in tt.bar is left untranslated except the 25 empty messages.

## 2026-10-01 worlds + sysB23 - rows >150% (real metric for worlds; retail table for sysB23), kept in the builds

### es.bar
| id | % | EN | AR now |
|---|---|---|---|
| 16188 | 152 | Yep. | أجل. |
| 16205 | 156 | Like...wanting to be like you. | مثل... أن أرغب في أن أكون مثلك. |

### dc.bar
| id | % | EN | AR now |
|---|---|---|---|
| 5377 | 190 | Must be nice to be home, huh? | لا بد أنه لطيف أن تعود إلى البيت, أليس كذلك? |
| 5397 | 156 | I know I can count on you, Sora.<C 14 78 00><C 10><C 14 28 00><C 10>Now, there´s something I´d like\nall of you to come and see.<C 14 DC 00><C 10><C 14 1E 00><C 10>Would you please escort me to the\naudience chamber? | أعلم أنني أستطيع الاعتماد عليك يا سورا.<C 14 78 00><C 10><C 14 28 00><C 10>والآن, هناك شيء أريد\nأن تروه جميعا.<C 14 DC 00><C 10><C 14 1E 00><C 10>هلا رافقتموني إلى\nقاعة الاستقبال? |
| 5398 | 181 | Hut! | هوت! |
| 5419 | 154 | I got ´em. | أمسكت بهم. |
| 5443 | 256 | What a hag. | يا لها من عجوز شمطاء. |
| 5446 | 175 | Ohhh! | أوووه! |
| 5458 | 158 | Mm-hmm...<C 14 42 00><C 10>interesting... | همم...<C 14 42 00><C 10>مثير للاهتمام... |
| 5500 | 169 | Going somewhere? | هل ستذهب إلى مكان? |
| 5511 | 164 | I will! | سأفعل! |
| 7973 | 151 | The King is out there\nsomewhere, doing all he can.<C 10>I´ll do my best, too, but most of\nall, we need your help! | الملك هناك في مكان ما\nيبذل كل ما بوسعه.<C 10>سأبذل جهدي أنا أيضا, لكننا\nنحتاج إلى مساعدتكم أكثر من أي شيء! |
| 16977 | 153 | Could this be the King? | أيمكن أن يكون هذا الملك? |

### wm.bar
| id | % | EN | AR now |
|---|---|---|---|
| 7684 | 159 | Old Friends | أصدقاء قدامى |
| 7722 | 186 | The greatest musical ever! | أعظم مسرحية موسيقية على الإطلاق! |
| 13852 | 234 | Level up! | ارتفع المستوى! |
| 18083 | 183 | Dash | اندفاع |
| 18084 | 184 | Warp | التحول |
| 18085 | 170 | Land | هبوط |
| 18545 | 271 | Land in ZZ | الهبوط في عالم تجريبي |
| 18554 | 151 | Land in 100 Acre Wood | الهبوط في غابة المئة فدان |
| 18555 | 162 | Land in Pride Lands | الهبوط في أراضي الكبرياء |
| 18560 | 267 | Land in FA | الهبوط في عالم تجريبي |
| 18561 | 155 | Land in Port Royal | الهبوط في ميناء رويال |
| 18817 | 151 | Only one? | واحد فقط? |
| 19382 | 160 | Uh-oh. Looks like a no go. | أوه أوه. يبدو أن الأمر مستحيل. |
| 19473 | 154 | Episode list | قائمة الحلقات |
| 19474 | 151 | Past events | أحداث سابقة |
| 19478 | 154 | Episode list | قائمة الحلقات |
| 19523 | 192 | HB Scenario 3 | سيناريو حصن هولو 3 |

### sysB23
14091 (181), 22019 (155), 22050 (180).

sysB23 not translated (27 ids, on purpose): empty/command-only messages 1108, 1149-1152, 2561, 2562, 15552, 15553, 15563-15566; dev/debug text 1444-1449 (command lists, TEST444, symbol tests), fragments that depend on the text printed next to them 17838, 17839, 19352-19354, 19600; dev markers 19388, 19998. dc.bar 18407 'NOT IN GAME' and wm.bar 13854 (symbol cell + number) left as is.

## 2026-10-01 wi / tr / po - rows >150% (real metric), kept in the builds

### wi.bar
| id | % | EN | AR now |
|---|---|---|---|
| 5525 | 228 | Déjà vu? | شعور بالتكرار? |
| 5536 | 184 | Not so fast! | ليس بهذه السرعة! |
| 5550 | 216 | Y-yes sir! | ن-نعم يا سيدي! |
| 5553 | 156 | Aw, that would\nbe too easy. | آه, هذا كان\nسيكون سهلا جدا. |
| 5557 | 151 | Oh, yeah! | آه, صحيح! |
| 5564 | 228 | Déjà vu? | شعور بالتكرار? |
| 5573 | 152 | Then what´ll we do? | وماذا سنفعل بعد ذلك? |
| 5589 | 160 | Hey! | مهلا! |
| 5623 | 171 | Hey, look! | مهلا, انظروا! |
| 5658 | 179 | Somebody sure\nwas angry. | من الواضح أن أحدا\nكان غاضبا. |
| 5690 | 176 | Look! | انظروا! |
| 5693 | 154 | Bad, bad, bad! | سيء, سيء, سيء! |
| 5694 | 159 | Oh, no! | يا للهول! |
| 5703 | 163 | Waaaait! | انتظروووا! |

### tr.bar
| id | % | EN | AR now |
|---|---|---|---|
| 850 | 178 | Users are amazing!\nI´ve never seen a program like this!<C 10>Now that I can use the solar sailer,\nI can access the MCP! | المستخدمون مذهلون!\nلم أر برنامجا كهذا من قبل!<C 10>الآن وقد صرت أستطيع استخدام المركب الشمسي,\nأستطيع الوصول إلى برنامج التحكم الرئيسي! |
| 876 | 261 | Users? | مستخدمون? |
| 877 | 157 | You´d better get out of here quickly.<C 14 5A 00><C 10><C 14 27 00><C 10>Who knows what the MCP will do to you? | الأفضل أن تخرجوا من هنا بسرعة.<C 14 5A 00><C 10><C 14 27 00><C 10>من يدري ماذا سيفعل بكم برنامج التحكم الرئيسي? |
| 878 | 535 | MCP? | برنامج التحكم الرئيسي? |
| 884 | 181 | But the MCP cut the power\n50 microcycles ago. | لكن برنامج التحكم الرئيسي قطع الطاقة\nقبل 50 دورة مجهرية. |
| 908 | 171 | Roger! | مفهوم! |
| 913 | 179 | DTD is the name my User gave\nto the dataspace.<C 14 D2 00><C 10>Copies of all the original system\nprograms are stored there,<C 14 CD 00><C 10>along with anything that´s\nsensitive or restricted. | دي تي دي هو الاسم الذي أعطاه مستخدمي\nلمساحة البيانات.<C 14 D2 00><C 10>نسخ من كل برامج النظام الأصلية\nمخزنة هناك,<C 14 CD 00><C 10>مع كل ما هو\nحساس أو محظور. |
| 917 | 152 | If I can get inside the DTD, I can access\nmy original backup program<C 14 EA 00><C 10>and restore all my functions. | إن استطعت دخول دي تي دي, أستطيع الوصول\nإلى برنامجي الاحتياطي الأصلي<C 14 EA 00><C 10>واستعادة كل وظائفي. |
| 919 | 169 | Gee, Tron, ain´t the MCP one\nof those programs, too? | يا ترون, ألا يعد برنامج التحكم الرئيسي\nواحدا من تلك البرامج أيضا? |
| 926 | 157 | Looks like the MCP´s on to us. | يبدو أن برنامج التحكم الرئيسي كشفنا. |
| 993 | 154 | You have the ability to take\nillogical routes<C 14 AA 00><C 10>and still arrive at the answers you seek. | لديكم القدرة على سلوك\nمسارات غير منطقية<C 14 AA 00><C 10>ومع ذلك الوصول إلى الإجابات التي تبحثون عنها. |
| 996 | 151 | I changed the password,<C 14 48 00><C 10>so you won´t have to worry\nabout the MCP for a while. | غيرت كلمة السر,<C 14 48 00><C 10>فلن تضطروا للقلق\nمن برنامج التحكم الرئيسي لفترة. |
| 998 | 164 | I knew you´d ask. | عرفت أنكم ستسألون. |
| 1013 | 174 | The MCP is ready to\nwage all-out war\nagainst the Users.<C 10>What´s been happening\non the outside? | برنامج التحكم الرئيسي مستعد\nلشن حرب شاملة\nعلى المستخدمين.<C 10>ماذا كان يحدث\nفي الخارج? |
| 1020 | 190 | I must have a lot\nof User friends. | لا بد أن لدي كثيرا\nمن الأصدقاء المستخدمين. |
| 1025 | 167 | Outta the way! | ابتعدوا عن الطريق! |
| 1037 | 183 | We´ll need a sailer to reach the MCP,<C 14 78 00><C 10>so let´s get to the simulation hangar! | سنحتاج إلى مركب للوصول إلى برنامج التحكم الرئيسي,<C 14 78 00><C 10>فلنتجه إلى حظيرة المحاكاة! |
| 1039 | 173 | The MCP is straight ahead. | برنامج التحكم الرئيسي أمامنا مباشرة. |
| 1042 | 208 | Sark.<C 14 3F 00><C 10>The MCP´s number two. | سارك.<C 14 3F 00><C 10>الرجل الثاني في برنامج التحكم الرئيسي. |
| 1047 | 221 | Now for the MCP! | الآن إلى برنامج التحكم الرئيسي! |
| 1048 | 208 | This thing is the MCP? | هذا الشيء هو برنامج التحكم الرئيسي? |
| 1067 | 166 | Isn´t this what Users do when\nthey´re sorry to say good-bye? | أليس هذا ما يفعله المستخدمون عندما\nيحزنون لوداع? |
| 1076 | 151 | Light Cycle | دراجة الضوء |
| 1078 | 151 | Test 1 | اختبار 1 |
| 1081 | 151 | Light Cycle | دراجة الضوء |
| 1087 | 158 | Yes | نعم |
| 8053 | 151 | Light Cycle | دراجة الضوء |
| 17876 | 166 | We can get to the <C 04 0A>game area <C 03>Tron is\nin from the terminal! Let´s hurry! | يمكننا الوصول إلى <C 04 0A>منطقة اللعب <C 03>التي فيها ترون\nمن الطرف! لنسرع! |
| 17899 | 188 | I´m glad that MCP is gone.\nI bet Tron is relieved, too! | يسعدني أن برنامج التحكم الرئيسي ذهب.\nأراهن أن ترون مرتاح أيضا! |

### po.bar
| id | % | EN | AR now |
|---|---|---|---|
| 4671 | 158 | So...how´s Piglet these days? | إذن... كيف حال بيركيت هذه الأيام? |
| 4679 | 153 | Why? | لماذا? |
| 4688 | 157 | Sora! Help! Please! | سورا! النجدة! أرجوك! |
| 4720 | 159 | Well, I´ll help you fix\nyour house, Eeyore. | حسنا, سأساعدك في إصلاح\nبيتك يا إيور. |
| 4722 | 153 | Well, hello, Piglet. | حسنا, مرحبا يا بيركيت. |
| 4725 | 206 | Um, I do? | أم, هل أعرفه? |
| 4744 | 152 | Sorry. It´s our fault.\nWe brought Pooh here. | آسفون. إنه خطؤنا.\nنحن من أحضر بوه إلى هنا. |
| 4779 | 307 | Hi! | مرحبا! |
| 4780 | 155 | Well, hello, Sora! | حسنا, مرحبا يا سورا! |
| 4816 | 172 | What do you think\nwe should do, Sora? | ماذا تظن\nأن علينا أن نفعل يا سورا? |
| 4838 | 162 | Oh, bother! | آه, يا للإزعاج! |
| 4851 | 164 | Yep, that´s all. | أجل, هذا كل شيء. |
| 4870 | 174 | See ya! | إلى اللقاء! |
| 7898 | 166 | Could he be eating honey?\n<C 15 33 00>Leave him be...\n<C 15 09 00>Let´s help him! | هل يمكن أن يكون يأكل العسل?\n<C 15 33 00>اتركه...\n<C 15 09 00>لنساعده! |
| 18722 | 219 | Hit | ضربة |
| 18723 | 183 | Dash | اندفاع |
| 19374 | 156 | I say, it seems we have a\nrather serious predicament!<C 10>Sora, would you mind\ngoing after poor Piglet? | أقول, يبدو أننا في\nورطة خطيرة!<C 10>يا سورا, هل تمانع\nفي الذهاب وراء بيركيت المسكين? |
| 21524 | 168 |  \nAtop the hill with the starry sky, Sora\nfinds Pooh with his head stuck in a honey\npot. Silly old bear!\n \nAlthough Sora's not quite sure whether to\nhelp him or leave him be, after some\npondering, he decides to give Pooh a hand.\n \n \n \n |  \nعلى قمة التل ذي السماء المرصعة بالنجوم, يجد سورا\nبوه ورأسه عالق في إناء\nعسل. يا له من دب أحمق!\n \nمع أن سورا غير متأكد إن كان سيساعده\nأم يتركه, بعد بعض\nالتفكير يقرر مساعدة بوه.\n \n \n \n |

Not translated on purpose: wi 5678, 5679 (empty text) and 5736-5765 (symbol-only placeholders); po 4871-4905 (plain numbers) and 19888 (single space). MCP/DTD were written out in Arabic (C and D are not allowed as Latin): MCP = برنامج التحكم الرئيسي, DTD = دي تي دي.

## 2026-10-01 al / lk / bb - rows >150% (real metric), kept in the builds

### al.bar
| id | % | EN | AR now |
|---|---|---|---|
| 52 | 162 | Bet that´s your new scam. | أراهن أن هذه خدعتك الجديدة. |
| 80 | 155 | All in a day´s work. | مجرد عمل يوم عادي. |
| 97 | 171 | Nice move. | حركة جميلة. |
| 103 | 206 | Hi, Sora! | مرحبا يا سورا! |
| 119 | 153 | Who said I was? | من قال إنني حزين? |
| 133 | 161 | Uh, Sora? | أم, يا سورا? |
| 134 | 161 | Iago!? | آياغو!? |
| 148 | 152 | Of course.\nThat is...<C 10>IF you can\nafford it. | بالطبع.\nأي...<C 10>إن استطعتم\nدفع ثمنه. |
| 150 | 153 | Yeah, we can pay you\nin royal treasu-- | أجل, نستطيع أن ندفع لك\nمن كنوز ملكي-- |
| 159 | 159 | But it´s not mine\nto take.\nAnd I can´t ask.<C 10>I don´t want\nto worry Jasmine\nor the Sultan. | لكنه ليس لي\nلآخذه.\nولا أستطيع أن أطلب.<C 10>لا أريد\nأن أقلق ياسمين\nأو السلطان. |
| 164 | 157 | You can count\non me! | يمكنكم الاعتماد\nعلي! |
| 176 | 153 | Hello? | مرحبا? |
| 181 | 182 | Lamp hog! | جشع المصباح! |
| 184 | 230 | No fair! | هذا ليس عدلا! |
| 190 | 197 | Nice try, bird brain. | محاولة جيدة, أيها الرأس الطائر. |
| 192 | 222 | I´m HOME! | لقد عدت إلى البيت! |
| 220 | 190 | Uhhhh...\nPrincess Jasmine,<C 10>you sure you want\nthat pigeon in the\ncoop? | أمم...\nيا أميرة ياسمين,<C 10>هل أنت متأكدة أنك تريدين\nذلك الحمام في\nالقن? |
| 222 | 162 | Aw, sure.\nYou´re\nprobably right. | آه, بالتأكيد.\nأنت\nعلى الأرجح محقة. |
| 225 | 167 | What happens\nnext, Sora? | ماذا يحدث\nبعد ذلك يا سورا? |
| 265 | 167 | Crush those urchins! | اسحقوا هؤلاء المتشردين! |
| 277 | 160 | I can´t take it!\nI know where\nJafar is! | لا أستطيع التحمل!\nأعرف أين\nجعفر! |
| 280 | 171 | Iago! | آياغو! |
| 291 | 200 | Hey, Genie! | مرحبا أيها الجني! |
| 299 | 158 | Nice timing, Carpet! | توقيت جميل أيها البساط! |
| 302 | 167 | Iago? | آياغو? |
| 323 | 152 | Indeed I will, Princess. | بالفعل سأنال, أيتها الأميرة. |
| 326 | 156 | Oh, please. | أوه, أرجوك. |
| 330 | 159 | You dare defy me! You useless bird! | تجرؤ على تحديني! أيها الطائر عديم الفائدة! |
| 331 | 221 | Al! | علاء! |
| 332 | 171 | Iago! | آياغو! |
| 334 | 154 |  <C 14 A0 00><C 10>No... How can I BE defeated again,\nby a pack of filthy street rats?<C 14 30 02><C 10> |  <C 14 A0 00><C 10>لا... كيف أهزم مجددا\nعلى يد حفنة من جرذان الشوارع القذرة?<C 14 30 02><C 10> |
| 339 | 154 | But, Genie, we still need your help! | لكن أيها الجني, ما زلنا نحتاج إلى مساعدتك! |
| 362 | 180 | Well, anyway... | حسنا, على أي حال... |
| 365 | 179 | Well...at least I can still fly. | حسنا... على الأقل ما زلت أستطيع الطيران. |
| 368 | 152 | Ooh! Was that my cue?\nAm I on?<C 14 9C 00><C 10>C´mon, Al, lemme build\na freeway or something! | أوه! هل كانت هذه إشارتي?\nهل جاء دوري?<C 14 9C 00><C 10>هيا يا علاء, دعني أبني\nطريقا سريعا أو شيئا! |
| 379 | 166 | I guess you know\neverything now, eh? | أظنك تعرف\nكل شيء الآن, أليس كذلك? |
| 380 | 164 | You can´t keep shady\nstuff secret for long. | لا يمكنك إبقاء الأمور\nالمشبوهة سرا لوقت طويل. |
| 381 | 176 | So true. | صحيح جدا. |
| 4101 | 167 | End | إنهاء |
| 14155 | 150 | This is the last battle! | هذه هي المعركة الأخيرة! |
| 17016 | 153 | A jewel floats above. | جوهرة تطفو في الأعلى. |
| 17030 | 174 | Next stop: Down! | المحطة التالية: للأسفل! |
| 17031 | 197 | Next stop: Up! | المحطة التالية: للأعلى! |

### lk.bar
| id | % | EN | AR now |
|---|---|---|---|
| 4926 | 188 | Hey--a snack. | مهلا--وجبة خفيفة. |
| 8494 | 206 | Going somewhere? | هل أنتم ذاهبون إلى مكان? |
| 8510 | 152 | Pride Lands? | أراضي الكبرياء? |
| 8511 | 155 | Hey, do you know if a guy\nnamed Riku is there? | مهلا, هل تعرفين إن كان رجل\nاسمه ريكو هناك? |
| 8559 | 158 | Run! | اركض! |
| 8599 | 154 | Call me Mr. Pig! | ناديني السيد الخنزير! |
| 8603 | 155 | I can´t go back. | لا أستطيع العودة. |
| 8604 | 153 | Why? | لماذا? |
| 8626 | 150 | Must this all end in violence? | هل يجب أن ينتهي كل هذا بالعنف? |
| 8670 | 176 | Hiya! | مرحبا! |
| 8673 | 156 | Hey, how´s Simba? | مهلا, كيف حال سيمبا? |
| 8700 | 152 | See, there ya go! | أرأيت, ها قد وصلت! |
| 8717 | 151 | Hey you! | مهلا أنتم! |
| 8743 | 162 | But Simba...\nThat´s not what you´re supposed to be.<C 14 C8 00><C 10>You can´t be Mufasa. You can only be you. | لكن يا سيمبا...\nهذا ليس ما يفترض أن تكونه.<C 14 C8 00><C 10>لا يمكنك أن تكون موفاسا. يمكنك فقط أن تكون أنت. |
| 8748 | 187 | I can´t! | لا أستطيع! |
| 8777 | 154 | Nice try. You´re coming, too! | محاولة جيدة. أنت قادم معنا أيضا! |
| 8797 | 168 | I hope that´s soon. | آمل أن يكون ذلك قريبا. |
| 12888 | 151 | Hey! I had to give\nit a try, right? | مهلا! كان علي\nأن أجرب, أليس كذلك? |
| 12920 | 169 | Aw, don´t say that! Not\nwhen he´s ready to try! | آه, لا تقل ذلك! ليس\nعندما يكون مستعدا للمحاولة! |

### bb.bar
| id | % | EN | AR now |
|---|---|---|---|
| 3022 | 151 | The ballroom and the garden are\nthe highlights of this castle.<C 10>I only hope those intruders\ndon´t cause any damage... | قاعة الرقص والحديقة هما\nأبرز ما في هذه القلعة.<C 10>أرجو فقط ألا يتسبب أولئك المقتحمون\nفي أي ضرر... |
| 3040 | 185 | Please talk to <C 04 0A>Cogsworth <C 03>upstairs\nabout the hidden passageway. | من فضلك تحدث إلى <C 04 0A>كوغزورث <C 03>في الطابق العلوي\nعن الممر المخفي. |
| 3075 | 176 | Look! | انظروا! |
| 3082 | 180 | Just in time! | في الوقت المناسب! |
| 3098 | 176 | Hiya! | مرحبا! |
| 3119 | 157 | West hall. Got it. | القاعة الغربية. فهمت. |
| 3125 | 201 | May I help you? | هل أستطيع مساعدتكم? |
| 3143 | 179 | Uh-oh! | أوه أوه! |
| 3177 | 159 | Is there anything we\ncan do to help? | هل هناك ما\nنستطيع فعله للمساعدة? |
| 3179 | 162 | Oh no, dear. | آه لا يا عزيزي. |
| 3204 | 168 | Hey, Prince! | مهلا أيها الأمير! |
| 3209 | 159 | I did what? | أنا فعلت ماذا? |
| 3275 | 183 | Take care, dears. | اعتنوا بأنفسكم يا أعزائي. |
| 3278 | 160 | Okay, gotta go! | حسنا, علينا الذهاب! |
| 3279 | 172 | I hope tonight goes well. | آمل أن تسير الليلة على ما يرام. |
| 3338 | 210 | Poor child... | يا للطفلة المسكينة... |
| 3343 | 174 | What´s so special about\none rose, anyway? | ما الخاص\nفي وردة واحدة على أي حال? |
| 3351 | 224 | Poor Beast! | أيها الوحش المسكين! |
| 3353 | 214 | Please do! | أرجوكم افعلوا! |
| 3355 | 188 | Hey, Beast. | مهلا أيها الوحش. |
| 3369 | 153 | So, Beast...you came after all. | إذن أيها الوحش... جئت بعد كل شيء. |
| 3386 | 169 | Hurry! | أسرعوا! |
| 3410 | 180 | Please? | من فضلك? |
| 3412 | 195 | Maestro--music! | أيها المايسترو--موسيقى! |
| 7526 | 223 | Are we all set? | هل نحن جاهزون جميعا? |
| 18754 | 165 | Move the wardrobe?\n<C 15 33 00>Leave it alone.\n<C 15 09 00>Move it! | هل تحرك خزانة الملابس?\n<C 15 33 00>اتركها.\n<C 15 09 00>حركها! |

Not translated on purpose: al 215, 216, 4084, 4085 (single spaces) and 14145, 14146 (symbol placeholders); lk 19869 (space).

## mu.bar - 41 rows >150% by real metric (deferred, kept in the build; shorten in the text-quality pass if a screenshot shows a problem)

| id | % | EN | AR now |
|---|---|---|---|
| 4106 | 185 | Should I reject it?\n<C 15 33 00>No sir!\n<C 15 0A 00>I need more rest. | هل أرفضها?\n<C 15 33 00>لا يا سيدي!\n<C 15 0A 00>أحتاج إلى مزيد من الراحة. |
| 4172 | 160 | Captain? | أيها القائد? |
| 4188 | 162 | You all knew, didn´t you?<C 14 73 00><C 10>You knew Ping was really a\nwoman in disguise. | كنتم تعرفون جميعا, أليس كذلك?<C 14 73 00><C 10>كنتم تعرفون أن بينغ في الحقيقة\nامرأة متنكرة. |
| 4198 | 157 | Mulan... I blew it. | مولان... أفسدت الأمر. |
| 4203 | 151 | Go back home. | سأعود إلى البيت. |
| 4211 | 153 | Mulan! | مولان! |
| 4262 | 178 | Hey, no cutting! | هيه, لا تتجاوز الدور! |
| 4270 | 158 | Please! | أرجوك! |
| 4271 | 151 | Please!? | أرجوك!? |
| 4273 | 151 | Uh...knock it off! | آه... توقف عن هذا! |
| 4296 | 153 | You should\nreturn home. | عليك أن\nتعود إلى البيت. |
| 4310 | 151 | I´ll brief you on\nthe details later.<C 10>Return when you´re\nready to depart.<C 10>Remember, the smallest\nmission may have the\ngreatest purpose.<C 10>Stay alert! | سأشرح لكم التفاصيل\nلاحقا.<C 10>عودوا عندما\nتكونون مستعدين للانطلاق.<C 10>تذكروا, أصغر مهمة\nقد تكون لها\nأعظم غاية.<C 10>ابقوا متيقظين! |
| 4311 | 205 | Sir! | حاضر! |
| 4312 | 205 | Sir! | حاضر! |
| 4313 | 205 | Sir! | حاضر! |
| 4314 | 205 | Sir! | حاضر! |
| 4317 | 151 | Captain... | أيها القائد... |
| 4322 | 154 | See me when you´re\nready to depart.<C 10>Remember, this may be\na test, but it´s still\nan important mission.<C 10>Be alert! | قابلني عندما\nتكونون مستعدين للانطلاق.<C 10>تذكروا, قد تكون هذه\nاختبارا, لكنها\nمهمة مهمة.<C 10>كونوا متيقظين! |
| 4323 | 205 | Sir! | حاضر! |
| 4324 | 205 | Sir! | حاضر! |
| 4325 | 205 | Sir! | حاضر! |
| 4326 | 205 | Sir! | حاضر! |
| 4330 | 163 | Captain! | أيها القائد! |
| 4337 | 205 | Sir! | حاضر! |
| 4352 | 198 | Dead end. | طريق مسدود. |
| 4364 | 178 | You okay? | هل أنت بخير? |
| 4369 | 163 | Captain! | أيها القائد! |
| 4399 | 171 | It ends now! | ينتهي الأمر الآن! |
| 4414 | 151 | Mulan. | مولان. |
| 4420 | 176 | Can I get an autograph? | هل أستطيع الحصول على توقيع? |
| 4434 | 171 | You two play nice. | كونا لطيفين مع بعضكما. |
| 4449 | 183 | The guy in black. | الرجل ذو الرداء الأسود. |
| 4459 | 152 | Again? | مجددا? |
| 4472 | 156 | Anyway... What now? | على أي حال... ماذا الآن? |
| 4479 | 154 | Huh? Everything´s fine. | هاه? كل شيء على ما يرام. |
| 4483 | 154 | We´re just glad you´re\nnot in black cloaks. | نحن سعداء فقط لأنكم\nلا ترتدون عباءات سوداء. |
| 4511 | 153 | Mulan! | مولان! |
| 4516 | 169 | Hurry! | أسرعوا! |
| 4530 | 186 | Did you? | وهل فعلت? |
| 4545 | 153 | And yet, Mulan... | ومع ذلك يا مولان... |
| 4606 | 158 | Yes | نعم |

## nm.bar - 26 rows >150% by real metric (deferred, kept in the build; shorten in the text-quality pass if a screenshot shows a problem)

| id | % | EN | AR now |
|---|---|---|---|
| 5772 | 187 | I can´t count on those kids\nto do anything right.<C 10>Would you be interested in\nhelping me in their place? | لا أستطيع الاعتماد على هؤلاء الأولاد\nلفعل أي شيء بشكل صحيح.<C 10>هل تهتم بمساعدتي\nمكانهم? |
| 5813 | 158 | Heave-ho! | هيا ارفعوا! |
| 5834 | 156 | Jack? Where are you?<C 14 72 00><C 10>I´m only an elected official--\nI can´t handle this by myself. | جاك? أين أنت?<C 14 72 00><C 10>أنا مجرد موظف منتخب--\nلا أستطيع التعامل مع هذا وحدي. |
| 5836 | 158 | We´re on it! | نحن على الأمر! |
| 5839 | 178 | Us? | نحن? |
| 5858 | 152 | Shall we? | هل نذهب? |
| 5860 | 200 | En garde, loyal bodyguards! | دافعوا عن أنفسكم أيها الحراس المخلصون! |
| 5866 | 166 | Um, Sora, sir. | آه, سورا يا سيدي. |
| 5881 | 167 | Busted! | ضبطناكم! |
| 5906 | 156 | They creamed ya! | هزموك شر هزيمة! |
| 5914 | 162 | My Heartless will help you.\nBut do not fail me! | بلا قلب الخاصون بي سيساعدونكم.\nلكن لا تخذلوني! |
| 5918 | 167 | Get ´em! | امسكوهم! |
| 5921 | 151 | Let´s go see if Mr. Oogie´s ready! | لنذهب لنرى إن كان السيد أوغي جاهزا! |
| 5942 | 159 | Oh, no! | يا للهول! |
| 5962 | 178 | Eh? | هاه? |
| 6014 | 171 | Oh! | أوه! |
| 6030 | 155 | Hey! | هيه! |
| 6058 | 166 | But wait! | لكن انتظروا! |
| 6061 | 158 | You! You can´t be here!<C 14 82 00><C 10>Leave Halloween Town,\nby order of the mayor! | أنتم! لا يجوز أن تكونوا هنا!<C 14 82 00><C 10>غادروا بلدة الهالوين\nبأمر من العمدة! |
| 6062 | 156 | Somebody? Anybody!<C 14 78 00><C 10>I´m only an elected official--\nI can´t handle this by myself. | أي أحد? أي أحد!<C 14 78 00><C 10>أنا مجرد موظف منتخب--\nلا أستطيع التعامل مع هذا وحدي. |
| 6108 | 165 | Stop kicking! | توقف عن الركل! |
| 6115 | 204 | Good plan, eh? | خطة جيدة, أليس كذلك? |
| 6129 | 151 | Yes, all that poor puppet\nwanted was a heart. | نعم, كل ما أرادته تلك الدمية\nالمسكينة هو قلب. |
| 6130 | 152 | Ho! Ho! Ho! | هو! هو! هو! |
| 7978 | 163 | Now then, are you all set? | والآن, هل أنتم جاهزون جميعا? |
| 18728 | 238 | Reload | أعد التعبئة |

## ca.bar - 35 rows >150% by real metric (deferred, kept in the build; shorten in the text-quality pass if a screenshot shows a problem)

| id | % | EN | AR now |
|---|---|---|---|
| 6217 | 267 | Go | اذهب |
| 6218 | 191 | Quit | خروج |
| 7809 | 153 | See? I told ya you´d\nbe needin´ ol´ Pete! | أرأيت? قلت لك إنك\nستحتاج إلى بيت العجوز! |
| 7888 | 154 | This ship may look old,\nbut she sure is fast.<C 10>If you need to rest, you can use\nthe captain´s room below. | قد تبدو هذه السفينة قديمة,\nلكنها سريعة جدا.<C 10>إن احتجت إلى الراحة, يمكنك استخدام\nغرفة القبطان بالأسفل. |
| 9960 | 155 | Hey! | هيه! |
| 9966 | 195 | Aye! | حاضر! |
| 9982 | 155 | Just kidding!<C 10>Weren´t those guys\nheaded into town? | أمزح فقط!<C 10>ألم يكن هؤلاء الرجال\nمتجهين إلى البلدة? |
| 9986 | 189 | Stop! | توقفوا! |
| 10078 | 169 | Hurry! | أسرعوا! |
| 10115 | 218 | You can´t...<C 14 3C 00><C 10> <C 14 A8 00><C 10>But I can. | أنتم لا تستطيعون...<C 14 3C 00><C 10> <C 14 A8 00><C 10>لكنني أستطيع. |
| 10125 | 249 | No fair! | هذا غير عادل! |
| 10126 | 217 | Good work,\nBarbossa!<C 10>Who knew it´d\nbe this easy? | عمل جيد\nيا باربوسا!<C 10>من كان يعلم أن الأمر\nسيكون بهذه السهولة? |
| 10133 | 163 | Why struggle, mate?<C 10>A pirate knows\nwhen to surrender. | لماذا المقاومة يا صاحبي?<C 10>القرصان يعرف\nمتى يستسلم. |
| 10137 | 160 | I still don´t plan to\ntrust pirates again. | ما زلت لا أنوي\nأن أثق بالقراصنة مجددا. |
| 10138 | 171 | Wise policy, lad. | سياسة حكيمة يا فتى. |
| 10139 | 194 | All clear! | كل شيء آمن! |
| 10145 | 182 | Then trust\nme instead! | إذن ثقي\nبي بدلا من ذلك! |
| 10178 | 182 | Aye aye... | حاضر حاضر... |
| 10189 | 178 | Well, if any lass could... | حسنا, لو كانت هناك فتاة تستطيع... |
| 10192 | 163 | Lucky man... | رجل محظوظ... |
| 10199 | 166 | Stop that, Jack. | توقف عن ذلك يا جاك. |
| 10210 | 162 | You´d best go prepared. We´ve\nno idea what´s out there. | الأفضل أن تذهبوا مستعدين. لا نعرف\nما الذي ينتظرنا هناك. |
| 10222 | 200 | Aye aye! | حاضر حاضر! |
| 10235 | 164 | Oh? | أوه? |
| 10237 | 196 | Fire! | أطلقوا! |
| 10253 | 176 | Look! | انظروا! |
| 10270 | 153 | Sora, I think we´ll\nneed your help. | سورا, أظننا\nسنحتاج إلى مساعدتك. |
| 10291 | 267 | All better. | كل شيء على ما يرام. |
| 10300 | 160 | Is there any way we can help? | هل من طريقة نستطيع مساعدتك بها? |
| 10302 | 172 | Anything at all? | أي شيء على الإطلاق? |
| 10312 | 150 | Okay. Sure. | حسنا. بالتأكيد. |
| 15904 | 155 | Do you want to try that\nsliding plank again? | هل تريد تجربة اللوح المنزلق\nمرة أخرى? |
| 15916 | 175 | Breezy, eh? | نسيم عليل, ها? |
| 17011 | 156 | Wait, Jack!\nI need your help. | انتظر يا جاك!\nأحتاج إلى مساعدتك. |
| 18405 | 153 | This place is not accessible now. | لا يمكن الوصول إلى هذا المكان الآن. |

## eh.bar - 26 rows >150% by real metric (deferred, kept in the build; shorten in the text-quality pass if a screenshot shows a problem)

| id | % | EN | AR now |
|---|---|---|---|
| 16222 | 172 | You can´t be Riku? | لا يمكن أن تكون ريكو? |
| 16244 | 164 | Oh? | أوه? |
| 16280 | 152 | Warriors of the Keyblade!<C 14 B1 00><C 10>Go forth,<C 14 6C 00><C 10>and bring me more hearts! | محاربو الكيبلايد!<C 14 B1 00><C 10>اذهبوا,<C 14 6C 00><C 10>وأحضروا لي المزيد من القلوب! |
| 16290 | 180 | Guys? | يا رفاق? |
| 16299 | 151 | Xemnas! Don´t! | زيمناس! لا تفعل! |
| 16319 | 161 | I need...more rage...<C 14 C3 00><C 10>I need more...hearts... | أحتاج... المزيد من الغضب...<C 14 C3 00><C 10>أحتاج المزيد... من القلوب... |
| 16328 | 169 | Hurry! | أسرعوا! |
| 16338 | 162 | Sure. | بالطبع. |
| 16342 | 157 | I did, didn´t I? | تعرفت, أليس كذلك? |
| 16348 | 151 | So, we can be together again! | إذن نستطيع أن نكون معا مجددا! |
| 16367 | 170 |  <C 14 6D 00><C 10>Sora...<C 14 77 00><C 10>I can´t... |  <C 14 6D 00><C 10>سورا...<C 14 77 00><C 10>لا أستطيع... |
| 16407 | 161 | This time...I´LL fight. | هذه المرة... أنا من سيقاتل. |
| 16418 | 155 | Sora! Roxas! | سورا! روكساس! |
| 16419 | 171 | Roxas? | روكساس? |
| 16437 | 155 | Then, I can end this charade? | إذن, أستطيع إنهاء هذه المسرحية? |
| 16443 | 151 | This spot should do. | هذا المكان يفي بالغرض. |
| 16454 | 178 | You okay? | هل أنت بخير? |
| 16498 | 215 | Lie? | تكذب? |
| 16505 | 162 | Uhhhh-oh! | أوووه-أوه! |
| 16519 | 203 | Is that all? | هل هذا كل شيء? |
| 16542 | 175 | Because, Sora.<C 14 3C 00><C 10><C 14 60 00>Roxas is your Nobody. | لأن, يا سورا.<C 14 3C 00><C 10><C 14 60 00>روكساس هو اللا أحد الخاص بك. |
| 16566 | 152 | I was wondering who would dare\ninterfere with my Kingdom Hearts.<C 14 7A 01><C 10>And look--<C 14 54 00><C 10>here you all are.<C 14 7E 00><C 10>How convenient for me. | كنت أتساءل من يجرؤ\nعلى التدخل في كينغدوم هارتس خاصتي.<C 14 7A 01><C 10>وانظروا--<C 14 54 00><C 10>ها أنتم جميعا هنا.<C 14 7E 00><C 10>كم هذا ملائم لي. |
| 16671 | 196 | Dead end? | طريق مسدود? |
| 19963 | 163 | If he is to die so easily,<C 14 E6 00><C 10> <C 14 2D 00><C 10>he is of no use to us. | إن كان سيموت بهذه السهولة,<C 14 E6 00><C 10> <C 14 2D 00><C 10>فهو عديم النفع لنا. |
| 21440 | 177 | Zexion! Zexion! | زيكسيون! زيكسيون! |
| 21443 | 155 | His usual spot. | في مكانه المعتاد. |

## lm.bar - 29 rows >150% by real metric (deferred, kept in the build; shorten in the text-quality pass if a screenshot shows a problem)

| id | % | EN | AR now |
|---|---|---|---|
| 5051 | 186 | See... | انظري... |
| 5081 | 156 | She can´t be in the\nmusical like that. | لا يمكنها أن تكون في\nالمسرحية هكذا. |
| 5102 | 171 | Oh! | أوه! |
| 5106 | 172 | No, don´t! | لا, لا تفعلوا! |
| 5110 | 158 | But we can´t reach it... | لكن لا نستطيع الوصول إليه... |
| 5119 | 152 | And if this is the only way... | وإن كان هذا هو الطريق الوحيد... |
| 5122 | 155 | Ariel, you poor child! | آرييل, يا طفلتي المسكينة! |
| 5127 | 154 | Oh, well. It mustn´t be love,\nif you´ll give up that easily. | أوه, حسنا. لا بد أنه ليس حبا,\nإن كنت ستستسلمين بهذه السهولة. |
| 5130 | 185 | A human?\nCan you do that? | بشرية?\nهل تستطيعين فعل ذلك? |
| 5143 | 185 | Wait! | انتظري! |
| 5147 | 170 | Ariel! Don´t! | آرييل! لا تفعلي! |
| 5149 | 185 | Wait! | انتظري! |
| 5153 | 163 | What´s wrong?\nYou can´t speak? | ما الخطب?\nألا تستطيعين الكلام? |
| 5179 | 169 | Hey, look! | هيه, انظروا! |
| 5181 | 205 | I can´t see! | لا أستطيع الرؤية! |
| 5202 | 184 | Not so fast! | ليس بهذه السرعة! |
| 5206 | 189 | Stop! | توقفوا! |
| 5231 | 166 | It´s over, Ursula! | انتهى الأمر يا أورسولا! |
| 5237 | 204 | This can´t be... | لا يمكن أن يكون هذا... |
| 5242 | 152 | Well, I guess it´s never\ntoo late to learn, right? | حسنا, أظن أن الوقت لا يفوت\nلتعلمها أبدا, أليس كذلك? |
| 5250 | 159 | Hey, wait... | هيه, انتظري... |
| 5251 | 191 | I almost forgot, Sebastian!<C 10>King Triton said this year´s\nfestival is so important<C 10>that the musical better\nbe your best ever! | كدت أنسى يا سيباستيان!<C 10>الملك تريتون قال إن مهرجان هذا العام\nمهم جدا<C 10>لدرجة أن المسرحية يجب\nأن تكون أفضل ما قدمت! |
| 5273 | 180 | Musical Tutorial | درس المسرحية الغنائية |
| 5331 | 158 | Yes | نعم |
| 6435 | 176 | I guess that´s\nall we CAN do. | أظن أن هذا\nكل ما نستطيع فعله. |
| 8831 | 190 | Drum solo! Here´s the sign.\nGive him the cue! | عزف الطبول المنفرد! هذه هي الإشارة.\nأعطه الإيعاز! |
| 18141 | 152 | How are the rehearsals for the\nmusical coming along?<C 10>Please make it grand enough to cure\nAriel of her interest in the surface. | كيف تسير التدريبات على\nالمسرحية الغنائية?<C 10>أرجو أن تجعلوها عظيمة بما يكفي لتشفي\nآرييل من اهتمامها بالسطح. |
| 18197 | 159 | I should go check\non Ariel. | علي أن أذهب لأتفقد\nآرييل. |
| 18726 | 169 | Swim | سباحة |

## he.bar - 53 rows >150% by real metric (deferred, kept in the build; shorten in the text-quality pass if a screenshot shows a problem)

| id | % | EN | AR now |
|---|---|---|---|
| 832 | 158 | Are ya sure this is the coliseum? | هل أنت متأكد أن هذا هو الكولوسيوم? |
| 3500 | 173 | Leaving so soon? | ستغادر بهذه السرعة? |
| 3529 | 183 | So how´s Herc? | إذن كيف حال هرقل? |
| 3560 | 179 | And all for one little job. | وكل ذلك لقاء مهمة صغيرة واحدة. |
| 3575 | 200 | Go now! | اذهبوا الآن! |
| 3584 | 168 | Cerberus, go! | سيربيروس, انطلق! |
| 3610 | 155 | Hey, Herc! | هيه, هرقل! |
| 3611 | 307 | Hi! | مرحبا! |
| 3615 | 150 | Junior heroes, always busy! | الأبطال الصغار, مشغولون دائما! |
| 3627 | 156 | Hey, good idea! | هيه, فكرة جيدة! |
| 3642 | 180 | By who? | من الفاعل? |
| 3646 | 181 | Sure. | بالتأكيد. |
| 3659 | 175 | Ah well. Can´t all be heroes. | آه حسنا. لا يمكن أن نكون كلنا أبطالا. |
| 3660 | 210 | Can you handle this? | هل تستطيعون التعامل مع هذا? |
| 3675 | 151 | Heroes, eh?\nYou could´ve just asked! | أبطال, ها?\nكان يمكنكم أن تسألوا فقط! |
| 3678 | 181 | Man... | يا رجل... |
| 3683 | 171 | Roxas? | روكساس? |
| 3694 | 169 | Hey, look! | هيه, انظروا! |
| 3718 | 170 | No one likes a\nsore loser, Hades. | لا أحد يحب\nالخاسر الحاقد يا هاديس. |
| 3719 | 224 | Can it, keyboy! | اخرس أيها صاحب المفتاح! |
| 3720 | 184 | Then let me. | إذن دعني أقولها. |
| 3726 | 204 | This can´t be... | لا يمكن أن يكون هذا... |
| 3736 | 182 | Herc needs help! | هرقل يحتاج مساعدة! |
| 3739 | 167 | We´re in. | نحن معكم. |
| 3757 | 184 | Well, time to go. | حسنا, حان وقت الذهاب. |
| 3759 | 165 | You think maybe\nHades is in here? | هل تظنون أن هاديس\nهنا? |
| 3770 | 163 | Hmph. | هممف. |
| 3773 | 151 | Hey. | هيه. |
| 3793 | 200 | Lowlife! | أيها الوضيع! |
| 3800 | 156 | I bet he´s a real hero, huh? | أراهن أنه بطل حقيقي, أليس كذلك? |
| 3804 | 175 | Stop that! | توقف عن ذلك! |
| 3825 | 155 | Hey! | هيه! |
| 3840 | 151 | Lord Hades. | اللورد هاديس. |
| 3878 | 165 | You must live! | عليكم أن تعيشوا! |
| 3901 | 160 | Wanna know why? | تريد أن تعرف لماذا? |
| 3913 | 156 | We can´t win. | لا نستطيع الفوز. |
| 3923 | 154 | Just no more crazy stunts. | فقط لا مزيد من الحيل المجنونة. |
| 3926 | 164 | How dare you get a happy\nending! How DARE you! | كيف تجرؤون على نهاية سعيدة!\nكيف تجرؤون! |
| 3941 | 168 | Thanks again, guys!\nYou´re the best. | شكرا مرة أخرى يا شباب!\nأنتم الأفضل. |
| 3954 | 164 | Hey, are we true heroes yet? | هيه, هل نحن أبطال حقيقيون الآن? |
| 3961 | 153 | Course if it was, you´d\nhave no problem.<C 14 9A 00><C 10>I´d make you all heroes,\nin a heartbeat! | طبعا لو كان بيدي,\nلما واجهتم مشكلة.<C 14 9A 00><C 10>كنت سأجعلكم جميعا أبطالا\nفي لمح البصر! |
| 3963 | 163 | Say it again! | قلها مرة أخرى! |
| 3969 | 152 | See that? | أرأيتم ذلك? |
| 3980 | 158 | Yes | نعم |
| 4006 | 162 | Fight alongside your\nfriends.\nThe Drive Gauge can´t be\nused but Limits consume\nless MP than usual.\n | قاتل بجانب\nأصدقائك.\nلا يمكن استخدام عداد الدرايف\nلكن الليميت تستهلك\nMP أقل من المعتاد.\n |
| 4012 | 187 | A solo fight using Sora.\nSora can use Summons\nalone in this tournament.\n | قتال فردي بسورا.\nيستطيع سورا استخدام الاستدعاءات\nمنفردا في هذه البطولة.\n |
| 4024 | 162 | Fight alongside your\nfriends.\nThe Drive Gauge can´t be\nused but Limits consume\nless MP than usual.\n | قاتل بجانب\nأصدقائك.\nلا يمكن استخدام عداد الدرايف\nلكن الليميت تستهلك\nMP أقل من المعتاد.\n |
| 4030 | 187 | A solo fight using Sora.\nSora can use Summons\nalone in this tournament.\n | قتال فردي بسورا.\nيستطيع سورا استخدام الاستدعاءات\nمنفردا في هذه البطولة.\n |
| 4041 | 158 | Yes | نعم |
| 7523 | 153 | There´s only one rule:\nKeep it clean! | هناك قاعدة واحدة فقط:\nحافظ على النظافة! |
| 16179 | 153 | If Hercules loses, our job\nwill be a lot easier.<C 10>But if he wins...\nNo, that won´t happen... | إن خسر هرقل, ستصبح مهمتنا\nأسهل بكثير.<C 10>لكن إن فاز...\nلا, لن يحدث ذلك... |
| 17585 | 154 | The light has faded, and\nyou can no longer enter. | انطفأ الضوء,\nولا يمكنك الدخول بعد الآن. |
| 19303 | 183 | Entered double-score mode! | تم الدخول في وضع النقاط المضاعفة! |

## title.bar - 44 rows >150% by real metric (deferred, kept in the build; shorten in the text-quality pass if a screenshot shows a problem)

| id | % | EN | AR now |
|---|---|---|---|
| 20698 | 157 | The Girl in White | الفتاة ذات الثوب الأبيض |
| 20711 | 154 | Back to Reality | العودة إلى الواقع |
| 20716 | 164 | Day 4: Road to War | اليوم 4: الطريق إلى الحرب |
| 20725 | 176 | Axel | آكسل |
| 20736 | 152 | Day 5: Changes | اليوم 5: التغييرات |
| 20741 | 277 | All Aboard | الجميع على متن القطار |
| 20810 | 159 | Their Agenda | جدول أعمالهم |
| 20824 | 166 | Beast Comes To | الوحش يستعيد وعيه |
| 20827 | 186 | Dark Thorn | الشوكة المظلمة |
| 20837 | 215 | Avalanche | الانهيار الجليدي |
| 20840 | 163 | It Ends Now | ينتهي الأمر الآن |
| 20933 | 214 | Run! | اهربوا! |
| 20951 | 153 | Stop, Thief! | توقف أيها اللص! |
| 20962 | 178 | Get the Lamp! | احصل على المصباح! |
| 20975 | 165 | Onward! | إلى الأمام! |
| 20988 | 168 | Jolly Ol' Oogie | أوغي المرح القديم |
| 21052 | 208 | The Starry Sky | السماء المرصعة بالنجوم |
| 21058 | 154 | Come Join the Musical | انضم إلى المسرحية الغنائية |
| 21067 | 150 | Helping Ariel | مساعدة آرييل |
| 21109 | 151 | Tron | ترون |
| 21110 | 176 | The MCP's Objective | هدف برنامج التحكم الرئيسي |
| 21131 | 207 | Data Access | الوصول إلى البيانات |
| 21144 | 205 | Gullwings, Go! | أجنحة النورس, انطلقوا! |
| 21151 | 167 | Demyx | ديميكس |
| 21164 | 156 | Uninvited Guests | ضيوف غير مدعوين |
| 21187 | 181 | Fireworks | الألعاب النارية |
| 21197 | 158 | Foe vs. Foe | عدو ضد عدو |
| 21206 | 162 | Back in Port Royal | العودة إلى ميناء رويال |
| 21218 | 154 | Grim Reaper | الحاصد المخيف |
| 21219 | 153 | Luxord Flees | لوكسورد يهرب |
| 21234 | 151 | Jafar's Evil Plan | خطة جعفر الشريرة |
| 21243 | 151 | The Real Culprits | المذنبون الحقيقيون |
| 21256 | 166 | To Be King | أن تكون ملكا |
| 21269 | 150 | More Heartless? | المزيد من بلا قلب? |
| 21272 | 157 | Meanwhile, in Ansem's Lab | في هذه الأثناء, في مختبر أنسيم |
| 21275 | 188 | Taunted by the MCP | سخرية برنامج التحكم الرئيسي |
| 21278 | 185 | Cyberspace | الفضاء السيبراني |
| 21284 | 165 | Run, Leon | اركض يا ليون |
| 21293 | 187 | Destroying the MCP | تدمير برنامج التحكم الرئيسي |
| 21304 | 177 | The Photograph | الصورة الفوتوغرافية |
| 21318 | 160 | Where Hearts Go | إلى أين تذهب القلوب |
| 21322 | 182 | Roxas | روكساس |
| 21338 | 174 | Luxord | لوكسورد |
| 21341 | 182 | Saïx | سايكس |

## gumi.bar - 112 rows >150% by real metric (deferred, kept in the build; shorten in the text-quality pass if a screenshot shows a problem)

| id | % | EN | AR now |
|---|---|---|---|
| 6221 | 222 | Aero/G | غامي الانسياب |
| 6222 | 228 | Flat Helm/G | غامي الخوذة المسطحة |
| 6223 | 190 | Bubble Helm/G | غامي الخوذة الفقاعية |
| 6224 | 185 | Solid Helm/G | غامي الخوذة الصلبة |
| 6225 | 182 | Sphere Helm/G | غامي الخوذة الكروية |
| 6226 | 156 | Bridge/G | غامي الجسر |
| 6227 | 166 | Big Bridge/G | غامي الجسر الكبير |
| 6229 | 154 | Booster/G | غامي المعزز |
| 6231 | 174 | Mini-Propeller/G | غامي المروحة الصغيرة |
| 6232 | 158 | Propeller/G | غامي المروحة |
| 6233 | 156 | Screw Propeller/G | غامي المروحة اللولبية |
| 6234 | 162 | Sonic Turbo/G | غامي التيربو الصوتي |
| 6235 | 172 | Rotor/G | غامي الدوار |
| 6236 | 152 | Large Rotor/G | غامي الدوار الكبير |
| 6237 | 159 | Tempest/G | غامي العاصفة |
| 6239 | 159 | Typhoon/G | غامي التايفون |
| 6240 | 187 | Cyclone/G | غامي السيكلون |
| 6241 | 177 | Vortex/G | غامي الدوامة |
| 6242 | 186 | Storm/G | غامي الزوبعة |
| 6243 | 182 | Angel/G | غامي الملاك |
| 6245 | 164 | Shield/G | غامي الدرع |
| 6247 | 205 | Shell/G | غامي الصدفة |
| 6248 | 183 | Large Shell/G | غامي الصدفة الكبيرة |
| 6249 | 167 | Fire/G | غامي فاير |
| 6250 | 162 | Fira/G | غامي فيرا |
| 6251 | 157 | Firaga/G | غامي فيراغا |
| 6255 | 162 | Gravity/G | غامي غرافيتي |
| 6256 | 154 | Gravira/G | غامي غرافيرا |
| 6257 | 160 | Graviga/G | غامي غرافيغا |
| 6261 | 177 | Comet/G | غامي المذنب |
| 6262 | 153 | Meteor/G | غامي النيزك |
| 6264 | 215 | Drill/G | غامي المثقاب |
| 6265 | 229 | Saw/G | غامي المنشار |
| 6266 | 160 | Orichalcum/G | غامي أوريكالكوم |
| 6267 | 158 | Masamune/G | غامي ماساموني |
| 6268 | 152 | Excalibur/G | غامي إكسكاليبر |
| 6269 | 160 | Infinity/G | غامي اللانهاية |
| 6270 | 174 | Neon Orb/G | غامي كرة النيون |
| 6271 | 200 | Neon Bar/G | غامي عمود النيون |
| 6272 | 189 | Wheel/G | غامي العجلة |
| 6273 | 218 | Parabola/G | غامي القطع المكافئ |
| 6275 | 172 | Radar/G | غامي الرادار |
| 6276 | 177 | Round Light/G | غامي الضوء المستدير |
| 6279 | 168 | Shuriken/G | غامي الشوريكن |
| 6280 | 165 | Gungnir/G | غامي غونغنير |
| 6282 | 165 | Moon Ring/G | غامي حلقة القمر |
| 6283 | 167 | Strike/G | غامي الضربة |
| 6284 | 184 | Bomb/G | غامي القنبلة |
| 6287 | 216 | Drain/G | غامي الامتصاص |
| 6311 | 159 | Auto-Life | حياة تلقائية |
| 6329 | 152 | Cockpit Gummies | غامي قمرة القيادة |
| 6342 | 205 | Edit | تعديل |
| 6344 | 174 | Undo | تراجع |
| 6345 | 173 | Redo | إعادة |
| 6350 | 200 | Exit | خروج |
| 6355 | 155 | Add Bevels | إضافة حواف |
| 6356 | 171 | Add Curves | إضافة منحنيات |
| 6416 | 158 | Teeny Ships | السفن الصغيرة |
| 6422 | 166 | World Map | خريطة العالم |
| 6425 | 205 | Cost | التكلفة |
| 6427 | 174 | Speed | السرعة |
| 14076 | 378 | Retry | إعادة المحاولة |
| 14079 | 155 | Full Auto | تلقائي كامل |
| 14080 | 287 | Y Axis | المحور الرأسي |
| 14087 | 166 | World Map | خريطة العالم |
| 14280 | 151 | Settings | الإعدادات |
| 14291 | 166 | World Map | خريطة العالم |
| 14692 | 166 | Decal Skins | أغلفة ملصقات |
| 14699 | 194 | Teeny System | نظام السفن الصغيرة |
| 15148 | 157 | Teeny Limit Upgrade | ترقية حد السفن الصغيرة |
| 15680 | 155 | : Open Topic | : فتح الموضوع |
| 15681 | 165 | : Back | : رجوع |
| 15877 | 225 | Info Log <C 07 80 80 F0 80>▸<C 03> | سجل المعلومات <C 07 80 80 F0 80>▸<C 03> |
| 15879 | 165 | 3. Rules | 3. القواعد |
| 17584 | 157 | Grid planes used to show depth in\nthe Editor appear solid. | تظهر مستويات الشبكة المستخدمة لإظهار\nالعمق في المحرر صلبة. |
| 17746 | 157 | Slash Precharge | شحن القطع المسبق |
| 17750 | 177 | Lump/G | غامي الكتلة |
| 18321 | 214 | Ship | السفينة |
| 18322 | 187 | Grid | الشبكة |
| 18485 | 156 | Crown Gummi obtained! | تم الحصول على غامي التاج! |
| 18486 | 243 |  obtained! |  تم الحصول عليه! |
| 18497 | 170 | Edit <C 07 80 80 F0 80>▸<C 03> | تعديل <C 07 80 80 F0 80>▸<C 03> |
| 18500 | 161 | Undo/Redo | تراجع/إعادة |
| 18501 | 151 | Settings | الإعدادات |
| 18504 | 200 | Exit | خروج |
| 18506 | 159 | Edit Gummi Ship | تعديل سفينة الغامي |
| 18510 | 164 | Edit Settings | تعديل الإعدادات |
| 18513 | 216 | Exit Editor | الخروج من المحرر |
| 18686 | 287 | ON | تشغيل |
| 18687 | 152 | OFF | إيقاف |
| 18691 | 165 | : Flip pages <C 09 DB>: Back | : تقليب الصفحات <C 09 DB>: رجوع |
| 18694 | 164 | No. | رقم |
| 18786 | 169 | Teeny Ship | سفينة صغيرة |
| 18788 | 150 | Item List Complete! | قائمة الأغراض مكتملة! |
| 18796 | 194 | Teeny System | نظام السفن الصغيرة |
| 18797 | 157 | Teeny Limit Upgrade | ترقية حد السفن الصغيرة |
| 18925 | 158 | Yes | نعم |
| 18927 | 280 | OK | موافق |
| 19132 | 378 | Retry | إعادة المحاولة |
| 19134 | 166 | World Map | خريطة العالم |
| 19398 | 181 | : Assemble a new\n      Gummi Ship | : تركيب\n      سفينة غامي جديدة |
| 19407 | 171 | : Set Area   <C 09 DB>: Back\n<C 07 80 80 F0 80><C 09 EB><C 03>: Change Selection\n<C 07 80 80 F0 80><C 09 E9><C 03>: Camera | : تعيين المنطقة   <C 09 DB>: رجوع\n<C 07 80 80 F0 80><C 09 EB><C 03>: تغيير الاختيار\n<C 07 80 80 F0 80><C 09 E9><C 03>: الكاميرا |
| 19408 | 153 | : Execute   <C 09 DF>: Reselect area\n<C 07 80 80 F0 80><C 09 E8><C 03>: Set direction\n<C 09 DB>: Back | : تنفيذ   <C 09 DF>: إعادة اختيار المنطقة\n<C 07 80 80 F0 80><C 09 E8><C 03>: ضبط الاتجاه\n<C 09 DB>: رجوع |
| 19432 | 204 | : Assemble a new\n      Teeny Ship | : تركيب\n      سفينة صغيرة جديدة |
| 20500 | 162 | EX Mission | مهمة إضافية |
| 20508 | 198 | Mast/G | غامي الصاري |
| 20509 | 188 | Flag/G | غامي العلم |
| 20512 | 153 | Figure B/G | غامي الشكل ب |
| 20513 | 154 | Figure C/G | غامي الشكل ج |
| 20691 | 218 | Pipe/G | غامي الأنبوب |
| 20719 | 221 | Figure/G Set | مجموعة غامي الأشكال |
| 21696 | 155 | NOTE<C 03>\n\nNames can only contain up to 5 numbers. | ملاحظة<C 03>\n\nيمكن أن تحتوي الأسماء على 5 أرقام كحد أقصى. |

## hb.bar - 75 rows >150% by real metric (deferred, kept in the build; shorten in the text-quality pass if a screenshot shows a problem)

| id | % | EN | AR now |
|---|---|---|---|
| 2956 | 171 | Oh! | أوه! |
| 2981 | 157 | Yeah...we will, too. | نعم... سنفعل نحن أيضا. |
| 2986 | 232 | Pit Cell | زنزانة الحفرة |
| 2987 | 245 | I/O Tower | برج الإدخال والإخراج |
| 2989 | 151 | Pit Cell Guide #0 | دليل زنزانة الحفرة 0 |
| 2990 | 152 | Pit Cell Guide #1 | دليل زنزانة الحفرة 1 |
| 2991 | 151 | Pit Cell Guide #2 | دليل زنزانة الحفرة 2 |
| 2998 | 158 | Yes | نعم |
| 8149 | 169 | Hey, look! | هيه, انظروا! |
| 8151 | 188 | Come on in! | تفضلوا بالدخول! |
| 8161 | 159 | The MCP is wreaking havoc\ninside the computer. | برنامج التحكم الرئيسي يعيث فسادا\nداخل الحاسوب. |
| 8163 | 150 | Accordin´ to\nLeon, anyway... | بحسب\nليون, على الأقل... |
| 8165 | 180 | Turns out the MCP is using\nthe data in that computer<C 14 B4 00><C 10>to crank out Heartless. | تبين أن برنامج التحكم الرئيسي يستخدم\nالبيانات الموجودة في ذلك الحاسوب<C 14 B4 00><C 10>ليصنع بلا قلب. |
| 8175 | 163 | Thanks, kid.<C 10>We´re puttin´ together an\nMCP Eradication program.<C 10>I got a hunch it´s\nalmost finished, too. | شكرا يا فتى.<C 10>نجمع برنامج\nالقضاء على برنامج التحكم الرئيسي.<C 10>لدي حدس أنه\nأوشك على الانتهاء أيضا. |
| 8176 | 154 | Well, I hope your hunch\nis right for once! | حسنا, آمل أن يكون حدسك\nصحيحا لمرة واحدة! |
| 8191 | 169 | How´s Tron? | كيف حال ترون? |
| 8194 | 184 | Then I have a\nfavor to ask.<C 10>When you find Tron,\ncould you tell him to\ncome to the I/O tower?<C 10>That´s where we´ll\nupload the MCP\nEradication program. | إذن لدي\nطلب.<C 10>عندما تجدون ترون,\nهل يمكن أن تخبروه\nبالحضور إلى برج الإدخال والإخراج?<C 10>هناك سنرفع\nبرنامج القضاء على\nبرنامج التحكم الرئيسي. |
| 8195 | 178 | The I/O tower.\nGot it! | برج الإدخال والإخراج.\nفهمت! |
| 8209 | 154 | Warning.<C 14 4B 00><C 10><C 14 0F 00>User control is terminated indefinitely. | تحذير.<C 14 4B 00><C 10><C 14 0F 00>تم إنهاء تحكم المستخدم إلى أجل غير مسمى. |
| 8213 | 156 | Bon appetit! | بالهناء والشفاء! |
| 8219 | 157 | Welcome back! | مرحبا بعودتكم! |
| 8221 | 224 | A-okay! | على ما يرام! |
| 8233 | 180 | Tron is ticklish? | ترون يشعر بالدغدغة? |
| 8235 | 191 | Please stop that! | أرجوكم توقفوا عن ذلك! |
| 8249 | 151 | Let those fools play their little game! | دعوا أولئك الحمقى يلعبون لعبتهم الصغيرة! |
| 8253 | 195 | Anybody home? | هل من أحد في البيت? |
| 8263 | 189 | Oh, dear... | أوه, يا عزيزي... |
| 8265 | 161 | Uh-oh! | آه-أوه! |
| 8276 | 158 | Wanna find out? | هل تريد أن تعرف? |
| 8283 | 155 | Hey! | هيه! |
| 12384 | 171 | Oh! | أوه! |
| 12388 | 201 | Kinda cool, huh? | رائعة نوعا ما, أليس كذلك? |
| 12394 | 161 | There´s still a lot to do, but I´m\nsure we can handle everything-- | ما زال هناك الكثير لفعله, لكنني\nمتأكدة أننا نستطيع التعامل مع كل شيء-- |
| 12415 | 153 | Move! | تحرك! |
| 12464 | 153 | Hey, fellas--\nyou´re just\nin time.<C 10>Got some good\nnews for ya,<C 10>so get yerselves\nover to Leon´s. | هيه يا شباب--\nجئتم\nفي الوقت المناسب.<C 10>لدي أخبار\nجيدة لكم,<C 10>فاذهبوا\nإلى ليون. |
| 12466 | 154 | We found the\ncomputer Ansem\nwas using! | وجدنا\nالحاسوب الذي كان\nيستخدمه أنسيم! |
| 12471 | 187 | Go see for\nyerselves! | اذهبوا وانظروا\nبأنفسكم! |
| 12477 | 241 | Scoop! | سبق صحفي! |
| 12496 | 172 | Well, at least I\ncan ask the King\nabout him.<C 10>And that computer\nmight be able to tell\nus something. | حسنا, على الأقل\nأستطيع سؤال الملك\nعنه.<C 10>وربما يستطيع ذلك الحاسوب\nإخبارنا\nبشيء. |
| 12497 | 156 | Good idea! | فكرة جيدة! |
| 12501 | 153 | Hello? | مرحبا? |
| 12504 | 168 | Spikier. | أكثر تدببا. |
| 12512 | 155 | Hey! | هيه! |
| 12528 | 214 | Run! | اهربوا! |
| 12533 | 173 | Look. | انظروا. |
| 12605 | 153 | Ansem the Wise--<C 14 54 00><C 10>the real Ansem--must know the\nimposter´s true identity.<C 14 D8 00><C 10><C 14 1E 00><C 10>That´s why I´ve got to find\nhim and ask him about it. | أنسيم الحكيم--<C 14 54 00><C 10>أنسيم الحقيقي--يجب أن يعرف الهوية\nالحقيقية للمحتال.<C 14 D8 00><C 10><C 14 1E 00><C 10>لهذا علي إيجاده\nوسؤاله عن ذلك. |
| 12608 | 224 | He´s...<C 14 3C 00><C 10><C 14 54 00><C 10>I´m sorry.<C 14 48 00><C 10>I can´t help. | إنه...<C 14 3C 00><C 10><C 14 54 00><C 10>آسف.<C 14 48 00><C 10>لا أستطيع المساعدة. |
| 12620 | 173 | Outside! | في الخارج! |
| 12624 | 157 | You pathetic coward! | أيها الجبان المثير للشفقة! |
| 12627 | 161 | Uh-oh! | آه-أوه! |
| 12632 | 181 | Umm, hey...if you´re looking\nto pick sides,<C 14 90 00><C 10>why don´t you pick Leon´s?\nThey can always use help. | آه, هيه... إن كنتم تريدون\nاختيار جانب,<C 14 90 00><C 10>فلماذا لا تختارون ليون?\nيمكنهم دائما الاستفادة من المساعدة. |
| 12634 | 151 | Yeah, lots of stuff! | نعم, الكثير من الأغراض! |
| 12640 | 164 | Later, taters! | إلى اللقاء يا بطاطا! |
| 12660 | 179 | Think you can handle this many? | هل تظن أنك تستطيع التعامل مع هذا العدد? |
| 12684 | 157 | You be careful, too! | وأنتم كونوا حذرين أيضا! |
| 12696 | 151 | Scram! | ابتعدوا! |
| 12698 | 158 | I bet you can´t even fight. | أراهن أنك لا تستطيع حتى القتال. |
| 12709 | 160 | Hey, Sora! | هيه يا سورا! |
| 12715 | 154 | You sure have lotsa friends to help. | لديكم فعلا الكثير من الأصدقاء لمساعدتهم. |
| 12742 | 155 | Hey! | هيه! |
| 12776 | 150 | The guy you just saw.<C 14 5A 00><C 10><C 14 14 00><C 10>He´s their leader.<C 14 5A 00><C 10><C 14 28 00><C 10>Got it memorized?<C 14 50 00><C 10><C 14 2D 00><C 10>X-E-M, N-A-S. | الرجل الذي رأيتموه للتو.<C 14 5A 00><C 10><C 14 14 00><C 10>إنه زعيمهم.<C 14 5A 00><C 10><C 14 28 00><C 10>هل حفظته?<C 14 50 00><C 10><C 14 2D 00><C 10>ز-ي-م, ن-ا-س. |
| 12789 | 167 | Axel! | آكسل! |
| 12790 | 161 | Uh-oh! | آه-أوه! |
| 12798 | 155 | Please. | أرجوك. |
| 12803 | 150 | And yet they know not the true\npower of what they hold. | ومع ذلك لا يعرفون القوة الحقيقية\nلما يحملون. |
| 12814 | 250 | Fool... | أيها الأحمق... |
| 12828 | 165 | Yes, Sora!<C 14 3C 00><C 10><C 14 18 00><C 10>Extract more hearts! | نعم يا سورا!<C 14 3C 00><C 10><C 14 18 00><C 10>استخرج المزيد من القلوب! |
| 12837 | 176 | Liars! | كاذبون! |
| 12847 | 253 | You sure? | هل أنتم متأكدون? |
| 15173 | 155 | And maybe something on\nthe dark realm, too?<C 10>It looks like that´s where\nRiku and Kairi are. | وربما شيء ما في عالم الظلام\nأيضا?<C 10>يبدو أن هناك مكان\nريكو وكايري. |
| 15271 | 160 | Wonder if he´ll be okay. | أتساءل إن كان سيكون بخير. |
| 16065 | 172 | Roxas. | روكساس. |
| 16072 | 174 | Got any leads? | هل لديك أي خيوط? |
| 18840 | 158 | Thanks,\nMerlin! | شكرا\nيا ميرلين! |
| 18842 | 150 | Oh! One more thing.<C 10>Let me give your clothes\nsome new powers, Sora. | أوه! شيء آخر.<C 10>دعني أمنح ملابسك\nبعض القوى الجديدة يا سورا. |

## jm.bar - 118 rows >150% by real metric (deferred, kept in the build; shorten in the text-quality pass if a screenshot shows a problem)

| id | % | EN | AR now |
|---|---|---|---|
| 9914 | 156 | Pride Lands | أراضي الكبرياء |
| 10344 | 154 | The Wise Little Hen (1934) | الدجاجة الصغيرة الحكيمة (1934) |
| 10477 | 152 | Go to the wardrobe! | اذهب إلى خزانة الملابس! |
| 10517 | 169 | Go see Merlin!\n\n | اذهب لترى ميرلين!\n\n |
| 10525 | 172 | Go to the postern!\n\n | اذهب إلى البوابة الخلفية!\n\n |
| 10621 | 173 | Go see Phil!\n\n | اذهب لترى فيل!\n\n |
| 10625 | 160 | Go talk to Hercules!\n\n | اذهب وتحدث إلى هرقل!\n\n |
| 10635 | 191 | Go help Meg!\n\n | اذهب وساعد ميغ!\n\n |
| 10713 | 152 | Head for the Imperial City!\n\n | توجه إلى المدينة الإمبراطورية!\n\n |
| 10741 | 162 | Go see Pooh!\n\n | اذهب لترى بوه!\n\n |
| 10765 | 172 | Talk to Rabbit and get more honey!\n\n | تحدث إلى الأرنب واحصل على المزيد من العسل!\n\n |
| 10769 | 165 | Go to the heavily laden tree!\n\n | اذهب إلى الشجرة المحملة بالأحمال!\n\n |
| 10783 | 164 | Go to the hill with the starry sky!\n\n | اذهب إلى التل ذي السماء المرصعة بالنجوم!\n\n |
| 10791 | 157 | Head for Pride Rock! | توجه إلى صخرة الكبرياء! |
| 10793 | 153 | Leave Pride Rock! | غادر صخرة الكبرياء! |
| 10813 | 166 | Go see Simba!\n\n | اذهب لترى سيمبا!\n\n |
| 10853 | 169 | Go see Merlin!\n\n | اذهب لترى ميرلين!\n\n |
| 10913 | 155 | Go to Santa´s house for help!\n\n | اذهب إلى بيت سانتا لتطلب المساعدة!\n\n |
| 10989 | 201 | Use the solar sailer to reach the MCP!\n\n | استخدم المركب الشمسي للوصول إلى برنامج التحكم الرئيسي!\n\n |
| 11294 | 156 | Battle Royale | معركة ملحمية |
| 11308 | 156 | Ballroom Battle | معركة قاعة الرقص |
| 11352 | 171 | Avalanche! | انهيار جليدي! |
| 11356 | 160 | China´s Bravest | أشجع من في الصين |
| 11404 | 207 | All Aboard! | الجميع على المتن! |
| 11444 | 168 | Tron´s User | مستخدم ترون |
| 11446 | 271 | MCP Runs Amok | برنامج التحكم الرئيسي يعيث فسادا |
| 11449 | 154 | Sora and friends ride the solar sailer\ntoward the MCP´s central computer core | يركب سورا وأصدقاؤه المركب الشمسي نحو نواة\nالحاسوب المركزي لبرنامج التحكم الرئيسي |
| 11450 | 274 | MCP Face-Off | مواجهة برنامج التحكم الرئيسي |
| 11460 | 152 | Kairi | كايري |
| 11464 | 156 | Riku | ريكو |
| 11482 | 190 | Zexion | زيكسيون |
| 11486 | 176 | Axel | آكسل |
| 11496 | 182 | Roxas | روكساس |
| 11532 | 182 | Roxas | روكساس |
| 11552 | 151 | Vivi | فيفي |
| 11570 | 159 | Huey | هوي |
| 11580 | 174 | Cid | سيد |
| 11620 | 152 | Chip | تشيب |
| 11640 | 155 | Pegasus | بيجاسوس |
| 11650 | 151 | Cerberus | سيربيروس |
| 11656 | 167 | Demyx | ديميكس |
| 11657 | 151 | Organization <X 5E>´s Number <X 5C>.\n\nHe was surveying the world of\nOlympus, and even swiped the\nOlympus Stone. He´s a lousy\nfighter.\n\nDemyx called Sora "Roxas." | منظمة <X 5E>, العضو <X 5C>.\n\nكان يستطلع عالم\nأولمبيا, بل وسرق\nحجر أولمبيا.\nهو مقاتل سيئ.\n\nنادى ديميكس سورا باسم "روكساس". |
| 11664 | 181 | Aladdin | علاء الدين |
| 11668 | 181 | Iago | آياغو |
| 11692 | 158 | Mulan | مولان |
| 11724 | 232 | Owl | البومة |
| 11756 | 152 | Rafiki | رفايكي |
| 11774 | 151 | Ariel | آرييل |
| 11776 | 151 | Ariel | آرييل |
| 11794 | 178 | Ursula | أورسولا |
| 11806 | 152 | Chip | تشيب |
| 11842 | 162 | Dr. Finkelstein | الدكتور فينكلشتاين |
| 11886 | 151 | Tron | ترون |
| 11888 | 164 | Sark | سارك |
| 11890 | 651 | MCP | برنامج التحكم الرئيسي |
| 11918 | 182 | Saïx | سايكس |
| 11924 | 174 | Luxord | لوكسورد |
| 11930 | 182 | Roxas | روكساس |
| 11936 | 151 | Large Body | الجسد الضخم |
| 11938 | 165 | Silver Rock | الصخرة الفضية |
| 11944 | 152 | Air Pirate | قرصان الجو |
| 11946 | 155 | Trick Ghost | الشبح المخادع |
| 11948 | 192 | Rabid Dog | الكلب المسعور |
| 11950 | 242 | Hook Bat | الخفاش المعقوف |
| 11974 | 258 | Icy Cube | المكعب الجليدي |
| 11990 | 252 | Hot Rod | السيارة السريعة |
| 12020 | 155 | Neoshadow | الظل الجديد |
| 12024 | 196 | Blizzard Lord | سيد العاصفة الثلجية |
| 12030 | 186 | Dark Thorn | الشوكة المظلمة |
| 12036 | 154 | Grim Reaper | الحاصد المخيف |
| 12046 | 195 | Dusk | الداسك |
| 12048 | 160 | Dragoon | الدراغون |
| 12052 | 165 | Samurai | الساموراي |
| 12064 | 265 | Paladin | الفارس المقدس |
| 12065 | 169 | Test | اختبار |
| 12066 | 179 | Monk | الراهب |
| 12067 | 169 | Test | اختبار |
| 12130 | 248 | Notes | الملاحظات |
| 12881 | 214 | Minigames | الألعاب المصغرة |
| 13158 | 172 | Go save Kairi!\n\n | اذهب وأنقذ كايري!\n\n |
| 13943 | 151 | Tron | ترون |
| 13989 | 156 | Pride Lands | أراضي الكبرياء |
| 14241 | 162 | Reunion | لم الشمل |
| 14773 | 156 | Riku | ريكو |
| 14781 | 167 | Demyx | ديميكس |
| 14783 | 174 | Luxord | لوكسورد |
| 17248 | 285 | Bathtub | حوض الاستحمام |
| 17250 | 174 | Luxord | لوكسورد |
| 17923 | 152 | Kairi | كايري |
| 17943 | 182 | Saïx | سايكس |
| 18587 | 316 | Slain | المهزومون |
| 18636 | 180 | Maps | الخرائط |
| 18643 | 176 | See past minigame results! | شاهد نتائج الألعاب المصغرة السابقة! |
| 18651 | 180 | Maps | الخرائط |
| 18653 | 214 | Minigames | الألعاب المصغرة |
| 18654 | 175 | Limits | الليميتات |
| 18664 | 176 | See past minigame results! | شاهد نتائج الألعاب المصغرة السابقة! |
| 18676 | 150 | Use the cursor to peek inside! | استخدم المؤشر للنظر في الداخل! |
| 18961 | 193 | Total | الإجمالي |
| 18963 | 193 | Total | الإجمالي |
| 19162 | 171 | Goofy/Teamwork | غوفي/العمل الجماعي |
| 19200 | 150 | Use <C 09 E0><C 09 E1>to scroll up and down. | استخدم <C 09 E0><C 09 E1>للتمرير لأعلى ولأسفل. |
| 19206 | 174 | <X 52>Hits | <X 52>ضربات |
| 19214 | 173 | Poster Duty | مهمة الملصقات |
| 19228 | 152 | Try Maniac Mode | جرب الوضع الجنوني |
| 19243 | 151 | Light Cycle | دراجة الضوء |
| 19246 | 156 | Skateboarding | التزلج على اللوح |
| 19255 | 161 | Moogle Level<X 52> | مستوى الموغل<X 52> |
| 19378 | 180 | Try again | حاول مجددا |
| 20140 | 186 | Iron Hammer | المطرقة الحديدية |
| 20142 | 242 | Mad Ride | الركوب المجنون |
| 20284 | 152 | Fight Zexion again | قاتل زيكسيون مجددا |
| 20296 | 161 | View which puzzle? | أي أحجية تود عرضها? |
| 20298 | 168 | Collect all of the pieces and\nsolve the puzzle!\n\n<Collecting Pieces>\nSearch carefully for puzzle pieces\nscattered throughout the world.\n\nIf you find a piece you can't reach,\ncome back later when Sora has\ndeveloped new powers.\n\n<Building the Puzzle>\nPlace the pieces correctly to\ncomplete the puzzle!\n\n  <C 09 EB>: Move cursor\n  <C 09 DA>: Grab/Place\n  <C 09 DB>: Cancel\n\nSome puzzles require you to\nrotate pieces.\n\n    <C 09 E9>: Rotate piece\n\nOnce a puzzle is completed,\nyou might obtain a reward!\nGood luck!\n | اجمع كل القطع\nوحل الأحجية!\n\n<جمع القطع>\nابحث بعناية عن قطع الأحجية\nالمبعثرة في أنحاء العالم.\n\nإن وجدت قطعة لا تستطيع\nالوصول إليها, عد لاحقا\nعندما يطور سورا قوى جديدة.\n\n<تركيب الأحجية>\nضع القطع بشكل صحيح\nلإكمال الأحجية!\n\n  <C 09 EB>: تحريك المؤشر\n  <C 09 DA>: إمساك/وضع\n  <C 09 DB>: إلغاء\n\nبعض الأحاجي تتطلب\nتدوير القطع.\n\n    <C 09 E9>: تدوير القطعة\n\nبمجرد إكمال الأحجية, قد تحصل على مكافأة!\nحظا\nموفقا!\n |
| 20349 | 211 | Duality | الازدواجية |
| 20351 | 170 | Daylight | ضوء النهار |
| 20352 | 151 | Sunset | الغروب |
| 20674 | 167 | Tutorial Help | مساعدة تعليمية |
