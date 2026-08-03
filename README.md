# Varan MIS

Varan MIS is a Persian production management and reporting system for PET,
flake, hotwash, and granule production lines.

The current implementation is a Django application with server-rendered pages,
SQLite storage, role-based access, KPI dashboards, daily and comparison reports,
and PDF/Excel exports.

## Start Here

- [Project memory and handoff rules](AGENTS.md)
- [Documentation index](docs/README.md)
- [Current status](docs/CURRENT_STATUS.md)
- [Handoff for the next agent](docs/HANDOFF.md)
- [Requirements](docs/REQUIREMENTS.md)
- [Business rules](docs/BUSINESS_RULES.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Database](docs/DATABASE.md)
- [Security](docs/SECURITY.md)
- [Setup](docs/SETUP.md)
- [Deployment](docs/DEPLOYMENT.md)
- [Backlog](docs/BACKLOG.md)
- [UML diagrams](docs/uml/README.md)

## Local Run

```bat
setup.bat
start.bat
```

After startup:

- App: http://127.0.0.1:8000
- Admin: http://127.0.0.1:8000/admin/

## Manual Commands

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py runserver
```

## Configuration

Copy `.env.example` to `.env` and set real local or production values. Never
commit real passwords, API keys, access tokens, cookies, private keys, or
production connection strings.

## Repository Memory

This repository is intended to be the transferable source of truth for project
state. A new Codex run should read `AGENTS.md` and the key files under `docs/`
before making changes.
