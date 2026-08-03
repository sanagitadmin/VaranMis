# Decision Log

## 2026-08-03 - Git As Central Project Memory

Decision: Use repository documentation, UML, hooks, scripts, and handoff files as the portable memory for Codex and human maintainers.

Reason: The project must be transferable across PCs and continue from Git state alone.

## 2026-08-03 - Hard Delete Currently Allowed

Decision: Implement production report delete with confirmation page and POST.

Reason: User requested edit/delete for registered reports. Soft delete was not explicitly requested.

Follow-up: Confirm whether audit trail or soft delete is required.

## 2026-08-01 - Remove Weight Balance Validation

Decision: Do not enforce material/production/waste balance.

Reason: Silo and line inventory can carry material between periods.

## 2026-08-01 - Operators Belong To Product Group

Decision: Operators are connected to product groups and cascaded in the report form.

Reason: User requested operator linkage consistent with product, line, raw material, and waste grouping.

## 2026-08-01 - VPS Deployment Instead Of Shared Hosting

Decision: Deploy to Linux VPS with nginx and gunicorn.

Reason: Shared host Python app setup failed because Apache Passenger was required but unavailable.

## 2026-07/08 - Server-Rendered Django

Decision: Use Django templates instead of a SPA.

Reason: Faster internal MIS delivery, simple deployment, native Django auth and admin.

