param(
    [string]$Reason = "Chat restart checkpoint to prevent drift and preserve continuity.",
    [string]$PythonExe = ".venv/Scripts/python.exe",
    [switch]$SkipApi
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

$scriptPath = Join-Path $repoRoot "scripts/maintenance/session_resume_guard.py"
if (-not (Test-Path $scriptPath)) {
    Write-Host "FAIL: Guard script not found: $scriptPath" -ForegroundColor Red
    exit 2
}

if ($SkipApi) {
    & $pythonPath $scriptPath "--reason" $Reason "--skip-api"
} else {
    & $pythonPath $scriptPath "--reason" $Reason
}
exit $LASTEXITCODE
