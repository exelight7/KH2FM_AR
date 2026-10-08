# review_list - wording written by me that needs human review (Arabic)

Everything below is my own wording (not from a settled glossary entry). Please accept, correct or send a replacement; the source files are noted so I can change them.

## Phase G rewrites (installed with INSTALL_FIXG.ps1; shorter forms)
| id | file | English | now | before |
|---|---|---|---|---|
| 19904 | tt | Go. | هيا. | اذهب. |
| 12250 | tt | Hey. | هيه. | مرحبا. |
| 12254 | tt | Hi... | هاي... | أهلا... |
| 12223 | tt | Guy? | شاب? | رجل? |
| 17611 | tt | Fool. | غبي. | أحمق. |
| 1110 | sys | Use | استخدم | استخدام |
| 14643 | sys | Dark City Map | خريطة مدينة الظلام | خريطة المدينة المظلمة |
| 16480 | sys | Serenity Materials note | (dropped "المتاحة") | |
| 22019 | sys | Turn left/right tutorial note | عبر بدل باستخدام | |
| 18023/18027/18031 | sys | Sora: station on the double | سورا: يجب أن أسرع إلى المحطة! | |
| 2690, 14425 | sys | Jump to World Map? | اذهب إلى خريطة العالم? | الانتقال إلى ... |

## World mu.bar (Land of Dragons, installed)
- Names: Ping = بينغ, Mulan = مولان, Mushu = موشو, Shan-Yu = شان-يو, Captain Shang / Li = القائد شانغ / لي, Fa Zhou = فا زو, Chien-Po = تشين-بو, Yao = ياو, Ling = لينغ, Xigbar = زيغبار (not in the glossary before), Hun = الهون.
- Placeholder rows "Untranslated" (ids 4552-4585) were written as «غير مترجم».
- Mission titles/briefings (4586-4609) and the morale-gauge hints (7944-7970): all my wording («مقياس المعنويات»).
- Dialogue jokes (4180-4181, 4401, 4417-4418, 4424) are free translations.

## Image labels and popups (installed fixP3-fixP7)
- Mini-game titles and bodies: الصراع, توصيل البريد, الملصقات, كنس الخردة, قاتل النحل, SB (سباقات: حفلة الشارع / منزلق الرمال / هجوم الوقت / أسلوب حر / حفلة الورشة), البساط السحري, معركة من أجل الوقت, تدريب فيل, تحد موسيقي, تغليف الهدايا, وعاء العسل, إنقاذ في يوم عاصف, منزلق العسل, قفز البالونات, الرحلة الاستكشافية, دراجة الضوء.
- UI labels: مطلوب عمال (HELP WANTED), القائمة, جديد!, أعلى نتيجة, مال, الوقت, حصلت على مال!, المستوى التالي, ارتفع المستوى!, معلومات, خذ العلاوة!, حصلت على, الأوامر, الأصدقاء, الأشكال, دمج, اختصارات, درايف, الشكل, استدعاء.
- Popup bodies (Abilities, Auto-Reload, MP Charge, Sub-Weapons): all sentences in out\fixP7 (make_popups.py).
- Others: عرض مميز (PREMIUM SHOWCASE), شكرا لأنك لعبت!, تطوير (DEVELOPED BY), اليابانية / الإنجليزية, تم الحصول, يوميات جيميني, التركيب, متجر, احصل!, النهاية, المسرح.

## HEAVY-1 additions (coined names and conventions, all mine - please review)
- **Rikku = ريكا** (jm.bar). Riku stays ريكو. Chosen to avoid the collision; if you prefer ريكّو/ريكو2 say so.
- **Final-Fantasy numbering uses digits** (FF 7, FF 8 ...), not Arabic words.
- **Gummi**: names in the jm/gumi bars follow "X/غ" with the article dropped (the /G convention), e.g. the Gummi Ship part lists.
- **jm "Total" = المجموع** (the sys row 15303 "<X 53>المجموع" was dropped by fixQ as non-improving).
- **hb I/O Tower = برج الإدخال**; sys typo fixed in 15027: جوهرة مشتعلة (was مشتعبة).
- **Bestiary names (jm.bar)**: coined transliterations/translations, see translation\glossary.md section "jm.bar"; not from an official source.
- **Gauge = عداد** (LIMIT gauge image label عداد الليميت); the morale gauge in mu.bar still says مقياس المعنويات (decide: unify to عداد المعنويات?).
- **Lyrics (lm.bar, 171 rows)**: translation\lm_songs_ar.tsv is my own free poetic rendering; the tags <C 0E 00>/<C 0E 0A> are preserved. Needs a native read.
- **lm id 8927**: EN is "What a feeble human." (the old decode lost the W); the Arabic is unchanged.
- **Image labels (this round)**: PAUSE = إيقاف (letter-by-letter on the P A U S E sprites: P=ف A=ا U=ق S=ي E=إ); HIT = ضربة, COMBO = كومبو, MAX COMBO = أقصى كومبو; gumimenu: COMPLETION RANK = رتبة الإكمال, DESTROYED = المدمر, MEDAL = الميدالية, TREASURES = الكنوز, ABILITY = القدرة, UNITS = الوحدات, COST = التكلفة, TEENY SHIP = سفينة صغيرة; mission HUD: BOSS = الزعيم, ESCAPE = الهروب, DATA = البيانات, GATES = البوابات, SWINGS = الضربات, JUNK = الخردة, TRIES = المحاولات, PRESENTS = الهدايا, CHEST = الصندوق, WEIGHT = الوزن, STAMINA = التحمل, CHARGE = الشحن, GRIP = القبضة.


## FULL-INSTALL additions (all mine - please review)
- **Glossary decisions (Phase 0, by installed frequency):** Cure = كور (2 vs 1), Wildebeest Valley = وادي الغزلان (4 vs 1), Kingdom Hearts = كينغدوم هارتس (typo fixed). Applied to glossary.md and sys.bar (ids 13049, 14853, 14133; 22 forced rows in fixQ/sys.tsv, new sys SHA abc2419b).
- **jm.bar installed without the lam-alef ligature** (jm_noliga, 292 rows) as well as title/gumi: same unverified-atlas risk, user asked -NoLiga only for title and gumi. Reversible.
- **tt_telop day cards**: «اليوم» replaces DAY, the THE slot stays empty, ordinals الأول..الثامن (Times Bold, white, same glow model). Built, not installed.
- **FILE package words**: NEW! = جديد!, RULES = القواعد, HI-SCORE = أعلى نتيجة, Underdrome = الحلبة السفلية, Extreme = قصوى, Space Paranoids = بارانويدز الفضاء (2 lines), IMAGE = الصورة, PCT = صورة, MENU = القائمة, MISSIONS = المهام, BRIEFING = الإحاطة, TERMINAL = المحطة, WORLD MENU = قائمة العالم, BATTLE LV = مستوى القتال, PLAY TIME = وقت اللعب, TREASURES = الكنوز, COMPLETE! = مكتمل!, MUSICAL ALBUM = الموسيقي الألبوم (two sprites, right-to-left: الألبوم الموسيقي), BAD/GOOD/CLEAR/FAILED/EXCELLENT = سيئ/جيد/نجاح/فشل/ممتاز, TARGET = الهدف, NEXT = التالي.
- **Gummi ship HUD (sprite.bar)**: MISSION CLEAR = اكتملت المهمة, RANK UP! = ارتفعت الرتبة (two sprites), COMPLETION RANK = رتبة الإكمال, COMPLETION BONUS = مكافأة الإكمال, NEXT TARGET = الهدف التالي, OBTAINED = مكتسب, MAXIMUM = الأقصى, ALERT! = تنبيه!, TEENY SHIP = سفينة صغيرة.
- **es0 command atlas** (stacked words): الفريق + أمر, الاستدعاء + سحر, الصديق + غرض, تحول, اختصار, دمج, زر; lm0 BUTTON = الزر.
- **TWINS**: byte copies of already installed Arabic images into the sibling paths (menu\fm, limit\fm, gumimenu\fm, menu\us pause, eventviewer, lm_telop): the game may read either path.
