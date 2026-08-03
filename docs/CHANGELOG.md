# Changelog

## Unreleased

- Added repository-level project memory, documentation sync, UML, Git hooks, GitHub templates, and validation scripts.
- Replaced the root README with a clean documentation entrypoint.
- Updated `.gitignore` and `.env.example` for safer portable setup.
- Validated docs, Django system check, and 17 Django tests.

## Historical Summary

- Built Django production MIS for product groups, lines, products, raw materials, waste, shifts, operators, and production reports.
- Added role model: Admin, Registrar, Viewer.
- Added management dashboard, KPI cards, charts, PDF exports, and Excel exports.
- Added daily, comparison, executive, operations, planning, and sales reports.
- Added one-report-per-date-line-shift constraint.
- Added cascade UI by product group.
- Removed material/production/waste balance checks because silo inventory can carry across days.
- Added operator-to-product-group relationship.
- Added edit and delete for production reports.
- Fixed Linux PDF font fallback for production server.
- Added top-of-dashboard seven-day daily production matrix by product group.
- Deployed production to Linux VPS with nginx, gunicorn, HTTPS, firewall, fail2ban, and unattended upgrades.
