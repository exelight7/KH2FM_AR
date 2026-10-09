Set-StrictMode -Version 2.0
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'src/Remover.Core.ps1')
if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) { throw 'Windows is required' }
$results=New-Object 'Collections.Generic.List[string]'
$root=Join-Path ([IO.Path]::GetTempPath()) ('kh2ar-win-smoke-'+[Guid]::NewGuid().ToString('N'))
$app=Join-Path $root 'KH2FM-Arabic'
[void][IO.Directory]::CreateDirectory($app)
$keyPath='Software\Microsoft\Windows\CurrentVersion\Uninstall\{'+$script:AppGuid+'}_is1'
$base=[Microsoft.Win32.RegistryKey]::OpenBaseKey([Microsoft.Win32.RegistryHive]::CurrentUser,[Microsoft.Win32.RegistryView]::Registry64)
$key=$base.OpenSubKey($keyPath)
if ($null -ne $key) { $key.Dispose(); $base.Dispose(); throw 'Pre-existing installation registry entry; refusing to touch it' }
try {
    $key=$base.CreateSubKey($keyPath)
    try {
        $key.SetValue('InstallLocation',$app)
        $key.SetValue('DisplayVersion','12.4.0')
        $key.SetValue('DisplayName','KH2FM uninstaller test fixture')
        $key.SetValue('TestDWORD',42,[Microsoft.Win32.RegistryValueKind]::DWord)
        $key.SetValue('TestBinary',[byte[]]@(1,2,3),[Microsoft.Win32.RegistryValueKind]::Binary)
    } finally { $key.Dispose() }
    $entries=@(Get-InstalledRegistrations | Where-Object { $_.Hive -eq 'CurrentUser' -and $_.View -eq 'Registry64' -and $_.InstallLocation -eq $app })
    if ($entries.Count -ne 1) { throw 'Registry detection failed' }
    Assert-RegistrationIdentity $entries
    Set-RegistrationState $entries $false
    $key=$base.OpenSubKey($keyPath)
    if ($null -ne $key) { $key.Dispose(); throw 'Registry removal failed' }
    Set-RegistrationState $entries $true
    $key=$base.OpenSubKey($keyPath)
    try {
        if ($key.GetValue('TestDWORD') -ne 42 -or ([byte[]]$key.GetValue('TestBinary')).Length -ne 3 -or $key.GetValue('DisplayVersion') -ne '12.4.0') { throw 'Registry restoration failed' }
    } finally { $key.Dispose() }
    $results.Add('Actual Windows registry discovery, removal and value restoration PASS')
    $key=$base.OpenSubKey($keyPath,$true)
    try { $key.SetValue('DisplayVersion','12.4.1') } finally { $key.Dispose() }
    $blocked=$false
    try { Assert-RegistrationIdentity $entries } catch { $blocked=$true }
    if (-not $blocked) { throw 'Newer installation registry was not protected' }
    $results.Add('Newer Windows registration blocks recovery before file mutations PASS')
} finally {
    $base.DeleteSubKeyTree($keyPath,$false); $base.Dispose()
    Remove-Item -LiteralPath $root -Recurse -Force
}
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class KH2WindowTest {
    [DllImport("user32.dll", CharSet=CharSet.Unicode)]
    public static extern IntPtr SendMessage(IntPtr window, uint msg, IntPtr w, IntPtr l);
}
'@
$exe=Join-Path $PSScriptRoot 'dist/KH2FM-Arabic-Uninstaller.exe'
$launcher=Start-Process -FilePath $exe -PassThru
$child=$null
try {
    for ($i=0;$i -lt 40;$i++) {
        Start-Sleep -Milliseconds 500
        $candidate=Get-CimInstance Win32_Process -Filter ("ParentProcessId="+$launcher.Id) | Where-Object { $_.Name -eq 'powershell.exe' } | Select-Object -First 1
        if ($candidate) {
            $child=Get-Process -Id $candidate.ProcessId -ErrorAction SilentlyContinue
            if ($child) { $child.Refresh(); if ($child.MainWindowTitle -eq 'KH2FM — أداة إزالة التعريب' -and $child.MainWindowHandle -ne [IntPtr]::Zero) { break } }
        }
        if ($launcher.HasExited) { throw 'EXE exited before creating its interface' }
    }
    if (-not $child -or $child.MainWindowTitle -ne 'KH2FM — أداة إزالة التعريب' -or $child.MainWindowHandle -eq [IntPtr]::Zero) { throw 'Expected Arabic Windows Forms interface not found' }
    [void][KH2WindowTest]::SendMessage($child.MainWindowHandle,0x0010,[IntPtr]::Zero,[IntPtr]::Zero)
    if (-not $launcher.WaitForExit(15000) -or $launcher.ExitCode -ne 0) { throw 'EXE did not exit cleanly after closing the interface' }
    $results.Add('Actual Windows EXE launch, Arabic GUI window and clean close PASS')
} finally {
    if ($child -and -not $child.HasExited) { Stop-Process -Id $child.Id -Force }
    if (-not $launcher.HasExited) { Stop-Process -Id $launcher.Id -Force }
}
$report=[pscustomobject]@{result='PASS';platform='Windows';powershell=$PSVersionTable.PSVersion.ToString();tests=@($results.ToArray());actual_game_installation_tested=$false;uac_interactive_prompt_tested=$false;scope='Windows runner real filesystem, registry and GUI smoke checks. No game or user computer tested.'}
$report | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $PSScriptRoot 'WINDOWS_TEST_REPORT.json') -Encoding UTF8
$results
