param(
    [string]$SuiteRoot = "C:\PMForgeSuite",
    [string]$Version = "",
    [string]$UpdateLegacyDashboard = "false"
)

$ErrorActionPreference = "Stop"

$shouldUpdateLegacyDashboard = ($UpdateLegacyDashboard -eq "true")

$sourceIndex = Join-Path $SuiteRoot "src\pmforge_dashboard\index.html"
if (-not (Test-Path $sourceIndex)) {
    throw "Suite source index not found: $sourceIndex"
}

if ([string]::IsNullOrWhiteSpace($Version)) {
    $versionFile = Join-Path $SuiteRoot "VERSION"
    if (Test-Path $versionFile) {
        $Version = (Get-Content $versionFile -Raw).Trim()
    }
}
if ([string]::IsNullOrWhiteSpace($Version)) {
    $Version = "v1.0.0"
}

$hcRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$targetDir = Join-Path $hcRoot "pmforge_dashboard"
$targetIndex = Join-Path $targetDir "index.html"

New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
Copy-Item $sourceIndex $targetIndex -Force

$versionMeta = @{
    suiteVersion = $Version
    importedAtUtc = (Get-Date).ToUniversalTime().ToString("o")
    source = $SuiteRoot
} | ConvertTo-Json

Set-Content -Path (Join-Path $targetDir "version.json") -Value $versionMeta -Encoding UTF8

if ($shouldUpdateLegacyDashboard) {
    $legacyTarget = Join-Path $hcRoot "Dashboard\index.html"
    if (Test-Path $legacyTarget) {
        Copy-Item $sourceIndex $legacyTarget -Force
    }
}

Write-Host "Imported PM Forge Suite $Version into $targetDir"
if ($shouldUpdateLegacyDashboard) {
    Write-Host "Updated legacy dashboard path: Dashboard/index.html"
}
