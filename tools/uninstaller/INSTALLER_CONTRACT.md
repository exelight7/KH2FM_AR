# Stable installer contract, Schema 1

This contract lets the standalone uninstaller read future translation releases without embedding each release's hashes. It describes local ownership; it is not a publisher signature or remote authenticity check.

Product identity: `8F3C2A71-6E0B-4D5C-9A1E-2B7D4F60C3A9`. Keep the Inno AppId, application folder `KH2FM-Arabic`, `kh2ar_state.txt`, backup suffix `.kh2ar.bak`, and backup list semantics unchanged.

Generate `build/installer/kh2ar_install_manifest.json` from the **actual release build** MANIFEST.tsv with `create_install_manifest.py --payload-manifest ... --version ... --output ...`. The future installer ships this file to `{app}` and writes `Version=<release version>` in `kh2ar_state.txt`. The application registry DisplayVersion must match. A mismatch stops removal.

```json
{
  "Schema": 1,
  "ProductId": "8F3C2A71-6E0B-4D5C-9A1E-2B7D4F60C3A9",
  "Version": "1.0.3",
  "Payload": [{"path": "msg\\us\\sys.bar", "size": 12345, "sha256": "64 lowercase hexadecimal characters"}],
  "Loader": [{"path": "DBGHELP.dll", "sha256": "64 lowercase hexadecimal characters"}]
}
```

Payload paths are relative to `ModRoot/kh2`. Supported extensions are `.bar`, `.png`, `.dds`. Loader paths are `DBGHELP.dll` and `dependencies/<name>.dll` relative to GameDir. The settings file is handled separately with its recorded ownership flag and exact expected content. Scope changes require a new tool contract instead of permitting arbitrary game files.

The scanner rejects unsupported schema, wrong product, conflicting versions, duplicate paths, invalid hashes, unsafe paths, and symbolic links. It verifies installed bytes before planning any deletion. Older 1.0.1 and 1.0.2 installers are supported through the embedded catalog. Without registry evidence, all 24 message/font BAR fingerprints must match the chosen manifest.

Recovery journals include their validated InstallManifest, so future removal backups restore through the same general tool. They retain schema/product/path checks and refuse to overwrite files or registration changed by a newer install.

The installer integration on this source branch is for future builds. The existing GitHub 1.0.2 draft and main are untouched. Merge or copy this integration into the build branch used for each future installer before claiming future compatibility.
