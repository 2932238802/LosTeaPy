from pydantic import BaseModel, Field


class SendCodeRequest(BaseModel):
    email: str


class MessageResponse(BaseModel):
    message: str


class RegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=6, max_length=128)
    code: str = Field(min_length=4, max_length=10)


class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=1, max_length=128)


class UserResponse(BaseModel):
    id: int
    email: str
    username: str | None = None
    is_admin: bool = False


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
