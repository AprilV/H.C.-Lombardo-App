param(
    [string]$PythonExe = ".venv/Scripts/python.exe"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = (Resolve-Path (Join-Path $scriptDir "../..")).Path

Push-Location $rootDir
try {
    & $PythonExe "scripts/verification/s16_blocker_test_automation.py"
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
