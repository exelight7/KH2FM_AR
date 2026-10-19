# Place-label native shadow

Panacea loads `kh2/dll/KH2FM_AR_PlaceTextShadow.dll` and calls `OnInit`.
The source selects built-in font mode 1 instead of mode 2 at the door-guide
and fallback entry-name call sites. It preserves the original system atlas,
metrics, text and positions. Pre-rendered entry-name images are independent.

Only two immediate operand bytes change in loaded memory. The plugin first
requires the KH2 process name, x64 build fingerprint and both complete original
function patterns. Unsupported builds and other code edits are refused.
No executable file on disk is changed; exiting discards the memory changes.

The committed 4KB DLL SHA256 is
`b18ab9db0192b816e6f95efd3bc4ca983b8006a119a6b2794ad368d24a2e2986`.
It was built with Zig 0.15.2 and has only kernel32 imports. The tested Steam
executable SHA256 is
`9002b2de6a1f91a790bd0673de125d1cf833f7942bfec827cdcf6ba64d5849ed`.
Runtime module/status checks and a real door-label screenshot verified activation
and the visible improvement on Windows. Proton gameplay remains unverified.

Compile `place_shadow.c` with `PLACE_TEST` defined to run the native private-memory
scope/guard tests. The release workflow executes these on Windows with MSVC.
The DLL exports only `OnInit` and `GetStatus`; it refuses non-game hosts.
