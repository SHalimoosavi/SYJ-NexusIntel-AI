from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr


class UserRoleUpdate(BaseModel):
    role_id: int


class UserStatusUpdate(BaseModel):
    is_active: bool


class UserManagementResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role_id: int | None = None
    is_active: bool
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
