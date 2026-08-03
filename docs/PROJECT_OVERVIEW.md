# Project Overview

Varan MIS is a Django-based internal production management system for recording and analyzing production reports for PET, flake, hotwash, granule, and similar product groups.

## Current Repository Facts

- Framework: Django 5.x
- App module: `production`
- Project module: `varanmis`
- Database: SQLite by default, configured through `DJANGO_DB_PATH`
- Frontend: Django templates, static CSS and JavaScript
- Exports: PDF through ReportLab, Excel through XlsxWriter
- Auth: Django auth plus role groups `Admin`, `Registrar`, `Viewer`
- Production deployment: Linux VPS with nginx, gunicorn, systemd, HTTPS

## Primary Users

- CEO / senior management: KPI dashboard, trend and comparison reports
- Factory manager: line, shift, operator and waste performance
- Production manager: daily production, useful output, waste and manpower productivity
- Production planning: daily and monthly rhythm, product mix, projected supply
- Sales manager: useful production available for sale and saleable waste
- Registrar: enters and corrects production statistics
- Viewer: reads dashboards and reports only

## Main Capabilities

- Master data management for product groups, products, production lines, raw materials, waste types, shifts, and operators
- Production report creation, editing, detail view, PDF/Excel export, and deletion with confirmation
- Cascade UI by product group
- Daily, comparison, executive, operations, planning, and sales reports
- KPI dashboard with charts and tables
- Daily 7-day production matrix by product group at top of dashboard

## Not A Public Marketing Site

This is an operational MIS application. UI decisions should favor fast scanning, low click count, accurate data entry, and management-grade reporting.

