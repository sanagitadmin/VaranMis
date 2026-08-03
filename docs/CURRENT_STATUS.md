# Current Status

Updated: 2026-08-03

## Repository

- Git branch: `master`
- Remote: `origin` -> `https://github.com/sanagitadmin/VaranMis.git`
- Latest observed commits: `4224a5c`, `2da7809`, `6ecbb9e`, `24558fd`
- Commit/push for this documentation work: not authorized yet

## Application

- Django app is functional locally and on production VPS.
- Production URL: `https://varanstat.sanacloud.ir/`
- Core CRUD for production reports exists.
- PDF and Excel exports are working after Linux font fallback fix.
- Dashboard includes 7-day production-by-product-group table.

## Tests

- `scripts/validate-docs.ps1`: passed on 2026-08-03.
- `.venv\Scripts\python.exe manage.py check`: passed on 2026-08-03.
- `.venv\Scripts\python.exe manage.py test`: passed on 2026-08-03, 17 tests OK.

## Known Operational Notes

- Production database is not tracked.
- Local `db.sqlite3`, `.venv`, `.vs`, `tmp`, and `.env` are ignored.
- A real VPS password was shared in chat and should be rotated. Its value is not documented here.
- Repository memory docs, UML sources, sync scripts, Git hooks, and GitHub
  templates now exist. Commit/push is still pending user review.
