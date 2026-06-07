param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "../..")
$hookPath = Join-Path $repoRoot ".githooks"
$prePushHook = Join-Path $hookPath "pre-push"

if (-not (Test-Path $prePushHook)) {
    Write-Host "FAIL: Missing hook file: $prePushHook" -ForegroundColor Red
    exit 1
}

if ($Force) {
    git config --local --unset core.hooksPath 2>$null
}

git config --local core.hooksPath ".githooks"

Write-Host "PASS: Git hooksPath set to .githooks" -ForegroundColor Green
Write-Host "Pre-push guard active via: .githooks/pre-push" -ForegroundColor Green
Write-Host "Optional public auth checks: set HCL_PREPUSH_BASE_URL and HCL_PREPUSH_PUBLIC_SITE_URL env vars before push." -ForegroundColor Yellow
Write-Host "Or persist repo-local URLs with: ./scripts/maintenance/set_prepush_public_gate_config.ps1" -ForegroundColor Yellow
Write-Host "Emergency bypass: set HCL_SKIP_PRE_PUSH_GUARD=1 for one push only." -ForegroundColor Yellow
