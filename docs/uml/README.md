# UML Diagrams

These PlantUML files describe the current repository state. They are source
files, not rendered images.

## Files

- `SYSTEM_CONTEXT.puml`: users, browser, Django app, SQLite database, and VPS.
- `CONTAINER_DIAGRAM.puml`: runtime containers and deployment boundaries.
- `COMPONENT_DIAGRAM.puml`: Django modules inside the application.
- `DEPLOYMENT_DIAGRAM.puml`: local and production deployment shape.
- `DOMAIN_MODEL.puml`: Django domain classes from `production/models.py`.
- `DATABASE_ERD.puml`: database tables and key relationships.
- `USE_CASES.puml`: Admin, Registrar, and Viewer use cases.
- `MAIN_SEQUENCES.puml`: main create report and export flows.
- `STATE_MACHINES.puml`: report lifecycle and role access states.
- `ACTIVITY_FLOWS.puml`: daily report creation workflow.
- `AUTHENTICATION_AUTHORIZATION.puml`: login and role checks.

## Sources

- Domain and ERD: `production/models.py`, `production/migrations/`.
- Use cases and authorization: `production/permissions.py`, `production/urls.py`,
  `production/views.py`, `varanmis/urls.py`.
- Components and sequences: `production/forms.py`, `production/analytics.py`,
  `production/management_reports.py`, `production/pdf_reports.py`,
  `production/excel_reports.py`, templates under `templates/`.
- Deployment: `docs/DEPLOYMENT.md`, `passenger_wsgi.py`, `requirements.txt`.

## Validation

Run:

```powershell
.\scripts\validate-docs.ps1
```

or:

```bash
./scripts/validate-docs.sh
```

The repository validator checks that every `.puml` file contains `@startuml`
and `@enduml`. Full rendering requires PlantUML, for example:

```bash
plantuml docs/uml/*.puml
```

## Update Policy

Update these diagrams whenever models, routes, permissions, reports, deployment
shape, or external integrations change.
