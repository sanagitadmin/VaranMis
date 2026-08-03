# Conversation Memory

This file is structured knowledge extracted from the accessible project conversation. It is not a raw transcript.

## Initial Product Need

- User provided production report PDFs for PET/flake/hotwash lines.
- Goal: create an application to register and analyze production statistics.
- Key entities requested: product groups, production lines, products, raw materials, total production, useful production, waste, shift, operator, date, and crew count.

## Product Group Center

- User confirmed:
  - product belongs to product group
  - line belongs to product group
  - raw material belongs to product group
  - waste belongs to product group
  - operator later also belongs to product group
- Decision: product group is the root for cascade UI and validation.

## Validation Evolution

- Initial request included weight controls:
  - material consumption should not exceed total production
  - useful + waste should not exceed total production
- Later user clarified silo inventory makes direct daily weight balance invalid.
- Decision: remove balance checks.
- Still enforced:
  - positive material/waste quantities
  - useful production <= total production
  - group consistency
  - date not in future
  - unique report per date/line/shift

## Reporting Evolution

- User requested dashboard, daily/monthly comparisons, bar charts with numbers, table comparisons, PDF and Excel exports.
- User rejected report count as not meaningful.
- User requested management-grade reports for CEO, factory manager, production, planning, and sales.
- Implemented executive, operations, planning, sales, daily, comparison reports.
- Dashboard later received a 7-day daily production matrix by product group.

## Roles

- User requested:
  - Admin for program management
  - Viewer for reports
  - Registrar for entering statistics
- Implemented Django groups: Admin, Viewer, Registrar.
- Later superusers were explicitly treated as Admin in permissions.

## Deployment

- User wanted public hosting.
- Shared hosting Python app creation failed because Apache Passenger was required.
- User then provided Linux VPS details.
- Application deployed to VPS with nginx, gunicorn, systemd.
- Domain `varanstat.sanacloud.ir` connected to VPS.
- HTTPS and hardening configured.
- Important: real VPS password was disclosed in chat and must be rotated. Do not store it.

## PDF Issue

- User reported `Server Error (500)` for all PDFs.
- Root cause: Linux server did not have Windows Tahoma fonts.
- Fix: add Linux font fallbacks in PDF generator.

## CRUD Evolution

- User requested editing or deleting registered statistics.
- Implemented edit with same form as create.
- Implemented delete confirmation page and POST-only delete.
- Access limited to Admin/Registrar/superuser.

## Rejected Or Avoided

- Do not store real secrets in Git.
- Do not deploy sample yearly data to production after user requested blank database.
- Do not overwrite/delete shared hosting files after Passenger blocker.

## Next Actions Suggested By Memory

- Review documentation memory system.
- Rotate VPS root password.
- Decide hard delete vs soft delete/audit.
- Add production database backup automation.

## Repository Memory Request

- User requested that Git become the central transferable project memory.
- Decision: add `AGENTS.md`, a full `docs/` memory set, conversation summaries,
  PlantUML sources, safe sync scripts, validation scripts, Git hooks, and GitHub
  collaboration templates.
- Constraint: do not commit or push until user reviews the result.
