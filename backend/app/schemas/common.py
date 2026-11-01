from pydantic import BaseModel, ConfigDict, Field


class SuccessResponse(BaseModel):
    success: bool


class AuthSessionResponse(BaseModel):
    success: bool
    token_type: str = Field(pattern="^cookie$")


class PasswordChangedResponse(BaseModel):
    success: bool
    message: str


class HealthResponse(BaseModel):
    status: str
    product: str
    version: str


class ReadinessResponse(BaseModel):
    success: bool
    message: str


class GenericErrorResponse(BaseModel):
    detail: str

    model_config = ConfigDict(extra="forbid")
