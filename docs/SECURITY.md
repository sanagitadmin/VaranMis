# Security

## Authentication

The application uses Django authentication.

## Authorization

Application roles are Django groups:

- `Admin`
- `Registrar`
- `Viewer`

Superusers are treated as Admin in `production/permissions.py`.

## Permissions

- View: Admin, Registrar, Viewer, superuser
- Register/edit/delete reports: Admin, Registrar, superuser
- Admin/settings: Admin, superuser
- Django admin access also requires `is_staff`.

## Production Hardening Already Applied

Based on the deployment conversation:

- nginx reverse proxy
- HTTPS for `varanstat.sanacloud.ir`
- Let's Encrypt certificate renewal
- HSTS and security headers
- secure cookies enabled for HTTPS
- UFW firewall with SSH, HTTP, HTTPS
- fail2ban for SSH
- unattended security upgrades
- rate limiting on nginx

## Secret Policy

Never commit:

- passwords
- API keys
- access tokens
- refresh tokens
- private keys
- production connection strings
- cookies or session values
- GitHub tokens

Use:

- `.env.example`
- GitHub Actions secrets
- server-side environment files

## Known Security Concern

A production VPS root password was shared in conversation. The value is not stored in this repository. Rotate it and prefer SSH keys with password login disabled.

