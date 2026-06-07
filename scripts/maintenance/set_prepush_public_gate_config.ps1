param(
    [string]$BaseUrl = "https://9dkkj5n2rc.execute-api.us-east-2.amazonaws.com",
    [string]$PublicSiteUrl = "https://www.hclombardo.com",
    [switch]$Clear
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "../..")
Set-Location $repoRoot

if ($Clear) {
    git config --local --unset hcl.prepush.baseUrl 2>$null
    git config --local --unset hcl.prepush.publicSiteUrl 2>$null
    Write-Host "PASS: Cleared repo-local pre-push public gate config." -ForegroundColor Green
    exit 0
}

git config --local hcl.prepush.baseUrl "$BaseUrl"
git config --local hcl.prepush.publicSiteUrl "$PublicSiteUrl"

$effectiveBase = git config --local --get hcl.prepush.baseUrl
$effectiveSite = git config --local --get hcl.prepush.publicSiteUrl

Write-Host "PASS: Repo-local pre-push public gate config saved." -ForegroundColor Green
Write-Host "  hcl.prepush.baseUrl      = $effectiveBase"
Write-Host "  hcl.prepush.publicSiteUrl= $effectiveSite"
Write-Host "Note: Env vars HCL_PREPUSH_BASE_URL and HCL_PREPUSH_PUBLIC_SITE_URL still override these values if set." -ForegroundColor Yellow
