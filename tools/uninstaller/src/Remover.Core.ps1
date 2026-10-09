Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'
$script:ToolId = 'KH2FM-Arabic-Uninstaller'
$script:AppGuid = '8F3C2A71-6E0B-4D5C-9A1E-2B7D4F60C3A9'

function Get-ContentHash([string]$Path) {
    $stream = [IO.File]::Open($Path, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
    $sha = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-', '').ToLowerInvariant() }
    finally { $sha.Dispose(); $stream.Dispose() }
}

function Get-NormalPath([string]$Path) {
    if ([string]::IsNullOrWhiteSpace($Path) -or -not [IO.Path]::IsPathRooted($Path)) {
        throw 'المسار غير صالح. اختر مجلد تثبيت التعريب الصحيح.'
    }
    $p = [IO.Path]::GetFullPath($Path).TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
    if ($p.Length -lt 4 -or $p -eq [IO.Path]::GetPathRoot($p).TrimEnd([IO.Path]::DirectorySeparatorChar)) {
        throw 'لا يمكن استعمال جذر القرص كمجلد للتعريب.'
    }
    if ($p.StartsWith('\\')) { throw 'اختر مجلدا على قرص محلي.' }
    return $p
}

function Test-InDirectory([string]$Path, [string]$Root) {
    $prefix = $Root.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
    return $Path.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)
}

function Assert-RegularPath([string]$Path) {
    $current = [IO.Path]::GetFullPath($Path)
    while ($current) {
        if ([IO.File]::Exists($current) -or [IO.Directory]::Exists($current)) {
            $attrs = [IO.File]::GetAttributes($current)
            if (($attrs -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw ('المسار يتضمن رابطا أو مجلدا محولا. لم يتغير شيء: ' + $Path)
            }
        }
        $parent = [IO.Path]::GetDirectoryName($current)
        if ($parent -eq $current) { break }
        $current = $parent
    }
}

function Join-SafePath([string]$Root, [string]$Relative) {
    if ($Relative -match '(^|[\\/])\.\.([\\/]|$)' -or [IO.Path]::IsPathRooted($Relative) -or $Relative.Contains(':')) {
        throw 'يوجد مسار غير آمن في قائمة الملفات.'
    }
    $rel = $Relative.Replace('\', [IO.Path]::DirectorySeparatorChar).Replace('/', [IO.Path]::DirectorySeparatorChar)
    $path = [IO.Path]::GetFullPath([IO.Path]::Combine($Root, $rel))
    if (-not (Test-InDirectory $path $Root)) { throw 'مسار الملف خارج المجلد المحدد.' }
    Assert-RegularPath $path
    return $path
}

function Read-InstallState([string]$AppDir) {
    $app = Get-NormalPath $AppDir
    Assert-RegularPath $app
    if ([IO.Path]::GetFileName($app) -ne 'KH2FM-Arabic') { throw 'اختر مجلد KH2FM-Arabic الذي أنشأه المثبت.' }
    $statePath = Join-SafePath $app 'kh2ar_state.txt'
    if (-not [IO.File]::Exists($statePath)) { throw 'لم أجد سجل تثبيت التعريب في هذا المجلد.' }
    $values = @{}
    foreach ($line in [IO.File]::ReadAllLines($statePath)) {
        if ($line -match '^([^=]+)=(.*)$') {
            if ($values.ContainsKey($matches[1])) { throw 'سجل التثبيت يحتوي قيما مكررة.' }
            $values[$matches[1]] = $matches[2]
        }
    }
    if (-not $values.ContainsKey('GameDir') -or -not $values.ContainsKey('ModRoot')) { throw 'سجل التثبيت غير مكتمل.' }
    $game = Get-NormalPath $values.GameDir
    $mod = Get-NormalPath $values.ModRoot
    Assert-RegularPath $game; Assert-RegularPath $mod
    if (-not [IO.File]::Exists((Join-SafePath $game 'KINGDOM HEARTS II FINAL MIX.exe'))) {
        throw 'لم أجد اللعبة في المسار المسجل. لم يتغير شيء.'
    }
    $owned = $values.ContainsKey('SettingsByUs') -and $values.SettingsByUs -eq '1'
    return [pscustomobject]@{ AppDir=$app; GameDir=$game; ModRoot=$mod; SettingsByUs=$owned; Version=$(if ($values.ContainsKey('Version')) { $values.Version } else { '' }) }
}

function Get-InstalledRegistrations {
    if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) { return }
    foreach ($hive in @([Microsoft.Win32.RegistryHive]::LocalMachine, [Microsoft.Win32.RegistryHive]::CurrentUser)) {
        foreach ($view in @([Microsoft.Win32.RegistryView]::Registry64, [Microsoft.Win32.RegistryView]::Registry32)) {
            $base = [Microsoft.Win32.RegistryKey]::OpenBaseKey($hive, $view)
            try {
                foreach ($suffix in @(('{' + $script:AppGuid + '}_is1'), ($script:AppGuid + '_is1'))) {
                    $keyPath = 'Software\Microsoft\Windows\CurrentVersion\Uninstall\' + $suffix
                    $key = $base.OpenSubKey($keyPath)
                    if ($null -eq $key) { continue }
                    try {
                        $values = @()
                        foreach ($name in $key.GetValueNames()) {
                            $values += [pscustomobject]@{ Name=$name; Value=$key.GetValue($name, $null, [Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames); Kind=$key.GetValueKind($name).ToString() }
                        }
                        [pscustomobject]@{
                            Hive=$hive.ToString(); View=$view.ToString(); Key=$keyPath
                            InstallLocation=[string]$key.GetValue('InstallLocation', '')
                            DisplayVersion=[string]$key.GetValue('DisplayVersion', '')
                            Values=$values
                        }
                    } finally { $key.Dispose() }
                }
            } finally { $base.Dispose() }
        }
    }
}

function Test-OnlyListedFiles([string]$Root, $KnownPaths) {
    if (-not [IO.Directory]::Exists($Root)) { return $true }
    $stack = New-Object 'Collections.Generic.Stack[string]'
    $stack.Push($Root); $count = 0
    while ($stack.Count -gt 0) {
        foreach ($path in [IO.Directory]::EnumerateFileSystemEntries($stack.Pop())) {
            $count++
            if ($count -gt 20000) { return $false }
            $attrs = [IO.File]::GetAttributes($path)
            if (($attrs -band [IO.FileAttributes]::ReparsePoint) -ne 0) { return $false }
            if (($attrs -band [IO.FileAttributes]::Directory) -ne 0) { $stack.Push($path) }
            elseif (-not $KnownPaths.ContainsKey($path)) { return $false }
        }
    }
    return $true
}

function New-FileAction([string]$Path, [string]$Hash, [string]$Group, $BackupPaths) {
    $bak = $Path + '.kh2ar.bak'
    Assert-RegularPath $bak
    $restore = $BackupPaths.ContainsKey($Path) -and [IO.File]::Exists($bak)
    return [pscustomobject]@{
        Path=$Path; BeforeHash=$Hash; Group=$Group
        BackupPath=$(if ($restore) { $bak } else { '' })
        BackupHash=$(if ($restore) { Get-ContentHash $bak } else { '' })
    }
}

function New-RemovalPlan([string]$AppDir, $PayloadManifest, $LoaderManifest, $Registrations, [scriptblock]$Progress = $null, [string]$Version = '1.0.1') {
    if (-not (Test-SupportedVersion $Version)) { throw 'رقم إصدار التعريب غير صالح.' }
    $state = Read-InstallState $AppDir
    $regs = @($Registrations | Where-Object {
        $_.InstallLocation -and (Get-NormalPath $_.InstallLocation.Trim('"')) -eq $state.AppDir
    })
    if (@($regs | Where-Object { $_.DisplayVersion -ne $Version }).Count -gt 0) {
        throw 'إصدار سجل البرامج لا يطابق قائمة ملفات التثبيت.'
    }
    $known = New-Object 'Collections.Generic.Dictionary[string,object]' ([StringComparer]::OrdinalIgnoreCase)
    foreach ($entry in $PayloadManifest) {
        if ($entry.sha256 -notmatch '^[a-f0-9]{64}$') { throw 'قائمة البصمات غير صالحة.' }
        $target = Join-SafePath $state.ModRoot ('kh2\' + $entry.path)
        if ($known.ContainsKey($target)) { throw 'قائمة الملفات تحتوي تكرارا.' }
        $known.Add($target, $entry)
    }
    $allowed = New-Object 'Collections.Generic.Dictionary[string,object]' ([StringComparer]::OrdinalIgnoreCase)
    foreach ($target in $known.Keys) { $allowed.Add($target, $true) }
    foreach ($entry in $LoaderManifest) {
        $target = Join-SafePath $state.GameDir $entry.path
        $allowed.Add($target, $true)
    }
    $settings = Join-SafePath $state.GameDir 'panacea_settings.txt'; $allowed.Add($settings, $true)
    $backups = New-Object 'Collections.Generic.Dictionary[string,object]' ([StringComparer]::OrdinalIgnoreCase)
    $unresolved = New-Object 'Collections.Generic.List[string]'
    $backupList = Join-SafePath $state.AppDir 'kh2ar_backups.txt'
    if ([IO.File]::Exists($backupList)) {
        foreach ($line in [IO.File]::ReadAllLines($backupList)) {
            if (-not $line.Trim()) { continue }
            $p = Get-NormalPath $line.Trim()
            if ($allowed.ContainsKey($p)) { $backups[$p] = $true }
            else { $unresolved.Add($p) }
        }
    }
    $actions = New-Object 'Collections.Generic.List[object]'
    $skipped = New-Object 'Collections.Generic.List[string]'
    $missing = 0; $matched = 0; $anchors = 0; $payloadBackups = $false
    $checked=0
    foreach ($target in ($known.Keys | Sort-Object)) {
        $checked++
        if ($Progress -and ($checked % 20 -eq 0 -or $checked -eq $known.Count)) { & $Progress 'scan' $checked $known.Count }
        $expected = $known[$target]
        $hash = ''
        if ([IO.File]::Exists($target)) {
            $info = New-Object IO.FileInfo($target)
            if ($info.Length -eq [long]$expected.size) { $hash = Get-ContentHash $target }
            if ($hash -ne $expected.sha256) { $skipped.Add($target); continue }
            $matched++
            if ($expected.path -match '^msg[\\/]us[\\/].+\.bar$') { $anchors++ }
        } else { $missing++ }
        if ($hash -or ($backups.ContainsKey($target) -and [IO.File]::Exists($target + '.kh2ar.bak'))) {
            $action = New-FileAction $target $hash 'payload' $backups
            if ($action.BackupPath) { $payloadBackups = $true }
            $actions.Add($action)
        }
    }
    if ($regs.Count -eq 0 -and $anchors -ne 24) {
        throw 'لم أتمكن من إثبات إصدار هذا التثبيت. لم يتغير شيء؛ احفظ نتيجة الفحص للمراجعة.'
    }
    $loaderRemoved = $false
    $otherMods = $payloadBackups -or $skipped.Count -gt 0 -or $unresolved.Count -gt 0 -or -not (Test-OnlyListedFiles $state.ModRoot $known)
    if ($state.SettingsByUs -and -not $otherMods -and [IO.File]::Exists($settings)) {
        $expectedText = 'mod_path=' + $state.ModRoot + "`nshow_console=false"
        $actualText = [IO.File]::ReadAllText($settings).Replace("`r`n", "`n").TrimEnd("`r", "`n")
        $loaderOK = ($actualText -ceq $expectedText) -and -not [IO.File]::Exists((Join-SafePath $state.GameDir 'version.dll'))
        foreach ($entry in $LoaderManifest) {
            $target = Join-SafePath $state.GameDir $entry.path
            if ([IO.File]::Exists($target) -and (Get-ContentHash $target) -ne $entry.sha256) { $loaderOK = $false }
        }
        if ($loaderOK) {
            foreach ($entry in $LoaderManifest) {
                $target = Join-SafePath $state.GameDir $entry.path
                if ([IO.File]::Exists($target) -or ($backups.ContainsKey($target) -and [IO.File]::Exists($target + '.kh2ar.bak'))) {
                    $h = $(if ([IO.File]::Exists($target)) { Get-ContentHash $target } else { '' })
                    $actions.Add((New-FileAction $target $h 'loader' $backups))
                }
            }
            $actions.Add((New-FileAction $settings (Get-ContentHash $settings) 'loader' $backups))
            $loaderRemoved = $true
        }
    }
    $complete = $skipped.Count -eq 0 -and $unresolved.Count -eq 0
    if ($complete) {
        $metadata = @('kh2ar_state.txt', 'kh2ar_backups.txt', 'kh2ar_dirs.txt', 'kh2ar_install_manifest.json')
        foreach ($file in [IO.Directory]::EnumerateFiles($state.AppDir)) {
            if ([IO.Path]::GetFileName($file) -match '^unins[0-9]{3}\.(exe|dat|msg)$') { $metadata += [IO.Path]::GetFileName($file) }
        }
        foreach ($relative in $metadata) {
            $target = Join-SafePath $state.AppDir $relative
            if ([IO.File]::Exists($target)) { $actions.Add((New-FileAction $target (Get-ContentHash $target) 'metadata' @{})) }
        }
    }
    $planRegistrations=@()
    if ($complete) { $planRegistrations=@($regs) }
    return [pscustomobject]@{
        ToolId=$script:ToolId; Version=$Version; InstallManifest=(New-InstallManifest $Version $PayloadManifest $LoaderManifest); State=$state; Actions=@($actions.ToArray())
        Skipped=@($skipped.ToArray()); UnresolvedBackups=@($unresolved.ToArray())
        Matched=$matched; Missing=$missing; Complete=$complete
        LoaderRemoved=$loaderRemoved; Registrations=$planRegistrations
        PayloadManifest=$PayloadManifest; LoaderManifest=$LoaderManifest
    }
}

function Write-RecoveryJournal([string]$Dir, $Journal) {
    $json = ConvertTo-Json -InputObject $Journal -Depth 14
    $tmp = Join-SafePath $Dir 'recovery.json.tmp'
    [IO.File]::WriteAllText($tmp, $json, (New-Object Text.UTF8Encoding($false)))
    Move-Item -LiteralPath $tmp -Destination (Join-SafePath $Dir 'recovery.json') -Force
}

function Get-CurrentHash([string]$Path) {
    Assert-RegularPath $Path
    if ([IO.Directory]::Exists($Path)) { throw ('يوجد مجلد مكان ملف متوقع: ' + $Path) }
    if ([IO.File]::Exists($Path)) { return Get-ContentHash $Path }
    return ''
}

function Save-SnapshotRecord($Records, [string]$Path, [string]$BeforeHash, [string]$AfterHash, [string]$Dir) {
    if ((Get-CurrentHash $Path) -ne $BeforeHash) { throw ('تغير ملف بعد الفحص. أعد الفحص: ' + $Path) }
    $relative = 'files/' + $Records.Count.ToString('D4') + '.bin'
    $attrs = 0; $ticks = 0
    if ($BeforeHash) {
        $dest = Join-SafePath $Dir $relative
        [IO.File]::Copy($Path, $dest, $false)
        if ((Get-ContentHash $dest) -ne $BeforeHash) { throw 'فشل التحقق من النسخة الاحتياطية. لم تبدأ الإزالة.' }
        $attrs = [int][IO.File]::GetAttributes($Path)
        $ticks = [IO.File]::GetLastWriteTimeUtc($Path).Ticks
    }
    $Records.Add([pscustomobject]@{ Path=$Path; BeforeHash=$BeforeHash; AfterHash=$AfterHash; Archive=$relative; Attributes=$attrs; LastWriteTicks=$ticks })
}

function Set-RegistrationState($Entries, [bool]$Restore) {
    if (@($Entries).Count -eq 0) { return }
    if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) { throw 'تغيير سجل البرامج متاح في Windows فقط.' }
    foreach ($entry in $Entries) {
        $allowedKeys = @(('Software\Microsoft\Windows\CurrentVersion\Uninstall\{' + $script:AppGuid + '}_is1'), ('Software\Microsoft\Windows\CurrentVersion\Uninstall\' + $script:AppGuid + '_is1'))
        if ($entry.Key -notin $allowedKeys -or -not (Test-SupportedVersion $entry.DisplayVersion) -or $entry.Hive -notin @('LocalMachine','CurrentUser') -or $entry.View -notin @('Registry64','Registry32')) { throw 'بيانات سجل الاستعادة غير صالحة.' }
        $hive = [Microsoft.Win32.RegistryHive]$entry.Hive
        $view = [Microsoft.Win32.RegistryView]$entry.View
        $base = [Microsoft.Win32.RegistryKey]::OpenBaseKey($hive, $view)
        try {
            $existing = $base.OpenSubKey($entry.Key)
            if ($null -ne $existing) {
                try {
                    if ([string]$existing.GetValue('DisplayVersion','') -ne $entry.DisplayVersion -or (Get-NormalPath ([string]$existing.GetValue('InstallLocation','')).Trim('"')) -ne (Get-NormalPath $entry.InstallLocation.Trim('"'))) { throw 'تغير سجل التثبيت. لن أكتب فوقه.' }
                } finally { $existing.Dispose() }
            }
            if ($Restore) {
                $key = $base.CreateSubKey($entry.Key)
                try {
                    foreach ($value in $entry.Values) {
                        $kind = [Microsoft.Win32.RegistryValueKind]$value.Kind
                        $data = $value.Value
                        if ($value.Kind -eq 'DWord') { $data = [int]$data }
                        elseif ($value.Kind -eq 'QWord') { $data = [long]$data }
                        elseif ($value.Kind -eq 'Binary') { $data = [byte[]]$data }
                        elseif ($value.Kind -eq 'MultiString') { $data = [string[]]$data }
                        $key.SetValue($value.Name, $data, $kind)
                    }
                } finally { $key.Dispose() }
            } elseif ($null -ne $existing) { $base.DeleteSubKeyTree($entry.Key, $false) }
        } finally { $base.Dispose() }
    }
}

function Assert-Journal($Journal, [string]$Dir, $PayloadManifest, $LoaderManifest) {
    if ($Journal.ToolId -ne $script:ToolId -or $Journal.Schema -ne 1) { throw 'هذه ليست نسخة استعادة أنشأتها الأداة.' }
    Assert-InstallManifest $Journal.InstallManifest
    $PayloadManifest=@($Journal.InstallManifest.Payload); $LoaderManifest=@($Journal.InstallManifest.Loader)
    $app = Get-NormalPath $Journal.State.AppDir; $game = Get-NormalPath $Journal.State.GameDir; $mod = Get-NormalPath $Journal.State.ModRoot
    if ([IO.Path]::GetFileName($app) -ne 'KH2FM-Arabic' -or -not [IO.File]::Exists((Join-SafePath $game 'KINGDOM HEARTS II FINAL MIX.exe'))) { throw 'مجلدات الاستعادة لم تعد في مواقعها الأصلية.' }
    $allowed = New-Object 'Collections.Generic.Dictionary[string,object]' ([StringComparer]::OrdinalIgnoreCase)
    foreach ($entry in $PayloadManifest) { $p=Join-SafePath $mod ('kh2\'+$entry.path); $allowed[$p]=$true; $allowed[$p+'.kh2ar.bak']=$true }
    foreach ($entry in $LoaderManifest) { $p=Join-SafePath $game $entry.path; $allowed[$p]=$true; $allowed[$p+'.kh2ar.bak']=$true }
    $p=Join-SafePath $game 'panacea_settings.txt'; $allowed[$p]=$true; $allowed[$p+'.kh2ar.bak']=$true
    foreach ($name in @('kh2ar_state.txt','kh2ar_backups.txt','kh2ar_dirs.txt','kh2ar_install_manifest.json')) { $allowed[(Join-SafePath $app $name)]=$true }
    $seen = @{}
    foreach ($record in $Journal.Records) {
        $path = Get-NormalPath $record.Path; Assert-RegularPath $path
        $metadata = (Test-InDirectory $path $app) -and [IO.Path]::GetDirectoryName($path) -eq $app -and [IO.Path]::GetFileName($path) -match '^unins[0-9]{3}\.(exe|dat|msg)$'
        if (-not $allowed.ContainsKey($path) -and -not $metadata) { throw 'سجل الاستعادة يشير إلى ملف غير تابع للتعريب.' }
        if ($seen.ContainsKey($path)) { throw 'سجل الاستعادة يحتوي مسارا مكررا.' }; $seen[$path]=$true
        if ($record.Archive -notmatch '^files/[0-9]{4,5}\.bin$' -or ($record.BeforeHash -and $record.BeforeHash -notmatch '^[a-f0-9]{64}$') -or ($record.AfterHash -and $record.AfterHash -notmatch '^[a-f0-9]{64}$')) { throw 'بيانات الاستعادة غير صالحة.' }
        if ($record.BeforeHash -and (Get-CurrentHash (Join-SafePath $Dir $record.Archive)) -ne $record.BeforeHash) { throw 'النسخة الاحتياطية ناقصة أو تغيرت. لم تبدأ الاستعادة.' }
    }
    foreach ($reg in $Journal.Registrations) {
        if ($reg.DisplayVersion -ne $Journal.InstallManifest.Version) { throw 'إصدار سجل الاستعادة غير مطابق.' }
        if ((Get-NormalPath $reg.InstallLocation.Trim('"')) -ne $app) { throw 'سجل البرامج لا يطابق مجلد التعريب.' }
    }
}

function Restore-Removal([string]$Dir, $PayloadManifest = $null, $LoaderManifest = $null, [scriptblock]$Progress = $null) {
    $dir = Get-NormalPath $Dir; Assert-RegularPath $dir
    $journal = [IO.File]::ReadAllText((Join-SafePath $dir 'recovery.json')) | ConvertFrom-Json
    Assert-Journal $journal $dir $PayloadManifest $LoaderManifest
    Assert-RegistrationIdentity @($journal.Registrations)
    # Check all destinations first, so a changed post-removal file is never overwritten.
    foreach ($record in $journal.Records) {
        $now = Get-CurrentHash $record.Path
        if ($now -and $now -ne $record.BeforeHash -and $now -ne $record.AfterHash) { throw ('تغير ملف بعد الإزالة. لن أكتب فوقه: ' + $record.Path) }
    }
    $records = @($journal.Records)
    for ($i=$records.Count-1; $i -ge 0; $i--) {
        if ($Progress) { & $Progress 'restore' ($records.Count-$i) $records.Count }
        $record=$records[$i]; $now=Get-CurrentHash $record.Path
        if ($now -eq $record.BeforeHash) { continue }
        if ($now -and $now -ne $record.AfterHash) { throw ('تغير ملف أثناء الاستعادة: ' + $record.Path) }
        if ($record.BeforeHash) {
            [void][IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($record.Path))
            if ([IO.File]::Exists($record.Path)) { [IO.File]::SetAttributes($record.Path,[IO.FileAttributes]::Normal) }
            [IO.File]::Copy((Join-SafePath $dir $record.Archive), $record.Path, $true)
            if ((Get-ContentHash $record.Path) -ne $record.BeforeHash) { throw 'لم تنجح مطابقة الملف المستعاد.' }
            [IO.File]::SetLastWriteTimeUtc($record.Path, (New-Object DateTime([long]$record.LastWriteTicks,[DateTimeKind]::Utc)))
            [IO.File]::SetAttributes($record.Path,[IO.FileAttributes]$record.Attributes)
        } elseif ([IO.File]::Exists($record.Path)) {
            [IO.File]::SetAttributes($record.Path,[IO.FileAttributes]::Normal)
            [IO.File]::Delete($record.Path)
        }
    }
    Set-RegistrationState @($journal.Registrations) $true
    $journal.Phase='Restored'; Write-RecoveryJournal $dir $journal
    return $journal
}

function Invoke-Removal($Plan, [string]$RecoveryBase, [scriptblock]$Progress = $null) {
    if ($Plan.Skipped.Count -gt 0 -or $Plan.UnresolvedBackups.Count -gt 0) {
        throw 'تغيرت ملفات عن سجل تثبيت التعريب. لم تبدأ الإزالة؛ راجع تقرير الفحص.'
    }
    Assert-RegistrationIdentity @($Plan.Registrations)
    $base=Get-NormalPath $RecoveryBase; Assert-RegularPath $base
    foreach ($root in @($Plan.State.AppDir,$Plan.State.ModRoot,$Plan.State.GameDir)) {
        if ($base -eq $root -or (Test-InDirectory $base $root) -or (Test-InDirectory $root $base)) { throw 'اختر مكانا مستقلا للنسخة الاحتياطية خارج مجلدات التثبيت.' }
    }
    $dir=Join-SafePath $base ((Get-Date -Format 'yyyyMMdd-HHmmss')+'-'+[Guid]::NewGuid().ToString('N').Substring(0,8))
    [void][IO.Directory]::CreateDirectory((Join-SafePath $dir 'files'))
    $records=New-Object 'Collections.Generic.List[object]'
    $journal=[pscustomobject]@{ ToolId=$script:ToolId; Schema=1; InstallManifest=$Plan.InstallManifest; CreatedAt=(Get-Date).ToString('o'); Phase='Preparing'; State=$Plan.State; Records=@(); Registrations=@($Plan.Registrations); Skipped=$Plan.Skipped; UnresolvedBackups=$Plan.UnresolvedBackups }
    Write-RecoveryJournal $dir $journal
    $processed=0
    foreach ($action in $Plan.Actions) {
        $processed++
        if ($Progress) { & $Progress 'backup' $processed $Plan.Actions.Count }
        Save-SnapshotRecord $records $action.Path $action.BeforeHash $action.BackupHash $dir
        if ($action.BackupPath) { Save-SnapshotRecord $records $action.BackupPath $action.BackupHash '' $dir }
    }
    $journal.Records=@($records.ToArray()); $journal.Phase='Prepared'; Write-RecoveryJournal $dir $journal
    Assert-Journal $journal $dir $Plan.PayloadManifest $Plan.LoaderManifest
    try {
        $journal.Phase='Removing'; Write-RecoveryJournal $dir $journal
        $processed=0
        foreach ($action in $Plan.Actions) {
            $processed++
            if ($Progress) { & $Progress 'remove' $processed $Plan.Actions.Count }
            if ((Get-CurrentHash $action.Path) -ne $action.BeforeHash) { throw ('تغير ملف أثناء الإزالة: '+$action.Path) }
            if ($action.BackupPath -and (Get-CurrentHash $action.BackupPath) -ne $action.BackupHash) { throw 'تغيرت نسخة ملف قديم؛ أوقفت العملية.' }
            if ($action.BeforeHash) { [IO.File]::SetAttributes($action.Path,[IO.FileAttributes]::Normal); [IO.File]::Delete($action.Path) }
            if ($action.BackupPath) {
                [void][IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($action.Path))
                [IO.File]::Copy($action.BackupPath,$action.Path,$false)
                if ((Get-ContentHash $action.Path) -ne $action.BackupHash) { throw 'فشل التحقق من استعادة ملف سابق.' }
                [IO.File]::SetAttributes($action.BackupPath,[IO.FileAttributes]::Normal); [IO.File]::Delete($action.BackupPath)
            }
        }
        Set-RegistrationState @($Plan.Registrations) $false
        $journal.Phase='Removed'; Write-RecoveryJournal $dir $journal
        return [pscustomobject]@{ RecoveryDir=$dir; Complete=$Plan.Complete; Matched=$Plan.Matched; Skipped=$Plan.Skipped; LoaderRemoved=$Plan.LoaderRemoved }
    } catch {
        $errorText=$_.Exception.Message
        try { [void](Restore-Removal $dir $Plan.PayloadManifest $Plan.LoaderManifest $Progress); $recoveryText='أعدت الملفات إلى حالتها السابقة.' }
        catch { $recoveryText='النسخة الاحتياطية محفوظة. استعمل زر الاستعادة؛ المسار: '+$dir+'. '+$_.Exception.Message }
        $failure=New-Object Management.Automation.RuntimeException($errorText+"`r`n"+$recoveryText)
        $failure.Data['RecoveryDir']=$dir
        throw $failure
    }
}

function Test-SupportedVersion([string]$Version) {
    if ($Version -notmatch '^([0-9]+)\.([0-9]+)\.([0-9]+)(-[0-9A-Za-z.-]+)?$') { return $false }
    try { return ([version]($matches[1]+'.'+$matches[2]+'.'+$matches[3])) -ge [version]'1.0.1' } catch { return $false }
}

function New-InstallManifest([string]$Version, $Payload, $Loader) {
    return [pscustomobject]@{ Schema=1; ProductId=$script:AppGuid; Version=$Version; Payload=@($Payload); Loader=@($Loader) }
}

function Assert-InstallManifest($Manifest) {
    if ($Manifest.Schema -ne 1 -or $Manifest.ProductId -ne $script:AppGuid -or -not (Test-SupportedVersion $Manifest.Version)) {
        throw 'سجل ملفات التعريب غير متوافق. لم يتغير شيء.'
    }
    if (@($Manifest.Payload).Count -lt 1 -or @($Manifest.Payload).Count -gt 10000 -or @($Manifest.Loader).Count -gt 100) { throw 'عدد الملفات في سجل التثبيت غير صالح.' }
    $seen=@{}
    foreach ($entry in $Manifest.Payload) {
        $rel=([string]$entry.path).Replace('\','/')
        if ($rel -notmatch '^[A-Za-z0-9_./-]+\.(bar|png|dds)$' -or $rel -match '(^|/)\.\.?(/|$)' -or $rel.StartsWith('/') -or $entry.sha256 -notmatch '^[a-f0-9]{64}$' -or [string]$entry.size -notmatch '^[0-9]+$' -or [decimal]$entry.size -gt 1073741824) { throw 'مسار أو بصمة مورد غير صالح في سجل التعريب.' }
        if ($seen.ContainsKey($rel)) { throw 'سجل التعريب يحتوي مسارا مكررا.' }; $seen[$rel]=$true
    }
    $seen=@{}
    foreach ($entry in $Manifest.Loader) {
        $rel=([string]$entry.path).Replace('\','/')
        if ($rel -notmatch '^(DBGHELP\.dll|dependencies/[A-Za-z0-9_-]+\.dll)$' -or $entry.sha256 -notmatch '^[a-f0-9]{64}$') { throw 'ملف محمل المودات خارج النطاق المتوافق.' }
        if ($seen.ContainsKey($rel)) { throw 'سجل المحمل يحتوي مسارا مكررا.' }; $seen[$rel]=$true
    }
}

function Get-RegistrationVersion($Registrations, [string]$AppDir) {
    $versions=@($Registrations | Where-Object { $_.InstallLocation -and (Get-NormalPath $_.InstallLocation.Trim('"')) -eq $AppDir } | ForEach-Object { $_.DisplayVersion } | Select-Object -Unique)
    if ($versions.Count -gt 1) { throw 'وجدت سجلات تثبيت بإصدارات مختلفة. لم يتغير شيء.' }
    if ($versions.Count -eq 1) { return [string]$versions[0] }
    return ''
}

function Resolve-InstallManifest([string]$AppDir, $Catalog, $LoaderManifest, $Registrations) {
    $state=Read-InstallState $AppDir
    $registered=Get-RegistrationVersion $Registrations $state.AppDir
    $path=Join-SafePath $state.AppDir 'kh2ar_install_manifest.json'
    if ([IO.File]::Exists($path)) {
        if (([IO.FileInfo]$path).Length -gt 8388608) { throw 'سجل ملفات التعريب أكبر من الحد المسموح.' }
        $manifest=[IO.File]::ReadAllText($path) | ConvertFrom-Json
        Assert-InstallManifest $manifest
        if (($registered -and $registered -ne $manifest.Version) -or ($state.Version -and $state.Version -ne $manifest.Version)) { throw 'إصدار التعريب لا يطابق سجل الملفات. لم يتغير شيء.' }
        if (-not $registered -and $state.Version -ne $manifest.Version) { throw 'سجل التثبيت لا يثبت ملكية قائمة الملفات.' }
        return $manifest
    }
    if ($state.Version -and (($registered -and $state.Version -ne $registered) -or -not $Catalog.ContainsKey($state.Version))) { throw 'سجل الملفات مفقود أو إصدار التثبيت متعارض. لم يتغير شيء.' }
    if ($registered) {
        if (-not $Catalog.ContainsKey($registered)) { throw 'هذا الإصدار يحتاج سجل الملفات الذي يوفره المثبت الجديد. لم يتغير شيء.' }
        return New-InstallManifest $registered $Catalog[$registered] $LoaderManifest
    }
    foreach ($version in ($Catalog.Keys | Sort-Object)) {
        $bars=@($Catalog[$version] | Where-Object { $_.path -match '^msg[\\/]us[\\/].+\.bar$' })
        if ($bars.Count -ne 24) { continue }
        $match=$true
        foreach ($bar in $bars) {
            $target=Join-SafePath $state.ModRoot ('kh2\'+$bar.path)
            if (-not [IO.File]::Exists($target) -or (Get-ContentHash $target) -ne $bar.sha256) { $match=$false; break }
        }
        if ($match) { return New-InstallManifest $version $Catalog[$version] $LoaderManifest }
    }
    throw 'لم أتمكن من تحديد إصدار التعريب المثبت. لم يتغير شيء.'
}

function New-GeneralRemovalPlan([string]$AppDir, $Catalog, $LoaderManifest, $Registrations, [scriptblock]$Progress = $null) {
    $manifest=Resolve-InstallManifest $AppDir $Catalog $LoaderManifest $Registrations
    Assert-InstallManifest $manifest
    return New-RemovalPlan $AppDir $manifest.Payload $manifest.Loader $Registrations $Progress $manifest.Version
}

function Assert-RegistrationIdentity($Entries) {
    foreach ($entry in $Entries) {
        $keys=@(('Software\Microsoft\Windows\CurrentVersion\Uninstall\{' + $script:AppGuid + '}_is1'), ('Software\Microsoft\Windows\CurrentVersion\Uninstall\' + $script:AppGuid + '_is1'))
        if ($entry.Key -notin $keys -or -not (Test-SupportedVersion $entry.DisplayVersion) -or $entry.Hive -notin @('LocalMachine','CurrentUser') -or $entry.View -notin @('Registry64','Registry32')) { throw 'سجل البرامج غير صالح.' }
        if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) { throw 'تغيير سجل البرامج متاح في Windows فقط.' }
        $base=[Microsoft.Win32.RegistryKey]::OpenBaseKey([Microsoft.Win32.RegistryHive]$entry.Hive,[Microsoft.Win32.RegistryView]$entry.View)
        try {
            $key=$base.OpenSubKey($entry.Key)
            if ($null -ne $key) {
                try {
                    if ([string]$key.GetValue('DisplayVersion','') -ne $entry.DisplayVersion -or (Get-NormalPath ([string]$key.GetValue('InstallLocation','')).Trim('"')) -ne (Get-NormalPath $entry.InstallLocation.Trim('"'))) { throw 'تغير سجل التثبيت. لم تبدأ العملية.' }
                } finally { $key.Dispose() }
            }
        } finally { $base.Dispose() }
    }
}

function Find-InstallationForGame([string]$GameDir, $Registrations, [string]$LocalAppDir = '') {
    $game=Get-NormalPath $GameDir.Trim().Trim('"')
    Assert-RegularPath $game
    if (-not [IO.File]::Exists((Join-SafePath $game 'KINGDOM HEARTS II FINAL MIX.exe'))) {
        throw 'اختر مجلد اللعبة الذي يحتوي KINGDOM HEARTS II FINAL MIX.exe.'
    }
    if (-not $LocalAppDir) { $LocalAppDir=Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'KH2FM-Arabic' }
    $candidates=New-Object 'Collections.Generic.List[string]'
    foreach ($reg in $Registrations) {
        if ($reg.InstallLocation) { $candidates.Add(([string]$reg.InstallLocation).Trim('"')) }
    }
    $candidates.Add($LocalAppDir)
    $candidates.Add((Join-SafePath $game 'KH2FM-Arabic'))
    $settings=Join-SafePath $game 'panacea_settings.txt'
    if ([IO.File]::Exists($settings) -and ([IO.FileInfo]$settings).Length -le 65536) {
        foreach ($line in [IO.File]::ReadAllLines($settings)) {
            if ($line -match '^mod_path=(.+)$') {
                try {
                    $modPath=$matches[1].Trim().Trim('"').Replace('/',[IO.Path]::DirectorySeparatorChar).Replace('\',[IO.Path]::DirectorySeparatorChar)
                    if (-not [IO.Path]::IsPathRooted($modPath)) { $modPath=[IO.Path]::Combine($game,$modPath) }
                    $current=Get-NormalPath $modPath
                    for ($i=0;$i -lt 6 -and $current;$i++) {
                        if ([IO.Path]::GetFileName($current) -eq 'KH2FM-Arabic') { $candidates.Add($current); break }
                        $current=[IO.Path]::GetDirectoryName($current)
                    }
                } catch { }
            }
        }
    }
    $seen=@{}; $found=New-Object 'Collections.Generic.List[string]'
    foreach ($candidate in $candidates) {
        try {
            $app=Get-NormalPath $candidate
            if ($seen.ContainsKey($app)) { continue }; $seen[$app]=$true
            $state=Read-InstallState $app
            if ($state.GameDir -eq $game) { $found.Add($state.AppDir) }
        } catch { }
    }
    if ($found.Count -eq 1) { return $found[0] }
    if ($found.Count -gt 1) { throw 'وجدت أكثر من تثبيت للتعريب لهذه اللعبة. لم أحذف شيئًا.' }
    throw 'لم أجد تعريبًا مثبتًا لهذه اللعبة. تأكد من مسار اللعبة ثم حاول مرة ثانية.'
}

function New-GameRemovalPlan([string]$GameDir, $Catalog, $LoaderManifest, $Registrations, [scriptblock]$Progress = $null, [string]$LocalAppDir = '') {
    $app=Find-InstallationForGame $GameDir $Registrations $LocalAppDir
    $matching=@($Registrations | Where-Object {
        try { $_.InstallLocation -and (Get-NormalPath ([string]$_.InstallLocation).Trim('"')) -eq $app } catch { $false }
    })
    return New-GeneralRemovalPlan $app $Catalog $LoaderManifest $matching $Progress
}
