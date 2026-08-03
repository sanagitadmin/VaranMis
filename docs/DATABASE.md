# Database

## Engine

The application uses SQLite by default:

- Development: `BASE_DIR / db.sqlite3`
- Production: configured by `DJANGO_DB_PATH`

## Domain Tables

- `ProductGroup`
- `Product`
- `ProductionLine`
- `Shift`
- `Operator`
- `RawMaterial`
- `WasteType`
- `ProductionReport`
- `MaterialConsumption`
- `WasteEntry`

## Important Constraints

- Unique product per `(group, name)`
- Unique raw material per `(group, name)`
- Unique waste type per `(group, name)`
- Unique production report per `(report_date, line, shift)`
- Unique material per report
- Unique waste type per report

## Migration History

- `0001_initial`: initial production domain
- `0002`: group relationships and related options
- `0003`: quantity precision and related changes
- `0004`: unique report per date, line, shift
- `0005`: operator options and group relationship
- `0006`: operator group form requirement while database field remains nullable for existing rows

## Production Data Caution

Production data lives outside Git. Never commit `db.sqlite3` or production database files.

