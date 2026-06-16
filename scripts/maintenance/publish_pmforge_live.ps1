param(
    [string]$CommitMessage = "Deploy PM Forge dashboard",
    [switch]$SkipEmptyCommit
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$worktreePath = Join-Path $repoRoot ".gh-pages-deploy-tmp"
$sourceFile = Join-Path $repoRoot "pmforge_dashboard\index.html"
$destFile = Join-Path $worktreePath "index.html"
$createdWorktree = $false

if (-not (Test-Path $sourceFile)) {
    throw "Source file not found: $sourceFile"
}

try {
    Set-Location $repoRoot
    git fetch origin gh-pages

    if (Test-Path $worktreePath) {
        git worktree remove "$worktreePath" --force
    }

    git worktree add "$worktreePath" gh-pages
    $createdWorktree = $true

    Copy-Item $sourceFile $destFile -Force

    Push-Location $worktreePath
    git add index.html

    $changes = git status --porcelain
    if ($changes) {
        git commit -m $CommitMessage
    }
    elseif (-not $SkipEmptyCommit) {
        git commit --allow-empty -m "$CommitMessage (rebuild trigger)"
    }
    else {
        Write-Output "NO_CHANGES_TO_DEPLOY"
        return
    }

    git push origin gh-pages
    $hash = (git rev-parse --short HEAD).Trim()

    Write-Output "PUSHED_COMMIT=$hash"
    Write-Output "LIVE_URL=https://aprilv.github.io/H.C.-Lombardo-App/"
}
finally {
    if ($PWD.Path -eq $worktreePath) {
        Pop-Location
    }

    if ($createdWorktree -and (Test-Path $worktreePath)) {
        git worktree remove "$worktreePath" --force
    }
}
