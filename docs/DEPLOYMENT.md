# Deployment

## Current Production

- Public URL: `https://varanstat.sanacloud.ir/`
- Host type: Linux VPS
- Stack: nginx -> gunicorn -> Django
- App path on VPS: `/opt/varanmis/app`
- Data path on VPS: `/opt/varanmis/data/db.sqlite3`
- Systemd service: `varanmis`
- HTTPS: Let's Encrypt certificate for `varanstat.sanacloud.ir`

## Production Environment Variables

Expected variables:

- `DJANGO_DEBUG=0`
- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `DJANGO_DB_PATH`
- `DJANGO_SECURE_COOKIES=1`

Do not store real production values in tracked files.

## Deployment Checklist

1. Run tests locally.
2. Build a clean zip excluding `.venv`, `.git`, `.vs`, `tmp`, `db.sqlite3`, `staticfiles`, and secrets.
3. Upload to the VPS.
4. Extract to `/opt/varanmis/app`.
5. Run migrations.
6. Run `collectstatic`.
7. Restart `varanmis`.
8. Check nginx.
9. Smoke test dashboard, report entry, PDF, and Excel.

## Earlier Hosting Attempt

A shared hosting attempt failed because the host's Python selector required Apache Passenger, which was not enabled. The project was then moved to VPS deployment.

