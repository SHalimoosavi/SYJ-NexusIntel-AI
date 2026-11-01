# Database Least Privilege, TLS, Backup and Restore

## Hosted database requirements

- Use PostgreSQL for hosted deployments. Application startup rejects SQLite outside development/local/desktop/test.
- The connection defaults to PostgreSQL `sslmode=require`; set `sslmode=verify-full` with a trusted CA certificate where supported. Do not downgrade to `disable` or `allow`.
- Use a dedicated application login role. It must not be a database owner, superuser, role administrator or schema owner.
- Use a separate migration/DBA identity for DDL and schema migrations. Never give the application role CREATE/ALTER/DROP privileges.
- Grant only required DML privileges to application tables and sequences. The app should not own `audit_logs`.
- Rotate database credentials through the secret manager; do not place passwords in repository files, CI output or shell history.

## Suggested role split (DBA-run)

Create a dedicated login role through the database provider's secret-management interface, not by committing a password in SQL. A DBA/migration identity should own schemas and tables. Grant the application role only CONNECT, schema USAGE, required operational-table DML and sequence USAGE/SELECT. For `audit_logs`, grant SELECT/INSERT only.

Do not grant UPDATE, DELETE, TRUNCATE, ALTER, DROP, CREATE or ownership on `audit_logs`. SQLAlchemy `before_update`/`before_delete` hooks are a second line of defense only; DB privileges are the authoritative boundary.

The `backend/sql/audit_log_hardening.sql` script adds a PostgreSQL trigger that rejects row UPDATE/DELETE. Apply it using a migration/DBA role after confirming the table and application role name.

## Backup

Example for a managed PostgreSQL database with credentials injected by the operator's secret manager:

```bash
umask 077
pg_dump --format=custom --no-owner --no-privileges \
  --file="nexusintel-$(date -u +%Y%m%dT%H%M%SZ).dump" \
  "$DATABASE_URL"
```

- Encrypt backups at rest using provider-managed encryption or an approved KMS.
- Store backups outside the application database account and restrict read access to designated operators.
- Define retention and recovery-point objectives before production launch.
- Back up encryption keys and recovery metadata separately; a backup without required keys is not a recovery plan.
- Monitor backup completion and alert on failures. Never upload production dumps to GitHub or a public issue.

## Restore drill

Restore into a new isolated recovery database, not over the live database:

```bash
createdb nexusintel_restore_drill
pg_restore --clean --if-exists --no-owner \
  --dbname="postgresql://RESTORE_OPERATOR@DB_HOST:5432/nexusintel_restore_drill?sslmode=verify-full" \
  nexusintel-backup.dump
```

Then verify table counts, schema version, foreign-key consistency and application read/write smoke tests using synthetic test accounts. Record restore duration and recovered backup timestamp. Destroy the isolated drill database after evidence is retained.

## Operational caveats

- The repository does not currently include a formal migration framework or automated backup scheduler. The commands above are operator guidance, not evidence that backups are configured or restore-tested.
- Use a separate migration identity; do not run production migrations as the application login.
- A PostgreSQL trigger cannot prevent a superuser/DBA from disabling it. Export high-value audit events to a separately administered append-only log/SIEM for stronger tamper evidence.
