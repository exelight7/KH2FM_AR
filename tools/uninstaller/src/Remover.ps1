param([string]$BundleDir = $PSScriptRoot)
Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[Windows.Forms.Application]::EnableVisualStyles()

try {
    . (Join-Path $BundleDir 'Remover.Core.ps1')
    $script:Catalog = @{
        '1.0.1' = @(Import-Csv -LiteralPath (Join-Path $BundleDir 'manifest_1.0.1.csv'))
        '1.0.2' = @(Import-Csv -LiteralPath (Join-Path $BundleDir 'manifest_1.0.2.csv'))
    }
    $script:Loader = @(Import-Csv -LiteralPath (Join-Path $BundleDir 'manifest_panacea.csv'))
    if ($script:Catalog['1.0.1'].Count -ne 798 -or $script:Catalog['1.0.2'].Count -ne 798 -or $script:Loader.Count -ne 14) { throw 'ملفات الأداة غير مكتملة.' }
} catch {
    [void][Windows.Forms.MessageBox]::Show($_.Exception.Message,'أداة إزالة التعريب', 'OK','Error')
    exit 1
}

$script:CurrentPlan = $null
$script:Busy = $false
$script:LastRecovery = ''
$script:RecoveryBase = Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'KH2FM-Arabic-Recovery'
$script:ConfigDir = Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'KH2FM-Arabic-Remover'
$script:LastFile = Join-Path $script:ConfigDir 'last-recovery.txt'
if ([IO.File]::Exists($script:LastFile)) {
    $script:LastRecovery = [IO.File]::ReadAllText($script:LastFile).Trim()
}

function Show-ToolMessage([string]$Text, [string]$Icon = 'Information') {
    [void][Windows.Forms.MessageBox]::Show($script:Window,$Text,'إزالة تعريب KH2FM',[Windows.Forms.MessageBoxButtons]::OK,[Windows.Forms.MessageBoxIcon]::$Icon)
}

function Test-GameClosed {
    $running = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -eq 'KINGDOM HEARTS II FINAL MIX' })
    if ($running.Count -gt 0) { throw 'أغلق Kingdom Hearts II Final Mix ثم أعد المحاولة.' }
}

function Set-Busy([bool]$Busy, [string]$Text) {
    $script:Busy=$Busy
    $script:Summary.Text=$Text
    $script:Window.UseWaitCursor=$Busy
    $script:Browse.Enabled=-not $Busy
    $script:Scan.Enabled=-not $Busy
    $script:Remove.Enabled=($null -ne $script:CurrentPlan) -and -not $Busy
    $script:Restore.Enabled=-not $Busy
    $script:OpenBackup.Enabled=(-not $Busy) -and [IO.Directory]::Exists($script:LastRecovery)
    $script:Window.Refresh()
}

$script:ProgressCallback = {
    param($Stage,$Number,$Total)
    $names=@{ scan='فحص التعريب'; backup='حفظ النسخة الاحتياطية'; remove='إزالة التعريب'; restore='استعادة الحالة السابقة' }
    $script:Summary.Text=$names[$Stage]+': '+$Number+' / '+$Total
    $script:Window.Refresh()
    [Windows.Forms.Application]::DoEvents()
}

function Set-LastRecovery([string]$Dir) {
    $script:LastRecovery=$Dir
    Assert-RegularPath $script:ConfigDir
    [void][IO.Directory]::CreateDirectory($script:ConfigDir)
    [IO.File]::WriteAllText($script:LastFile,$Dir,(New-Object Text.UTF8Encoding($false)))
    $script:RecoveryLabel.Text='النسخة الاحتياطية: '+$Dir
}

function Find-Installation {
    $candidates = @(Get-InstalledRegistrations | Where-Object { (Test-SupportedVersion $_.DisplayVersion) -and $_.InstallLocation })
    foreach ($entry in $candidates) {
        if ([IO.File]::Exists((Join-Path $entry.InstallLocation.Trim('"') 'kh2ar_state.txt'))) {
            return $entry.InstallLocation.Trim('"')
        }
    }
    return Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'KH2FM-Arabic'
}

function Invoke-Scan {
    $script:CurrentPlan=$null
    Set-Busy $true 'جاري فحص ملفات التعريب...'
    try {
        Test-GameClosed
        $plan=New-GeneralRemovalPlan $script:InstallPath.Text $script:Catalog $script:Loader @(Get-InstalledRegistrations) $script:ProgressCallback
        $script:CurrentPlan=$plan
        $text='إصدار التعريب '+$plan.Version+': '+$plan.Matched+' ملفا مطابقا.'
        if ($plan.Skipped.Count -gt 0) { $text+="`r`n"+$plan.Skipped.Count+' ملفا تغير بعد التثبيت؛ ستتركه الأداة.' }
        if ($plan.UnresolvedBackups.Count -gt 0) { $text+="`r`n"+'يوجد سجل قديم يحتاج مراجعة؛ ستبقى بيانات إلغاء التثبيت محفوظة.' }
        if ($plan.LoaderRemoved) { $text+="`r`n"+'ستزال أيضا ملفات محمل المودات التي أضافها المثبت.' }
        else { $text+="`r`n"+'سيبقى محمل المودات وإعداداته الحالية محفوظين.' }
        if ($plan.Actions.Count -eq 0) { $script:CurrentPlan=$null; $text='لم أجد ملفات مطابقة تستلزم الإزالة.' }
        if ($plan.Skipped.Count -gt 0 -or $plan.UnresolvedBackups.Count -gt 0) {
            $script:CurrentPlan=$null
            $report=[pscustomobject]@{ ToolId=$plan.ToolId; State=$plan.State; Matched=$plan.Matched; Missing=$plan.Missing; ChangedFiles=$plan.Skipped; OldBackupLocations=$plan.UnresolvedBackups; Result='Needs custom review; no files removed' }
            Assert-RegularPath $script:ConfigDir
            [void][IO.Directory]::CreateDirectory($script:ConfigDir)
            $reportPath=Join-SafePath $script:ConfigDir 'scan-report.json'
            [IO.File]::WriteAllText($reportPath,($report | ConvertTo-Json -Depth 6),(New-Object Text.UTF8Encoding($false)))
            $text='التثبيت يحتوي ملفات مختلفة عن سجل تثبيت التعريب. تحتاج مراجعة قبل الإزالة.'+"`r`n"+'تقرير الفحص: '+$reportPath
        }
        Set-Busy $false $text
    } catch {
        $script:CurrentPlan=$null
        Set-Busy $false $_.Exception.Message
    }
}

$script:Window=New-Object Windows.Forms.Form
$script:Window.Text='KH2FM — أداة إزالة التعريب'
$script:Window.ClientSize=New-Object Drawing.Size(760,570)
$script:Window.MinimumSize=New-Object Drawing.Size(776,609)
$script:Window.StartPosition='CenterScreen'
$script:Window.RightToLeft='Yes'
$script:Window.RightToLeftLayout=$true
$script:Window.Font=New-Object Drawing.Font('Segoe UI',10)
$script:Window.BackColor=[Drawing.Color]::FromArgb(247,249,250)
$script:Window.AutoScaleMode='Dpi'

function New-Label([string]$Text,[int]$X,[int]$Y,[int]$Width,[int]$Height) {
    $control=New-Object Windows.Forms.Label
    $control.Text=$Text; $control.Location=New-Object Drawing.Point($X,$Y)
    $control.Size=New-Object Drawing.Size($Width,$Height)
    $control.TextAlign='MiddleRight'; $control.Anchor='Top,Left,Right'
    $script:Window.Controls.Add($control)
    return $control
}

$title=New-Label 'إزالة تعريب KH2FM' 24 18 712 42
$title.Font=New-Object Drawing.Font('Segoe UI',18,[Drawing.FontStyle]::Bold)
[void](New-Label 'برنامج مستقل لإزالة التعريب. يفحص الإصدار ويحفظ نسخة احتياطية قبل الإزالة.' 24 66 712 46)
[void](New-Label 'مجلد تثبيت التعريب' 24 120 712 26)

$script:InstallPath=New-Object Windows.Forms.TextBox
$script:InstallPath.Location=New-Object Drawing.Point(150,152)
$script:InstallPath.Size=New-Object Drawing.Size(586,30)
$script:InstallPath.Anchor='Top,Left,Right'; $script:InstallPath.RightToLeft='No'; $script:InstallPath.ReadOnly=$true
$script:Window.Controls.Add($script:InstallPath)

function New-Button([string]$Text,[int]$X,[int]$Y,[int]$Width) {
    $control=New-Object Windows.Forms.Button
    $control.Text=$Text; $control.Location=New-Object Drawing.Point($X,$Y)
    $control.Size=New-Object Drawing.Size($Width,42)
    $control.FlatStyle='System'; $script:Window.Controls.Add($control)
    return $control
}

$script:Browse=New-Button 'اختيار المجلد' 24 148 116
$script:Scan=New-Button 'فحص التعريب' 24 198 712
$script:Scan.Anchor='Top,Left,Right'
$script:Summary=New-Label 'اضغط فحص التعريب لمعرفة الملفات التي ستزال.' 24 252 712 115
$script:Summary.BackColor=[Drawing.Color]::White
$script:Summary.Padding=New-Object Windows.Forms.Padding(12)
$script:Summary.BorderStyle='FixedSingle'
$script:Remove=New-Button 'إزالة التعريب وحفظ نسخة احتياطية' 24 382 712
$script:Remove.Anchor='Top,Left,Right'; $script:Remove.Enabled=$false
$script:Restore=New-Button 'استعادة الحالة قبل الإزالة' 24 440 349
$script:OpenBackup=New-Button 'فتح النسخة الاحتياطية' 386 440 350
$script:RecoveryLabel=New-Label 'النسخة الاحتياطية تحفظ في مجلد مستقل عن اللعبة.' 24 491 712 58
$script:RecoveryLabel.AutoEllipsis=$true

$script:Browse.Add_Click({
    $dialog=New-Object Windows.Forms.FolderBrowserDialog
    $dialog.Description='اختر مجلد KH2FM-Arabic الذي أنشأه المثبت'
    $dialog.ShowNewFolderButton=$false
    if ([IO.Directory]::Exists($script:InstallPath.Text)) { $dialog.SelectedPath=$script:InstallPath.Text }
    if ($dialog.ShowDialog($script:Window) -eq 'OK') {
        $script:InstallPath.Text=$dialog.SelectedPath; Invoke-Scan
    }
    $dialog.Dispose()
})
$script:Scan.Add_Click({ Invoke-Scan })
$script:Remove.Add_Click({
    Invoke-Scan
    if ($null -eq $script:CurrentPlan) { return }
    $answer=[Windows.Forms.MessageBox]::Show($script:Window,'سيحفظ البرنامج نسخة من الملفات أولا، ثم يزيل إصدار التعريب المكتشف. هل تريد المتابعة؟','إزالة التعريب',[Windows.Forms.MessageBoxButtons]::YesNo,[Windows.Forms.MessageBoxIcon]::Question,[Windows.Forms.MessageBoxDefaultButton]::Button2)
    if ($answer -ne 'Yes') { return }
    Set-Busy $true 'جاري حفظ النسخة الاحتياطية ثم إزالة التعريب...'
    try {
        Test-GameClosed
        $result=Invoke-Removal $script:CurrentPlan $script:RecoveryBase $script:ProgressCallback
        Set-LastRecovery $result.RecoveryDir
        $script:CurrentPlan=$null
        if ($result.Complete) { $text='تمت إزالة تعريب KH2FM. يمكنك الآن تشغيل اللعبة أو تثبيت النسخة الجديدة.' }
        else { $text='أزلت الملفات المطابقة. أبقيت الملفات التي تغيرت بعد التثبيت؛ تفاصيلها في تقرير النسخة الاحتياطية.' }
        Set-Busy $false $text
        Show-ToolMessage ($text+"`r`n`r`n"+'النسخة الاحتياطية: '+$result.RecoveryDir)
    } catch {
        $script:CurrentPlan=$null; Set-Busy $false 'لم تكتمل العملية. راجع الرسالة ومسار النسخة الاحتياطية.'
        if ($_.Exception.Data.Contains('RecoveryDir')) { Set-LastRecovery ([string]$_.Exception.Data['RecoveryDir']) }
        Show-ToolMessage $_.Exception.Message 'Error'
    }
})
$script:Restore.Add_Click({
    $dialog=New-Object Windows.Forms.FolderBrowserDialog
    $dialog.Description='اختر مجلد النسخة الاحتياطية الذي يحتوي recovery.json'
    $dialog.ShowNewFolderButton=$false
    if ([IO.Directory]::Exists($script:LastRecovery)) { $dialog.SelectedPath=$script:LastRecovery }
    elseif ([IO.Directory]::Exists($script:RecoveryBase)) { $dialog.SelectedPath=$script:RecoveryBase }
    if ($dialog.ShowDialog($script:Window) -ne 'OK') { $dialog.Dispose(); return }
    $directory=$dialog.SelectedPath; $dialog.Dispose()
    $answer=[Windows.Forms.MessageBox]::Show($script:Window,'هل تريد إعادة الملفات إلى حالتها قبل الإزالة؟ إذا ثبت تعريبا جديدا بعدها، ستمنع الأداة الكتابة فوق الملفات المختلفة.','استعادة التعريب',[Windows.Forms.MessageBoxButtons]::YesNo,[Windows.Forms.MessageBoxIcon]::Question,[Windows.Forms.MessageBoxDefaultButton]::Button2)
    if ($answer -ne 'Yes') { return }
    Set-Busy $true 'جاري التحقق من النسخة الاحتياطية واستعادة الملفات...'
    try {
        Test-GameClosed
        [void](Restore-Removal -Dir $directory -Progress $script:ProgressCallback)
        Set-LastRecovery $directory; $script:CurrentPlan=$null
        Set-Busy $false 'تمت استعادة الحالة قبل الإزالة.'
        Show-ToolMessage 'تمت استعادة الحالة قبل الإزالة.'
    } catch {
        $script:CurrentPlan=$null; Set-Busy $false 'لم تكتمل الاستعادة. راجع الرسالة.'
        Show-ToolMessage $_.Exception.Message 'Error'
    }
})
$script:OpenBackup.Add_Click({
    if ([IO.Directory]::Exists($script:LastRecovery)) {
        try { Start-Process -FilePath (Join-Path $env:WINDIR 'explorer.exe') -ArgumentList ('"'+$script:LastRecovery+'"') }
        catch { Show-ToolMessage $script:LastRecovery }
    }
})
$script:Window.Add_Shown({
    try {
        $script:InstallPath.Text=Find-Installation
        if ([IO.Directory]::Exists($script:LastRecovery)) { $script:RecoveryLabel.Text='النسخة الاحتياطية: '+$script:LastRecovery }
        Set-Busy $false 'اضغط فحص التعريب لمعرفة الملفات التي ستزال.'
    } catch { Show-ToolMessage $_.Exception.Message 'Error' }
})
$script:Window.Add_FormClosing({ param($Sender,$Event) if ($script:Busy) { $Event.Cancel=$true } })
[void]$script:Window.ShowDialog()
$script:Window.Dispose()
