-- Run as DBA/migration owner after creating nexusintel_app and nexusintel_migrator.
-- nexusintel_app must not own the schema or tables and must not be superuser.
-- Set a password through the database provider/secret manager, not in this file.

REVOKE CREATE ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM nexusintel_app;
GRANT USAGE ON SCHEMA public TO nexusintel_app;

-- Operational data requires normal CRUD. Audit logs are narrowed immediately below.
GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA public
TO nexusintel_app;

GRANT USAGE, SELECT
ON ALL SEQUENCES IN SCHEMA public
TO nexusintel_app;

REVOKE UPDATE, DELETE, TRUNCATE
ON TABLE public.audit_logs
FROM nexusintel_app;
GRANT SELECT, INSERT
ON TABLE public.audit_logs
TO nexusintel_app;

-- Ensure future tables created by the separate migration identity inherit the
-- same application DML permissions. The audit table is narrowed separately
-- after creation by applying audit_log_hardening.sql.
ALTER DEFAULT PRIVILEGES FOR ROLE nexusintel_migrator IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO nexusintel_app;

ALTER DEFAULT PRIVILEGES FOR ROLE nexusintel_migrator IN SCHEMA public
GRANT USAGE, SELECT ON SEQUENCES TO nexusintel_app;
