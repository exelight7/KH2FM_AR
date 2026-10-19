# Menu and reaction-command legibility — 1.0.12

The user confirmed the green reaction command and command menu are too small,
not clipped. This overlay changes only the shared system/menu font; the
published 1.0.11 dialogue atlas and its advance table remain byte-identical.

- Noto Sans Arabic Condensed Medium at 26 HD pixels (was Regular at 22).
- Native width-axis design (75), weight 500; no per-glyph stretching.
- 117 Arabic menu cells; 1,145 HD/SD joining pairs and 478 nonjoining pairs.
- All 3,031 encodable system-font review rows fit the frozen original font
  width budget. The 14 retail-English debug rows retain their native cells.
- The separate `build/tools/enlarge_commands.py` prefixes scale 18/16 to 234
  reaction/primary command labels, preserving every original control byte.
- `build/tools/replace_command_labels.py` redraws 55 baked labels in five
  small-label world atlases. Outside-slot pixels and dimensions are unchanged.
  Existing glossary choices are used for the baked Limit label (الذروة).

Run from the repository root:

```sh
python experiments/fonts/menu-legibility/sources/build_font.py --verify
```

The comparison PNG is an atlas simulation, **not** an in-game screenshot.
In-game appearance still requires the player to verify the release.

## Font provenance

Google Fonts source:
https://github.com/google/fonts/tree/main/ofl/notosansarabic
Variable source `NotoSansArabic[wdth,wght].ttf` SHA256:
`63111b5b2e074dd48cc67692e0a2726d86ee94c1c37fe8598257b7b4e87e869e`.
The committed static font was instantiated with fontTools 4.61.1 at
`wdth=75, wght=500`; its SHA256 is
`d291afc97a28d97ee0e4063e11314d091efd54261b2db2013daee31a7a6b5254`.
The accompanying `fonts/OFL.txt` is the upstream SIL Open Font License.
The renderer uses the committed static font and does not fetch a mutable
remote font during the build.
