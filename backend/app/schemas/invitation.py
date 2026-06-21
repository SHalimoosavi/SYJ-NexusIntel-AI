from pydantic import BaseModel
from pydantic import EmailStr


class InvitationCreate(BaseModel):
    email: EmailStr
    role_id: int


class InvitationAccept(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    invitation_token: str


class InvitationResponse(BaseModel):
    id: int

    organization_id: int

    email: EmailStr

    role_id: int

    token: str

    is_used: bool

    model_config = {
        "from_attributes": True
    }
