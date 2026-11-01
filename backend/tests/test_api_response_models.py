from app.schemas.common import AuthSessionResponse, PasswordChangedResponse, SuccessResponse
from app.schemas.lead import LeadResponse
from app.schemas.user_management import UserManagementResponse
from app.schemas.invitation import InvitationResponse
from app.schemas.subscription import SubscriptionResponse
from app.schemas.audit import AuditResponse


def test_user_response_contract_does_not_expose_password_hash_or_tokens():
    fields = set(UserManagementResponse.model_fields)
    assert "hashed_password" not in fields
    assert "password" not in fields
    assert "access_token" not in fields
    assert "refresh_token" not in fields


def test_lead_response_contract_does_not_expose_internal_tenant_or_auth_fields():
    fields = set(LeadResponse.model_fields)
    assert "hashed_password" not in fields
    assert "access_token" not in fields
    assert "refresh_token" not in fields
    assert "organization_id" not in fields


def test_cookie_auth_response_contract_contains_no_token_value():
    fields = set(AuthSessionResponse.model_fields)
    assert fields == {"success", "token_type"}
    assert "token" not in fields


def test_mutation_responses_are_allowlisted():
    assert set(SuccessResponse.model_fields) == {"success"}
    assert set(PasswordChangedResponse.model_fields) == {"success", "message"}


def test_tenant_and_actor_foreign_keys_are_not_in_list_responses():
    assert "organization_id" not in InvitationResponse.model_fields
    assert "role_id" not in InvitationResponse.model_fields
    assert "organization_id" not in SubscriptionResponse.model_fields
    assert "organization_id" not in AuditResponse.model_fields
    assert "user_id" not in AuditResponse.model_fields
    assert "resource_id" not in AuditResponse.model_fields
