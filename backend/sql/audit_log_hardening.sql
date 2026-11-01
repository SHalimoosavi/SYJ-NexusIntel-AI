-- Apply as a DBA/migration role after verifying public.audit_logs exists.
-- The runtime application role must be named nexusintel_app and must not own this table.

CREATE OR REPLACE FUNCTION public.reject_audit_log_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'audit log rows are append-only';
END;
$$;

DROP TRIGGER IF EXISTS audit_logs_append_only ON public.audit_logs;
CREATE TRIGGER audit_logs_append_only
BEFORE UPDATE OR DELETE ON public.audit_logs
FOR EACH ROW
EXECUTE FUNCTION public.reject_audit_log_mutation();

REVOKE UPDATE, DELETE, TRUNCATE ON TABLE public.audit_logs FROM nexusintel_app;
GRANT SELECT, INSERT ON TABLE public.audit_logs TO nexusintel_app;
