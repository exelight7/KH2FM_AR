@echo off
setlocal
set "KH2_FONT_CHECK=%~f0"
powershell.exe -NoLogo -NoProfile -STA -Command "$source=[System.IO.File]::ReadAllText($env:KH2_FONT_CHECK); & ([scriptblock]::Create(($source -split '(?m)^# POWERSHELL\r?$',2)[1]))"
if errorlevel 1 echo Font check failed. Copy the error above.
pause
exit /b
# POWERSHELL
param([string]$GameDir, [string]$ReportPath)

# Read-only runtime-path diagnosis. Only the report file is written.
# Compatible with Windows PowerShell 5.1; an explicit GameDir also works in pwsh.
$ErrorActionPreference = 'Stop'
$exeName = 'KINGDOM HEARTS II FINAL MIX.exe'
if (!$GameDir) {
    Add-Type -AssemblyName System.Windows.Forms
    $picker = New-Object System.Windows.Forms.FolderBrowserDialog
    $picker.Description = 'Choose the folder containing KINGDOM HEARTS II FINAL MIX.exe'
    if ($picker.ShowDialog() -ne 'OK') { return }
    $GameDir = $picker.SelectedPath
    $picker.Dispose()
}
$GameDir = (Resolve-Path -LiteralPath $GameDir).Path
if (!(Test-Path -LiteralPath (Join-Path $GameDir $exeName) -PathType Leaf)) {
    throw 'Choose the game folder containing KINGDOM HEARTS II FINAL MIX.exe.'
}
if (!$ReportPath) {
    $outputDir = $PSScriptRoot
    if (!$outputDir -and $env:KH2_FONT_CHECK) { $outputDir = Split-Path -Parent $env:KH2_FONT_CHECK }
    if (!$outputDir) { $outputDir = (Get-Location).Path }
    $ReportPath = Join-Path $outputDir 'KH2FM-font-report.json'
}

function Digest($File) {
    if (Test-Path -LiteralPath $File -PathType Leaf) {
        return (Get-FileHash -LiteralPath $File -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    return $null
}
function Resolve-GamePath($Value) {
    if ([IO.Path]::IsPathRooted($Value)) { return [IO.Path]::GetFullPath($Value) }
    return [IO.Path]::GetFullPath((Join-Path $GameDir $Value))
}
$findings = New-Object 'System.Collections.Generic.List[string]'
$settingsPath = Join-Path $GameDir 'panacea_settings.txt'
$settings = @{}
if (Test-Path -LiteralPath $settingsPath -PathType Leaf) {
    foreach ($line in [IO.File]::ReadAllLines($settingsPath)) {
        # Match Panacea's exact keys and untrimmed values, including duplicate keys.
        $at = $line.IndexOf('=')
        if ($at -lt 1) { continue }
        $key = $line.Substring(0, $at)
        if ($key -cin @('mod_path', 'dev_path', 'extract_path')) {
            if ($settings.ContainsKey($key)) { $findings.Add('DUPLICATE_SETTING: ' + $key) }
            $settings[$key] = $line.Substring($at + 1)
        }
    }
} else { $findings.Add('SETTINGS_MISSING: loader defaults to ./mod') }
$activeRoot = Resolve-GamePath './mod'
if ($settings.ContainsKey('mod_path') -and $settings.mod_path.Length) {
    $activeRoot = Resolve-GamePath $settings.mod_path
}
$roots = @([ordered]@{source='mod_path'; path=$activeRoot})
foreach ($key in @('dev_path', 'extract_path')) {
    if ($settings.ContainsKey($key) -and $settings[$key].Length) {
        $roots += [ordered]@{source=$key; path=(Resolve-GamePath $settings[$key])}
    }
}
$state = $null
$statePath = Join-Path $GameDir '.kh2fm-arabic/state.json'
if (Test-Path -LiteralPath $statePath -PathType Leaf) {
    $state = [IO.File]::ReadAllText($statePath) | ConvertFrom-Json
    $roots += [ordered]@{source='installer_state'; path=$state.modRoot}
    if (![string]::Equals([IO.Path]::GetFullPath($state.modRoot).TrimEnd('/','\'), $activeRoot.TrimEnd('/','\'), [StringComparison]::OrdinalIgnoreCase)) {
        $findings.Add('ACTIVE_PATH_DIFFERS_FROM_INSTALLER_STATE')
    }
} else { $findings.Add('INSTALLER_STATE_MISSING') }
$expected = [ordered]@{
    'kh2/msg/us/fontimage.bar' = '20560daa10bfb94de68e701d61efbb5421e33bd2cea468deac634416ef497408'
    'kh2/msg/us/fontinfo.bar' = '3d6f54f41a8dbe7a0b5b966991210c57844fd1e9e8876301ee5bb30a0a1b061e'
    'kh2/remastered/msg/us/fontimage.bar/US_fontimage_bar0.png' = '5fbf86172aca371992fbb9cba8a5a82c8bae5b12c957750b79b871e947960b99'
    'kh2/remastered/msg/us/fontimage.bar/US_fontimage_bar1.png' = '4b8a5b92b3b2b4083c708860b1d5953ef659c0d59c782970b9d318ade2124c0e'
}
$results = @()
foreach ($root in $roots) {
    $files = @()
    foreach ($relative in $expected.Keys) {
        $digest = Digest (Join-Path $root.path $relative)
        $status = 'MISSING'
        if ($digest) { $status = 'OTHER_FONT'; if ($digest -eq $expected[$relative]) { $status = 'FONT_1.0.8' } }
        $files += [ordered]@{path=$relative; status=$status; sha256=$digest}
    }
    $folder = Join-Path $root.path 'kh2/remastered/msg/us/fontimage.bar'
    $extras = @()
    if (Test-Path -LiteralPath $folder -PathType Container) {
        $extras = @(Get-ChildItem -LiteralPath $folder -File -Recurse | ForEach-Object {
            [ordered]@{name=$_.FullName.Substring($folder.Length + 1); sha256=(Digest $_.FullName)}
        })
        if (@($extras | Where-Object { $_.name -match '\.dds$' }).Count) {
            $findings.Add('DDS_PRECEDENCE: ' + $root.source)
        }
    }
    if ($root.source -eq 'dev_path' -and (Test-Path -LiteralPath $folder -PathType Container)) {
        $findings.Add('DEV_FONT_FOLDER_OVERRIDES_MOD_PATH')
    }
    $results += [ordered]@{source=$root.source; path=$root.path; fonts=$files; remasteredFiles=$extras}
}
$loaders = @('DBGHELP.dll', 'version.dll') | ForEach-Object {
    [ordered]@{name=$_; sha256=(Digest (Join-Path $GameDir $_))}
}
$running = @(Get-Process -Name 'KINGDOM HEARTS II FINAL MIX' -ErrorAction SilentlyContinue | ForEach-Object {
    try { $_.Path } catch { 'PROCESS_PATH_UNAVAILABLE' }
})
if ($running.Count) { $findings.Add('GAME_RUNNING: restart it after applying an update') }
$report = [ordered]@{
    schema=1; tool='KH2FM-font-check'; expectedFont='1.0.8'; gameDir=$GameDir
    installedVersion=$(if ($state) {$state.version} else {$null})
    findings=@($findings.ToArray()); roots=$results; loaders=@($loaders); runningGamePaths=$running
}
$json = $report | ConvertTo-Json -Depth 12
[IO.File]::WriteAllText([IO.Path]::GetFullPath($ReportPath), $json, (New-Object Text.UTF8Encoding($false)))
Write-Output $json
Write-Host "Report saved: $ReportPath"
