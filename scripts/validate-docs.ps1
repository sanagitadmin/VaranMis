param(
    [switch]$Strict
)

$ErrorActionPreference = "Stop"

function Fail($Message) {
    Write-Error $Message
    exit 1
}

$repo = git rev-parse --show-toplevel 2>$null
if (-not $repo) { Fail "Not inside a Git repository." }
$repo = $repo.Trim()
Set-Location $repo

$requiredDocs = @(
    "AGENTS.md",
    "README.md",
    "docs/README.md",
    "docs/PROJECT_OVERVIEW.md",
    "docs/REQUIREMENTS.md",
    "docs/BUSINESS_RULES.md",
    "docs/ARCHITECTURE.md",
    "docs/DATABASE.md",
    "docs/API.md",
    "docs/SECURITY.md",
    "docs/SETUP.md",
    "docs/DEPLOYMENT.md",
    "docs/TESTING.md",
    "docs/GIT_WORKFLOW.md",
    "docs/CHANGELOG.md",
    "docs/CURRENT_STATUS.md",
    "docs/ROADMAP.md",
    "docs/BACKLOG.md",
    "docs/KNOWN_ISSUES.md",
    "docs/DECISION_LOG.md",
    "docs/WORK_HISTORY.md",
    "docs/CONVERSATION_MEMORY.md",
    "docs/HANDOFF.md",
    "docs/GLOSSARY.md",
    "docs/history/INDEX.md",
    "docs/uml/README.md"
)

$requiredUml = @(
    "docs/uml/SYSTEM_CONTEXT.puml",
    "docs/uml/CONTAINER_DIAGRAM.puml",
    "docs/uml/COMPONENT_DIAGRAM.puml",
    "docs/uml/DEPLOYMENT_DIAGRAM.puml",
    "docs/uml/DOMAIN_MODEL.puml",
    "docs/uml/DATABASE_ERD.puml",
    "docs/uml/USE_CASES.puml",
    "docs/uml/MAIN_SEQUENCES.puml",
    "docs/uml/STATE_MACHINES.puml",
    "docs/uml/ACTIVITY_FLOWS.puml",
    "docs/uml/AUTHENTICATION_AUTHORIZATION.puml"
)

foreach ($file in $requiredDocs + $requiredUml) {
    if (-not (Test-Path $file)) { Fail "Missing required documentation file: $file" }
}

foreach ($file in $requiredUml) {
    $text = Get-Content $file -Raw
    if ($text -notmatch "@startuml") { Fail "PlantUML file misses @startuml: $file" }
    if ($text -notmatch "@enduml") { Fail "PlantUML file misses @enduml: $file" }
}

$markdownFiles = @()
foreach ($path in git ls-files "*.md") {
    if (Test-Path $path) {
        $markdownFiles += Get-Item $path
    }
}
foreach ($path in Get-ChildItem -Path docs -Recurse -File -Include *.md -ErrorAction SilentlyContinue) {
    if ($markdownFiles.FullName -notcontains $path.FullName) {
        $markdownFiles += $path
    }
}

foreach ($md in $markdownFiles) {
    $dir = Split-Path $md.FullName -Parent
    $content = Get-Content $md.FullName -Raw
    $matches = [regex]::Matches($content, '\[[^\]]+\]\((?!https?://|mailto:|#)([^)#]+)(?:#[^)]+)?\)')
    foreach ($match in $matches) {
        $target = $match.Groups[1].Value.Trim()
        if ($target.StartsWith("<") -and $target.EndsWith(">")) {
            $target = $target.Substring(1, $target.Length - 2)
        }
        if ($target -match "^[A-Za-z]:") { continue }
        $candidate = Join-Path $dir $target
        if (-not (Test-Path $candidate)) {
            Fail "Broken markdown link in $($md.FullName): $target"
        }
    }
}

$tracked = git ls-files
$secretPattern = "(?i)(password\s*[:=]\s*[^`\s]+|api[_-]?key\s*[:=]\s*[^`\s]+|access[_-]?token\s*[:=]\s*[^`\s]+|private[_-]?key|refresh[_-]?token)"
$allowedSecretDocs = @(
    ".env.example",
    "README.md",
    "docs/SECURITY.md",
    "docs/KNOWN_ISSUES.md",
    "docs/BACKLOG.md",
    "production/tests.py",
    "production/management/commands/setup_roles.py"
)
foreach ($file in $tracked) {
    if (-not (Test-Path $file)) { continue }
    if ($allowedSecretDocs -contains $file) { continue }
    $text = Get-Content $file -Raw -ErrorAction SilentlyContinue
    if ($text -match $secretPattern) {
        if ($Strict) { Fail "Potential secret-like text found in tracked file: $file" }
        Write-Warning "Potential secret-like text found in tracked file: $file"
    }
}

Write-Host "Documentation validation passed."
