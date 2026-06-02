param(
    [string]$PythonExe = ".venv/Scripts/python.exe"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = (Resolve-Path (Join-Path $scriptDir "../..")).Path

Push-Location $rootDir
try {
    & $PythonExe "scripts/verification/ta016_probe_status.py" | Out-Null
    & $PythonExe "scripts/verification/ta037_gate_status.py" | Out-Null

    $ta016Path = "docs/sprints/ta016_production_updater_check/ta016_probe_status_latest.json"
    $ta037Path = "docs/sprints/ta037_stability_gate/ta037_gate_status_latest.json"

    $ta016 = Get-Content $ta016Path -Raw | ConvertFrom-Json
    $ta037 = Get-Content $ta037Path -Raw | ConvertFrom-Json

    $ta016Ready = -not [bool]$ta016.blocked
    $ta037Ready = [bool]$ta037.closure_ready
    $allReady = $ta016Ready -and $ta037Ready

    Write-Output "TA016_BLOCKED=$($ta016.blocked)"
    Write-Output "TA037_CLOSURE_READY=$($ta037.closure_ready)"
    Write-Output "TA037_ELAPSED_HOURS=$($ta037.elapsed_hours)"
    Write-Output "S16_EXTERNAL_GATES_COMPLETE=$allReady"

    if ($allReady) {
        exit 0
    }

    exit 2
}
finally {
    Pop-Location
}
