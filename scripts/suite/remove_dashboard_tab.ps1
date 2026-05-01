[CmdletBinding()]
param(
    [string]$FilePath = "pmforge_dashboard/index.html",
    [string]$TabKey = "ailog",
    [string]$PanelId = "tab-ailog",
    [string]$PanelCloseId = "tab-ailog",
    [string]$SectionMarker = "",
    [string]$BackupDir = "backups",
    [switch]$Apply
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

$targetPath = if ([System.IO.Path]::IsPathRooted($FilePath)) {
    $FilePath
}
else {
    Join-Path $repoRoot $FilePath
}

if (-not (Test-Path $targetPath)) {
    throw "Target file not found: $targetPath"
}

$backupRoot = if ([System.IO.Path]::IsPathRooted($BackupDir)) {
    $BackupDir
}
else {
    Join-Path $repoRoot $BackupDir
}

$tabKeyEsc = [regex]::Escape($TabKey)
$panelIdEsc = [regex]::Escape($PanelId)
$panelCloseEsc = [regex]::Escape($PanelCloseId)

$navPattern = '(?m)^[ \t]*<button[^>]*class="nav-tab"[^>]*onclick="showTab\(''{0}'',\s*this\)"[^>]*>.*?</button>\r?\n?' -f $tabKeyEsc
$panelPattern = '(?s)\r?\n?<div id="{0}" class="tab-panel">.*?</div><!-- /{1} -->\r?\n?' -f $panelIdEsc, $panelCloseEsc
$cssHidePattern = '(?m)^[ \t]*#{0}\s*\{{\s*display:\s*none\s*!important;\s*\}}\r?\n?' -f $panelIdEsc

$markerPattern = $null
if (-not [string]::IsNullOrWhiteSpace($SectionMarker)) {
    $markerEsc = [regex]::Escape($SectionMarker)
    $markerPattern = '(?m)^.*{0}.*\r?\n?' -f $markerEsc
}

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$content = [System.IO.File]::ReadAllText($targetPath, $utf8NoBom)

$navCount = [regex]::Matches($content, $navPattern).Count
$panelCount = [regex]::Matches($content, $panelPattern).Count
$cssHideCount = [regex]::Matches($content, $cssHidePattern).Count
$markerCount = if ($markerPattern) { [regex]::Matches($content, $markerPattern).Count } else { 0 }

if ($navCount -gt 1) { throw "Expected at most 1 nav tab match for key '$TabKey', found $navCount." }
if ($panelCount -gt 1) { throw "Expected at most 1 panel block for id '$PanelId', found $panelCount." }
if ($cssHideCount -gt 1) { throw "Expected at most 1 CSS hide rule for '$PanelId', found $cssHideCount." }
if ($markerCount -gt 1) { throw "Expected at most 1 section marker line containing '$SectionMarker', found $markerCount." }

if (($navCount -eq 1 -and $panelCount -eq 0) -or ($navCount -eq 0 -and $panelCount -eq 1)) {
    throw "Inconsistent tab state in $targetPath (nav=$navCount, panel=$panelCount). Refusing to edit."
}

if ($navCount -eq 0 -and $panelCount -eq 0 -and $cssHideCount -eq 0 -and $markerCount -eq 0) {
    Write-Host "No matching tab artifacts found. File already clean: $targetPath"
    exit 0
}

Write-Host "Target: $targetPath"
Write-Host "Plan: nav=$navCount panel=$panelCount cssHideRule=$cssHideCount marker=$markerCount"

if (-not $Apply) {
    Write-Host "Dry run only. Re-run with -Apply to write changes."
    exit 0
}

New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$baseName = [System.IO.Path]::GetFileNameWithoutExtension($targetPath)
$extension = [System.IO.Path]::GetExtension($targetPath)
$backupPath = Join-Path $backupRoot ("{0}_pre_tab_remove_{1}{2}" -f $baseName, $timestamp, $extension)
Copy-Item -Path $targetPath -Destination $backupPath -Force

$newContent = [regex]::Replace($content, $navPattern, '', 1)
$newContent = [regex]::Replace($newContent, $panelPattern, "`r`n", 1)
$newContent = [regex]::Replace($newContent, $cssHidePattern, '', 1)
if ($markerPattern) {
    $newContent = [regex]::Replace($newContent, $markerPattern, '', 1)
}

$verifyNavCount = [regex]::Matches($newContent, $navPattern).Count
$verifyPanelCount = [regex]::Matches($newContent, $panelPattern).Count
$verifyCssHideCount = [regex]::Matches($newContent, $cssHidePattern).Count
$verifyMarkerCount = if ($markerPattern) { [regex]::Matches($newContent, $markerPattern).Count } else { 0 }

if ($verifyNavCount -ne 0 -or $verifyPanelCount -ne 0 -or $verifyCssHideCount -ne 0 -or $verifyMarkerCount -ne 0) {
    throw "Post-edit verification failed (nav=$verifyNavCount panel=$verifyPanelCount css=$verifyCssHideCount marker=$verifyMarkerCount)."
}

[System.IO.File]::WriteAllText($targetPath, $newContent, $utf8NoBom)

Write-Host "Backup created: $backupPath"
Write-Host "Removed nav match count: $navCount"
Write-Host "Removed panel match count: $panelCount"
Write-Host "Removed CSS hide rule count: $cssHideCount"
if ($markerPattern) {
    Write-Host "Removed marker line count: $markerCount"
}
Write-Host "Completed safely."
