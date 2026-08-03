param(
    [switch]$RunTests
)

$ErrorActionPreference = "Stop"

function Stop-Sync($Message) {
    Write-Error $Message
    exit 1
}

$repo = git rev-parse --show-toplevel 2>$null
if (-not $repo) { Stop-Sync "Not inside a Git repository." }
$repo = $repo.Trim()
Set-Location $repo

$branch = git branch --show-current
$remote = git remote -v
Write-Host "Repository: $repo"
Write-Host "Branch: $branch"
Write-Host "Remotes:"
$remote | ForEach-Object { Write-Host "  $_" }

git fetch --prune

$status = git status --porcelain
if ($status) {
    git status --short --branch
    Stop-Sync "Working tree has local changes. Nothing was pulled."
}

$upstream = git rev-parse --abbrev-ref --symbolic-full-name "@{u}" 2>$null
if (-not $upstream) {
    Stop-Sync "Current branch has no upstream. Configure upstream before syncing."
}
$upstream = $upstream.Trim()

$counts = (git rev-list --left-right --count "HEAD...$upstream").Trim().Split()
$ahead = [int]$counts[0]
$behind = [int]$counts[1]

if ($ahead -gt 0 -and $behind -gt 0) {
    Stop-Sync "Branch diverged from $upstream. Resolve manually."
}
if ($ahead -gt 0) {
    Stop-Sync "Branch has $ahead unpushed commit(s). Push or inspect before pulling."
}
if ($behind -gt 0) {
    git pull --ff-only
} else {
    Write-Host "Already up to date."
}

& "$PSScriptRoot\validate-docs.ps1"

if ($RunTests) {
    $python = ".\.venv\Scripts\python.exe"
    if (-not (Test-Path $python)) { $python = "python" }
    & $python manage.py check
    & $python manage.py test
}

Write-Host "`n--- docs/CURRENT_STATUS.md ---"
Get-Content docs/CURRENT_STATUS.md | Select-Object -First 80
Write-Host "`n--- docs/HANDOFF.md ---"
Get-Content docs/HANDOFF.md | Select-Object -First 120
Write-Host "`nSync completed safely."
