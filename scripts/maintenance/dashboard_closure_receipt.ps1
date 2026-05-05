param(
    [Parameter(Mandatory = $true)]
    [int]$Sprint,

    [Parameter(Mandatory = $true)]
    [string]$Subtask,

    [string]$PythonExe = ".venv/Scripts/python.exe"
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "../..")
Set-Location $repoRoot

$gateScript = Join-Path $repoRoot "scripts/maintenance/dashboard_closure_gate.py"
if (-not (Test-Path $gateScript)) {
    Write-Host "FAIL: Gate script not found: $gateScript" -ForegroundColor Red
    exit 2
}

$pythonPath = $PythonExe
if (-not (Test-Path $pythonPath)) {
    $pythonPath = Join-Path $repoRoot $PythonExe
}

if (-not (Test-Path $pythonPath)) {
    Write-Host "FAIL: Python executable not found at: $PythonExe" -ForegroundColor Red
    exit 2
}

Write-Host "Running subtask closure gate for sprint $Sprint, subtask $Subtask ..." -ForegroundColor Cyan
& $pythonPath $gateScript subtask --sprint $Sprint --subtask $Subtask
if ($LASTEXITCODE -ne 0) {
    Write-Host "FAIL: Subtask closure gate failed." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "Running full sprint closure gate for sprint $Sprint ..." -ForegroundColor Cyan
& $pythonPath $gateScript check --sprint $Sprint
if ($LASTEXITCODE -ne 0) {
    Write-Host "FAIL: Sprint closure gate failed." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "PASS: Dashboard closure receipt is clean. Safe to mark this subtask complete." -ForegroundColor Green
exit 0
