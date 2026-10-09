Set-StrictMode -Version 2.0
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'src/Remover.Core.ps1')
$script:TestRoot=Join-Path ([IO.Path]::GetTempPath()) ('kh2ar-remover-tests-'+[Guid]::NewGuid().ToString('N'))
[void][IO.Directory]::CreateDirectory($script:TestRoot)
$script:Results=New-Object 'Collections.Generic.List[object]'

function Assert([bool]$Condition,[string]$Message='assertion failed') { if (-not $Condition) { throw $Message } }
function Put([string]$Path,[string]$Text) { [void][IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($Path)); [IO.File]::WriteAllText($Path,$Text,(New-Object Text.UTF8Encoding($false))) }
function Expect-Failure([scriptblock]$Run) {
    $failed=$false
    try { & $Run | Out-Null } catch { $failed=$true }
    Assert $failed 'operation should have failed'
}
function Fixture {
    $root=Join-Path $script:TestRoot ([Guid]::NewGuid().ToString('N'))
    $app=Join-Path $root 'KH2FM-Arabic'; $game=Join-Path $root 'game'; $mod=Join-Path $app 'mod'
    [void][IO.Directory]::CreateDirectory($app); [void][IO.Directory]::CreateDirectory($game)
    Put (Join-Path $game 'KINGDOM HEARTS II FINAL MIX.exe') 'fake game executable, must remain untouched'
    Put (Join-Path $game 'Save/save.dat') 'private save, must remain untouched'
    Put (Join-Path $game 'original.pkg') 'original game archive, must remain untouched'
    Put (Join-Path $app 'kh2ar_state.txt') ("GameDir=$game`nModRoot=$mod`nSettingsByUs=1`n")
    Put (Join-Path $app 'kh2ar_backups.txt') ''
    Put (Join-Path $app 'kh2ar_dirs.txt') "$app`n$mod"
    Put (Join-Path $app 'unins000.exe') 'fake uninstaller metadata'
    Put (Join-Path $app 'unins000.dat') 'fake uninstaller data'
    Put (Join-Path $game 'panacea_settings.txt') ("mod_path=$mod`nshow_console=false`n")
    $payload=@()
    foreach ($relative in @('msg/us/sys.bar','msg/us/fontimage.bar','image/test.dds')) {
        $p=Join-Path $mod ('kh2/'+$relative); Put $p ('Arabic 1.0.1 '+$relative)
        $payload += [pscustomobject]@{ path=$relative; size=([IO.FileInfo]$p).Length; sha256=(Get-ContentHash $p) }
    }
    $loader=@()
    foreach ($relative in @('DBGHELP.dll','dependencies/bass.dll')) {
        $p=Join-Path $game $relative; Put $p ('official loader '+$relative)
        $loader += [pscustomobject]@{ path=$relative; sha256=(Get-ContentHash $p) }
    }
    $reg=[pscustomobject]@{ InstallLocation=$app; DisplayVersion='1.0.1'; Hive='LocalMachine'; View='Registry64'; Key=('Software\Microsoft\Windows\CurrentVersion\Uninstall\{'+$script:AppGuid+'}_is1'); Values=@() }
    return [pscustomobject]@{ Root=$root; App=$app; Game=$game; Mod=$mod; Payload=$payload; Loader=$loader; Reg=$reg; Recovery=(Join-Path $root 'recovery') }
}
function Plan($F) {
    $plan=New-RemovalPlan $F.App $F.Payload $F.Loader @($F.Reg)
    Assert ((@($plan.Registrations).Count -eq 1 -and $plan.Complete) -or (@($plan.Registrations).Count -eq 0 -and -not $plan.Complete)) 'registration collection must not contain null'
    # Linux tests simulate registration discovery. Never change an actual registry.
    $plan.Registrations=@()
    return $plan
}
function Run-Test([string]$Name,[scriptblock]$Run) {
    try { & $Run; $script:Results.Add([pscustomobject]@{name=$Name;result='PASS'}); Write-Output ('PASS '+$Name) }
    catch { Write-Output ('FAIL '+$Name+': '+$_.Exception.Message); throw }
}

Run-Test 'fresh install removal and byte-identical recovery' {
    $f=Fixture; $plan=Plan $f
    Assert ($plan.Matched -eq 3 -and $plan.Complete -and $plan.LoaderRemoved)
    $before=@{}
    foreach ($file in Get-ChildItem -LiteralPath $f.Root -File -Recurse) { $before[$file.FullName]=Get-ContentHash $file.FullName }
    $result=Invoke-Removal $plan $f.Recovery
    Assert (-not [IO.File]::Exists((Join-Path $f.Mod 'kh2/msg/us/sys.bar')))
    Assert (-not [IO.File]::Exists((Join-Path $f.Game 'DBGHELP.dll')))
    Assert ([IO.File]::ReadAllText((Join-Path $f.Game 'Save/save.dat')) -eq 'private save, must remain untouched')
    Assert ([IO.File]::ReadAllText((Join-Path $f.Game 'original.pkg')) -eq 'original game archive, must remain untouched')
    [void](Restore-Removal $result.RecoveryDir $f.Payload $f.Loader)
    foreach ($path in $before.Keys) { Assert ((Get-ContentHash $path) -eq $before[$path]) ('recovery mismatch '+$path) }
}
Run-Test 'previous mod backup restored and recoverable' {
    $f=Fixture; $p=Join-Path $f.Mod 'kh2/msg/us/sys.bar'; $old=Get-ContentHash $p
    Put ($p+'.kh2ar.bak') 'previous non-Arabic mod'; Put (Join-Path $f.App 'kh2ar_backups.txt') $p
    $plan=Plan $f; Assert (-not $plan.LoaderRemoved)
    $r=Invoke-Removal $plan $f.Recovery
    Assert ([IO.File]::ReadAllText($p) -eq 'previous non-Arabic mod')
    Assert (-not [IO.File]::Exists($p+'.kh2ar.bak'))
    [void](Restore-Removal $r.RecoveryDir $f.Payload $f.Loader)
    Assert ((Get-ContentHash $p) -eq $old)
    Assert ([IO.File]::ReadAllText($p+'.kh2ar.bak') -eq 'previous non-Arabic mod')
}
Run-Test 'missing override can restore its registered previous file' {
    $f=Fixture; $p=Join-Path $f.Mod 'kh2/msg/us/sys.bar'
    [IO.File]::Delete($p); Put ($p+'.kh2ar.bak') 'previous file'; Put (Join-Path $f.App 'kh2ar_backups.txt') $p
    $r=Invoke-Removal (Plan $f) $f.Recovery
    Assert ([IO.File]::ReadAllText($p) -eq 'previous file')
    [void](Restore-Removal $r.RecoveryDir $f.Payload $f.Loader)
    Assert (-not [IO.File]::Exists($p))
    Assert ([IO.File]::ReadAllText($p+'.kh2ar.bak') -eq 'previous file')
}
Run-Test 'changed override prevents all removal and preserves installed files' {
    $f=Fixture; $p=Join-Path $f.Mod 'kh2/msg/us/sys.bar'; Put $p 'changed by another mod'
    $plan=Plan $f; Assert ($plan.Skipped.Count -eq 1 -and -not $plan.Complete -and -not $plan.LoaderRemoved)
    Expect-Failure { Invoke-Removal $plan $f.Recovery }
    Assert ([IO.File]::ReadAllText($p) -eq 'changed by another mod')
    Assert ([IO.File]::Exists((Join-Path $f.App 'unins000.exe')))
    Assert ([IO.File]::Exists((Join-Path $f.App 'kh2ar_state.txt')))
    Assert ([IO.File]::Exists((Join-Path $f.Mod 'kh2/msg/us/fontimage.bar')))
}
Run-Test 'other world mod preserves loader and settings' {
    $f=Fixture; $p=Join-Path $f.Mod 'kh1/other-mod.bar'; Put $p 'unrelated mod'
    $plan=Plan $f; Assert (-not $plan.LoaderRemoved)
    [void](Invoke-Removal $plan $f.Recovery)
    Assert ([IO.File]::ReadAllText($p) -eq 'unrelated mod')
    Assert ([IO.File]::Exists((Join-Path $f.Game 'DBGHELP.dll')))
    Assert ([IO.File]::Exists((Join-Path $f.Game 'panacea_settings.txt')))
}
Run-Test 'preexisting loader retained even when hashes are official' {
    $f=Fixture
    Put (Join-Path $f.App 'kh2ar_state.txt') ("GameDir=$($f.Game)`nModRoot=$($f.Mod)`nSettingsByUs=0`n")
    $plan=Plan $f; Assert (-not $plan.LoaderRemoved)
    [void](Invoke-Removal $plan $f.Recovery)
    Assert ([IO.File]::Exists((Join-Path $f.Game 'DBGHELP.dll')))
}
Run-Test 'changed loader group retained' {
    $f=Fixture; Put (Join-Path $f.Game 'dependencies/bass.dll') 'different DLL'
    $plan=Plan $f; Assert (-not $plan.LoaderRemoved)
    [void](Invoke-Removal $plan $f.Recovery)
    Assert ([IO.File]::ReadAllText((Join-Path $f.Game 'dependencies/bass.dll')) -eq 'different DLL')
    Assert ([IO.File]::Exists((Join-Path $f.Game 'DBGHELP.dll')))
}
Run-Test 'changed settings retained' {
    $f=Fixture; Put (Join-Path $f.Game 'panacea_settings.txt') 'mod_path=another-mod-folder'
    $plan=Plan $f; Assert (-not $plan.LoaderRemoved)
    [void](Invoke-Removal $plan $f.Recovery)
    Assert ([IO.File]::ReadAllText((Join-Path $f.Game 'panacea_settings.txt')) -eq 'mod_path=another-mod-folder')
}
Run-Test 'additional game loader preserves Panacea and dependencies' {
    $f=Fixture; Put (Join-Path $f.Game 'version.dll') 'another loader'
    $plan=Plan $f; Assert (-not $plan.LoaderRemoved)
    [void](Invoke-Removal $plan $f.Recovery)
    Assert ([IO.File]::ReadAllText((Join-Path $f.Game 'version.dll')) -eq 'another loader')
    Assert ([IO.File]::Exists((Join-Path $f.Game 'DBGHELP.dll')))
    Assert ([IO.File]::Exists((Join-Path $f.Game 'dependencies/bass.dll')))
}
Run-Test 'unknown backup list destination never acted on' {
    $f=Fixture; $outside=Join-Path $f.Root 'unrelated.txt'; Put $outside 'unrelated'; Put ($outside+'.kh2ar.bak') 'unrelated old'
    Put (Join-Path $f.App 'kh2ar_backups.txt') $outside
    $plan=Plan $f; Assert (-not $plan.Complete -and -not $plan.LoaderRemoved)
    Expect-Failure { Invoke-Removal $plan $f.Recovery }
    Assert ([IO.File]::ReadAllText($outside) -eq 'unrelated')
    Assert ([IO.File]::ReadAllText($outside+'.kh2ar.bak') -eq 'unrelated old')
}
Run-Test 'file changed after scan aborts before removal' {
    $f=Fixture; $plan=Plan $f; $p=Join-Path $f.Mod 'kh2/msg/us/sys.bar'; Put $p 'new edit after scan'
    Expect-Failure { Invoke-Removal $plan $f.Recovery }
    Assert ([IO.File]::ReadAllText($p) -eq 'new edit after scan')
    Assert ([IO.File]::Exists((Join-Path $f.Mod 'kh2/msg/us/fontimage.bar')))
    Assert ([IO.File]::Exists((Join-Path $f.App 'kh2ar_state.txt')))
}
Run-Test 'failure after removing files rolls back original content' {
    $f=Fixture; $plan=Plan $f; $expected=Get-ContentHash (Join-Path $f.Mod 'kh2/msg/us/sys.bar')
    $script:OriginalRegistration=(Get-Item Function:Set-RegistrationState).ScriptBlock
    function Set-RegistrationState($Entries,[bool]$Restore) { if (-not $Restore) { throw 'simulated late failure' }; & $script:OriginalRegistration $Entries $Restore }
    try {
        Expect-Failure { Invoke-Removal $plan $f.Recovery }
        Assert ((Get-ContentHash (Join-Path $f.Mod 'kh2/msg/us/sys.bar')) -eq $expected)
        Assert ([IO.File]::Exists((Join-Path $f.App 'kh2ar_state.txt')))
        Assert ([IO.File]::Exists((Join-Path $f.Game 'DBGHELP.dll')))
    } finally { Set-Item Function:Set-RegistrationState $script:OriginalRegistration }
}
Run-Test 'corrupt recovery archive rejected before restoring any file' {
    $f=Fixture; $r=Invoke-Removal (Plan $f) $f.Recovery
    $j=[IO.File]::ReadAllText((Join-Path $r.RecoveryDir 'recovery.json')) | ConvertFrom-Json
    Put (Join-Path $r.RecoveryDir $j.Records[0].Archive) 'corrupted backup'
    Expect-Failure { Restore-Removal $r.RecoveryDir $f.Payload $f.Loader }
    Assert (-not [IO.File]::Exists((Join-Path $f.Mod 'kh2/msg/us/sys.bar')))
}
Run-Test 'new mod after removal prevents overwrite during recovery' {
    $f=Fixture; $r=Invoke-Removal (Plan $f) $f.Recovery; $p=Join-Path $f.Mod 'kh2/msg/us/sys.bar'; Put $p 'new 1.0.2 mod'
    Expect-Failure { Restore-Removal $r.RecoveryDir $f.Payload $f.Loader }
    Assert ([IO.File]::ReadAllText($p) -eq 'new 1.0.2 mod')
    Assert (-not [IO.File]::Exists((Join-Path $f.Mod 'kh2/msg/us/fontimage.bar')))
}
Run-Test 'recovery journal cannot target saves or arbitrary files' {
    $f=Fixture; $r=Invoke-Removal (Plan $f) $f.Recovery
    $j=[IO.File]::ReadAllText((Join-Path $r.RecoveryDir 'recovery.json')) | ConvertFrom-Json
    $save=Join-Path $f.Game 'Save/save.dat'; $before=Get-ContentHash $save
    $j.Records[0].Path=$save; Write-RecoveryJournal $r.RecoveryDir $j
    Expect-Failure { Restore-Removal $r.RecoveryDir $f.Payload $f.Loader }
    Assert ((Get-ContentHash $save) -eq $before)
}
Run-Test 'recovery folder inside mod root rejected' {
    $f=Fixture
    Expect-Failure { Invoke-Removal (Plan $f) (Join-Path $f.Mod 'unsafe-recovery') }
    Assert ([IO.File]::Exists((Join-Path $f.Mod 'kh2/msg/us/sys.bar')))
}
Run-Test 'unproven version rejected' {
    $f=Fixture
    Expect-Failure { New-RemovalPlan $f.App $f.Payload $f.Loader @() }
    $f.Reg.DisplayVersion='1.0.0'
    Expect-Failure { New-RemovalPlan $f.App $f.Payload $f.Loader @($f.Reg) }
    Assert ([IO.File]::Exists((Join-Path $f.Mod 'kh2/msg/us/sys.bar')))
}
Run-Test 'unsafe manifest path rejected' {
    $f=Fixture; $f.Payload[0].path='../Save/save.dat'
    Expect-Failure { Plan $f }
}
Run-Test 'symbolic link in payload path rejected' {
    $f=Fixture; $p=Join-Path $f.Mod 'kh2/msg/us/sys.bar'; $external=Join-Path $f.Root 'external.bar'; Put $external 'external'
    [IO.File]::Delete($p)
    [void](New-Item -ItemType SymbolicLink -Path $p -Target $external)
    Expect-Failure { Plan $f }
    Assert ([IO.File]::ReadAllText($external) -eq 'external')
}
Run-Test 'untracked backup stays untouched' {
    $f=Fixture; $p=Join-Path $f.Mod 'kh2/msg/us/sys.bar'; Put ($p+'.kh2ar.bak') 'untracked original'
    $plan=Plan $f; Assert (-not $plan.LoaderRemoved)
    [void](Invoke-Removal $plan $f.Recovery)
    Assert ([IO.File]::ReadAllText($p+'.kh2ar.bak') -eq 'untracked original')
}

Run-Test '24 resource fingerprints prove an unregistered 1.0.1 install' {
    $f=Fixture; $payload=@($f.Payload | Where-Object { $_.path -eq 'image/test.dds' })
    $bars=@('sys','tt','di','es','wm','hb','mu','bb','he','dc','ca','al','nm','lk','lm','tr','po','wi','eh','jm','title','gumi','fontimage','fontinfo')
    foreach ($bar in $bars) {
        $relative='msg/us/'+$bar+'.bar'; $p=Join-Path $f.Mod ('kh2/'+$relative); Put $p ('known 1.0.1 '+$bar)
        $payload += [pscustomobject]@{ path=$relative; size=([IO.FileInfo]$p).Length; sha256=(Get-ContentHash $p) }
    }
    $plan=New-RemovalPlan $f.App $payload $f.Loader @()
    Assert ($plan.Matched -eq 25 -and @($plan.Registrations).Count -eq 0)
    $r=Invoke-Removal $plan $f.Recovery
    [void](Restore-Removal $r.RecoveryDir $payload $f.Loader)
    Assert ([IO.File]::Exists((Join-Path $f.Mod 'kh2/msg/us/sys.bar')))
}

Run-Test 'progress callbacks execute during removal and recovery' {
    $f=Fixture; $script:Stages=New-Object 'Collections.Generic.List[string]'
    $callback={ param($stage,$number,$total) Assert ($number -gt 0 -and $total -ge $number); $script:Stages.Add($stage) }
    $r=Invoke-Removal (Plan $f) $f.Recovery $callback
    [void](Restore-Removal $r.RecoveryDir $f.Payload $f.Loader $callback)
    Assert ($script:Stages.Contains('backup') -and $script:Stages.Contains('remove') -and $script:Stages.Contains('restore'))
}

Run-Test 'legacy catalog selects 1.0.2 and supports full recovery' {
    $f=Fixture; $f.Reg.DisplayVersion='1.0.2'
    $catalog=@{'1.0.1'=$f.Payload; '1.0.2'=$f.Payload}
    $plan=New-GeneralRemovalPlan $f.App $catalog $f.Loader @($f.Reg)
    Assert ($plan.Version -eq '1.0.2'); $plan.Registrations=@()
    $r=Invoke-Removal $plan $f.Recovery
    [void](Restore-Removal -Dir $r.RecoveryDir)
    Assert ([IO.File]::Exists((Join-Path $f.Mod 'kh2/msg/us/sys.bar')))
}
Run-Test 'future 1.0.3 and 12.4.0 resources work without changing the tool catalog' {
    foreach ($version in @('1.0.3','12.4.0')) {
        $f=Fixture; $f.Reg.DisplayVersion=$version
        $path=Join-Path $f.Mod 'kh2/msg/us/new-world.bar'; Put $path ('future translation '+$version)
        $f.Payload+= [pscustomobject]@{path='msg/us/new-world.bar';size=([IO.FileInfo]$path).Length;sha256=(Get-ContentHash $path)}
        $manifest=New-InstallManifest $version $f.Payload $f.Loader
        Put (Join-Path $f.App 'kh2ar_install_manifest.json') ($manifest | ConvertTo-Json -Depth 8)
        $plan=New-GeneralRemovalPlan $f.App @{'1.0.1'=@()} @() @($f.Reg)
        Assert ($plan.Version -eq $version -and $plan.Matched -eq 4); $plan.Registrations=@()
        $r=Invoke-Removal $plan $f.Recovery
        Assert (-not [IO.File]::Exists($path))
        [void](Restore-Removal -Dir $r.RecoveryDir)
        Assert ([IO.File]::ReadAllText($path) -eq ('future translation '+$version))
        Assert ([IO.File]::Exists((Join-Path $f.App 'kh2ar_install_manifest.json')))
    }
}
Run-Test 'unknown release without ownership manifest stops without changing files' {
    $f=Fixture; $f.Reg.DisplayVersion='1.0.3'
    Expect-Failure { New-GeneralRemovalPlan $f.App @{'1.0.1'=$f.Payload} $f.Loader @($f.Reg) }
    Assert ([IO.File]::Exists((Join-Path $f.Mod 'kh2/msg/us/sys.bar')))
}
Run-Test 'unsupported schema and wrong product ownership are rejected' {
    foreach ($mode in @('schema','product')) {
        $f=Fixture; $m=New-InstallManifest '1.0.1' $f.Payload $f.Loader
        if ($mode -eq 'schema') { $m.Schema=2 } else { $m.ProductId='other-project' }
        Put (Join-Path $f.App 'kh2ar_install_manifest.json') ($m | ConvertTo-Json -Depth 8)
        Expect-Failure { New-GeneralRemovalPlan $f.App @{} $f.Loader @($f.Reg) }
        Assert ([IO.File]::Exists((Join-Path $f.Mod 'kh2/msg/us/sys.bar')))
    }
}
Run-Test 'manifest version mismatch prevents removal' {
    $f=Fixture; $m=New-InstallManifest '1.0.3' $f.Payload $f.Loader
    Put (Join-Path $f.App 'kh2ar_install_manifest.json') ($m | ConvertTo-Json -Depth 8)
    Expect-Failure { New-GeneralRemovalPlan $f.App @{} $f.Loader @($f.Reg) }
}
Run-Test 'manifest cannot include game executable, saves, traversal or duplicate resources' {
    foreach ($path in @('../Save/save.dat','/absolute.dds','C:\save.dds','image/a/../save.dds','game.exe')) {
        $f=Fixture; $m=New-InstallManifest '1.0.1' $f.Payload $f.Loader; $m.Payload[0].path=$path
        Expect-Failure { Assert-InstallManifest $m }
    }
    $f=Fixture; $m=New-InstallManifest '1.0.1' $f.Payload $f.Loader; $m.Payload+= $m.Payload[0]
    Expect-Failure { Assert-InstallManifest $m }
    $f=Fixture; $m=New-InstallManifest '1.0.1' $f.Payload $f.Loader; $m.Loader[0].path='Save/save.dat'
    Expect-Failure { Assert-InstallManifest $m }
}
Run-Test 'unregistered future manifest needs matching installer state and bar fingerprints' {
    $f=Fixture; $m=New-InstallManifest '1.0.3' $f.Payload $f.Loader
    Put (Join-Path $f.App 'kh2ar_install_manifest.json') ($m | ConvertTo-Json -Depth 8)
    Expect-Failure { Resolve-InstallManifest $f.App @{} $f.Loader @() }
    Put (Join-Path $f.App 'kh2ar_state.txt') ("GameDir=$($f.Game)`nModRoot=$($f.Mod)`nSettingsByUs=1`nVersion=1.0.3`n")
    $resolved=Resolve-InstallManifest $f.App @{} $f.Loader @()
    Assert ($resolved.Version -eq '1.0.3')
    Expect-Failure { New-GeneralRemovalPlan $f.App @{} $f.Loader @() }
}
Run-Test 'recovery manifest tampering cannot write to a save file' {
    $f=Fixture; $r=Invoke-Removal (Plan $f) $f.Recovery
    $j=[IO.File]::ReadAllText((Join-Path $r.RecoveryDir 'recovery.json')) | ConvertFrom-Json
    $j.InstallManifest.Loader[0].path='Save/save.dat'; Write-RecoveryJournal $r.RecoveryDir $j
    Expect-Failure { Restore-Removal -Dir $r.RecoveryDir }
    Assert ([IO.File]::ReadAllText((Join-Path $f.Game 'Save/save.dat')) -eq 'private save, must remain untouched')
}

$report=[pscustomobject]@{ result='PASS'; passed=$script:Results.Count; platform=[Environment]::OSVersion.Platform.ToString(); scope='Real filesystem tests on Linux; Windows GUI, UAC and registry execution require a Windows smoke test.'; tests=@($script:Results.ToArray()) }
$report | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'CORE_TEST_REPORT.json') -Encoding utf8
Write-Output ('ALL '+$script:Results.Count+' TESTS PASS')
Remove-Item -LiteralPath $script:TestRoot -Recurse -Force
