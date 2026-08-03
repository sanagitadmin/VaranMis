# Business Rules

## Master Data Rules

- Product group is the root classification for production-related master data.
- Product, production line, raw material, waste type, and operator must be connected to a product group.
- Cascade UI must hide or disable options outside the selected product group.

## Report Entry Rules

- `report_date` cannot be in the future.
- `crew_count` must be greater than zero.
- `useful_production` cannot be greater than `total_production`.
- Material quantity must be greater than zero.
- Waste quantity must be greater than zero.
- Product, line, operator, raw materials, and waste types must match the selected product group.
- One report per `(report_date, line, shift)`.

## Weight Balance Rules

The following checks are intentionally not enforced:

- material consumption greater than total production
- total production greater than material consumption
- useful production plus waste greater than total production

Reason: materials may remain in silos, buffers, or line inventory from previous periods, and material consumption can be recorded with operational timing differences.

## Reporting Rules

- Yield percent = useful production / total production.
- Waste percent = total waste / total production.
- Useful per person = useful production / crew count.
- Dashboard daily group matrix covers the last seven calendar days ending today.

