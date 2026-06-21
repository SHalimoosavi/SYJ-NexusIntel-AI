from pydantic import BaseModel
from pydantic import EmailStr


class UserRoleUpdate(BaseModel):
    role_id: int


class UserStatusUpdate(BaseModel):
    is_active: bool


class UserManagementResponse(BaseModel):
    id: int

    full_name: str
    email: EmailStr

    organization_id: int | None = None
    role_id: int | None = None

    is_active: bool

    created_at: str | None = None

    model_config = {
        "from_attributes": True
    }
