# Requirements

## Confirmed Functional Requirements

1. Product groups are master data.
2. Production lines belong to a product group.
3. Products belong to a product group.
4. Raw materials belong to a product group.
5. Waste types belong to a product group and have category:
   - reusable
   - saleable
   - disposal
6. Operators belong to a product group.
7. Production reports capture:
   - report date
   - shift
   - operator
   - crew count
   - line
   - product
   - total production
   - useful production
   - material consumption rows
   - waste rows
   - notes
8. A line can have only one report for the same date and shift.
9. Reports can be created, edited, viewed, exported, and deleted.
10. Delete requires a confirmation page and POST.
11. UI cascade must respect selected product group for line, product, operator, raw material, and waste type.
12. Material and waste panels start with one row; users add rows manually.
13. Daily reports and management reports must export to PDF and Excel.
14. Dashboard and reports must support product group, line, and date filtering where applicable.
15. Dashboard must show a 7-day daily matrix of total production by product group.
16. Reports should be management-oriented and visually polished.

## Confirmed Access Requirements

- Admin: manage system and can register/edit/delete reports.
- Registrar: can register/edit/delete production reports.
- Viewer: can view dashboards and reports only.
- Django superuser is treated as Admin.

## Confirmed Non-Functional Requirements

- No hardcoded production data.
- Real secrets must not be committed.
- Git repository is the central portable project memory.
- Documentation and UML must stay in sync with code changes.

## Explicitly Rejected Or Removed Requirements

- Weight balance checks between material input, total production, useful production, and waste were removed because silo inventory can carry materials across days.
- Report count KPI was removed because it was not meaningful for management reporting.

## Unclear Or Needs Confirmation

- Whether delete should be soft delete/audit logged instead of hard delete.
- Whether SQLite remains acceptable long-term for production load.
- Whether production should be migrated to PostgreSQL.

