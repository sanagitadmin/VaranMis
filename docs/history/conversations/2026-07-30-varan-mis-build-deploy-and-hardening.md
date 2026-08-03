# 2026-07-30 - Varan MIS Build, Deploy, and Hardening

## Session Summary

The user requested a production statistics system for PET, flake, hotwash, and
granule lines. The implementation evolved into a Django MIS with product groups,
cascaded master data, daily production reports, dashboards, role access,
management reports, PDF/Excel exports, and VPS deployment.

## Requests

- Model product groups, production lines, products, raw materials, waste types,
  operators, shifts, crew count, total production, useful production, and waste.
- Link product, line, raw material, waste type, and operator to product group.
- Use cascaded UI controls so selections match the selected product group.
- Keep material and waste panels to one initial row and let users add rows.
- Remove material-balance validation because silo inventory can carry material.
- Allow production 1500 with material consumption 1000.
- Keep useful production less than or equal to total production.
- Make reports and dashboard exportable as PDF and Excel.
- Add role access: Admin, Registrar, Viewer.
- Prevent duplicate daily report for the same date, line, and shift.
- Deploy to a Linux VPS and configure HTTPS for `varanstat.sanacloud.ir`.

## Decisions

- Use Django server-rendered templates with SQLite for the current deployment.
- Use database-driven master data only; no production master data hardcoded in
  forms or templates.
- Treat superusers as Admin for authorization.
- Use product group as the central cascade boundary.
- Keep PDF rendering on the server using ReportLab with Linux-safe font fallback.

## Changes

- Added and updated models in `production/models.py`.
- Added cascaded forms and formsets in `production/forms.py`.
- Added dashboard/report views and exports in `production/views.py`.
- Added analytics helpers in `production/analytics.py` and
  `production/management_reports.py`.
- Added role helpers in `production/permissions.py`.
- Added tests in `production/tests.py`.
- Deployed app behind Nginx/systemd with HTTPS.

## Results

- Local tests passed after report edit/delete and dashboard changes.
- Production smoke checks showed the live site was reachable.
- PDF 500 errors were fixed.

## Unresolved Notes

- Production backup and restore process needs a documented and tested routine.
- Sample-data and role setup commands include starter credentials and should be
  handled carefully in production.
