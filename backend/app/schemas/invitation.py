from pydantic import BaseModel, ConfigDict, EmailStr, Field


class InvitationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    email: EmailStr
    role_id: int = Field(gt=0)


class InvitationAccept(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

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

    model_config = ConfigDict(from_attributes=True)


class InvitationCreatedResponse(InvitationResponse):
    token: str


class InvitationAcceptResponse(BaseModel):
    success: bool
