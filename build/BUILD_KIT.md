# BUILD_KIT - rebuild the Arabic text bars and the installer without the original PC

Contains no game files, fonts, images or Panacea binaries. Linux or Windows runner; Python 3.12+ (stdlib only, tested on 3.12).
Tested versions: Python 3.12, Inno Setup 6.7.3 (Windows only, installer step), OpenKH release2-1691 (Panacea, downloaded at build time).

## Files

| path | what it does |
|---|---|
| `tools/arabic_msg.py` | Message encoder/decoder: Arabic shaping (4 forms), visual (RTL) order, lam+alef ligature, command tags, `msgs()` read a bar, `replace_msg()` rewrite one message (offsets/sizes fixed). Python port of `Shape / ToVisualOrder / EncodeMsg`. |
| `tools/width.py` | Width tool: reads the advance table from `fontinfo.bar` at build time (not shipped) and measures the widest line of a message. `python tools/width.py <fontinfo.bar> <bar> [id..]` |
| `tools/selftest.py` | Self-test (below). |
| `tools/fetch_panacea.py` | Downloads the official OpenKH release from `config/panacea.json`, checks the zip SHA256 and 14 file SHA256s, extracts to `vendor/`. |
| `tools/gen_iss_files.py` | Payload-list generator: `config/FROZEN_MANIFEST.tsv` -> `installer/payload_files.iss` (one `[Files]` line per payload file with SHA256 check). |
| `tools/privacy_scan.py` | `python tools/privacy_scan.py <folder> <needle>...` must print `0 hits` before publishing. |
| `tables/allocation.tsv` | Arabic letter + form -> font cell (the shaping table). |
| `tables/codemap.tsv` | Cell -> character for Latin/digits/punctuation (non-Arabic cells). |
| `tables/cmd_sizes.tsv` | Command-byte parameter sizes (command-size table; `0E` = 1). Boundary commands `10 14 17`, icon `09` are constants in `arabic_msg.py`. |
| `tables/bar_options.tsv` | Per-bar options of the INSTALLED build: atlas (`sys`/`evt`) and lam+alef ligature on/off. Ligature ON: tt di es wm hb mu bb he dc ca al nm lk lm tr po wi eh. OFF (no ligature, cell 36 is Latin W): sys jm title gumi. |
| `tables/noliga_ids.txt` | Message ids that never use the ligature in any bar (popup/help ids drawn from the sys atlas, bb included). |
| `config/panacea.json` | Panacea download URL + SHA256s (zip and each file), Inno Setup version/SHA256. |
| `config/expected_bars.sha256` | SHA256 of the 22 installed text bars (also below). |
| `config/FROZEN_MANIFEST.tsv` | path, size, SHA256 of all 798 installed payload files (bars, fontinfo, fontimage, PNG/DDS overrides). |
| `installer/kh2fm_arabic.iss` | Inno Setup script (paths relative to `installer/`). |
| `docs/` | Player docs packed by the installer: README, KNOWN_ISSUES, CREDITS, THIRD_PARTY_LICENSES, DISCLAIMER; `docs/licenses/`. |
| `tools/build_bars.py` | Release build: consistency gate (kit decode vs `review/*.csv`), applies `corrections/*.csv`, measures `needs_width_check.csv` terms with real widths (all rows of a term or none), runs every gate, writes `out/kh2/msg/us/*.bar`, `out/MANIFEST.tsv`, `report/BUILD_REPORT.md`, `report/CHANGELOG.md`. |
| `tools/verify_payload.py` | Checks a payload folder (`<dir>/kh2/...`) against a manifest: every file, size and SHA256, no extra files. |
| `config/consistency_known.tsv` | The 19 review rows whose AR differs from the kit decode of the installed bars (15 retail-English rows, 4 sys rows with a tag/space the review export lacks). Accepted only while none of them has a correction. |
| `reference/Program.cs` | Original C# tool (read-only reference). `FixState` (colour/size state commands re-ordered for RTL), `Batch`, etc. live here and are NOT ported to Python; machine paths replaced by `<OPENKH_DIR>` / `<PROJECT_DIR>`. |

## What the kit can and cannot do

- CAN: decode any message of an installed bar to Arabic text, re-encode it byte-identically, apply a correction to one id (`replace_msg`), measure widths, rebuild the installer around a supplied payload.
- CANNOT (needs inputs not in the repo): turn translation TSVs into bars from scratch (that includes `FixState`, only in `reference/Program.cs`), or produce the payload PNG/fontinfo/fontimage files. The build job must supply the payload (laid out as `config/FROZEN_MANIFEST.tsv`) as `payload/kh2/...`.
- Untranslated retail-English rows whose cells overlap Arabic glyph cells (15 rows: sys 14, dc 1) cannot be shaped as Arabic; they round-trip in plain mode (`decode(raw, False, False)`), exactly what `selftest.py` does.

## Build steps

```
# 1. self-test (needs the installed bars: a folder with sys.bar tt.bar ... gumi.bar)
python tools/selftest.py <BARS_DIR>

# 2. apply corrections (example)
python - <<'PY'
import sys; sys.path.insert(0, 'tools'); import arabic_msg as A
bar = 'tt'; b = open('<BARS_DIR>/tt.bar', 'rb').read()
lig = A.use_lig(bar, 2865)
txt = A.decode(A.msgs(b)[2865], True, lig)          # edit txt here
open('out/tt.bar', 'wb').write(A.replace_msg(b, 2865, A.encode(txt, lig)))
PY

# 3. installer (Windows runner)
python tools/fetch_panacea.py                        # -> vendor/openkh-release2-1691 (hash-checked)
# place payload at payload/kh2/... (see config/FROZEN_MANIFEST.tsv); verify SHA256 of each file against it
python tools/gen_iss_files.py                        # -> installer/payload_files.iss
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\kh2fm_arabic.iss     # -> dist/KH2FM-Arabic-Setup-1.0.0-beta.exe
```

Inno Setup: install 6.7.3 (released build used `innosetup-6.7.3.exe`, SHA256 in `config/panacea.json`). Edit `AppVer` in the .iss to bump the version. Never commit `vendor/`, `payload/` or `dist/`.

## Expected SHA256 of the installed bars (`msg/us/*.bar`)

| bar | SHA256 |
|---|---|
| sys.bar | `1cc7aa19168379b14f357a48cb7270dc22f6c10fdb00e1ad70578bdf894bd4e7` |
| tt.bar | `799cced67e607fca372673df56d1650ab188ab7f3acafbe03bedc51d2394cc7c` |
| di.bar | `cd03aa7b4b8968e8490d8b40ff8bd7c61daf1faadec1229b4c0094e5aa71811e` |
| es.bar | `6f0480693745c9755f5cfed2df45c5b58e8437189555d17c4f3aaa8f09987507` |
| wm.bar | `76de984f7307b8a40f2f9059eb174de5caab68d17b5262b98184fb63bb153d40` |
| hb.bar | `39c53640b4327ded4bbf102803f6723887875f478ac520fdfa8e1f9892995b5e` |
| mu.bar | `d3199dfa6832cdf0314e8e5f6965e181537f80879400c04941fa225d779e9652` |
| bb.bar | `e3bcdbc7dd3beafd0f9b56fdef3e279bda3f38ca26c7198dd112e89ba188d94c` |
| he.bar | `5c00e59fcf6468de1d853f10849fe9a4603c63b1672b058fee078dc87257be3a` |
| dc.bar | `a52369b2953678a4b3b2663f8cfb8b7579554664902ddeaf6415cf09ffa98129` |
| ca.bar | `46ebac9f1654dbbde18f1addaadc5714013cabe54fe22fef7d27b74afc7e9ad5` |
| al.bar | `0a0303b4fd877301e1d81eedfa4809b24c49e9efb6a17e896b194312707085e0` |
| nm.bar | `0aaa565837a5e64440a048fc18fd1d9ad86b568f6e46b336e530ceba26a084ee` |
| lk.bar | `a89f8f07333bb30501fbd73609fa9a24619458bf5ae8142c4af45ebfe625c8a3` |
| lm.bar | `3e6ec1493bf1c44192ac6fc65cddfbb171da4c55e18c66c547e439ef1f091fd5` |
| tr.bar | `b1bd578a78683045e1d1b9157649d7dadff7b8bf7764d003f4f23c94233678e1` |
| po.bar | `ab808451fa3a7ba870da47e1f7c47ed0c3e0a59981e473253a68ef2b8022b987` |
| wi.bar | `2a30709c70a316b02995b203394ad177fd95d1f28a8764a797a188eb0ca69a88` |
| eh.bar | `db69a9936863ae542937198f89383e9e999e967c0c58c7cfedd3609587faf087` |
| jm.bar | `25bf3108dbe8f0e316c5df4df55f8ef236cfd7abd8c34a961bb15dee301d5c5b` |
| title.bar | `82348f57a393cd60daea3b4a6a1e8045b81c0e9d33ff82602145241089e6ba79` |
| gumi.bar | `656655a00407dc5f2c5ee874099c3c1ec8e5fadfdd31f5e08eee91a6ddb54c8b` |

## Self-test result (round BUILD-KIT)

See `state/LAST_REPORT.md` of the source project; the script prints `SELFTEST PASS` and returns 0.

## Automated release build (`.github/workflows/build-release.yml`)

Triggers: manual (`workflow_dispatch`, input `version`, default 1.0.1) or a push to a `build/**` branch.

1. Linux: download `build-payload-1.0.0-beta.zip` from the `build-payload` release; `verify_payload.py` (798 files); `selftest.py` on the payload bars; `build_bars.py --version <v>` (gates b-e, report, changelog); upload `out/` + `report/`.
2. Windows: download the payload again, overlay the new bars, verify against the new `out/MANIFEST.tsv`; `fetch_panacea.py`; install Inno Setup 6.7.3 (SHA256 checked); `gen_iss_files.py out/MANIFEST.tsv`; README version + CHANGELOG; `ISCC /DAppVer=<v> /DAppVerNum=<v>.0`; `SHA256SUMS.txt`; upload; create or replace the DRAFT release `v<v>` (refuses to touch a published release).
