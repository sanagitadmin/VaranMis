# Work History

## Major Completed Work

- Parsed initial production-report needs from user-supplied PDFs and conversation context.
- Designed product group-centered domain model.
- Implemented Django app with master data and production reports.
- Added role-based access control.
- Added validation for date, positive quantities, group consistency, useful <= total, and unique daily line/shift report.
- Removed material balance validations after silo inventory requirement.
- Added management dashboards and reports.
- Added PDF and Excel exports.
- Added production deployment to VPS and HTTPS hardening.
- Fixed Linux PDF font issue.
- Added operator product-group relation.
- Added report edit and delete.
- Added 7-day product group production table at top of dashboard.
- Added repository memory and handoff system.

## 2026-08-03 - Repository Memory System Details

- Analyzed repository structure, Git branch/remote/history, code modules, tests,
  and accessible conversation context.
- Created `AGENTS.md`, project docs, conversation history, and UML source files.
- Added sync/validation scripts, Git hooks, GitHub workflow, PR template, issue
  templates, and Dependabot config.
- Validation passed:
  - `scripts/validate-docs.ps1`
  - `.venv\Scripts\python.exe manage.py check`
  - `.venv\Scripts\python.exe manage.py test` with 17 tests OK
- Commit/push was not performed because the user requested review first.

## Deployment History Summary

- Shared hosting attempted through DirectAdmin-like panel.
- Python selector reported Apache Passenger requirement.
- User provided Linux VPS.
- Application deployed to VPS at `varanstat.sanacloud.ir`.
- HTTPS, firewall, fail2ban, and unattended upgrades configured.
