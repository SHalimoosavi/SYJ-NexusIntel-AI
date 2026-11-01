from pydantic import BaseModel, Field, EmailStr


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr

    organization_id: int | None = None
    role_id: int | None = None

    model_config = {
        "from_attributes": True
    }


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=12, max_length=128)
