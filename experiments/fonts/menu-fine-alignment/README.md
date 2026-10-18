# Fine HD menu alignment — 1.0.17

Translate all 264 nonempty system font cells down exactly one HD texel from
the SHA256-pinned menu-alignment overlay. This is half an original SD pixel,
so the native SD atlas stays byte-identical rather than being resampled.
The two deepest cells use the final row of their 48-row cell after the move.
No visible pixels are discarded or wrapped into another cell.

Glyph size, horizontal spacing, color and alpha values remain unchanged.
Font metrics, fontimage.bar, the dialogue PNG and every message byte retain
their published 1.0.16 values. In particular, no Position command is added.
The adjustment applies to the shared HD menu font, including green reaction
labels, primary commands, digits and punctuation, keeping their baseline
consistent. This is a small font adjustment, not a HUD-layout replacement.

```sh
python experiments/fonts/menu-fine-alignment/sources/align_font.py --verify
python build/tools/check_font_texture.py experiments/fonts/menu-fine-alignment/font-overlay.zip
```

The comparison is an atlas simulation, not an in-game screenshot. The final
visual margin still requires confirmation in the original game renderer.
Font source and SIL OFL licensing remain in ../menu-legibility/.
