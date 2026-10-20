# KH2FM_AR Manual Edition 2.0.1

Windows x64, tested Steam executable only. Same final mod hashes as the normal 2.0.1 release. Extract the entire ZIP, close KH2 and run `Install_Arabic.bat`. Select English in Steam. The script detects Steam or requests the directory containing `KINGDOM HEARTS II FINAL MIX.exe`.

No GUI installer, Electron or separately installed Node/.NET/Python is required. Portable Node 24.19.0 and a self-contained .NET 8.0.31 helper are included. OpenKH EGS/Panacea are pinned to release2-1691. Offline operation is supported. Full Arabic instructions, troubleshooting and limitations are in README_AR.md.

The package contains original-dependent compressed XOR differences, two project-owned plugins, loaders and tools. It does not bundle complete original game assets or PKG/HED archives. The helper opens your archives read-only and verifies originals before reconstructing files locally. Do not redistribute those generated files.

Uninstall: `Uninstall_Arabic.bat`. Verify: `Verify_Arabic.bat`. Undo: `Undo_Arabic.bat`. All accept `--game "directory"`. Backups/ownership use the normal manager's `.kh2fm-arabic` state. Preserve that directory. Unknown loaders and modified files are protected. Saves and Steam configuration are not edited.

Temporary preparation data is under `%LOCALAPPDATA%\KH2FM-Arabic\manual-cache`; it can be removed manually with the tools closed and regenerated later. Allow about 4 GiB of additional free space, more if previous mods need backups. No automatic update service is included. Epic, Linux and all-screen gameplay have not been tested for this edition.

https://github.com/exelight7/KH2FM_AR — unofficial fan project; no affiliation with Square Enix or Disney. Third-party notices are in licenses/.
