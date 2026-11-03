import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

EMAIL_REGEX = re.compile(r"^[\w\.-]+@([\w-]+\.)+[\w-]{2,4}$")


class UserRegisterRequest(BaseModel):
    email: str = Field(..., max_length=255, description="User email address")
    password: str = Field(..., min_length=8, description="Password with minimum 8 characters")
    display_name: Optional[str] = Field(None, max_length=100, description="Optional full name or display name")

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        clean = v.strip().lower()
        if not EMAIL_REGEX.match(clean):
            raise ValueError("Invalid email format.")
        return clean


class UserLoginRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        clean = v.strip().lower()
        if not EMAIL_REGEX.match(clean):
            raise ValueError("Invalid email format.")
        return clean


class UserResponse(BaseModel):
    id: str
    email: str
    account_status: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
