import ast
from pathlib import Path


def test_backend_does_not_build_sql_with_f_strings_or_formatting():
    backend_app = Path(__file__).resolve().parents[1] / "app"
    violations = []
    for source_path in backend_app.rglob("*.py"):
        tree = ast.parse(source_path.read_text(), filename=str(source_path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not node.args:
                continue
            function_name = (
                node.func.id
                if isinstance(node.func, ast.Name)
                else node.func.attr
                if isinstance(node.func, ast.Attribute)
                else ""
            )
            if function_name not in {"execute", "text", "exec_driver_sql"}:
                continue
            first = node.args[0]
            if isinstance(first, ast.JoinedStr):
                violations.append(f"{source_path}:{node.lineno}")
            if (
                isinstance(first, ast.Call)
                and isinstance(first.func, ast.Attribute)
                and first.func.attr == "format"
            ):
                violations.append(f"{source_path}:{node.lineno}")
    assert violations == []


def test_no_unrestricted_file_upload_routes_exist_without_explicit_policy():
    backend_app = Path(__file__).resolve().parents[1] / "app"
    source = "\n".join(path.read_text() for path in backend_app.rglob("*.py"))
    # This MVP currently has no file-upload endpoint. Any future addition must
    # introduce a dedicated allowlist/size/content-type scanning policy first.
    assert "UploadFile" not in source
    assert "File(" not in source


def test_frontend_avoids_raw_html_injection_apis():
    frontend = Path(__file__).resolve().parents[2] / "frontend"
    source_files = [
        path for path in frontend.rglob("*")
        if path.suffix in {".tsx", ".ts", ".jsx", ".js"}
        and "node_modules" not in path.parts
        and ".next" not in path.parts
    ]
    source = "\n".join(path.read_text() for path in source_files)
    assert "dangerouslySetInnerHTML" not in source
    assert ".innerHTML" not in source
    assert ".outerHTML" not in source



def test_postgres_audit_trigger_and_runtime_grants_are_documented():
    root = Path(__file__).resolve().parents[2]
    sql = (root / "backend" / "sql" / "audit_log_immutability.sql").read_text()
    assert "BEFORE UPDATE OR DELETE" in sql
    assert "REVOKE UPDATE, DELETE, TRUNCATE" in sql
    assert "GRANT SELECT, INSERT" in sql
