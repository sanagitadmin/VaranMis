# API And URL Surface

This project currently exposes server-rendered Django views, not a public JSON API.

## Main URLs

- `/` dashboard
- `/dashboard/pdf/`
- `/dashboard/excel/`
- `/reports/`
- `/reports/pdf/`
- `/reports/excel/`
- `/reports/hub/`
- `/reports/new/`
- `/reports/<id>/`
- `/reports/<id>/edit/`
- `/reports/<id>/delete/`
- `/reports/<id>/pdf/`
- `/reports/<id>/excel/`

## Management Reports

Each report has HTML, PDF, and Excel endpoints:

- executive
- operations
- planning
- sales
- daily
- comparison

## Authentication URLs

Django auth URLs are included under `/accounts/`.

## API Policy

If a JSON API is added later, update this file plus:

- `docs/uml/MAIN_SEQUENCES.puml`
- `docs/SECURITY.md`
- tests for access control

