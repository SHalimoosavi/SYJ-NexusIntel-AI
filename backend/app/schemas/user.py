from pydantic import BaseModel
from pydantic import EmailStr


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr

    model_config = {
        "from_attributes": True
    }


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
