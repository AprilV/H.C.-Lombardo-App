param(
    [Parameter(Mandatory = $true)]
    [string]$BackupFile,

    [string]$TargetFile = "pmforge_dashboard/index.html",
    [string]$PreRestoreBackupDir = "backups/dashboard_automation/pre_restore"
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "../..")
Set-Location $repoRoot

$backupPath = $BackupFile
if (-not (Test-Path $backupPath)) {
    $backupPath = Join-Path $repoRoot $BackupFile
}

if (-not (Test-Path $backupPath)) {
    Write-Host "FAIL: Backup file not found: $BackupFile" -ForegroundColor Red
    exit 2
}

$targetPath = $TargetFile
if (-not (Test-Path $targetPath)) {
    $targetPath = Join-Path $repoRoot $TargetFile
}

if (-not (Test-Path $targetPath)) {
    Write-Host "FAIL: Target file not found: $TargetFile" -ForegroundColor Red
    exit 2
}

$preRestoreDir = $PreRestoreBackupDir
if (-not (Test-Path $preRestoreDir)) {
    $preRestoreDir = Join-Path $repoRoot $PreRestoreBackupDir
}
if (-not (Test-Path $preRestoreDir)) {
    New-Item -ItemType Directory -Path $preRestoreDir -Force | Out-Null
}

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$targetName = [System.IO.Path]::GetFileName($targetPath)
$preRestoreSnapshot = Join-Path $preRestoreDir ("{0}_{1}.bak" -f $targetName, $stamp)

Copy-Item -Path $targetPath -Destination $preRestoreSnapshot -Force
Copy-Item -Path $backupPath -Destination $targetPath -Force

Write-Host "PASS: Restore complete." -ForegroundColor Green
Write-Host "restored_from=$backupPath"
Write-Host "restored_to=$targetPath"
Write-Host "pre_restore_snapshot=$preRestoreSnapshot"
exit 0
