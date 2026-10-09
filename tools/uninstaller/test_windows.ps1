Set-StrictMode -Version 2.0
$ErrorActionPreference='Stop'
trap {
    $detail=($_ | Out-String)+' '+$_.ScriptStackTrace
    Write-Output ('::error::'+$detail.Replace('%','%25').Replace("`r",'%0D').Replace("`n",'%0A'))
    throw
}

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
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @'
using System;
using System.Text;
using System.Collections.Generic;
using System.Runtime.InteropServices;
public static class KH2WindowTest {
    [DllImport("user32.dll", CharSet=CharSet.Unicode)]
    public static extern IntPtr SendMessage(IntPtr window, uint msg, IntPtr w, IntPtr l);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)]
    public static extern int GetWindowText(IntPtr window, StringBuilder text, int count);
    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr window, out RECT rect);
    public struct RECT { public int Left, Top, Right, Bottom; }
    public delegate bool EnumProc(IntPtr window, IntPtr data);
    [DllImport("user32.dll")] static extern bool EnumChildWindows(IntPtr parent, EnumProc callback, IntPtr data);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] static extern int GetClassName(IntPtr window, StringBuilder text, int count);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern bool SetWindowText(IntPtr window, string text);
    [DllImport("user32.dll")] public static extern bool IsWindowEnabled(IntPtr window);
    [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr window, out uint process);
    [DllImport("kernel32.dll")] static extern uint GetCurrentThreadId();
    [DllImport("user32.dll")] static extern bool AttachThreadInput(uint a, uint b, bool attach);
    [DllImport("user32.dll")] static extern bool SetForegroundWindow(IntPtr window);
    [DllImport("user32.dll")] static extern IntPtr SetFocus(IntPtr window);
    [DllImport("user32.dll")] static extern IntPtr GetFocus();
    [DllImport("user32.dll")] static extern bool PostMessage(IntPtr window, uint msg, IntPtr w, IntPtr l);
    public static string Text(IntPtr window) {
        var text=new StringBuilder(2048); GetWindowText(window,text,text.Capacity); return text.ToString();
    }
    public static IntPtr Find(IntPtr parent, string text, bool edit) {
        IntPtr found=IntPtr.Zero;
        EnumChildWindows(parent,delegate(IntPtr window,IntPtr data) {
            var name=new StringBuilder(256); GetClassName(window,name,name.Capacity);
            if((edit && name.ToString().Contains(".EDIT.")) || (!edit && Text(window)==text)) { found=window;return false; }
            return true;
        },IntPtr.Zero);
        return found;
    }
    public static bool ActivateLink(IntPtr form,IntPtr link) {
        uint process; uint target=GetWindowThreadProcessId(link,out process); uint current=GetCurrentThreadId();
        bool attached=AttachThreadInput(current,target,true);
        try {
            SetForegroundWindow(form);SetFocus(link);
            if(GetFocus()!=link) return false;
            return PostMessage(link,0x0100,new IntPtr(13),IntPtr.Zero) && PostMessage(link,0x0101,new IntPtr(13),IntPtr.Zero);
        } finally { if(attached) AttachThreadInput(current,target,false); }
    }
}
'@
function Put-TestFile([string]$Path,[string]$Text) {
    [void][IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($Path))
    [IO.File]::WriteAllText($Path,$Text,(New-Object Text.UTF8Encoding($false)))
}
$uiRoot=Join-Path ([IO.Path]::GetTempPath()) ('kh2ar-click-test-'+[Guid]::NewGuid().ToString('N'))
$uiApp=Join-Path $uiRoot 'KH2FM-Arabic'
$uiGame=Join-Path $uiRoot 'KINGDOM HEARTS -HD 1.5+2.5 ReMIX-'
$uiMod=Join-Path $uiApp 'mod'
Put-TestFile (Join-Path $uiGame 'KINGDOM HEARTS II FINAL MIX.exe') 'original game fixture'
Put-TestFile (Join-Path $uiGame 'Save/save.dat') 'original save fixture'
Put-TestFile (Join-Path $uiGame 'original.pkg') 'original archive fixture'
Put-TestFile (Join-Path $uiApp 'kh2ar_state.txt') ("GameDir=$uiGame`nModRoot=$uiMod`nSettingsByUs=1`nVersion=12.4.0`n")
Put-TestFile (Join-Path $uiApp 'kh2ar_backups.txt') ''
Put-TestFile (Join-Path $uiApp 'unins000.dat') 'uninstall fixture'
Put-TestFile (Join-Path $uiGame 'panacea_settings.txt') ("mod_path=$uiMod`nshow_console=false`n")
$uiPayload=@()
foreach($relative in @('msg/us/sys.bar','msg/us/fontimage.bar','image/test.dds')) {
    $path=Join-Path $uiMod ('kh2/'+$relative); Put-TestFile $path ('translation fixture '+$relative)
    $uiPayload+=[pscustomobject]@{path=$relative;size=([IO.FileInfo]$path).Length;sha256=(Get-ContentHash $path)}
}
$uiLoader=@()
foreach($relative in @('DBGHELP.dll','dependencies/bass.dll')) {
    $path=Join-Path $uiGame $relative; Put-TestFile $path ('loader fixture '+$relative)
    $uiLoader+=[pscustomobject]@{path=$relative;sha256=(Get-ContentHash $path)}
}
Put-TestFile (Join-Path $uiApp 'kh2ar_install_manifest.json') ((New-InstallManifest '12.4.0' $uiPayload $uiLoader) | ConvertTo-Json -Depth 8)
$uiBefore=@{}
foreach($file in Get-ChildItem $uiRoot -Recurse -File) { $uiBefore[$file.FullName]=Get-ContentHash $file.FullName }
$uiBase=[Microsoft.Win32.RegistryKey]::OpenBaseKey([Microsoft.Win32.RegistryHive]::CurrentUser,[Microsoft.Win32.RegistryView]::Registry64)
$existing=$uiBase.OpenSubKey($keyPath)
if ($existing) { $existing.Dispose(); $uiBase.Dispose(); throw 'Existing registry entry prevents GUI fixture test' }
$key=$uiBase.CreateSubKey($keyPath)
try { $key.SetValue('InstallLocation',$uiApp);$key.SetValue('DisplayVersion','12.4.0');$key.SetValue('DisplayName','GUI click test fixture') } finally { $key.Dispose() }
$exe=Join-Path $PSScriptRoot 'dist/KH2FM-Arabic-Uninstaller.exe'
$launcher=$null; $child=$null
$script:ControlHandles=@{}
function Find-Control([string]$Name) {
    if($script:ControlHandles.ContainsKey($Name)) { return $script:ControlHandles[$Name] }
    $texts=@{GamePath='';DeleteTranslation='حذف التعريب';StatusText='اضغط حذف التعريب.';UndoRemoval='تراجع عن الحذف'}
    for($i=0;$i -lt 40;$i++) {
        $handle=[KH2WindowTest]::Find($child.MainWindowHandle,$texts[$Name],($Name -eq 'GamePath'))
        if($handle -ne [IntPtr]::Zero) { $script:ControlHandles[$Name]=$handle;return $handle }
        Start-Sleep -Milliseconds 250
    }
    throw ('Missing native interface control '+$Name)
}
function Read-ControlText([IntPtr]$Control) { return [KH2WindowTest]::Text($Control) }
function Wait-Status([string]$Expected) {
    for($i=0;$i -lt 100;$i++) {
        $text=Read-ControlText (Find-Control 'StatusText')
        if($text.StartsWith($Expected)) { return }
        Start-Sleep -Milliseconds 200
    }
    throw ('Expected status '+$Expected+'; actual '+$text)
}
function Save-WindowImage([string]$Name) {
    $rect=New-Object KH2WindowTest+RECT
    if(-not [KH2WindowTest]::GetWindowRect($child.MainWindowHandle,[ref]$rect)) { throw 'Cannot read actual window bounds' }
    $bmp=New-Object Drawing.Bitmap(($rect.Right-$rect.Left),($rect.Bottom-$rect.Top))
    $graphics=[Drawing.Graphics]::FromImage($bmp)
    try {
        $graphics.CopyFromScreen($rect.Left,$rect.Top,0,0,$bmp.Size)
        $bmp.Save((Join-Path $PSScriptRoot $Name),[Drawing.Imaging.ImageFormat]::Png)
    } finally { $graphics.Dispose();$bmp.Dispose() }
}
try {
    $launcher=Start-Process -FilePath $exe -PassThru
    for($i=0;$i -lt 40;$i++) {
        Start-Sleep -Milliseconds 500
        $candidate=Get-CimInstance Win32_Process -Filter ("ParentProcessId="+$launcher.Id) | Where-Object {$_.Name -eq 'powershell.exe'} | Select-Object -First 1
        if($candidate) {
            $child=Get-Process -Id $candidate.ProcessId -ErrorAction SilentlyContinue
            if($child) { $child.Refresh();if($child.MainWindowTitle -eq 'حذف تعريب KH2FM' -and $child.MainWindowHandle -ne [IntPtr]::Zero) { break } }
        }
        if($launcher.HasExited) { throw 'EXE exited before showing the simple interface' }
    }
    if(-not $child -or $child.MainWindowTitle -ne 'حذف تعريب KH2FM' -or $child.MainWindowHandle -eq [IntPtr]::Zero) { throw 'Simple Arabic interface did not appear' }
    $gameField=Find-Control 'GamePath'
    $expected='C:\Program Files (x86)\Steam\steamapps\common\KINGDOM HEARTS -HD 1.5+2.5 ReMIX-'
    if((Read-ControlText $gameField) -cne $expected) { throw 'Game path is not prefilled as requested' }
    $delete=Find-Control 'DeleteTranslation'
    if(-not [KH2WindowTest]::IsWindowEnabled($delete) -or (Read-ControlText $delete) -ne 'حذف التعريب') { throw 'One-click delete button is not ready' }
    [void](Find-Control 'StatusText')
    Save-WindowImage 'PROGRAM_PREVIEW.png'
    $results.Add('Actual simple Windows GUI has requested default game path and one enabled Delete button PASS')
    if(-not [KH2WindowTest]::SetWindowText($gameField,$uiRoot)) { throw 'Cannot set game path in actual UI' }
    [void][KH2WindowTest]::SendMessage($delete,0x00F5,[IntPtr]::Zero,[IntPtr]::Zero)
    Wait-Status 'اختر مجلد اللعبة'
    foreach($path in $uiBefore.Keys) { if((Get-ContentHash $path) -ne $uiBefore[$path]) { throw 'Wrong game path changed a fixture file' } }
    $results.Add('Actual Delete click on wrong game folder shows inline error and preserves all files PASS')
    if(-not [KH2WindowTest]::SetWindowText($gameField,$uiGame)) { throw 'Cannot set selected game in actual UI' }
    [void][KH2WindowTest]::SendMessage($delete,0x00F5,[IntPtr]::Zero,[IntPtr]::Zero)
    Wait-Status 'تم حذف التعريب'
    if([IO.File]::Exists((Join-Path $uiMod 'kh2/msg/us/sys.bar'))) { throw 'One-click GUI did not remove the translation' }
    foreach($relative in @('KINGDOM HEARTS II FINAL MIX.exe','Save/save.dat','original.pkg')) {
        $path=Join-Path $uiGame $relative
        if((Get-ContentHash $path) -ne $uiBefore[$path]) { throw 'Original game or save changed' }
    }
    $key=$uiBase.OpenSubKey($keyPath)
    if($key) { $key.Dispose();throw 'GUI did not remove its fixture registration' }
    $last=Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'KH2FM-Arabic-Remover/last-recovery.txt'
    $recovery=[IO.File]::ReadAllText($last)
    $journal=[IO.File]::ReadAllText((Join-Path $recovery 'recovery.json')) | ConvertFrom-Json
    if($journal.Phase -ne 'Removed' -or $journal.State.GameDir -ne $uiGame) { throw 'Automatic backup was not saved for the selected game' }
    Save-WindowImage 'PROGRAM_SUCCESS.png'
    $results.Add('Actual one Delete click automatically discovers, scans, backs up and removes only selected game translation PASS')
    $undo=Find-Control 'UndoRemoval'
    if(-not [KH2WindowTest]::ActivateLink($child.MainWindowHandle,$undo)) { throw 'Cannot activate actual Undo link' }
    Wait-Status 'رجع التعريب'
    foreach($path in $uiBefore.Keys) { if((Get-ContentHash $path) -ne $uiBefore[$path]) { throw ('Undo did not restore original bytes '+$path) } }
    $key=$uiBase.OpenSubKey($keyPath)
    if(-not $key) { throw 'Undo did not restore Windows registration' }
    try { if($key.GetValue('DisplayVersion') -ne '12.4.0') { throw 'Undo restored wrong version' } } finally { $key.Dispose() }
    $results.Add('Actual optional Undo link restores all original fixture bytes and Windows registration PASS')
    [void][KH2WindowTest]::SendMessage($child.MainWindowHandle,0x0010,[IntPtr]::Zero,[IntPtr]::Zero)
    if(-not $launcher.WaitForExit(15000) -or $launcher.ExitCode -ne 0) { throw 'EXE did not close cleanly' }
    $results.Add('Actual Windows EXE closes cleanly PASS')
} finally {
    if($child -and -not $child.HasExited) { Stop-Process -Id $child.Id -Force }
    if($launcher -and -not $launcher.HasExited) { Stop-Process -Id $launcher.Id -Force }
    $uiBase.DeleteSubKeyTree($keyPath,$false);$uiBase.Dispose()
    if([IO.Directory]::Exists($uiRoot)) { Remove-Item -LiteralPath $uiRoot -Recurse -Force }
}
$report=[pscustomobject]@{result='PASS';platform='Windows';powershell=$PSVersionTable.PSVersion.ToString();tests=@($results.ToArray());real_native_exe_delete_and_undo_clicked=$true;actual_game_installation_tested=$false;uac_interactive_prompt_tested=$false;scope='Native Windows EXE and native Windows control clicks against controlled fixture files, registry, original game and save fixtures.'}
$report | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $PSScriptRoot 'WINDOWS_TEST_REPORT.json') -Encoding UTF8
$results
