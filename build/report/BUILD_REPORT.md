round: BUILD-1.0.14

# Build report 1.0.14

**Result: ALL GATES PASS.** 1855 messages changed in 22 bars; 14403 other messages byte-identical.

## Gates

| gate | result | detail |
|---|---|---|
| b. consistency (kit decode == review AR) | PASS | 15552 review rows compared, 19 differ: 19 accepted (config/consistency_known.tsv: dc 18407, sys 1444, sys 1445, sys 1446, sys 1447, sys 1448, sys 1449, sys 2774, sys 14844, sys 17753, sys 17838, sys 17839, sys 19352, sys 19353, sys 19354, sys 19388, sys 19600, sys 19862, sys 19998), 0 unexpected |
| c0. one correction per id | PASS | 1851 corrections in 83 files, no id twice |
| c1. AR_old equals the current text | PASS | all 1851 rows |
| d0. width rows readable | PASS | 22 rows in 15 terms/rows measured |
| e0. every correction encodes (allowed characters) | PASS | all 1855 encoded |
| e1. only intended ids differ | PASS | 1855 messages changed, 1855 intended |
| e2. every untouched message byte-identical | PASS | 14403 untouched messages identical |
| e3. round-trip (decode == AR_new, re-encode identical) | PASS | all 1855 changed messages |
| e4. tags and line breaks equal to the old row | PASS | all 1855 changed messages |
| e5. allowed cells only (no new unknown cell) | PASS | all 1855 changed messages |
| e6. bars re-parse | PASS | 22 bars, 16258 messages parsed |
| e7. payload files = FROZEN_MANIFEST (input) | PASS | 798 files, size and SHA256 match |
| e8. all other payload files unchanged in the new manifest | PASS | 776 of 798 files unchanged, 22 bars replaced |

## Changes per bar

| bar | proofreading | glossary | shorten | width-check term | total | new SHA256 |
|---|---:|---:|---:|---:|---:|---|
| sys | 121 | 280 | 5 | 2 | 408 | `9eeb0c5a7427c9b0…` |
| tt | 239 | 61 | 1 | 1 | 302 | `bc5ed2b4abddc1eb…` |
| di | 3 | 1 | 1 | 0 | 5 | `800ab16a5b1bbeae…` |
| es | 4 | 1 | 1 | 0 | 6 | `0a1522ea9c8fb719…` |
| wm | 7 | 6 | 5 | 0 | 18 | `abf0530bb09c7ca8…` |
| hb | 104 | 16 | 14 | 0 | 134 | `dbc3ec138a2f2b8c…` |
| mu | 37 | 13 | 6 | 1 | 57 | `d1cc64318e0f6112…` |
| bb | 44 | 2 | 5 | 0 | 51 | `7fe7c349d6762211…` |
| he | 67 | 33 | 2 | 0 | 102 | `44e64d876d8dac1e…` |
| dc | 12 | 0 | 1 | 0 | 13 | `840087a4251b6083…` |
| ca | 47 | 3 | 3 | 0 | 53 | `f9bb15841d23f438…` |
| al | 49 | 1 | 3 | 0 | 53 | `e9c01be887602475…` |
| nm | 42 | 0 | 6 | 0 | 48 | `9921674751a0cbda…` |
| lk | 42 | 4 | 3 | 0 | 49 | `55adf197eee6efe6…` |
| lm | 47 | 0 | 6 | 0 | 53 | `8559314ce46de1ea…` |
| tr | 16 | 4 | 6 | 0 | 26 | `2ba62d66cf5a4c22…` |
| po | 38 | 0 | 0 | 0 | 38 | `779b344765536b38…` |
| wi | 38 | 0 | 1 | 0 | 39 | `af2c14f9a61d1e90…` |
| eh | 55 | 2 | 2 | 0 | 59 | `7902d64fbd67ec20…` |
| jm | 142 | 124 | 9 | 0 | 275 | `27830141af2cca2e…` |
| title | 5 | 6 | 4 | 0 | 15 | `d25d29a92a75e588…` |
| gumi | 7 | 22 | 22 | 0 | 51 | `a5ad28bd79cb6f76…` |
| **total** | **1166** | **579** | **106** | **4** | **1855** | |

## needs_width_check.csv: real widths

Width = widest line in font units from `fontinfo.bar` (sys or evt atlas). English width = old width / (width_pct / 100). A row fits if new ≤ 130% of English or new ≤ old. A term is applied only if all its rows fit.

| term / row | applied | rows: bar id — English → old → new width (new % of English, review width_pct) |
|---|---|---|
| DTD | no | hb 2958 — 27 → 26 → 77 (284%, was 94%) ✗; hb 12536 — 159 → 198 → 200 (126%, was 124%) |
| Whirli-Goof / -ra / -ga | no | jm 19195 — 220 → 214 → 214 (97%, was 97%); sys 1176 — 54 → 68 → 83 (153%, was 126%) ✗; sys 1177 — 65 → 86 → 101 (155%, was 133%) ✗; sys 1178 — 65 → 88 → 102 (157%, was 135%) ✗; sys 13116 — 198 → 176 → 134 (68%, was 89%) |
| (row) mu 4188 | yes | mu 4188 — 143 → 176 → 184 (129%, was 123%) |
| Postern | no | sys 732 — 38 → 74 → 88 (232%, was 194%) ✗ |
| Auto | no | sys 14110 — 21 → 22 → 38 (177%, was 105%) ✗; sys 17154 — 21 → 22 → 38 (177%, was 105%) ✗; sys 17239 — 62 → 82 → 97 (156%, was 131%) ✗ |
| Reprogram | no | sys 14625 — 51 → 38 → 89 (176%, was 76%) ✗ |
| (row) sys 14910 | yes | sys 14910 — 181 → 118 → 162 (90%, was 65%) |
| Grind | no | sys 16941 — 25 → 36 → 46 (181%, was 140%) ✗ |
| MCP | no | sys 18066 — 166 → 184 → 260 (157%, was 111%) ✗ |
| (row) sys 20624 | yes | sys 20624 — 167 → 172 → 206 (123%, was 103%) |
| (row) tt 12251 | no | tt 12251 — 46 → 44 → 78 (170%, was 94%) ✗ |
| (row) tt 13772 | yes | tt 13772 — 180 → 187 → 215 (120%, was 104%) |
| (row) tt 13787 | no | tt 13787 — 50 → 44 → 68 (137%, was 88%) ✗ |
| (row) tt 19004 | no | tt 19004 — 72 → 68 → 120 (167%, was 94%) ✗ |
| 100 Acre Wood | no | wm 18554 — 126 → 154 → 190 (152%, was 123%) ✗ |

## Consistency (review CSV vs installed bars)

15552 rows compared; 15 decoded in plain-English mode; differences: dc 18407, sys 1444, sys 1445, sys 1446, sys 1447, sys 1448, sys 1449, sys 2774, sys 14844, sys 17753, sys 17838, sys 17839, sys 19352, sys 19353, sys 19354, sys 19388, sys 19600, sys 19862, sys 19998.

Inputs: payload from the `build-payload` release, verified against `config/FROZEN_MANIFEST.tsv`; corrections from `corrections/`.
