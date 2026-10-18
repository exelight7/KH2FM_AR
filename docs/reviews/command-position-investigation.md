# Command text position: evidence and required native inputs

Base release: 1.0.19 (`c401147`). The player reports that Examine remains
above its green row in Beast's Castle after the scale change.

## Established

- The release changes message TextScale, not the native drawing origin.
  Its passed installer/update tests do not establish correct in-game alignment.
- The frozen payload has 27 remastered `*command.2dd` image directories.
  It has no corresponding original `field2d/us/*command.2dd` BAR files.
  These PNGs contain artwork, not the native layout/sequence records.
- OpenKH's message renderer assigns Position to absolute pen X/Y; it is not
  an additive offset. The earlier 1.0.15 Position prefix visibly moved the
  reaction label above the frame and was reverted. Do not repeat that guess.
- The available KH2 decompilation declares `COMMAND_DRAW::drawCurrent`,
  `drawCommandPage`, and `MESSAGEDRAW::draw_line` but does not supply their
  implementations in the reviewed files. It also targets the PS2 executable,
  not the player's Steam executable.

## Next evidence

Read the original command BARs, especially `bb0command.2dd`,
`he0command.2dd`, and `zz0command.2dd`. Determine whether the text origin
comes from their sequence/layout data or from the native drawing code.
Only then select a per-context vertical adjustment, preserving font size,
button origin, frame geometry, and the distinct primary-command rows.

The read-only exporter v3 collects the 27 layouts named by the frozen
payload, including all its world variants. It emits only those BARs and
a checksum report. Tests cover the package reader and unchanged source
files. It does not upload data or repair the alignment.

The missing files must come from the player's installation; they are not
available in this execution environment. A stable alignment-fix release
is blocked on those inputs and subsequent validation. The diagnostic
prerelease must not replace the launcher's stable update feed.
