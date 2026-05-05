param(
    [Parameter(Mandatory = $true)]
    [int]$Sprint,

    [Parameter(Mandatory = $true)]
    [string]$Subtask,

    [Parameter(Mandatory = $true)]
    [string]$Resolution,

    [string]$Date,
    [string]$Timestamp,
    [string]$UpdatedBy = "Copilot (automation)",
    [string]$PythonExe = ".venv/Scripts/python.exe",
    [string]$BackupDir = "backups/dashboard_automation",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "../..")
Set-Location $repoRoot

$pythonPath = $PythonExe
if (-not (Test-Path $pythonPath)) {
    $pythonPath = Join-Path $repoRoot $PythonExe
}

if (-not (Test-Path $pythonPath)) {
    Write-Host "FAIL: Python executable not found at: $PythonExe" -ForegroundColor Red
    exit 2
}

$updateScript = Join-Path $repoRoot "scripts/maintenance/dashboard_complete_subtask.py"
if (-not (Test-Path $updateScript)) {
    Write-Host "FAIL: Update script not found: $updateScript" -ForegroundColor Red
    exit 2
}

$receiptScript = Join-Path $repoRoot "scripts/maintenance/dashboard_closure_receipt.ps1"
if (-not (Test-Path $receiptScript)) {
    Write-Host "FAIL: Receipt script not found: $receiptScript" -ForegroundColor Red
    exit 2
}

$args = @(
    $updateScript,
    "--sprint", $Sprint,
    "--subtask", $Subtask,
    "--resolution", $Resolution,
    "--updated-by", $UpdatedBy,
    "--backup-dir", $BackupDir
)

if ($Date) { $args += @("--date", $Date) }
if ($Timestamp) { $args += @("--timestamp", $Timestamp) }
if ($DryRun) { $args += "--dry-run" }

Write-Host "Updating dashboard bookkeeping for sprint $Sprint subtask $Subtask ..." -ForegroundColor Cyan
& $pythonPath @args
if ($LASTEXITCODE -ne 0) {
    Write-Host "FAIL: Subtask bookkeeping update failed." -ForegroundColor Red
    exit $LASTEXITCODE
}

if ($DryRun) {
    Write-Host "DRY RUN: skipping closure receipt." -ForegroundColor Yellow
    exit 0
}

Write-Host "Running closure receipt ..." -ForegroundColor Cyan
& $receiptScript -Sprint $Sprint -Subtask $Subtask -PythonExe $PythonExe
if ($LASTEXITCODE -ne 0) {
    Write-Host "FAIL: Closure receipt failed after bookkeeping update." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "PASS: Subtask bookkeeping + closure receipt complete." -ForegroundColor Green
exit 0
