# Glossary decisions

Every glossary decision, one row each: term, form before, chosen form, reason,
rows changed. Decisions are made by the supervisor; the correction file for each
one is named in the last column.

| term | form before | chosen form | why | rows changed | file |
|---|---|---|---|---|---|
| Naminé | «نامين» in 22 rows, «ناميني» in 15 rows | «ناميني» everywhere | `docs/glossary.md` already approves «ناميني» (eh line 1187); the supervisor decided on 2026-10-08 to follow the glossary and change the other rows. Same form for the whole game, including the prefixed forms (لنامين → لناميني) | 22 rows: di 16808; sys 15125, 15126; tt 12241, 12274, 12276, 12313, 12314, 12316, 13289, 13389, 13402, 13403, 13511, 13527, 13528, 13567, 13588, 13601, 13603, 14316, 19915 | `corrections/glossary_namine.csv` |

## Decisions that change no row

| term | decision | why |
|---|---|---|
| «المدينة» for Twilight Town in dialogue | keep | The supervisor decided on 2026-10-08 that «المدينة» ("the town/city") in dialogue is natural speech, not an error. The place name stays «بلدة الشفق» (`docs/glossary.md` line 43). Proofreaders do not report it as a conflict. |

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
