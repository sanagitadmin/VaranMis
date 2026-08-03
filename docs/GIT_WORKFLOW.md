# Git Workflow

## Current State

- Branch: `master`
- Remote: `origin`
- Remote URL: `https://github.com/sanagitadmin/VaranMis.git`

## Branch Strategy

- `master`: stable deployable branch
- feature/fix branches: recommended for larger changes
- direct `master` edits are acceptable only for urgent small fixes with tests

## Commit Convention

Recommended format:

```text
type(scope): short summary
```

Types:

- `feat`
- `fix`
- `docs`
- `test`
- `refactor`
- `chore`
- `deploy`

## Pull Request Requirements

- Explain user-facing change.
- List tests run.
- Update docs and UML where relevant.
- Do not include secrets or local database files.

## Tag And Release Strategy

- `v0.x.y` for internal releases
- Tag only after successful tests and deployment smoke tests.

## Safe Sync

Use `scripts/project-sync.ps1` or `scripts/project-sync.sh`.

## Suggested GitHub Repository Metadata

- Description: `Persian Django MIS for production reporting, KPI dashboards, and PDF/Excel management reports.`
- Topics: `django`, `python`, `manufacturing`, `production-reporting`, `kpi-dashboard`, `persian`, `plantuml`, `sqlite`, `mis`

## CODEOWNERS

No `CODEOWNERS` file is currently added because the exact reviewer GitHub handle
is not confirmed.
