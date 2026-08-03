# Varan MIS Agent Operating Manual

This repository is the central, portable project memory for Varan MIS. Every Codex or human maintainer must treat Git plus the files under `docs/` as the source of truth for handoff, decisions, architecture, and current state.

## Start Of Every Task

1. Confirm the current directory is the correct Git repository:
   - `git rev-parse --show-toplevel`
   - Expected project: `VaranMis`
2. Check branch, remote, and working tree:
   - `git status --short --branch`
   - `git remote -v`
   - `git branch --show-current`
3. Inspect recent history:
   - `git log --oneline --decorate -n 12`
4. If there are no local changes, conflicts, unpushed commits, or branch divergence, safely sync the current branch:
   - `git fetch --prune`
   - `git pull --ff-only`
5. Never delete, reset, overwrite, or stash local user changes without explicit user approval.
6. If there is divergence, conflict, uncommitted work, or unpushed local commits, stop and report the exact status before doing work.
7. Before changing code, read these files:
   - `AGENTS.md`
   - `docs/CURRENT_STATUS.md`
   - `docs/HANDOFF.md`
   - `docs/PROJECT_OVERVIEW.md`
   - `docs/ARCHITECTURE.md`
   - `docs/DECISION_LOG.md`
   - `docs/BACKLOG.md`
   - `docs/KNOWN_ISSUES.md`
   - `docs/CONVERSATION_MEMORY.md`
8. Review commits after the latest handoff entry and compare code against documentation.
9. Clearly separate:
   - facts present in code
   - confirmed requirements
   - accepted decisions
   - unimplemented proposals
   - unclear items needing user confirmation
10. Before edits, report a short status summary and implementation plan to the user.

## During Every Change

Update documentation in the same change set as code:

- Requirement change -> `docs/REQUIREMENTS.md`
- Business rule change -> `docs/BUSINESS_RULES.md`
- Architecture change -> `docs/ARCHITECTURE.md` and relevant `docs/uml/*.puml`
- Database change -> `docs/DATABASE.md` and `docs/uml/DATABASE_ERD.puml`
- URL/API/report endpoint change -> `docs/API.md` and sequence diagrams if relevant
- Authentication or authorization change -> `docs/SECURITY.md` and `docs/uml/AUTHENTICATION_AUTHORIZATION.puml`
- Bug fix -> `docs/KNOWN_ISSUES.md` and `docs/CHANGELOG.md`
- Technical decision -> `docs/DECISION_LOG.md`
- Completed work -> `docs/WORK_HISTORY.md`
- Priority change -> `docs/BACKLOG.md` and `docs/ROADMAP.md`
- Final status -> `docs/CURRENT_STATUS.md` and `docs/HANDOFF.md`
- Durable conversation knowledge -> `docs/CONVERSATION_MEMORY.md`

## Before Ending Every Task

1. Review code changes with `git diff`.
2. Run relevant build and tests. Default for this Django project:
   - `.venv\Scripts\python.exe manage.py check`
   - `.venv\Scripts\python.exe manage.py test`
3. Update all affected documentation and UML.
4. Validate documentation:
   - `scripts/validate-docs.ps1` on Windows
   - `scripts/validate-docs.sh` on Linux/macOS
5. Check that PlantUML files contain matching `@startuml` and `@enduml`.
6. Remove or resolve obvious duplicated or contradictory documentation.
7. Update `docs/CURRENT_STATUS.md` with the real state.
8. Update `docs/HANDOFF.md` so the next agent knows:
   - what was done
   - changed files
   - decisions made
   - tests run and results
   - remaining issues
   - exact next action
9. Update `docs/CONVERSATION_MEMORY.md` only with durable and actionable conversation knowledge.
10. Never commit real passwords, API keys, tokens, private keys, cookies, sessions, or production connection strings.
11. Report results to the user.
12. Do not commit or push unless the user explicitly authorizes it for that task and tests pass.

## Git Safety Rules

- Never use `git reset --hard`, force push, or destructive cleanup unless the user explicitly requests it.
- Prefer `git pull --ff-only` for safe updates.
- Do not rewrite Git history to remove secrets without explicit user approval.
- If a real secret appears in chat or local untracked files, document the risk without storing the secret value.

## Deployment Reality

The public production deployment is a Linux VPS currently documented in `docs/DEPLOYMENT.md`. Do not store production credentials in tracked files. Deployment changes must be tested locally first, then deployed deliberately.

