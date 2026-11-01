# Database Least Privilege, Audit Integrity and Recovery

## Runtime and migration identities

Use two PostgreSQL identities:
- **Migration owner:** used only by the controlled schema migration pipeline. Owns tables, indexes, triggers and functions. Credentials are not present in the API runtime.
- **Runtime role:** used by FastAPI through `DATABASE_URL`. It must not own application tables, must not be a superuser, and must not have `CREATEDB`, `CREATEROLE`, `BYPASSRLS` or replication privileges.

Grant the runtime role only the operations required by the application:
- `CONNECT` to the application database and `USAGE` on the application schema.
- `SELECT, INSERT, UPDATE, DELETE` on business tables where the API needs those operations.
- `USAGE, SELECT` on required sequences.
- On `audit_logs`, grant only `SELECT, INSERT`; revoke `UPDATE, DELETE, TRUNCATE`.

Do not grant table ownership to the runtime role. Use a separately managed role name and a secret-manager-managed password; never place a live connection string in Git or CI logs.

## Audit-log immutability

The SQL in `backend/sql/audit_log_immutability.sql` adds a PostgreSQL trigger that rejects row updates and deletes and removes those privileges from `nexusintel_runtime`. Replace that role name only if the actual least-privilege runtime identity differs.

SQLAlchemy ORM listeners in `backend/app/models/audit_log.py` are an additional application-layer safeguard, not a database security boundary. The database trigger and grants are the enforcement layer. A PostgreSQL superuser or table owner can still alter triggers/records; protect those credentials, enable database audit logging, and export audit events to a separately administered append-only destination for high-assurance deployments.

## TLS

The application refuses SQLite in production and configures PostgreSQL TLS with `sslmode=require` when no explicit stronger mode is supplied. Prefer `verify-full` with a trusted CA bundle where the provider supports it. Do not weaken TLS to `disable` or `prefer`.

## Backup and restore

Use a dedicated backup identity with read access to the required schemas. Store backups encrypted, outside the production database account, with retention and access controls. Example commands use environment variables injected by the approved secret manager:

```bash
pg_dump --format=custom --no-owner --no-acl "$BACKUP_DATABASE_URL" \
  --file="nexusintel-$(date -u +%Y%m%dT%H%M%SZ).dump"

# Restore into a separate recovery database first; never overwrite production
# as an untested recovery exercise.
pg_restore --clean --if-exists --no-owner --no-acl \
  --dbname="$RESTORE_DATABASE_URL" "nexusintel-backup.dump"
```

Operational requirements:
1. Encrypt backups at rest and in transit; restrict download/decryption to recovery operators.
2. Define and approve RPO/RTO values before launch.
3. Schedule backups and verify completion independently of application logs.
4. Perform periodic restore drills into an isolated database.
5. Verify schema, row counts, critical tenant boundaries and application startup after restore.
6. Record backup age, restore duration and integrity checks without exposing database URLs or credentials.

## Current verification state

- PostgreSQL TLS enforcement is configured in `backend/app/database/database.py`.
- Runtime-role grants and the audit trigger are provided as an operator-applied SQL script; they have **not** been executed against any database.
- Backup/restore commands are guidance only; no production or real customer data was accessed.
- No automated backup scheduler, retention policy, restore drill, or external immutable audit sink has been configured. These remain deployment responsibilities and release blockers until evidenced.
