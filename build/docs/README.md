# تعريب Kingdom Hearts II Final Mix — الإصدار 1.0.0-beta

ترجمة هواة **غير رسمية** إلى العربية لـ Kingdom Hearts II Final Mix ضمن **KINGDOM HEARTS -HD 1.5+2.5 ReMIX-** على **Steam** (ويندوز).
لا علاقة لها بـ Square Enix أو Disney. تحتاج نسخة أصلية من اللعبة على Steam.

## التثبيت في 3 خطوات

**1) شغّل الملف `KH2FM-Arabic-Setup-1.0.0-beta.exe`**
اختر «العربية» ثم اضغط «نعم» عندما يسألك ويندوز عن الصلاحيات.

> [صورة 1: نافذة اختيار اللغة]

**إذا ظهرت شاشة زرقاء «Windows protected your PC» (SmartScreen):**
اضغط **More info** (مزيد من المعلومات) ثم **Run anyway** (تشغيل على أي حال).
السبب: المثبِّت غير موقَّع بشهادة تجارية، وهذا معتاد في مشاريع الهواة.

> [صورة 2: SmartScreen ← More info ← Run anyway]

**2) اضغط «التالي» حتى النهاية**
المثبِّت يجد اللعبة تلقائياً. إن لم يجدها سيطلب منك اختيار مجلدها، وعادةً يكون:
`C:\Program Files (x86)\Steam\steamapps\common\KINGDOM HEARTS -HD 1.5+2.5 ReMIX-`
(في Steam: كليك يمين على اللعبة ← إدارة ← تصفّح الملفات المحلية).

> [صورة 3: صفحة الملخّص قبل التثبيت]

**3) اضغط «إنهاء» ثم شغّل اللعبة من Steam كالمعتاد**
المكتبة ← KINGDOM HEARTS -HD 1.5+2.5 ReMIX- ← تشغيل ← Kingdom Hearts II Final Mix.

> [صورة 4: أول شاشة عربية داخل اللعبة]

## مهم: لغة اللعبة في Steam يجب أن تكون English
التعريب يستبدل النصوص الإنجليزية، فلا يظهر إن كانت لغة اللعبة غير الإنجليزية. المثبِّت ينبّهك إن كانت مختلفة، والتغيير هكذا:
1. في Steam افتح «المكتبة» واضغط بالزر الأيمن على KINGDOM HEARTS -HD 1.5+2.5 ReMIX- ثم «خصائص».
2. افتح تبويب «اللغة» واختر **English**.
3. انتظر حتى ينتهي Steam من التحديث، ثم شغّل اللعبة.

## برنامج الحماية (Antivirus)
بعض برامج الحماية تشتبه في الملف `DBGHELP.dll` الذي يضعه المثبِّت في مجلد اللعبة. هذا الملف هو **Panacea** من مشروع OpenKH المفتوح المصدر (محمِّل المودات)، ويعمل بأن «يحمّل نفسه» داخل اللعبة، ولهذا تشتبه فيه بعض البرامج. هذا إنذار كاذب معروف. إن حذفه برنامج الحماية فلن يظهر التعريب: أضف مجلد اللعبة إلى الاستثناءات ثم أعد تشغيل المثبِّت.

## ماذا يغيّر المثبِّت؟
- **ملفات اللعبة الأصلية لا تتغيّر.**
- يضيف ملفات التعريب في: `%LOCALAPPDATA%\KH2FM-Arabic\mod\kh2`
- إن لم يكن Panacea موجوداً: يضيف إلى مجلد اللعبة `DBGHELP.dll` ومجلد `dependencies` والملف `panacea_settings.txt` (نسخة OpenKH الرسمية release2-1691).
- إن كان Panacea موجوداً (لأنك تستعمل مودات أخرى): يبقيه كما هو ويضع التعريب في مجلد المودات الذي يستعمله، ويحفظ أي ملف يستبدله باسم `*.kh2ar.bak`.
- **ملفات الحفظ (Save) لا تُمسّ إطلاقاً.**

## الإزالة
الإعدادات ← التطبيقات ← التطبيقات المثبتة ← **KH2FM Arabic** ← إلغاء التثبيت.
تُحذف ملفات التعريب فقط، وتُعاد أي ملفات كانت قبلها، ويُحذف Panacea فقط إن كان المثبِّت هو من وضعه.

## إن كنت تستعمل OpenKH Mod Manager
زر **Build** فيه يحذف مجلد المود ويعيد بناءه، فيختفي التعريب. بعد كل Build أعد تشغيل هذا المثبِّت.

## مشاكل معروفة
انظر `KNOWN_ISSUES.md` (بعض الصور ما زالت إنجليزية، وجزء من النصوص لم يُراجَع بلقطات من اللعبة بعد).

---

# Arabic translation for Kingdom Hearts II Final Mix — 1.0.0-beta (English)

An **unofficial** fan translation of Kingdom Hearts II Final Mix in **KINGDOM HEARTS -HD 1.5+2.5 ReMIX-** on **Steam** (Windows). Not affiliated with Square Enix or Disney. You need a legal Steam copy.

## Install in 3 steps
1. Run `KH2FM-Arabic-Setup-1.0.0-beta.exe`, choose a language, accept the Windows permission prompt.
   If **"Windows protected your PC"** (SmartScreen) appears: click **More info**, then **Run anyway** (the installer is not signed with a paid certificate).
2. Click **Next** until the end. The game is found automatically; if not, pick the folder `...\steamapps\common\KINGDOM HEARTS -HD 1.5+2.5 ReMIX-`.
3. Click **Finish** and start the game from Steam as usual.

**Steam language must be English** (Library > right-click the game > Properties > Language > English). The installer warns you if it is not.

**Antivirus:** some antivirus tools flag `DBGHELP.dll` in the game folder. It is **Panacea**, the open-source OpenKH mod loader, which injects itself into the game; this is a known false positive. If it gets removed, the translation will not load: whitelist the game folder and run the installer again.

**What changes:** no original game file is modified. Translation files go to `%LOCALAPPDATA%\KH2FM-Arabic\mod\kh2`. If Panacea is missing, `DBGHELP.dll`, `dependencies\` and `panacea_settings.txt` (official OpenKH release2-1691) are added to the game folder. If Panacea is already there, it is kept and the translation goes into its mod folder; any file replaced there is kept as `*.kh2ar.bak`. Saves are never touched.

**Uninstall:** Settings > Apps > Installed apps > **KH2FM Arabic** > Uninstall. Only the translation files are removed, replaced files are restored, and Panacea is removed only if this installer added it.

**OpenKH Mod Manager users:** its **Build** button deletes and rebuilds the mod folder, which removes the translation; run this installer again after every Build.

Known issues: `KNOWN_ISSUES.md`. Credits: `CREDITS.md`. Licenses: `THIRD_PARTY_LICENSES.md`. Disclaimer: `DISCLAIMER.txt`.
