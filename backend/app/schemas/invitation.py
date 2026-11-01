from pydantic import BaseModel, EmailStr, Field


class InvitationCreate(BaseModel):
    email: EmailStr
    role_id: int = Field(gt=0)


class InvitationAccept(BaseModel):
    full_name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    invitation_token: str = Field(min_length=32, max_length=256)


class InvitationResponse(BaseModel):
    id: int
    organization_id: int
    email: EmailStr
    role_id: int
    is_used: bool

    model_config = {"from_attributes": True}


class InvitationCreatedResponse(InvitationResponse):
    token: str


class InvitationAcceptResponse(BaseModel):
    success: bool
