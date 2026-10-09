Set-StrictMode -Version 2.0
$ErrorActionPreference='Stop'
trap {
    $detail=($_ | Out-String)+' '+$_.ScriptStackTrace
    Write-Output ('::error::'+$detail.Replace('%','%25').Replace("`r",'%0D').Replace("`n",'%0A'))
    throw
}

$dist=Join-Path $PSScriptRoot 'dist'
[void][IO.Directory]::CreateDirectory($dist)
$vswhere='C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe'
$vs=& $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if (-not $vs) { throw 'Visual C++ compiler not found' }
$src=Join-Path $PSScriptRoot 'src'
$cmd=@"
@echo off
call "$vs\Common7\Tools\VsDevCmd.bat" -no_logo -arch=x64
if errorlevel 1 exit /b 1
cd /d "$src"
rc /nologo /fo "$dist\resources.res" resources.rc
if errorlevel 1 exit /b 1
cl /nologo /std:c++17 /O2 /W4 /WX /EHsc /MT /utf-8 /DUNICODE /D_UNICODE launcher.cpp /Fo"$dist\launcher.obj" /Fe"$dist\KH2FM-Arabic-Uninstaller.exe" "$dist\resources.res" /link /SUBSYSTEM:WINDOWS /MANIFEST:NO /DYNAMICBASE /NXCOMPAT /HIGHENTROPYVA advapi32.lib ole32.lib user32.lib
if errorlevel 1 exit /b 1
"@
$cmdFile=Join-Path $dist 'compile.cmd'
[IO.File]::WriteAllText($cmdFile,$cmd,[Text.Encoding]::ASCII)
& cmd.exe /c $cmdFile
if ($LASTEXITCODE -ne 0) { throw 'Native Windows build failed' }
$exe=Join-Path $dist 'KH2FM-Arabic-Uninstaller.exe'
$report=[pscustomobject]@{result='BUILT';tool_version='1.0.0';target='Windows 10/11 x64';compiler='Microsoft Visual C++ /MT static CRT';bytes=([IO.FileInfo]$exe).Length;sha256=(Get-FileHash $exe -Algorithm SHA256).Hash.ToLowerInvariant();legacy_versions=@('1.0.1','1.0.2');future_install_manifest_schema=1;commit=$env:GITHUB_SHA}
$report | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $dist 'BUILD_REPORT.json') -Encoding UTF8
