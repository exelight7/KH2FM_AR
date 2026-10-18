# Context alignment and location separator — 1.0.19

The primary command rows and the green reaction row share the sys atlas but
have different native drawing origins. A shared atlas translation cannot
raise Attack/Items while lowering Save/Talk/Examine.

`build/tools/enlarge_commands.py` keeps those origins and all original message
bytes, changing only the existing TextScale prefix:

| Context | IDs | Old scale byte | New scale byte |
| --- | --- | --- | --- |
| Primary HUD | 480, 481, 482, 483, 1284, 1287 | 18 | 17 |
| Green actions | 225 names matched from sys 1444–1449, plus 490, 491, 1286 | 18 | 20 |

At a fixed native pen, the primary letters shrink by 5.56% relative to 1.0.18,
moving their ink up; green letters grow by 11.11%, extending their ink down.
This deliberately changes size as well as the visible ink position. It is
not a pure translation or a patch to the original HUD layout. All 234
widths remain within the original frozen-font budgets. The three colored,
icon-bearing help messages 22020–22022 are deliberately excluded.

The Arabic glyphs themselves remain pixel-identical to 1.0.18. Only the
oversized native colon is replaced with a 26px Noto Sans Arabic Condensed
Medium colon, in HD and SD, with the same advance. The colon's visible HD
height drops from 19 to 15 pixels, and its bottom matches baseline 37.
Every other atlas pixel, fontinfo byte and dialogue byte is preserved.
Font license: ../menu-legibility/FONT_SOURCE_LICENSE.txt.

```sh
python experiments/fonts/menu-context-alignment/sources/fix_separator.py --verify
python build/tools/check_font_texture.py experiments/fonts/menu-context-alignment/font-overlay.zip
```

The comparison is an atlas simulation. Native game rendering and the final
in-frame optical balance cannot be verified in the build environment.
