from fastapi.routing import APIRoute

from app.core.dependencies import get_current_user
from app.main import app


PUBLIC_AUTHENTICATION_ROUTES = {
    ("POST", "/auth/login"),
    ("POST", "/auth/refresh"),
    ("POST", "/auth/logout"),
    ("POST", "/invitations/accept"),
    ("GET", "/"),
    ("GET", "/health"),
}


def _has_dependency(dependant, target) -> bool:
    for child in dependant.dependencies:
        if child.call is target or _has_dependency(child, target):
            return True
    return False


def test_every_non_public_api_route_requires_database_authenticated_user():
    missing = []
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        if not route.include_in_schema:
            continue
        for method in route.methods or set():
            if (method, route.path) in PUBLIC_AUTHENTICATION_ROUTES:
                continue
            if not _has_dependency(route.dependant, get_current_user):
                missing.append((method, route.path))
    assert missing == []


def test_every_documented_api_route_has_an_explicit_response_model():
    missing = [
        (method, route.path)
        for route in app.routes
        if isinstance(route, APIRoute) and route.include_in_schema
        for method in (route.methods or set())
        if route.response_model is None
    ]
    assert missing == []
