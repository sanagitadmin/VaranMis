# Handoff

Updated: 2026-08-03

## What Was Done Most Recently

- Created the permanent repository memory and Git handoff system.
- Added `AGENTS.md` with mandatory start/change/finish instructions for future
  Codex runs.
- Added the `docs/` documentation set, structured conversation history, and
  PlantUML source diagrams.
- Added safe sync, validation, and Git hook installation scripts.
- Added versioned Git hooks, GitHub Actions, Dependabot, PR template, and issue
  templates.
- Replaced root `README.md` with a clean documentation entrypoint.
- Expanded `.gitignore` for local/generated/secret-like files and refreshed
  `.env.example` for the active domain.

## Decisions Made

- Documentation is mostly ASCII/English for reliable cross-platform tooling.
- CODEOWNERS was not added because the exact GitHub reviewer handle is not
  confirmed.
- Git hooks detect missing documentation updates but do not generate fake docs.
- Sync scripts never use reset, force push, or destructive cleanup.

## Validation Run

- `scripts/validate-docs.ps1`: passed.
- `.venv\Scripts\python.exe manage.py check`: passed.
- `.venv\Scripts\python.exe manage.py test`: passed, 17 tests OK.

## Commit Status

- Commit and push are not authorized yet.
- Working tree contains documentation/memory-system changes plus `.env.example`,
  `.gitignore`, and `README.md` updates.

## Known Remaining Issues

- VPS root password must be rotated.
- Delete is hard delete; confirm audit/soft-delete requirement.
- SQLite production backup process must be documented and automated.
- Sample setup commands contain starter users/passwords for local bootstrapping;
  do not run them blindly in production.

## Next Agent Start

Read `AGENTS.md`, then this file, then `docs/CURRENT_STATUS.md`,
`docs/DECISION_LOG.md`, and `docs/CONVERSATION_MEMORY.md`.

Exact next action: user should review these repository-memory changes. If
approved, run validation again and then commit/push.
