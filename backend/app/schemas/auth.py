import re

from pydantic import BaseModel, EmailStr, Field, field_validator

PASSWORD_POLICY = (
    "A senha deve ter ao menos 8 caracteres, incluindo letra maiúscula, "
    "minúscula e número."
)


def _validate_password_strength(value: str) -> str:
    if len(value) < 8:
        raise ValueError(PASSWORD_POLICY)
    if not re.search(r"[A-Z]", value):
        raise ValueError(PASSWORD_POLICY)
    if not re.search(r"[a-z]", value):
        raise ValueError(PASSWORD_POLICY)
    if not re.search(r"\d", value):
        raise ValueError(PASSWORD_POLICY)
    return value


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(max_length=128)

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        return _validate_password_strength(value)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
