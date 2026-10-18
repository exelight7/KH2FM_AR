# Additional HD menu lowering — 1.0.18

Move the 264 nonempty HD system glyph bodies down one more texel relative
to 1.0.17, keeping their sizes, advances and visible pixel values intact.

The isolated and final ya cells (20 and 31) already use the final cell row
for their lower dots. Their body moves down; their dot group retains rows
44–47. This tightens the body-to-dot gap by one HD texel. Both dot shapes
and every visible body/dot pixel are retained. The opaque body and both
dots remain three separate components with their original component sizes.
All other glyph cells receive an exact independent one-row translation.

SD, fontinfo, dialogue and messages remain byte-identical to 1.0.17. No
Position command, wrapping, glyph stretching or HUD layout patch is used.
The source is SHA256-pinned ../menu-fine-alignment/font-overlay.zip.
Font licensing remains in ../menu-legibility/.

```sh
python experiments/fonts/menu-lower-baseline/sources/align_font.py --verify
python build/tools/check_font_texture.py experiments/fonts/menu-lower-baseline/font-overlay.zip
```

The comparison is an atlas simulation; the final on-screen margin needs
confirmation in the original game renderer.
