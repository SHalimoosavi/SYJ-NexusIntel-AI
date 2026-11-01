from app.schemas.agent_memory import AgentMemoryResponse
from app.schemas.invitation import InvitationCreatedResponse, InvitationResponse
from app.schemas.lead import LeadResponse
from app.schemas.report import ReportGenerationResponse
from app.schemas.user_management import UserManagementResponse


def test_user_and_lead_responses_exclude_password_hash_and_tenant_internal_fields():
    assert "hashed_password" not in UserManagementResponse.model_fields
    assert "organization_id" not in UserManagementResponse.model_fields
    assert "hashed_password" not in LeadResponse.model_fields
    assert "organization_id" not in LeadResponse.model_fields


def test_agent_memory_and_report_responses_exclude_internal_storage_fields():
    assert "organization_id" not in AgentMemoryResponse.model_fields
    assert "pdf_path" not in ReportGenerationResponse.model_fields


def test_invitation_token_is_only_present_on_explicit_one_time_creation_response():
    assert "token" not in InvitationResponse.model_fields
    assert "token" in InvitationCreatedResponse.model_fields
