param([string]$BundleDir = $PSScriptRoot)
Set-StrictMode -Version 2.0
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[Windows.Forms.Application]::EnableVisualStyles()
try {
    . (Join-Path $BundleDir 'Remover.Core.ps1')
    $script:Catalog=@{
        '1.0.1'=@(Import-Csv -LiteralPath (Join-Path $BundleDir 'manifest_1.0.1.csv'))
        '1.0.2'=@(Import-Csv -LiteralPath (Join-Path $BundleDir 'manifest_1.0.2.csv'))
    }
    $script:Loader=@(Import-Csv -LiteralPath (Join-Path $BundleDir 'manifest_panacea.csv'))
    if ($script:Catalog['1.0.1'].Count -ne 798 -or $script:Catalog['1.0.2'].Count -ne 798 -or $script:Loader.Count -ne 14) { throw 'ملف البرنامج غير مكتمل. أعد تحميله.' }
} catch {
    [void][Windows.Forms.MessageBox]::Show($_.Exception.Message,'حذف التعريب','OK','Error')
    exit 1
}
$script:Busy=$false
$script:LastRecovery=''
$script:RecoveryBase=Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'KH2FM-Arabic-Recovery'
$script:ConfigDir=Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'KH2FM-Arabic-Remover'

function Set-Status([string]$Text,[bool]$IsError=$false) {
    $script:Status.Text=$Text
    if ($IsError) { $script:Status.ForeColor=[Drawing.Color]::FromArgb(168,32,32) }
    else { $script:Status.ForeColor=[Drawing.Color]::FromArgb(36,79,56) }
    $script:Window.Refresh()
}
function Set-Busy([bool]$Busy,[string]$Text) {
    $script:Busy=$Busy
    $script:GamePath.Enabled=-not $Busy
    $script:Browse.Enabled=-not $Busy
    $script:Delete.Enabled=-not $Busy
    $script:Undo.Enabled=-not $Busy
    $script:Window.UseWaitCursor=$Busy
    Set-Status $Text
}
function Test-GameClosed {
    $running=@(Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -in @('KINGDOM HEARTS II FINAL MIX','OpenKh.Tools.ModsManager') })
    if ($running.Count -gt 0) { throw 'أغلق اللعبة وبرنامج OpenKH، ثم اضغط حذف التعريب.' }
}
$script:ProgressCallback={
    param($Stage,$Number,$Total)
    $script:Window.Refresh()
    [Windows.Forms.Application]::DoEvents()
}
function Save-LastRecovery([string]$Dir) {
    $script:LastRecovery=$Dir
    Assert-RegularPath $script:ConfigDir
    [void][IO.Directory]::CreateDirectory($script:ConfigDir)
    [IO.File]::WriteAllText((Join-SafePath $script:ConfigDir 'last-recovery.txt'),$Dir,(New-Object Text.UTF8Encoding($false)))
}

$script:Window=New-Object Windows.Forms.Form
$script:Window.Text='حذف تعريب KH2FM'
$script:Window.ClientSize=New-Object Drawing.Size(820,230)
$script:Window.FormBorderStyle='FixedDialog'
$script:Window.MaximizeBox=$false
$script:Window.StartPosition='CenterScreen'
$script:Window.RightToLeft='Yes'
$script:Window.RightToLeftLayout=$true
$script:Window.Font=New-Object Drawing.Font('Segoe UI',10)
$script:Window.BackColor=[Drawing.Color]::FromArgb(247,249,250)
$script:Window.AutoScaleMode='Dpi'

$label=New-Object Windows.Forms.Label
$label.Text='مجلد اللعبة'
$label.Location=New-Object Drawing.Point(20,16)
$label.Size=New-Object Drawing.Size(780,28)
$label.TextAlign='MiddleRight'
$script:Window.Controls.Add($label)

$script:GamePath=New-Object Windows.Forms.TextBox
$script:GamePath.Name='GamePath'; $script:GamePath.AccessibleName='GamePath'
$script:GamePath.Location=New-Object Drawing.Point(20,50)
$script:GamePath.Size=New-Object Drawing.Size(722,30)
$script:GamePath.RightToLeft='No'
$script:GamePath.Font=New-Object Drawing.Font('Segoe UI',9)
$script:GamePath.Text='C:\Program Files (x86)\Steam\steamapps\common\KINGDOM HEARTS -HD 1.5+2.5 ReMIX-'
$script:GamePath.TabIndex=0
$script:Window.Controls.Add($script:GamePath)

$script:Browse=New-Object Windows.Forms.Button
$script:Browse.Name='BrowseGame'; $script:Browse.AccessibleName='BrowseGame'
$script:Browse.Text='...'
$script:Browse.Location=New-Object Drawing.Point(754,48)
$script:Browse.Size=New-Object Drawing.Size(46,30)
$script:Browse.TabIndex=1
$script:Window.Controls.Add($script:Browse)

$script:Delete=New-Object Windows.Forms.Button
$script:Delete.Name='DeleteTranslation'; $script:Delete.AccessibleName='DeleteTranslation'
$script:Delete.Text='حذف التعريب'
$script:Delete.Location=New-Object Drawing.Point(20,96)
$script:Delete.Size=New-Object Drawing.Size(780,50)
$script:Delete.Font=New-Object Drawing.Font('Segoe UI',13,[Drawing.FontStyle]::Bold)
$script:Delete.TabIndex=2
$script:Window.Controls.Add($script:Delete)
$script:Window.AcceptButton=$script:Delete

$script:Status=New-Object Windows.Forms.Label
$script:Status.Name='StatusText'; $script:Status.AccessibleName='StatusText'
$script:Status.Location=New-Object Drawing.Point(20,155)
$script:Status.Size=New-Object Drawing.Size(780,36)
$script:Status.TextAlign='MiddleRight'
$script:Window.Controls.Add($script:Status)

$script:Undo=New-Object Windows.Forms.LinkLabel
$script:Undo.Name='UndoRemoval'; $script:Undo.AccessibleName='UndoRemoval'
$script:Undo.Text='تراجع عن الحذف'
$script:Undo.Location=New-Object Drawing.Point(20,194)
$script:Undo.Size=New-Object Drawing.Size(780,24)
$script:Undo.TextAlign='MiddleRight'; $script:Undo.Visible=$false
$script:Undo.TabIndex=3
$script:Window.Controls.Add($script:Undo)

$script:GamePath.Add_TextChanged({
    if (-not $script:Busy) { $script:Undo.Visible=$false; $script:Delete.Enabled=$true; Set-Status 'اضغط حذف التعريب.' }
})
$script:Browse.Add_Click({
    $dialog=New-Object Windows.Forms.FolderBrowserDialog
    $dialog.Description='اختر مجلد اللعبة'
    $dialog.ShowNewFolderButton=$false
    if ([IO.Directory]::Exists($script:GamePath.Text)) { $dialog.SelectedPath=$script:GamePath.Text }
    if ($dialog.ShowDialog($script:Window) -eq 'OK') { $script:GamePath.Text=$dialog.SelectedPath }
    $dialog.Dispose()
})
$script:Delete.Add_Click({
    $script:Undo.Visible=$false
    Set-Busy $true 'جاري حذف التعريب...'
    try {
        Test-GameClosed
        $plan=New-GameRemovalPlan $script:GamePath.Text $script:Catalog $script:Loader @(Get-InstalledRegistrations) $script:ProgressCallback
        if ($plan.Skipped.Count -gt 0 -or $plan.UnresolvedBackups.Count -gt 0) {
            Assert-RegularPath $script:ConfigDir
            [void][IO.Directory]::CreateDirectory($script:ConfigDir)
            $report=[pscustomobject]@{GameDir=$plan.State.GameDir;ChangedFiles=$plan.Skipped;OldBackupLocations=$plan.UnresolvedBackups;Result='Stopped before deletion'}
            [IO.File]::WriteAllText((Join-SafePath $script:ConfigDir 'scan-report.json'),($report | ConvertTo-Json -Depth 6),(New-Object Text.UTF8Encoding($false)))
            throw 'بعض ملفات التعريب تغيّرت. لم أحذف شيئًا؛ تحتاج مراجعة هذه الملفات.'
        }
        Test-GameClosed
        $result=Invoke-Removal $plan $script:RecoveryBase $script:ProgressCallback
        Save-LastRecovery $result.RecoveryDir
        Set-Busy $false 'تم حذف التعريب. تقدر تشغل اللعبة الآن.'
        $script:Delete.Enabled=$false
        $script:Undo.Visible=$true
    } catch {
        $message=$_.Exception.Message
        if ($_.Exception.Data.Contains('RecoveryDir')) { Save-LastRecovery ([string]$_.Exception.Data['RecoveryDir']) }
        Set-Busy $false ''
        Set-Status $message $true
    }
})
$script:Undo.Add_LinkClicked({
    Set-Busy $true 'جاري التراجع عن الحذف...'
    try {
        Test-GameClosed
        [void](Restore-Removal -Dir $script:LastRecovery -Progress $script:ProgressCallback)
        Set-Busy $false 'رجع التعريب مثل ما كان.'
        $script:Undo.Visible=$false
    } catch {
        Set-Busy $false ''
        Set-Status $_.Exception.Message $true
    }
})
$script:Window.Add_FormClosing({ param($Sender,$Event) if ($script:Busy) { $Event.Cancel=$true } })
Set-Status 'اضغط حذف التعريب.'
[void]$script:Window.ShowDialog()
$script:Window.Dispose()
