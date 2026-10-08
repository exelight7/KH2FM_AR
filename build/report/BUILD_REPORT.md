round: BUILD-1.0.1

# Build report 1.0.1

**Result: ALL GATES PASS.** 728 messages changed in 22 bars; 15530 other messages byte-identical.

## Gates

| gate | result | detail |
|---|---|---|
| b. consistency (kit decode == review AR) | PASS | 15552 review rows compared, 19 differ: 19 accepted (config/consistency_known.tsv: dc 18407, sys 1444, sys 1445, sys 1446, sys 1447, sys 1448, sys 1449, sys 2774, sys 14844, sys 17753, sys 17838, sys 17839, sys 19352, sys 19353, sys 19354, sys 19388, sys 19600, sys 19862, sys 19998), 0 unexpected |
| c0. one correction per id | PASS | 724 corrections in 78 files, no id twice |
| c1. AR_old equals the current text | PASS | all 724 rows |
| d0. width rows readable | PASS | 22 rows in 15 terms/rows measured |
| e0. every correction encodes (allowed characters) | PASS | all 728 encoded |
| e1. only intended ids differ | PASS | 728 messages changed, 728 intended |
| e2. every untouched message byte-identical | PASS | 15530 untouched messages identical |
| e3. round-trip (decode == AR_new, re-encode identical) | PASS | all 728 changed messages |
| e4. tags and line breaks equal to the old row | PASS | all 728 changed messages |
| e5. allowed cells only (no new unknown cell) | PASS | all 728 changed messages |
| e6. bars re-parse | PASS | 22 bars, 16258 messages parsed |
| e7. payload files = FROZEN_MANIFEST (input) | PASS | 798 files, size and SHA256 match |
| e8. all other payload files unchanged in the new manifest | PASS | 776 of 798 files unchanged, 22 bars replaced |

## Changes per bar

| bar | proofreading | glossary | shorten | width-check term | total | new SHA256 |
|---|---:|---:|---:|---:|---:|---|
| sys | 64 | 163 | 5 | 2 | 234 | `075f6818ffcf24c9…` |
| tt | 69 | 46 | 6 | 1 | 122 | `3dd6d9dfbdf22428…` |
| di | 1 | 1 | 1 | 0 | 3 | `73c58919de218836…` |
| es | 0 | 0 | 1 | 0 | 1 | `9928a5372975965d…` |
| wm | 2 | 1 | 5 | 0 | 8 | `975b9d78c0c3ea32…` |
| hb | 7 | 9 | 15 | 0 | 31 | `51e1ed9327706ecb…` |
| mu | 3 | 12 | 6 | 1 | 22 | `d7ad43e19402bee7…` |
| bb | 5 | 0 | 5 | 0 | 10 | `3adfd145df096fc9…` |
| he | 11 | 25 | 2 | 0 | 38 | `b4e154be72f7d3b1…` |
| dc | 2 | 0 | 1 | 0 | 3 | `7d259d64e904d53d…` |
| ca | 3 | 2 | 3 | 0 | 8 | `ae9c3522195f3995…` |
| al | 3 | 0 | 3 | 0 | 6 | `701ce5a10f375935…` |
| nm | 5 | 0 | 6 | 0 | 11 | `59c0cc5a84ec28a2…` |
| lk | 1 | 4 | 3 | 0 | 8 | `07727c7761137c62…` |
| lm | 2 | 0 | 6 | 0 | 8 | `50f56b1f5b0608fb…` |
| tr | 1 | 3 | 6 | 0 | 10 | `7e5ac067de366fea…` |
| po | 6 | 0 | 0 | 0 | 6 | `1decf7d58bb1e562…` |
| wi | 4 | 0 | 1 | 0 | 5 | `fd3e57c63ed17b4d…` |
| eh | 4 | 0 | 2 | 0 | 6 | `243aefba7fcd8727…` |
| jm | 19 | 111 | 11 | 0 | 141 | `fccee11e5f08217a…` |
| title | 0 | 6 | 4 | 0 | 10 | `436c6ee274fba0b7…` |
| gumi | 0 | 15 | 22 | 0 | 37 | `a0cfa1744ee0ae80…` |
| **total** | **212** | **398** | **114** | **4** | **728** | |

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
