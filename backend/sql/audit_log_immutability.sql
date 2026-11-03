-- Run with a dedicated migration/DB-owner role, never the application role.
-- The runtime role must not own audit_logs and must not be a PostgreSQL superuser.

CREATE OR REPLACE FUNCTION public.prevent_audit_log_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'audit log records are append-only';
END;
$$;

DROP TRIGGER IF EXISTS audit_logs_no_update_delete ON public.audit_logs;
CREATE TRIGGER audit_logs_no_update_delete
BEFORE UPDATE OR DELETE ON public.audit_logs
FOR EACH ROW
EXECUTE FUNCTION public.prevent_audit_log_mutation();

-- Create this role separately with a secret manager-managed password.
REVOKE UPDATE, DELETE, TRUNCATE ON TABLE public.audit_logs FROM nexusintel_runtime;
GRANT SELECT, INSERT ON TABLE public.audit_logs TO nexusintel_runtime;
