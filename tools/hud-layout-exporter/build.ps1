$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
New-Item -ItemType Directory -Force out | Out-Null
$compiler = Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
& $compiler /nologo /target:exe /platform:x64 /optimize+ /out:out/KH2FM-HUD-Layout.exe /reference:System.IO.Compression.dll /reference:System.IO.Compression.FileSystem.dll /reference:System.Windows.Forms.dll /reference:System.Drawing.dll /reference:System.Web.Extensions.dll Collector.cs PackageCrypto.cs Tests.cs
if ($LASTEXITCODE -ne 0) { throw 'Compilation failed' }
& ./out/KH2FM-HUD-Layout.exe --self-test fixtures
if ($LASTEXITCODE -ne 0) { throw 'Exporter tests failed' }
$report = Get-Content out/SELF_TEST.json -Raw | ConvertFrom-Json
if (-not $report.passed -or $report.checks -ne 32) { throw 'Required 32 exporter checks did not run' }
Copy-Item README_AR.md, NOTICE.txt, LICENSE-OpenKH.txt out/
Compress-Archive -Path out/* -DestinationPath KH2FM-HUD-Layout-Windows-x64.zip
(Get-FileHash KH2FM-HUD-Layout-Windows-x64.zip -Algorithm SHA256).Hash.ToLower() + '  KH2FM-HUD-Layout-Windows-x64.zip' | Set-Content -Encoding ascii SHA256SUMS.txt
