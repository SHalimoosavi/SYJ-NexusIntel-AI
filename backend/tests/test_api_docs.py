from app.core.api_docs import api_docs_config


def test_production_disables_all_schema_endpoints():
    config = api_docs_config("production")
    assert config == {
        "docs_url": None,
        "redoc_url": None,
        "openapi_url": None,
    }


def test_prod_alias_disables_all_schema_endpoints():
    assert api_docs_config("prod") == {
        "docs_url": None,
        "redoc_url": None,
        "openapi_url": None,
    }


def test_development_keeps_docs_enabled():
    assert api_docs_config("development") == {
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "openapi_url": "/openapi.json",
    }
