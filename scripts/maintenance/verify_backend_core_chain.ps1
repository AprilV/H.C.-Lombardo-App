param(
    [string]$BaseUrl = "http://localhost:5000",
    [int]$Season = 2025,
    [string]$PythonExe = ".venv/Scripts/python.exe"
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

$verifyScript = Join-Path $repoRoot "scripts/verification/test_backend_core_chain.py"
if (-not (Test-Path $verifyScript)) {
    Write-Host "FAIL: Verification script not found: $verifyScript" -ForegroundColor Red
    exit 2
}

Write-Host "Running core backend verification chain ..." -ForegroundColor Cyan
& $pythonPath $verifyScript --base-url $BaseUrl --season $Season

if ($LASTEXITCODE -ne 0) {
    Write-Host "FAIL: Core backend verification chain reported regressions." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "PASS: Core backend verification chain completed successfully." -ForegroundColor Green
exit 0
