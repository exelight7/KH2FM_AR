# KH2FM_AR

<div dir="rtl">

## تعريب Kingdom Hearts II Final Mix
https://x.com/psycho_njjm
مشروع مجاني من المعجبين لتعريب نصوص لعبة **Kingdom Hearts II Final Mix**
(ضمن مجموعة Kingdom Hearts HD 1.5+2.5 ReMIX على Steam). المشروع غير رسمي ولا علاقة له
بـ Square Enix أو Disney، ولا يحتوي على ملفات اللعبة.

### للاعبين

حمّل برنامج التثبيت من صفحة
[الإصدارات (Releases)](https://github.com/exelight7/KH2FM_AR/releases)
واتبع التعليمات المرفقة به. لا تحتاج إلى أي ملف من هذا المستودع.

### للمساهمين: مراجعة النص العربي

النص العربي المثبّت في اللعبة موجود في المجلد `review/` (75 ملفاً، 15552 سطراً).
الأعمدة: `bar,id,EN,AR,width_pct,flags`.

1. اختر ملفاً غير مُنجز من `docs/TASKS.md`.
2. اقرأ `RULES.md`: الأحرف المسموحة، الوسوم مثل `<10>` و`<X 5E>` تبقى كما هي
   وبنفس الترتيب، عدد فواصل الأسطر `⏎` لا يتغير، أسماء المسرد
   (`docs/glossary.md`) لا تتغير، والتصحيح لا يزيد طوله عن 10% أو حرفين، أيهما أكبر.
3. لا تعدّل `review/` أبداً. اكتب تصحيحاتك في ملف
   `corrections/<FILE>.csv` بالأعمدة
   `bar,id,AR_old,AR_new,type,severity,reason`:
   النص الحالي كما هو، النص المصحح، نوع الخطأ
   (`spelling` | `grammar` | `phrasing` | `meaning` | `glossary`)،
   الدرجة (1 بسيط، 2 واضح، 3 يغيّر المعنى)، وسبب بالعربية في 8 كلمات أو أقل.
4. شغّل `python tools/validate_corrections.py` وأصلح الأخطاء حتى تظهر `PASS`.
5. افتح طلب دمج (Pull Request). يشغّل GitHub الفحص نفسه تلقائياً
   (**validate**) على كل طلب يغيّر `corrections/` أو `tools/`، ولا يُدمج
   الطلب إلا إذا نجح الفحص.

للمراجعة عبر جلسة Claude في السحابة استخدم النص الجاهز في `docs/CLOUD_PROMPT.md`.

</div>

---

## Arabic translation of Kingdom Hearts II Final Mix

A free fan project that translates the text of **Kingdom Hearts II Final Mix**
(part of Kingdom Hearts HD 1.5+2.5 ReMIX on Steam) into Arabic. It is
unofficial, not affiliated with Square Enix or Disney, and contains no game
files.

### Players

Download the installer from the
[Releases page](https://github.com/exelight7/KH2FM_AR/releases) and follow the
instructions that come with it. You do not need anything else from this
repository.

### Contributors: proofreading the Arabic

The Arabic installed in the game is in `review/` (75 files, 15,552 rows),
columns `bar,id,EN,AR,width_pct,flags`.

1. Pick an unchecked file in `docs/TASKS.md`.
2. Read `RULES.md`: allowed characters, tags such as `<10>` and `<X 5E>` kept
   exactly and in order, the same number of `⏎` line breaks, glossary terms
   (`docs/glossary.md`) never changed, and a correction at most 10% (or 2 characters,
   whichever is larger) longer.
3. Never edit `review/`. Put your corrections in `corrections/<FILE>.csv` with
   the columns `bar,id,AR_old,AR_new,type,severity,reason`: the current text
   exactly, the corrected text, the type
   (`spelling` | `grammar` | `phrasing` | `meaning` | `glossary`), the severity
   (1 minor, 2 clear, 3 changes the meaning) and a reason in Arabic, 8 words at
   most.
4. Run `python tools/validate_corrections.py` and fix errors until it prints
   `PASS`.
5. Open a pull request. GitHub runs the same check automatically
   (**validate**) on every pull request that touches `corrections/` or
   `tools/`; a pull request is merged only when it passes.

For a Claude cloud session, use the ready-made prompt in `docs/CLOUD_PROMPT.md`.

### Repository layout

| path | contents |
|---|---|
| `review/` | the installed Arabic, one CSV per part (read-only) |
| `corrections/` | correction files, one per review file or task |
| `RULES.md` | proofreading rules (also read by the validator) |
| `tools/validate_corrections.py` | the automatic check |
| `tests/` | validator tests (`python -m unittest discover -s tests`) |
| `docs/TASKS.md` | the task list: 75 review files, GLOSSARY, SHORTEN |
| `docs/CLOUD_PROMPT.md` | prompt for a cloud proofreading session |
| `docs/glossary.md` | approved names and terms |
| `docs/consistency.md`, `docs/review_list.md`, `docs/long_rows.md` | open naming conflicts, wording to review, rows too wide for the screen |
