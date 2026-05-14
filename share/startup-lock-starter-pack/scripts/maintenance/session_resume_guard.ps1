param(
    [string]$Reason = "Chat restart checkpoint to prevent drift and preserve continuity.",
    [string]$PythonExe = ".venv/Scripts/python.exe",
    [string]$ApiBase = "http://127.0.0.1:5000",
    [string[]]$Check,
    [switch]$SkipApi
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "../..")
Set-Location $repoRoot

function Resolve-PythonPath {
    param([string]$Candidate, [string]$Repo)

    if (Test-Path $Candidate) {
        return (Resolve-Path $Candidate).Path
    }

    $joined = Join-Path $Repo $Candidate
    if (Test-Path $joined) {
        return (Resolve-Path $joined).Path
    }

    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        return $pythonCmd.Source
    }

    return $null
}

$pythonPath = Resolve-PythonPath -Candidate $PythonExe -Repo $repoRoot
if (-not $pythonPath) {
    Write-Host "FAIL: Python executable not found." -ForegroundColor Red
    Write-Host "Tried: $PythonExe and PATH lookup for 'python'" -ForegroundColor Red
    exit 2
}

$scriptPath = Join-Path $repoRoot "scripts/maintenance/session_resume_guard.py"
if (-not (Test-Path $scriptPath)) {
    Write-Host "FAIL: Guard script not found: $scriptPath" -ForegroundColor Red
    exit 2
}

$args = @(
    $scriptPath,
    "--reason", $Reason,
    "--api-base", $ApiBase
)

if ($SkipApi) {
    $args += "--skip-api"
}

if ($Check) {
    foreach ($entry in $Check) {
        $args += "--check"
        $args += $entry
    }
}

& $pythonPath @args
exit $LASTEXITCODE
