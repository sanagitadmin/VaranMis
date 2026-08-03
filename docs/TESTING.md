# Testing

## Default Commands

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
```

## Current Test Coverage

The Django test suite covers:

- report creation
- report update
- report delete
- role restrictions
- duplicate report prevention
- group cascade validation
- quantity validation
- PDF and Excel response loading
- dashboard 7-day product-group table
- viewer access restrictions

## Latest Known Result

At the time this memory system was created, the suite had 17 tests passing after the report edit/delete work.

## Documentation Validation

Use:

```powershell
scripts\validate-docs.ps1
```

or:

```bash
scripts/validate-docs.sh
```

