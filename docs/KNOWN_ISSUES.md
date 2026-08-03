# Known Issues

## Open

1. Production VPS root password was shared in chat.
   - Impact: security risk outside repository.
   - Action: rotate password and configure SSH keys.
2. Deletes are hard deletes.
   - Impact: no built-in audit recovery.
   - Action: confirm whether soft delete/audit trail is required.
3. SQLite is used in production.
   - Impact: acceptable for small internal workload, but may not scale.
   - Action: monitor and consider PostgreSQL later.
4. Some Persian source files may display incorrectly in legacy Windows console encodings.
   - Impact: display issue, not necessarily runtime issue.
   - Action: prefer UTF-8 capable editors and terminals.
5. Sample setup commands include starter users/passwords.
   - Impact: convenient locally, risky if run blindly in production.
   - Action: keep documented as sample-only or replace with an interactive
     setup flow.

## Resolved

- Shared hosting deployment blocked by missing Apache Passenger; moved to VPS.
- PDF exports failed with Server Error 500 on Linux because Tahoma fonts were unavailable; Linux font fallback was added.
- Weight balance validations blocked valid silo scenarios; removed.
- Operator combo was empty after product group cascade because operators were not grouped; operator group relation added.
