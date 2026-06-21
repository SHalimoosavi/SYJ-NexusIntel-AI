from pydantic import BaseModel
from pydantic import EmailStr


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr

    organization_id: int | None = None
    role_id: int | None = None

    model_config = {
        "from_attributes": True
    }


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
