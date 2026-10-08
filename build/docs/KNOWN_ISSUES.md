# مشاكل معروفة — Known issues (1.0.0-beta, 2026-10-07)

هذا إصدار تجريبي (beta). الأرقام مقيسة على الملفات المشحونة نفسها، وليست تقديراً.
This is a beta. Numbers are measured on the shipped files.

## 1. ما زال بالإنجليزية — Still English
| ماذا | العدد | لماذا |
|---|---|---|
| أسطر نص (رسائل) | **23 من 15552** (التعريب 99.9 %) | HP / MP / AP اختصارات مقصودة؛ نصوص مطوِّرين لا تظهر للاعب؛ `´s Status.` لا تُترجم في مكانها لأن العربية تضع الاسم بعد الكلمة؛ `Points` / `Time:` / `Round` / `Swings` في ألعاب مصغّرة (مخطط لها) |
| صور فيها نص | **538 صورة** ما زالت إنجليزية (بعضها بلا نص أصلاً) | جمل القواعد في لوحات الألعاب المصغّرة (msn)، محرّر سفينة غومي (gumiedit)، أزرار Limit (trinity)، لافتات advice، كلمات أوامر مركّبة من حروف لاتينية (po0/wi0)، نص مرسوم على خريطة |

| what | count | why |
|---|---|---|
| text rows | **23 of 15552** (99.9 % translated) | HP/MP/AP on purpose; developer/test text never shown; `´s Status.` fragments cannot be translated in place; minigame HUD words `Points`/`Time:`/`Round`/`Swings` (planned) |
| images with text | **538** still English (some have no text) | minigame rule panels, Gummi editor, Limit buttons, advice banners, letter-sprite command words, text printed on a map |

## 2. لم يُتحقَّق منه بلقطات — Not screenshot-verified
- نحو **31 %** فقط من النص رُوجع داخل اللعبة بلقطات. الباقي مبني بفحوص آلية (ترميز، عدد الأسطر، الوسوم) لكن قد تظهر أسطر **أطول من النافذة** أو كلمات تحتاج مراجعة لغوية.
- About **31 %** of the text was checked in-game. The rest passed automatic gates (encoding, line counts, tags) but some lines may **overflow their window** or need wording review.
- الخط الحالي في القوائم والحوار نسخة **اختبار** (Segoe UI Regular بتباعد أوسع): قيس أنه يزيد العرض فيفيض نحو **110 سطراً** إضافياً (79 في الحوار، 31 في jm/gumi)، ولم يجتز «بوابة الشاشة» الآلية بالكامل.
- The current menu/dialogue font is a **test** build (Segoe UI Regular, wider spacing): it makes about **110 more lines** overflow (79 dialogue, 31 in jm/gumi) and does not fully pass the automatic screen gate.
- شاشة **Load Game**: إصلاح موضع رقم المستوى (LV) مثبَّت لكنه **بانتظار لقطة** تؤكده. / **Load Game** screen: the level-number fix is installed but **awaits a screenshot**.
- كلمات أغاني عالم Pride Lands (lm، 171 سطراً) ترجمة حرّة تحتاج مراجعة متحدّث أصلي. / Pride Lands song lyrics (171 lines) are a free rendering that needs a native review.

## 3. التثبيت والتشغيل — Install / run
- **لغة اللعبة في Steam يجب أن تكون English**، وإلا لا يظهر التعريب. / **Steam game language must be English.**
- **Steam Beta:** مع عميل Steam التجريبي (Beta) قد ترفض اللعبة العمل وتظهر رسالة `SymFromAddr … tier0_s64.dll` بسبب `DBGHELP.dll` (مشكلة مفتوحة في OpenKH رقم #1290 و#1293). الحل: Steam ← الإعدادات ← الواجهة ← مشاركة Beta ← «لا مشاركة»، ثم أعد تشغيل Steam.
  With the **Steam client beta**, the launcher can fail with `SymFromAddr … tier0_s64.dll` while Panacea's DBGHELP.dll is present (OpenKH issues #1290/#1293, open). Fix: leave the Steam beta (Settings > Interface > Client Beta Participation > No beta) and restart Steam.
- **OpenKH Mod Manager:** زر Build يحذف مجلد المود كاملاً ويعيد بناءه ⇐ يختفي التعريب؛ أعد تشغيل المثبِّت بعد كل Build. / Its **Build** button deletes the whole mod folder: run this installer again after every Build.
- إن كان Panacea مثبَّتاً مسبقاً وفيه مود آخر يغيّر نفس الملفات (مثل `msg\us\sys.bar`)، فالتعريب يحلّ محلها (والأصل محفوظ `*.kh2ar.bak` ويعود عند الإزالة). / If another mod already changes the same files, the translation replaces them (originals kept as `*.kh2ar.bak`, restored on uninstall).
- إن كانت ملفات التعريب نفسها موجودة قبل التثبيت (مثلاً من حزمة المختبرين القديمة في نفس مجلد المود)، فالإزالة تحذفها أيضاً. / If identical translation files were already there (e.g. an old tester pack in the same mod folder), uninstall removes them too.
- إذا استبدلت أداة أخرى ملفاً من ملفات التعريب بعد التثبيت، فالإزالة تحذف ذلك الملف أيضاً لأنه في مسار ملفاتنا. / If another tool overwrites one of our files after install, uninstall removes that file too (same path).
- المثبِّت يطلب صلاحيات المسؤول (ليكتب `DBGHELP.dll` في مجلد اللعبة). إن كان حسابك «مستخدماً عادياً» وكتبت كلمة سر حساب مسؤول آخر، تذهب الملفات إلى مجلد ذلك الحساب ولا يراها حسابك. ثبّت من حساب المسؤول نفسه الذي تلعب منه. / The installer runs as administrator; on a standard account that elevates with **another** admin account, files land in that account's `%LOCALAPPDATA%`. Install from the account you play on.
- أغلق اللعبة قبل التثبيت أو الإزالة. / Close the game before installing or uninstalling.
- على Linux / Steam Deck (Proton) لم يُختبر: OpenKH يستعمل هناك اسم `version.dll`، والمثبِّت يضع `DBGHELP.dll` فقط. / Linux/Steam Deck is not supported by this installer (OpenKH uses `version.dll` there).
- Epic Games Store غير مدعوم في الاكتشاف التلقائي (يمكن اختيار المجلد يدوياً، لكنه لم يُختبر). / Epic Games Store: not auto-detected and not tested.

## 4. الخطوط — Fonts
الحروف العربية في الأطلس والصور مرسومة من خط Segoe UI (من Microsoft). راجع `THIRD_PARTY_LICENSES.md`.
The Arabic glyphs in the font atlases and images are rendered from Segoe UI (Microsoft). See `THIRD_PARTY_LICENSES.md`.
