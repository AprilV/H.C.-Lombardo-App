param(
    [string]$OutputZip,
    [switch]$SkipBuild
)

$ErrorActionPreference = 'Stop'

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$frontendDir = Join-Path $repoRoot "frontend"
$buildDir = Join-Path $frontendDir "build"

if (-not $OutputZip) {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $OutputZip = Join-Path $repoRoot "frontend_build_upload_posix_live_$timestamp.zip"
}

if (-not $SkipBuild) {
    Write-Host "[1/3] Building frontend production bundle..."
    Push-Location $frontendDir
    try {
        npm run build
        if ($LASTEXITCODE -ne 0) {
            throw "Frontend build failed with exit code $LASTEXITCODE"
        }
    }
    finally {
        Pop-Location
    }
}

if (-not (Test-Path $buildDir)) {
    throw "Build directory not found: $buildDir"
}

$outputDir = Split-Path -Parent $OutputZip
if ($outputDir -and -not (Test-Path $outputDir)) {
    New-Item -Path $outputDir -ItemType Directory -Force | Out-Null
}

if (Test-Path $OutputZip) {
    Remove-Item $OutputZip -Force
}

Write-Host "[2/3] Creating Amplify upload zip with POSIX paths..."
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$zip = [System.IO.Compression.ZipFile]::Open($OutputZip, [System.IO.Compression.ZipArchiveMode]::Create)
try {
    $buildRoot = (Resolve-Path $buildDir).Path
    Get-ChildItem -Path $buildDir -Recurse -File | ForEach-Object {
        $fullPath = $_.FullName
        $relativePath = $fullPath.Substring($buildRoot.Length).TrimStart([char[]](92, 47))
        $relativePath = ($relativePath -replace '\\', '/')
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
            $zip,
            $_.FullName,
            $relativePath,
            [System.IO.Compression.CompressionLevel]::Optimal
        ) | Out-Null
    }
}
finally {
    $zip.Dispose()
}

Write-Host "[3/3] Validating zip entry paths..."
$zipRead = [System.IO.Compression.ZipFile]::OpenRead($OutputZip)
$entries = $zipRead.Entries
try {
    $hasBackslash = $entries | Where-Object { $_.FullName -match '\\' } | Select-Object -First 1
    if ($hasBackslash) {
        throw "Zip validation failed: found Windows-style path separator in entry $($hasBackslash.FullName)"
    }
}
finally {
    $zipRead.Dispose()
}

$zipHash = Get-FileHash -Path $OutputZip -Algorithm SHA256

Write-Host "Bundle ready: $OutputZip"
Write-Host "SHA256: $($zipHash.Hash)"