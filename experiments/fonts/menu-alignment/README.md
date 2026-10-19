# Menu baseline alignment — 1.0.13

The player confirmed that the green reaction label is too high and touches
the upper frame in 1.0.12. Move the shared system/menu glyphs down by 4 HD
pixels (2 SD pixels), with no resizing and no horizontal movement.

All 264 nonempty system cells move together, including Arabic, digits and
punctuation, so their common baseline remains intact. Transparent padding
replaces wrapping. The build rejects any translation that would discard
visible pixels. Every HD alpha value and every SD coverage level is retained.
At least one transparent HD row remains below the deepest glyph.

The source is the SHA256-pinned `../menu-legibility/font-overlay.zip` from
1.0.12. Font advances, the dialogue atlas, message bytes (including 18/16
command scaling), and baked menu images retain their published 1.0.12 bytes.
Only the system section of fontimage.bar and its HD PNG change.

```sh
python experiments/fonts/menu-alignment/sources/align_font.py --verify
```

`comparison-alignment.png` is an atlas simulation, not a game screenshot.
The player still needs to confirm the final margin in the real HUD.
Font source and SIL OFL licensing remain in `../menu-legibility/`.
