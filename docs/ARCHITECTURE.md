# Architecture

## Style

Varan MIS is a server-rendered Django monolith.

## Runtime Components

- Browser: user-facing UI rendered by Django templates.
- Django project: `varanmis`
- Django app: `production`
- Database: SQLite file configured by `DJANGO_DB_PATH`
- Static assets: served locally in development and by WhiteNoise/nginx in production
- PDF export: ReportLab with Persian text reshaping
- Excel export: XlsxWriter
- Production web stack: nginx reverse proxy -> gunicorn -> Django

## Code Modules

- `production/models.py`: domain and database models
- `production/forms.py`: report entry and validation forms
- `production/views.py`: page, report, export, create/edit/delete views
- `production/analytics.py`: aggregation helpers
- `production/management_reports.py`: management report contexts and sections
- `production/pdf_reports.py`: PDF rendering
- `production/excel_reports.py`: Excel rendering
- `production/permissions.py`: role checks
- `production/context_processors.py`: template role flags
- `templates/`: server-rendered HTML
- `static/production/`: CSS and browser JavaScript

## External Services

- GitHub remote repository: `https://github.com/sanagitadmin/VaranMis.git`
- Production domain: `varanstat.sanacloud.ir`
- HTTPS certificate: Let's Encrypt via certbot on VPS

## Architectural Decisions

- Server-rendered UI was used instead of SPA to keep deployment and maintenance simple.
- Reports are exported on demand rather than pre-generated.
- SQLite is currently used for simple deployment; this is a known scaling consideration.

