$ErrorActionPreference = "Stop"

$repo = git rev-parse --show-toplevel 2>$null
if (-not $repo) {
    Write-Error "Not inside a Git repository."
    exit 1
}
Set-Location $repo.Trim()
git config core.hooksPath .githooks
Write-Host "Git hooks installed: core.hooksPath=.githooks"
